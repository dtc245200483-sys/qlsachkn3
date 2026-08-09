/* Trang tra cứu sách — mọi vai trò đã đăng nhập đều dùng được. */
(function () {
  var API = window.API;
  var Auth = window.Auth;
  var messageTimer = null;
  var theLoaiSet = {};

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
    }, 5000);
  }

  function clearMessage() {
    if (messageTimer) {
      clearTimeout(messageTimer);
      messageTimer = null;
    }
    var el = document.getElementById("page-message");
    if (el) {
      el.hidden = true;
    }
  }

  function setLoading(visible) {
    var el = document.getElementById("loading");
    if (el) {
      el.hidden = !visible;
    }
  }

  /*
   * Backend GET /api/books hiện chưa hỗ trợ q/theLoai/trangThai
   * (api_docs 0.3.0) nên ngoài việc gửi query đúng tên, tạm thời lọc
   * client-side để trang dùng được ngay. Khi Backend bổ sung param,
   * bỏ phần lọc này (chỉ giữ API.call với buildQuery).
   */
  function clientFilter(list, filters) {
    return list.filter(function (book) {
      if (filters.q) {
        var needle = filters.q.toLowerCase();
        var haystack = ((book.ten || "") + " " + (book.tacGia || "")).toLowerCase();
        if (haystack.indexOf(needle) === -1) {
          return false;
        }
      }
      if (filters.theLoai && book.theLoai !== filters.theLoai) {
        return false;
      }
      if (filters.trangThai === "con" && !(book.soLuong > 0)) {
        return false;
      }
      if (
        (filters.trangThai === "het" || filters.trangThai === "dang_muon") &&
        book.soLuong > 0
      ) {
        return false;
      }
      /*
       * Lưu ý: "dang_muon" hiện tạm tính như soLuong = 0 (cùng dữ liệu
       * với "het") vì Backend chưa có API trả trạng thái mượn thật.
       * Khi Backend bổ sung, tách 2 trạng thái này theo dữ liệu mượn.
       */
      return true;
    });
  }

  function addTheLoaiOptions(list) {
    var select = document.getElementById("search-theloai");
    if (!select) {
      return;
    }
    var current = select.value;
    list.forEach(function (book) {
      var value = book.theLoai;
      if (value && !theLoaiSet[value]) {
        theLoaiSet[value] = true;
        var option = document.createElement("option");
        option.value = value;
        option.textContent = value;
        select.appendChild(option);
      }
    });
    select.value = current;
  }

  function parseSort(value) {
    if (!value) {
      return { sort: "", order: "" };
    }
    var parts = String(value).split("_");
    return { sort: parts[0] || "", order: parts[1] || "asc" };
  }

  function loadBooks() {
    clearMessage();
    setLoading(true);
    var q = document.getElementById("search-q").value.trim();
    var theLoai = document.getElementById("search-theloai").value;
    var trangThai = document.getElementById("search-trangthai").value;
    var sortParsed = parseSort(document.getElementById("search-sort").value);
    var built = API.buildQuery("books", {
      q: q,
      theLoai: theLoai,
      trangThai: trangThai,
      sort: sortParsed.sort,
      order: sortParsed.order
    });

    API.call("books", undefined, "GET", undefined, built.query)
      .then(function (res) {
        setLoading(false);
        if (!res.ok) {
          showMessage(res.message);
          return;
        }
        if (!Array.isArray(res.data)) {
          showMessage("API trả về danh sách sách không đúng định dạng.");
          return;
        }
        addTheLoaiOptions(res.data);
        var list = clientFilter(res.data, { q: q, theLoai: theLoai, trangThai: trangThai });
        if (!API.config.sortBooksBackend) {
          list = API.sortBooks(list, sortParsed.sort, sortParsed.order);
        }
        render(list);
      })
      .catch(function () {
        setLoading(false);
        showMessage("Đã xảy ra lỗi không xác định khi tra cứu sách.");
      });
  }

  function render(list) {
    var tbody = document.getElementById("search-tbody");
    if (!tbody) {
      return;
    }
    tbody.innerHTML = "";

    if (list.length === 0) {
      var emptyRow = document.createElement("tr");
      var emptyCell = document.createElement("td");
      emptyCell.className = "empty-row";
      emptyCell.colSpan = 9;
      emptyCell.textContent = "Không tìm thấy sách nào phù hợp.";
      emptyRow.appendChild(emptyCell);
      tbody.appendChild(emptyRow);
      return;
    }

    list.forEach(function (book) {
      var mapped = API.mapResponse("book", book);
      if (!mapped) {
        return;
      }
      tbody.appendChild(row(mapped));
    });
  }

  function row(book) {
    var tr = document.createElement("tr");
    var values = [
      book.ma,
      book.ten,
      book.tacGia,
      book.theLoai,
      book.nxb,
      book.namXb,
      book.soLuong
    ];
    values.forEach(function (value) {
      var td = document.createElement("td");
      td.textContent = value === "" || value === null ? "—" : value;
      tr.appendChild(td);
    });

    var statusTd = document.createElement("td");
    var available = Number(book.soLuong) > 0;
    var badge = document.createElement("span");
    if (available) {
      badge.className = "status-badge status-badge--active";
      badge.textContent = "Còn";
    } else {
      badge.className = "status-badge status-badge--warning";
      badge.textContent = "Hết sách";
    }
    statusTd.appendChild(badge);
    tr.appendChild(statusTd);

    var actionsTd = document.createElement("td");
    var user = Auth.currentUser();
    if (user && user.role === "reader" && Number(book.soLuong) <= 0) {
      var reserveBtn = document.createElement("button");
      reserveBtn.type = "button";
      reserveBtn.className = "btn btn-primary";
      reserveBtn.textContent = "Đặt trước";
      reserveBtn.addEventListener("click", function () {
        reserveBtn.disabled = true;
        reserveBtn.textContent = "Đã gửi...";
        API.call("createReservation", { ma_sach: book.ma }, "POST").then(function (res) {
          if (!res.ok) {
            reserveBtn.disabled = false;
            reserveBtn.textContent = "Đặt trước";
            showMessage(res.message);
            return;
          }
          reserveBtn.textContent = "Đã đặt trước";
          showMessage("Đã gửi yêu cầu đặt trước sách " + book.ten + ".", "alert-success");
        });
      });
      actionsTd.appendChild(reserveBtn);
    } else {
      actionsTd.textContent = "—";
    }
    tr.appendChild(actionsTd);
    return tr;
  }

  function init() {
    if (!Auth.requireAuth()) {
      return;
    }
    Auth.applyRoleUI();

    var searchButton = document.getElementById("search-button");
    if (searchButton) {
      searchButton.addEventListener("click", loadBooks);
    }
    var clearButton = document.getElementById("clear-search-button");
    if (clearButton) {
      clearButton.addEventListener("click", function () {
        document.getElementById("search-q").value = "";
        document.getElementById("search-theloai").value = "";
        document.getElementById("search-trangthai").value = "";
        document.getElementById("search-sort").value = "";
        loadBooks();
      });
    }
    var sortSelect = document.getElementById("search-sort");
    if (sortSelect) {
      sortSelect.addEventListener("change", loadBooks);
    }
    var qInput = document.getElementById("search-q");
    if (qInput) {
      qInput.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
          loadBooks();
        }
      });
    }

    loadBooks();
  }

  document.addEventListener("DOMContentLoaded", init);
})();
