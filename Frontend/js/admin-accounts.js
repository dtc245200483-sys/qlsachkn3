/* Quản lý tài khoản thủ thư + độc giả (UC23) — chỉ admin. */
(function () {
  var API = window.API;
  var Auth = window.Auth;
  var state = { editId: null };
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

  function loadAccounts(opts) {
    if (!opts || opts.clear !== false) {
      clearMessage();
    }
    setLoading(true);
    var role = document.getElementById("account-role-filter").value;
    var built = API.buildQuery("accounts", { role: role });
    API.call("accounts", undefined, "GET", undefined, built.query)
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
        showMessage("Đã xảy ra lỗi khi tải danh sách tài khoản.");
      });
  }

  function render(list) {
    var tbody = document.getElementById("account-tbody");
    tbody.innerHTML = "";
    if (list.length === 0) {
      var emptyRow = document.createElement("tr");
      var emptyCell = document.createElement("td");
      emptyCell.className = "empty-row";
      emptyCell.colSpan = 8;
      emptyCell.textContent = "Chưa có tài khoản nào.";
      emptyRow.appendChild(emptyCell);
      tbody.appendChild(emptyRow);
      return;
    }
    list.forEach(function (item) {
      var account = API.mapResponse("accountOut", item);
      if (!account) {
        return;
      }
      tbody.appendChild(row(account));
    });
  }

  function row(account) {
    var tr = document.createElement("tr");
    var roleLabels = {
      admin: "Quản trị viên",
      librarian: "Thủ thư",
      reader: "Độc giả"
    };
    var roleText = roleLabels[account.role] || account.role || "—";
    var values = [
      account.id,
      account.username,
      account.hoTen || "—",
      roleText,
      account.readerId || "—",
      null,
      account.createdAt ? new Date(account.createdAt).toLocaleString("vi-VN") : "—"
    ];
    values.forEach(function (value, index) {
      var td = document.createElement("td");
      if (index === 5) {
        var badge = document.createElement("span");
        badge.className = "status-badge " + (account.isActive ? "status-badge--active" : "status-badge--locked");
        badge.textContent = account.isActive ? "Hoạt động" : "Đã khoá";
        td.appendChild(badge);
      } else {
        td.textContent = value === "" || value === null ? "—" : value;
      }
      tr.appendChild(td);
    });

    var actionsTd = document.createElement("td");
    var actions = document.createElement("div");
    actions.className = "row-actions";
    var edit = document.createElement("button");
    edit.type = "button";
    edit.className = "btn btn-secondary";
    edit.textContent = "Sửa";
    edit.addEventListener("click", function () {
      openForm(account);
    });
    var lock = document.createElement("button");
    lock.type = "button";
    lock.className = "btn btn-secondary";
    lock.textContent = account.isActive ? "Khoá" : "Mở khoá";
    lock.addEventListener("click", function () {
      toggleLock(account);
    });
    var del = document.createElement("button");
    del.type = "button";
    del.className = "btn btn-danger";
    del.textContent = "Xoá";
    del.addEventListener("click", function () {
      deleteAccount(account);
    });
    actions.appendChild(edit);
    actions.appendChild(lock);
    actions.appendChild(del);
    actionsTd.appendChild(actions);
    tr.appendChild(actionsTd);
    return tr;
  }

  function openForm(account) {
    state.editId = account ? account.id : null;
    var form = document.getElementById("account-form");
    var title = document.getElementById("account-form-title");
    var username = document.getElementById("account-username");
    var password = document.getElementById("account-password");
    form.reset();
    var roleSelect = form.elements.role;
    var readerOption = roleSelect.querySelector('option[value="reader"]');
    var showReaderOption = !!account && account.role === "reader";
    if (showReaderOption && !readerOption) {
      var opt = document.createElement("option");
      opt.value = "reader";
      opt.textContent = "Độc giả";
      roleSelect.appendChild(opt);
    } else if (!showReaderOption && readerOption) {
      readerOption.remove();
    }
    var readerGroup = document.getElementById("account-reader-group");
    if (readerGroup) {
      readerGroup.hidden = !showReaderOption;
    }
    if (account) {
      title.textContent = "Sửa tài khoản";
      username.value = account.username;
      username.disabled = true;
      form.elements.hoTen.value = account.hoTen || "";
      form.elements.email.value = account.email || "";
      form.elements.soDienThoai.value = account.soDienThoai || "";
      form.elements.role.value = account.role;
      form.elements.readerId.value = account.readerId || "";
      form.elements.isActive.checked = !!account.isActive;
      password.placeholder = "Để trống = giữ nguyên";
      password.required = false;
    } else {
      title.textContent = "Tạo tài khoản";
      username.disabled = false;
      password.placeholder = "";
      password.required = true;
      form.elements.role.value = "librarian";
      form.elements.isActive.checked = true;
    }
    document.getElementById("account-modal").hidden = false;
  }

  function closeForm() {
    document.getElementById("account-modal").hidden = true;
    state.editId = null;
  }

  function validateForm(form, isEdit) {
    var username = form.elements.username.value.trim();
    var hoTen = form.elements.hoTen.value.trim();
    var email = form.elements.email.value.trim();
    var sdt = form.elements.soDienThoai.value.trim();
    var password = form.elements.password.value;

    if (!isEdit && !username) {
      return "Chưa nhập tên đăng nhập.";
    }
    if (username.length < 6) {
      return "Tên đăng nhập phải từ 6 ký tự trở lên.";
    }
    if (!hoTen) {
      return "Chưa nhập họ tên.";
    }
    if (!isEdit && !email) {
      return "Chưa nhập email.";
    }
    if (email && !/^[^@\s]+@ictu\.edu\.vn$/i.test(email)) {
      return "Email sai định dạng — phải là email @ictu.edu.vn.";
    }
    if (!isEdit && !sdt) {
      return "Chưa nhập số điện thoại.";
    }
    if (sdt && !/^0\d{9}$/.test(sdt)) {
      return "Số điện thoại phải là 10 chữ số và bắt đầu bằng 0.";
    }
    if (!isEdit && !password) {
      return "Chưa nhập mật khẩu.";
    }
    if (password && password.length < 6) {
      return "Mật khẩu phải từ 6 ký tự trở lên.";
    }
    return "";
  }

  function saveForm(e) {
    e.preventDefault();
    var form = document.getElementById("account-form");
    var request;
    var isEdit = state.editId !== null;
    var error = validateForm(form, isEdit);
    if (error) {
      showMessage(error);
      return;
    }
    if (isEdit) {
      var payload = {
        ho_ten: form.elements.hoTen.value,
        email: form.elements.email.value.trim(),
        so_dien_thoai: form.elements.soDienThoai.value.trim(),
        role: form.elements.role.value,
        reader_id: form.elements.readerId.value || null,
        is_active: form.elements.isActive.checked
      };
      var password = form.elements.password.value;
      if (password) {
        payload.password = password;
      }
      request = API.call("updateAccount", payload, "PUT", { id: state.editId });
    } else {
      var built = API.serializeForm(form, "accountCreate");
      if (!built.ok) {
        showMessage(built.message);
        return;
      }
      request = API.call("createAccount", built.payload, "POST");
    }
    request
      .then(function (res) {
        if (!res.ok) {
          showMessage(res.message);
          return;
        }
        closeForm();
        showMessage(state.editId === null ? "Đã tạo tài khoản." : "Đã cập nhật tài khoản.", "alert-success");
        loadAccounts({ clear: false });
      })
      .catch(function () {
        showMessage("Đã xảy ra lỗi khi lưu tài khoản.");
      });
  }

  function toggleLock(account) {
    API.call("updateAccount", { is_active: !account.isActive }, "PUT", { id: account.id })
      .then(function (res) {
        if (!res.ok) {
          showMessage(res.message);
          return;
        }
        showMessage(account.isActive ? "Đã khoá tài khoản." : "Đã mở khoá tài khoản.", "alert-success");
        loadAccounts({ clear: false });
      })
      .catch(function () {
        showMessage("Đã xảy ra lỗi khi đổi trạng thái tài khoản.");
      });
  }

  function deleteAccount(account) {
    var ok = window.confirm('Xoá tài khoản "' + account.username + '"?');
    if (!ok) {
      return;
    }
    API.call("deleteAccount", undefined, "DELETE", { id: account.id })
      .then(function (res) {
        if (!res.ok) {
          showMessage(res.message);
          return;
        }
        showMessage("Đã xoá tài khoản.", "alert-success");
        loadAccounts({ clear: false });
      })
      .catch(function () {
        showMessage("Đã xảy ra lỗi khi xoá tài khoản.");
      });
  }

  document.addEventListener("DOMContentLoaded", function () {
    if (!Auth.requireAdmin()) {
      return;
    }
    Auth.applyRoleUI();
    document.getElementById("add-account-button").addEventListener("click", function () {
      openForm(null);
    });
    document.getElementById("apply-account-filter").addEventListener("click", loadAccounts);
    document.getElementById("cancel-account-button").addEventListener("click", closeForm);
    document.getElementById("account-form").addEventListener("submit", saveForm);
    loadAccounts();
  });
})();
