/* Lịch sử mượn/trả/phạt của độc giả (UC10) — chỉ reader. */
(function () {
  var API = window.API;
  var Auth = window.Auth;
  var messageTimer = null;

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

  function loadHistory() {
    setLoading(true);
    API.call("myBorrows")
      .then(function (res) {
        setLoading(false);
        if (!res.ok) {
          showMessage(res.message);
          return;
        }
        render(res.data || []);
      })
      .catch(function () {
        setLoading(false);
        showMessage("Đã xảy ra lỗi khi tải lịch sử mượn.");
      });
  }

  function render(list) {
    var tbody = document.getElementById("history-tbody");
    tbody.innerHTML = "";
    if (list.length === 0) {
      var emptyRow = document.createElement("tr");
      var emptyCell = document.createElement("td");
      emptyCell.className = "empty-row";
      emptyCell.colSpan = 8;
      emptyCell.textContent = "Chưa có phiếu mượn nào.";
      emptyRow.appendChild(emptyCell);
      tbody.appendChild(emptyRow);
      return;
    }
    list.forEach(function (item) {
      var slip = API.mapResponse("borrowHistoryOut", item);
      if (!slip) {
        return;
      }
      tbody.appendChild(row(slip));
    });
  }

  function row(slip) {
    var tr = document.createElement("tr");
    var detailsText = (slip.details || [])
      .map(function (d) {
        var detail = API.mapResponse("borrowDetailOut", d);
        return detail ? detail.maSach + " x" + detail.soLuong : "";
      })
      .filter(Boolean)
      .join(", ");

    var fines = (slip.fines || [])
      .map(function (f) {
        var fine = API.mapResponse("fineOut", f);
        return fine ? fine.soNgayQuaHan + " ngày — " + fine.soDiem + " điểm" : "";
      })
      .filter(Boolean)
      .join("; ");

    var status = slip.trangThai === "dang_muon" ? "Đang mượn" : "Đã trả";
    var values = [
      slip.maPhieu,
      detailsText,
      slip.ngayMuon ? new Date(slip.ngayMuon).toLocaleString("vi-VN") : "—",
      slip.hanTra ? new Date(slip.hanTra).toLocaleString("vi-VN") : "—",
      slip.ngayTra ? new Date(slip.ngayTra).toLocaleString("vi-VN") : "—",
      status,
      fines || "—"
    ];
    values.forEach(function (value) {
      var td = document.createElement("td");
      td.textContent = value || "—";
      tr.appendChild(td);
    });

    var actionsTd = document.createElement("td");
    if (slip.trangThai === "da_tra") {
      var actions = document.createElement("div");
      actions.className = "row-actions";
      var del = document.createElement("button");
      del.type = "button";
      del.className = "btn btn-danger";
      del.textContent = "Xoá";
      del.addEventListener("click", function () {
        deleteOne(slip);
      });
      actions.appendChild(del);
      actionsTd.appendChild(actions);
    } else {
      actionsTd.textContent = "—";
    }
    tr.appendChild(actionsTd);
    return tr;
  }

  function deleteOne(slip) {
    var ok = window.confirm('Xoá lịch sử phiếu "' + slip.maPhieu + '"?');
    if (!ok) {
      return;
    }
    API.call("deleteMyBorrow", undefined, "DELETE", { ma_phieu: slip.maPhieu })
      .then(function (res) {
        if (!res.ok) {
          showMessage(res.message);
          return;
        }
        showMessage("Đã xoá lịch sử phiếu " + slip.maPhieu + ".", "alert-success");
        loadHistory();
      })
      .catch(function () {
        showMessage("Đã xảy ra lỗi khi xoá lịch sử.");
      });
  }

  function deleteAll() {
    var ok = window.confirm("Xoá toàn bộ lịch sử mượn (chỉ các phiếu đã trả)?");
    if (!ok) {
      return;
    }
    API.call("deleteMyBorrows", undefined, "DELETE")
      .then(function (res) {
        if (!res.ok) {
          showMessage(res.message);
          return;
        }
        showMessage("Đã xoá toàn bộ lịch sử.", "alert-success");
        loadHistory();
      })
      .catch(function () {
        showMessage("Đã xảy ra lỗi khi xoá lịch sử.");
      });
  }

  document.addEventListener("DOMContentLoaded", function () {
    if (!Auth.requireReader()) {
      return;
    }
    Auth.applyRoleUI();
    var clearButton = document.getElementById("clear-history-button");
    if (clearButton) {
      clearButton.addEventListener("click", deleteAll);
    }
    loadHistory();
  });
})();
