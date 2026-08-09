/* Trang yêu cầu — reader gửi/xem; librarian duyệt/từ chối (UC07/08/09/15-17). */
(function () {
  var API = window.API;
  var Auth = window.Auth;
  var messageTimer = null;
  var availableBooks = [];
  var loadToken = 0;
  var pendingApprove = null;
  var bookTitles = {};

  function showMessage(text, type) {
    var el = document.getElementById("page-message");
    if (!el) {
      return;
    }
    if (messageTimer) {
      clearTimeout(messageTimer);
    }
    el.className = "alert " + (type || "alert-error");
    el.textContent = text;
    el.hidden = false;
    messageTimer = setTimeout(function () {
      el.hidden = true;
      messageTimer = null;
    }, 6000);
  }

  function setLoading(visible) {
    var el = document.getElementById("loading");
    if (el) {
      el.hidden = !visible;
    }
  }

  function LOAI_LABEL(loai) {
    return { MUON: "Mượn sách", DAT_TRUOC: "Đặt trước sách", TRA: "Trả sách", GIA_HAN: "Gia hạn" }[loai] || loai;
  }

  function newRequestMa() {
    /*
     * Mã yêu cầu tự sinh: timestamp base36 (8 ký tự) + 8 ký tự ngẫu nhiên.
     * Tổng "YC" + 16 = 18 ký tự (đúng max 18 của API). Không gian ngẫu nhiên
     * 36^8 ≈ 2.8 nghìn tỷ — xác suất trùng gần bằng 0 kể cả ở tần suất cao.
     */
    return "YC" + Date.now().toString(36).slice(-8) + Math.random().toString(36).slice(2, 10);
  }

  function loadBooksFor(trangThai) {
    var token = ++loadToken;
    var built = API.buildQuery("books", { trangThai: trangThai });
    API.call("books", undefined, "GET", undefined, built.query)
      .then(function (res) {
        if (token !== loadToken) {
          return;
        }
        if (res.ok) {
          availableBooks = (res.data || []).map(function (item) {
            return API.mapResponse("book", item) || item;
          });
          refreshItemSelects();
        }
      })
      .catch(function () {});
  }

  function loadBooksCon() {
    loadBooksFor("con");
  }

  function loadBooksHet() {
    loadBooksFor("dang_muon");
  }

  function refreshItemSelects() {
    document.querySelectorAll(".req-item-book").forEach(function (select) {
      var current = select.value;
      select.innerHTML = '<option value="">— Chọn sách —</option>';
      availableBooks.forEach(function (book) {
        var option = document.createElement("option");
        option.value = book.ma;
        option.textContent = book.ma + " — " + book.ten + " (còn " + book.soLuong + ")";
        select.appendChild(option);
      });
      select.value = current;
    });
  }

  function addReqItem() {
    var container = document.getElementById("req-items");
    var row = document.createElement("div");
    row.className = "borrow-item-row";
    var bookGroup = document.createElement("div");
    bookGroup.className = "form-group borrow-item-book-group";
    var label = document.createElement("label");
    label.textContent = "Sách";
    var select = document.createElement("select");
    select.className = "req-item-book";
    select.innerHTML = '<option value="">— Chọn sách —</option>';
    availableBooks.forEach(function (book) {
      var option = document.createElement("option");
      option.value = book.ma;
      option.textContent = book.ma + " — " + book.ten;
      select.appendChild(option);
    });
    bookGroup.appendChild(label);
    bookGroup.appendChild(select);
    var qtyGroup = document.createElement("div");
    qtyGroup.className = "form-group borrow-item-qty-group";
    var qtyLabel = document.createElement("label");
    qtyLabel.textContent = "Số lượng";
    var qty = document.createElement("input");
    qty.type = "number";
    qty.min = "1";
    qty.value = "1";
    qtyGroup.appendChild(qtyLabel);
    qtyGroup.appendChild(qty);
    var remove = document.createElement("button");
    remove.type = "button";
    remove.className = "btn btn-danger";
    remove.textContent = "Xoá dòng";
    remove.addEventListener("click", function () {
      row.remove();
    });
    row.appendChild(bookGroup);
    row.appendChild(qtyGroup);
    row.appendChild(remove);
    container.appendChild(row);
  }

  function loadMyActiveBorrows() {
    API.call("myBorrows")
      .then(function (res) {
        if (!res.ok) {
          return;
        }
        var select = document.getElementById("req-borrow");
        select.innerHTML = '<option value="">— Chọn phiếu —</option>';
        (res.data || []).forEach(function (item) {
          var slip = API.mapResponse("borrowHistoryOut", item);
          if (!slip) {
            return;
          }
          var isTra = document.getElementById("req-loai").value === "TRA";
          if (slip.trangThai !== "dang_muon") {
            return;
          }
          if (!isTra && Number(slip.soLanGiaHan) >= 1) {
            return;
          }
          var option = document.createElement("option");
          option.value = slip.maPhieu;
          option.textContent = slip.maPhieu + " — hạn " + new Date(slip.hanTra).toLocaleDateString("vi-VN");
          select.appendChild(option);
        });
      })
      .catch(function () {});
  }

  function updateFields() {
    var loai = document.getElementById("req-loai").value;
    var needsBooks = loai === "MUON" || loai === "DAT_TRUOC";
    document.getElementById("req-muon-fields").hidden = !needsBooks;
    document.getElementById("req-borrow-field").hidden = needsBooks;
    if (loai === "DAT_TRUOC") {
      loadBooksHet();
    } else if (loai === "MUON") {
      loadBooksCon();
    }
    loadMyActiveBorrows();
  }

  function createRequest() {
    var ma = document.getElementById("req-ma").value.trim();
    var loai = document.getElementById("req-loai").value;
    if (!ma) {
      showMessage("Vui lòng nhập mã yêu cầu.");
      return;
    }
    var payload = { ma_yeu_cau: ma, loai: loai };
    if (loai === "MUON" || loai === "DAT_TRUOC") {
      var items = [];
      document.querySelectorAll(".req-item-row, #req-items .borrow-item-row").forEach(function (row) {
        var bookSel = row.querySelector(".req-item-book");
        var qtyInput = row.querySelector(".borrow-item-qty-group input");
        if (bookSel && bookSel.value && qtyInput && parseInt(qtyInput.value, 10) >= 1) {
          items.push({ ma_sach: bookSel.value, so_luong: parseInt(qtyInput.value, 10) });
        }
      });
      if (items.length === 0) {
        showMessage("Vui lòng chọn ít nhất 1 sách.");
        return;
      }
      payload.items = items;
      if (loai === "MUON") {
        var soNgay = parseInt(document.getElementById("req-so-ngay").value, 10);
        if (isNaN(soNgay) || soNgay < 1) {
          showMessage("Vui lòng nhập số ngày mượn hợp lệ (>= 1).");
          return;
        }
        /*
         * Reader đề xuất số ngày mượn; thủ thư sẽ xem và xác nhận khi duyệt.
         * Backend chưa lưu field này — cần Backend bổ sung so_ngay_muon.
         */
        payload.so_ngay_muon = soNgay;
      } else {
        /*
         * DAT_TRUOC: đặt trước sách hết. Backend /api/requests hiện chỉ nhận
         * loai MUON/TRA/GIA_HAN — cần Backend bổ sung loai DAT_TRUOC
         * (hoặc Frontend chuyển sang /api/reservations).
         */
        payload.loai = "DAT_TRUOC";
      }
    } else {
      var maPhieu = document.getElementById("req-borrow").value;
      if (!maPhieu) {
        showMessage("Vui lòng chọn phiếu mượn.");
        return;
      }
      payload.ma_phieu = maPhieu;
    }

    API.call("createRequest", payload, "POST")
      .then(function (res) {
        if (!res.ok) {
          if (loai === "DAT_TRUOC") {
            showMessage(
              "Backend chưa hỗ trợ loại 'Đặt trước sách' trong yêu cầu — cần Backend bổ sung loai DAT_TRUOC (hoặc dùng nút Đặt trước ở trang Tra cứu)."
            );
          } else {
            showMessage(res.message);
          }
          return;
        }
        showMessage("Đã gửi yêu cầu " + ma + ".", "alert-success");
        document.getElementById("req-ma").value = newRequestMa();
        loadMyRequests();
        loadMyActiveBorrows();
      })
      .catch(function () {
        showMessage("Đã xảy ra lỗi không xác định khi gửi yêu cầu.");
      });
  }

  function loadMyRequests() {
    API.call("requests")
      .then(function (res) {
        if (!res.ok) {
          showMessage(res.message);
          return;
        }
        renderMyRequests(res.data || []);
      })
      .catch(function () {});
  }

  function renderMyRequests(list) {
    var tbody = document.getElementById("my-request-tbody");
    tbody.innerHTML = "";
    if (list.length === 0) {
      var emptyRow = document.createElement("tr");
      var emptyCell = document.createElement("td");
      emptyCell.className = "empty-row";
      emptyCell.colSpan = 8;
      emptyCell.textContent = "Chưa có yêu cầu nào.";
      emptyRow.appendChild(emptyCell);
      tbody.appendChild(emptyRow);
      return;
    }
    list.forEach(function (item) {
      var req = API.mapResponse("requestOut", item);
      if (!req) {
        return;
      }
      var tr = document.createElement("tr");
      var itemsText = (req.items || [])
        .map(function (i) {
          return i.ma_sach + " x" + i.so_luong;
        })
        .join(", ");
      var values = [
        req.maYeuCau,
        LOAI_LABEL(req.loai),
        req.maPhieu || "—",
        itemsText || "—",
        req.soNgayMuon || "—",
        req.trangThai,
        req.ngayTao ? new Date(req.ngayTao).toLocaleString("vi-VN") : "—"
      ];
      values.forEach(function (v) {
        var td = document.createElement("td");
        td.textContent = v;
        tr.appendChild(td);
      });
      var actionsTd = document.createElement("td");
      if (req.trangThai !== "CHO_XU_LY") {
        var delBtn = document.createElement("button");
        delBtn.type = "button";
        delBtn.className = "btn btn-danger";
        delBtn.textContent = "Xoá";
        delBtn.addEventListener("click", function () {
          deleteRequestOne(req);
        });
        actionsTd.appendChild(delBtn);
      } else {
        actionsTd.textContent = "—";
      }
      tr.appendChild(actionsTd);
      tbody.appendChild(tr);
    });
  }

  function deleteRequestOne(req) {
    var ok = window.confirm('Xoá yêu cầu "' + req.maYeuCau + '" khỏi lịch sử?');
    if (!ok) {
      return;
    }
    API.call("deleteMyRequest", undefined, "DELETE", { id: req.maYeuCau })
      .then(function (res) {
        if (!res.ok) {
          if (res.status === 404 || res.status === 405 || res.code === "API_CHUA_CO_TAI_LIEU") {
            showMessage("Backend chưa hỗ trợ xoá lịch sử yêu cầu (cần API DELETE /api/requests/me/{ma}).");
          } else {
            showMessage(res.message);
          }
          return;
        }
        showMessage("Đã xoá yêu cầu " + req.maYeuCau + ".", "alert-success");
        loadMyRequests();
      })
      .catch(function () {
        showMessage("Đã xảy ra lỗi khi xoá yêu cầu.");
      });
  }

  function deleteAllRequests() {
    var ok = window.confirm("Xoá toàn bộ lịch sử yêu cầu đã xử lý?");
    if (!ok) {
      return;
    }
    API.call("deleteMyRequests", undefined, "DELETE")
      .then(function (res) {
        if (!res.ok) {
          if (res.status === 404 || res.status === 405 || res.code === "API_CHUA_CO_TAI_LIEU") {
            showMessage("Backend chưa hỗ trợ xoá lịch sử yêu cầu (cần API DELETE /api/requests/me).");
          } else {
            showMessage(res.message);
          }
          return;
        }
        showMessage("Đã xoá toàn bộ lịch sử yêu cầu.", "alert-success");
        loadMyRequests();
      })
      .catch(function () {
        showMessage("Đã xảy ra lỗi khi xoá lịch sử yêu cầu.");
      });
  }

  function loadPending() {
    var built = API.buildQuery("requests", { trangThai: "CHO_XU_LY" });
    API.call("requests", undefined, "GET", undefined, built.query)
      .then(function (res) {
        if (!res.ok) {
          showMessage(res.message);
          return;
        }
        renderPending(res.data || []);
      })
      .catch(function () {});
  }

  function loadBookTitles() {
    return API.call("books")
      .then(function (res) {
        if (!res.ok || !Array.isArray(res.data)) {
          return;
        }
        res.data.forEach(function (item) {
          var book = API.mapResponse("book", item);
          if (book && book.ma) {
            bookTitles[book.ma] = book.ten;
          }
        });
      })
      .catch(function () {});
  }

  function renderPending(list) {
    var tbody = document.getElementById("pending-tbody");
    tbody.innerHTML = "";
    if (list.length === 0) {
      var emptyRow = document.createElement("tr");
      var emptyCell = document.createElement("td");
      emptyCell.className = "empty-row";
      emptyCell.colSpan = 8;
      emptyCell.textContent = "Không có yêu cầu chờ xử lý.";
      emptyRow.appendChild(emptyCell);
      tbody.appendChild(emptyRow);
      return;
    }
    list.forEach(function (item) {
      var req = API.mapResponse("requestOut", item);
      if (!req) {
        return;
      }
      var tr = document.createElement("tr");
      var itemsText = (req.items || [])
        .map(function (i) {
          return (bookTitles[i.ma_sach] || i.ma_sach) + " x" + i.so_luong;
        })
        .join(", ");
      var values = [
        itemsText || "—",
        LOAI_LABEL(req.loai),
        req.maDocGia,
        req.maPhieu || "—",
        (req.items || []).map(function (i) { return i.ma_sach; }).join(", ") || "—",
        req.soNgayMuon || "—",
        req.ngayTao ? new Date(req.ngayTao).toLocaleString("vi-VN") : "—",
        null
      ];
      values.forEach(function (v, index) {
        var td = document.createElement("td");
        if (index === 7) {
          var actions = document.createElement("div");
          actions.className = "row-actions";
          var approve = document.createElement("button");
          approve.type = "button";
          approve.className = "btn btn-primary";
          approve.textContent = "Duyệt";
          approve.addEventListener("click", function () {
            decide(req, "approve");
          });
          var reject = document.createElement("button");
          reject.type = "button";
          reject.className = "btn btn-danger";
          reject.textContent = "Từ chối";
          reject.addEventListener("click", function () {
            decide(req, "reject");
          });
          actions.appendChild(approve);
          actions.appendChild(reject);
          td.appendChild(actions);
        } else {
          td.textContent = v;
        }
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
  }

  function decide(req, action) {
    if (action === "approve" && req.loai === "MUON") {
      pendingApprove = { req: req, action: action };
      document.getElementById("approve-ma").textContent = req.maYeuCau;
      document.getElementById("approve-days").value = req.soNgayMuon || "14";
      document.getElementById("approve-modal").hidden = false;
      return;
    }
    doDecide(req, action, undefined);
  }

  function doDecide(req, action, days) {
    var name = action === "approve" ? "approveRequest" : "rejectRequest";
    var body = {};
    if (days !== undefined && days !== null) {
      /*
       * so_ngay_muon: thủ thư nhập khi duyệt yêu cầu MUON của reader.
       * Backend chưa nhận body này — cần Backend bổ sung.
       */
      body.so_ngay_muon = days;
    }
    API.call(name, body, "PUT", { id: req.maYeuCau })
      .then(function (res) {
        if (!res.ok) {
          showMessage(res.message);
          return;
        }
        showMessage(
          action === "approve" ? "Đã duyệt yêu cầu " + req.maYeuCau + "." : "Đã từ chối yêu cầu " + req.maYeuCau + ".",
          "alert-success"
        );
        loadPending();
      })
      .catch(function () {
        showMessage("Đã xảy ra lỗi khi xử lý yêu cầu.");
      });
  }

  function confirmApprove() {
    if (!pendingApprove) {
      return;
    }
    var days = parseInt(document.getElementById("approve-days").value, 10);
    if (isNaN(days) || days < 1) {
      showMessage("Số ngày mượn không hợp lệ (phải >= 1).");
      return;
    }
    document.getElementById("approve-modal").hidden = true;
    var target = pendingApprove;
    pendingApprove = null;
    doDecide(target.req, target.action, days);
  }

  function cancelApprove() {
    pendingApprove = null;
    document.getElementById("approve-modal").hidden = true;
  }

  function init() {
    var user = Auth.currentUser();
    if (!user) {
      window.location.replace("index.html");
      return;
    }
    if (user.role === "admin") {
      window.location.replace("search.html");
      return;
    }
    Auth.applyRoleUI();

    if (user.role === "reader") {
      document.getElementById("req-loai").addEventListener("change", updateFields);
      document.getElementById("add-req-item").addEventListener("click", addReqItem);
      document.getElementById("create-request-button").addEventListener("click", createRequest);
      document.getElementById("clear-my-requests").addEventListener("click", deleteAllRequests);
      document.getElementById("req-ma").value = newRequestMa();
      loadBooksCon();
      addReqItem();
      updateFields();
      loadMyRequests();
    } else {
      document.getElementById("approve-confirm").addEventListener("click", confirmApprove);
      document.getElementById("approve-cancel").addEventListener("click", cancelApprove);
      loadBookTitles().then(loadPending);
    }
  }

  document.addEventListener("DOMContentLoaded", init);
})();
