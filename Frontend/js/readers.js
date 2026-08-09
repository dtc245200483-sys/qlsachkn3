/* Trang quản lý độc giả (admin + librarian; xoá chỉ admin). */
(function () {
  var API = window.API;
  var Auth = window.Auth;
  var state = { editId: null };
  var messageTimer = null;

  var LOAI_LABEL = {
    sinh_vien: "Sinh viên",
    giang_vien: "Giảng viên",
    khac: "Khác"
  };

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

  function canDelete() {
    var user = Auth.currentUser();
    return !!user && user.role === "admin";
  }

  function canManage() {
    var user = Auth.currentUser();
    return !!user && user.role === "admin";
  }

  function loadReaders(opts) {
    if (!opts || opts.clear !== false) {
      clearMessage();
    }
    setLoading(true);
    var q = document.getElementById("reader-q").value.trim();
    API.call("readers", undefined, "GET", undefined, { q: q })
      .then(function (res) {
        setLoading(false);
        if (!res.ok) {
          showMessage(res.message);
          return;
        }
        if (!Array.isArray(res.data)) {
          showMessage("API trả về danh sách độc giả không đúng định dạng.");
          return;
        }
        render(res.data);
      })
      .catch(function () {
        setLoading(false);
        showMessage("Đã xảy ra lỗi không xác định khi tải danh sách độc giả.");
      });
  }

  function render(list) {
    var tbody = document.getElementById("reader-tbody");
    if (!tbody) {
      return;
    }
    tbody.innerHTML = "";

    if (list.length === 0) {
      var emptyRow = document.createElement("tr");
      var emptyCell = document.createElement("td");
      emptyCell.className = "empty-row";
      emptyCell.colSpan = 8;
      emptyCell.textContent = "Không tìm thấy độc giả nào.";
      emptyRow.appendChild(emptyCell);
      tbody.appendChild(emptyRow);
      return;
    }

    list.forEach(function (item) {
      var reader = API.mapResponse("readerOut", item);
      if (!reader) {
        showMessage("Chưa có cấu hình field độc giả trong api.js.");
        return;
      }
      tbody.appendChild(row(reader));
    });
  }

  function row(reader) {
    var tr = document.createElement("tr");

    var values = [
      reader.ma,
      reader.hoTen,
      reader.email,
      reader.soDienThoai,
      LOAI_LABEL[reader.loaiDocGia] || reader.loaiDocGia,
      null,
      reader.ngayTao ? new Date(reader.ngayTao).toLocaleString("vi-VN") : "—"
    ];

    values.forEach(function (value, index) {
      var td = document.createElement("td");
      if (index === 5) {
        var badge = document.createElement("span");
        var active = reader.trangThaiThe === "hoat_dong";
        badge.className = "status-badge " + (active ? "status-badge--active" : "status-badge--locked");
        badge.textContent = active ? "Hoạt động" : "Đã khoá";
        td.appendChild(badge);
      } else {
        td.textContent = value === "" || value === null ? "—" : value;
      }
      tr.appendChild(td);
    });

    var actionsTd = document.createElement("td");
    var actions = document.createElement("div");
    actions.className = "row-actions";

    if (canManage()) {
      var editBtn = document.createElement("button");
      editBtn.type = "button";
      editBtn.className = "btn btn-secondary";
      editBtn.textContent = "Sửa";
      editBtn.addEventListener("click", function () {
        openForm(reader);
      });
      actions.appendChild(editBtn);
    }

    var lockBtn = document.createElement("button");
    lockBtn.type = "button";
    lockBtn.className = "btn btn-secondary";
    lockBtn.textContent = reader.trangThaiThe === "hoat_dong" ? "Khoá thẻ" : "Mở khoá";
    lockBtn.addEventListener("click", function () {
      toggleLock(reader);
    });

    actions.appendChild(lockBtn);

    if (canDelete()) {
      var deleteBtn = document.createElement("button");
      deleteBtn.type = "button";
      deleteBtn.className = "btn btn-danger";
      deleteBtn.textContent = "Xoá";
      deleteBtn.addEventListener("click", function () {
        deleteReader(reader);
      });
      actions.appendChild(deleteBtn);
    }

    actionsTd.appendChild(actions);
    tr.appendChild(actionsTd);
    return tr;
  }

  function openForm(reader) {
    state.editId = reader ? reader.ma : null;
    var form = document.getElementById("reader-form");
    var title = document.getElementById("reader-form-title");
    var modal = document.getElementById("reader-modal");
    var maInput = document.getElementById("reader-ma");

    if (title) {
      title.textContent = reader ? "Sửa độc giả" : "Thêm độc giả";
    }
    if (form) {
      form.reset();
      if (reader) {
        form.elements.hoTen.value = reader.hoTen;
        form.elements.email.value = reader.email;
        form.elements.soDienThoai.value = reader.soDienThoai;
        form.elements.loaiDocGia.value = reader.loaiDocGia;
        form.elements.trangThaiThe.value = reader.trangThaiThe;
      } else {
        form.elements.loaiDocGia.value = "sinh_vien";
        form.elements.trangThaiThe.value = "hoat_dong";
      }
    }
    if (maInput) {
      maInput.disabled = !!reader;
      maInput.value = reader ? reader.ma : "";
    }
    if (modal) {
      modal.hidden = false;
    }
  }

  function closeForm() {
    var modal = document.getElementById("reader-modal");
    if (modal) {
      modal.hidden = true;
    }
    state.editId = null;
  }

  function saveForm(e) {
    e.preventDefault();
    var form = document.getElementById("reader-form");
    var isEdit = state.editId !== null;
    var request;

    if (isEdit) {
      var payload = {
        hoTen: form.elements.hoTen.value,
        email: form.elements.email.value,
        soDienThoai: form.elements.soDienThoai.value,
        loaiDocGia: form.elements.loaiDocGia.value,
        trangThaiThe: form.elements.trangThaiThe.value
      };
      request = API.call("updateReader", payload, "PUT", { id: state.editId });
    } else {
      var built = API.serializeForm(form, "readerCreate");
      if (!built.ok) {
        showMessage(built.message);
        return;
      }
      request = API.call("createReader", built.payload, "POST");
    }

    request
      .then(function (res) {
        if (!res.ok) {
          showMessage(res.message);
          return;
        }
        closeForm();
        showMessage(isEdit ? "Đã cập nhật độc giả." : "Đã thêm độc giả.", "alert-success");
        loadReaders({ clear: false });
      })
      .catch(function () {
        showMessage("Đã xảy ra lỗi không xác định khi lưu độc giả.");
      });
  }

  function toggleLock(reader) {
    var next = reader.trangThaiThe === "hoat_dong" ? "khoa" : "hoat_dong";
    API.call("lockReader", { trangThaiThe: next }, "PUT", { id: reader.ma })
      .then(function (res) {
        if (!res.ok) {
          showMessage(res.message);
          return;
        }
        showMessage(
          next === "khoa" ? "Đã khoá thẻ độc giả." : "Đã mở khoá thẻ độc giả.",
          "alert-success"
        );
        loadReaders({ clear: false });
      })
      .catch(function () {
        showMessage("Đã xảy ra lỗi không xác định khi đổi trạng thái thẻ.");
      });
  }

  function deleteReader(reader) {
    var ok = window.confirm('Xoá độc giả "' + (reader.hoTen || reader.ma || "") + '"?');
    if (!ok) {
      return;
    }
    API.call("deleteReader", undefined, "DELETE", { id: reader.ma })
      .then(function (res) {
        if (!res.ok) {
          showMessage(res.message);
          return;
        }
        showMessage("Đã xoá độc giả.", "alert-success");
        loadReaders({ clear: false });
      })
      .catch(function () {
        showMessage("Đã xảy ra lỗi không xác định khi xoá độc giả.");
      });
  }

  function init() {
    if (!Auth.requireStaff()) {
      return;
    }
    Auth.applyRoleUI();

    var searchButton = document.getElementById("search-readers-button");
    if (searchButton) {
      searchButton.addEventListener("click", function () {
        loadReaders();
      });
    }
    var qInput = document.getElementById("reader-q");
    if (qInput) {
      qInput.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
          loadReaders();
        }
      });
    }

    var addButton = document.getElementById("add-reader-button");
    if (addButton && canManage()) {
      addButton.addEventListener("click", function () {
        openForm(null);
      });
    }

    var form = document.getElementById("reader-form");
    if (form) {
      form.addEventListener("submit", saveForm);
    }

    var cancelButton = document.getElementById("cancel-reader-button");
    if (cancelButton) {
      cancelButton.addEventListener("click", closeForm);
    }

    var modal = document.getElementById("reader-modal");
    if (modal) {
      modal.addEventListener("click", function (e) {
        if (e.target === modal) {
          closeForm();
        }
      });
    }

    loadReaders();
  }

  document.addEventListener("DOMContentLoaded", init);
})();
