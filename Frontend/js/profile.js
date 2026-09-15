/* Trang hồ sơ cá nhân — dùng cho cả 3 vai trò. */
(function () {
  var API = window.API;
  var Auth = window.Auth;
  var messageTimer = null;
  var state = {
    mock: false,
    data: null
  };

  var ROLE_LABELS = {
    admin: "Quản trị viên",
    librarian: "Thủ thư",
    reader: "Độc giả"
  };

  var LOAI_LABELS = {
    sinh_vien: "Sinh viên",
    giang_vien: "Giảng viên"
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
    }, 6000);
  }

  function setLoading(visible) {
    var el = document.getElementById("loading");
    if (el) {
      el.hidden = !visible;
    }
  }

  function isMissing(res) {
    return res && (res.code === "API_CHUA_CO_TAI_LIEU" || res.status === 404 || res.status === 405);
  }

  function mockProfile() {
    var user = Auth.currentUser() || {};
    return {
      username: "chưa có (chờ API)",
      hoTen: user.name || "",
      email: "—",
      soDienThoai: "—",
      loaiDocGia: user.role === "reader" ? "sinh_vien" : "",
      role: user.role || "",
      avatarUrl: ""
    };
  }

  function loadProfile() {
    setLoading(true);
    API.call("profileMe")
      .then(function (res) {
        setLoading(false);
        if (!res.ok) {
          if (isMissing(res)) {
            state.mock = true;
            state.data = mockProfile();
            render(state.data);
            document.getElementById("mock-banner").hidden = false;
            return;
          }
          showMessage(res.message);
          return;
        }
        var mapped = API.mapResponse("profileOut", res.data);
        if (!mapped) {
          state.mock = true;
          state.data = mockProfile();
          render(state.data);
          document.getElementById("mock-banner").hidden = false;
          return;
        }
        state.mock = false;
        state.data = mapped;
        syncSessionName(mapped.hoTen);
        render(mapped);
        document.getElementById("mock-banner").hidden = true;
      })
      .catch(function () {
        setLoading(false);
        showMessage("Đã xảy ra lỗi khi tải hồ sơ.");
      });
  }

  function render(profile) {
    var nameEl = document.getElementById("profile-name");
    var usernameEl = document.getElementById("profile-username");
    var roleEl = document.getElementById("profile-role");
    var loaiEl = document.getElementById("profile-loai");
    var avatarEl = document.getElementById("profile-avatar");
    var form = document.getElementById("profile-form");

    if (nameEl) {
      nameEl.textContent = profile.hoTen || "—";
      var roleLabelText = ROLE_LABELS[profile.role];
      nameEl.hidden = !profile.hoTen || profile.hoTen === roleLabelText;
    }
    if (usernameEl) {
      usernameEl.textContent = profile.username || "—";
    }
    if (roleEl) {
      roleEl.textContent = ROLE_LABELS[profile.role] || profile.role || "—";
    }
    if (loaiEl) {
      var isReader = profile.role === "reader";
      loaiEl.hidden = !isReader;
      loaiEl.textContent = "Loại độc giả: " + (LOAI_LABELS[profile.loaiDocGia] || profile.loaiDocGia || "—");
    }
    if (avatarEl) {
      avatarEl.src = profile.avatarUrl || "assets/default-avatar.svg";
    }

    var loaiGroup = document.getElementById("profile-loai-group");
    if (loaiGroup) {
      loaiGroup.hidden = profile.role !== "reader";
    }

    if (form) {
      if (form.elements.hoTen) {
        form.elements.hoTen.value = profile.hoTen || "";
      }
      if (form.elements.email) {
        form.elements.email.value = profile.email || "";
      }
      if (form.elements.soDienThoai) {
        form.elements.soDienThoai.value = profile.soDienThoai || "";
      }
      if (form.elements.loaiDocGia) {
        form.elements.loaiDocGia.value = profile.loaiDocGia || "sinh_vien";
      }
    }
  }

  function setButtonLoading(button, loading, loadingText, normalText) {
    if (!button) {
      return;
    }
    button.disabled = loading;
    button.textContent = loading ? loadingText : normalText;
  }

  function updateProfile(e) {
    e.preventDefault();
    var form = document.getElementById("profile-form");
    var built = API.serializeForm(form, "profileUpdate");
    if (!built.ok) {
      showMessage(built.message);
      return;
    }
    if (state.data && state.data.role !== "reader") {
      delete built.payload.loai_doc_gia;
    }

    var button = document.getElementById("save-profile-button");
    setButtonLoading(button, true, "Đang lưu...", "Lưu thông tin");

    API.call("updateProfileMe", built.payload, "PUT")
      .then(function (res) {
        setButtonLoading(button, false, "", "Lưu thông tin");
        if (!res.ok) {
          if (isMissing(res)) {
            state.mock = true;
            state.data = state.data || mockProfile();
            state.data.hoTen = form.elements.hoTen.value;
            state.data.email = form.elements.email.value;
            state.data.soDienThoai = form.elements.soDienThoai.value;
            if (state.data.role === "reader") {
              state.data.loaiDocGia = form.elements.loaiDocGia.value;
            }
            syncSessionName(state.data.hoTen);
            render(state.data);
            document.getElementById("mock-banner").hidden = false;
            showMessage("Backend chưa có API cập nhật hồ sơ — thông tin chỉ hiển thị tạm, chưa lưu thật.", "alert-warning");
            return;
          }
          showMessage(res.message);
          return;
        }
        showMessage("Đã cập nhật thông tin cá nhân.", "alert-success");
        loadProfile();
      })
      .catch(function () {
        setButtonLoading(button, false, "", "Lưu thông tin");
        showMessage("Đã xảy ra lỗi khi cập nhật thông tin.");
      });
  }

  function syncSessionName(name) {
    var user = Auth.currentUser();
    if (!user) {
      return;
    }
    user.name = name || user.name || "";
    sessionStorage.setItem("thuvien_session", JSON.stringify(user));
    localStorage.setItem("thuvien_session", JSON.stringify(user));
    var nameEl = document.getElementById("user-name");
    if (nameEl) {
      nameEl.textContent = user.name;
      var roleLabelText = ROLE_LABELS[user.role];
      nameEl.hidden = !user.name || user.name === roleLabelText;
    }
  }

  function changePassword(e) {
    e.preventDefault();
    var form = document.getElementById("password-form");
    var oldPwd = form.elements.matKhauCu.value;
    var newPwd = form.elements.matKhauMoi.value;
    var confirmPwd = document.getElementById("password-confirm").value;

    if (!oldPwd || !newPwd) {
      showMessage("Vui lòng nhập đầy đủ mật khẩu cũ và mật khẩu mới.");
      return;
    }
    if (newPwd.length < 6) {
      showMessage("Mật khẩu mới phải có ít nhất 6 ký tự.");
      return;
    }
    if (newPwd !== confirmPwd) {
      showMessage("Xác nhận mật khẩu mới không khớp.");
      return;
    }

    var button = document.getElementById("change-password-button");
    setButtonLoading(button, true, "Đang xử lý...", "Đổi mật khẩu");

    API.call(
      "changeProfilePassword",
      { mat_khau_cu: oldPwd, mat_khau_moi: newPwd },
      "PUT"
    )
      .then(function (res) {
        setButtonLoading(button, false, "", "Đổi mật khẩu");
        if (!res.ok) {
          if (isMissing(res)) {
            showMessage("Backend chưa có API đổi mật khẩu — chưa thể đổi mật khẩu thật.", "alert-warning");
            return;
          }
          showMessage(res.message);
          return;
        }
        form.reset();
        showMessage("Đã đổi mật khẩu thành công.", "alert-success");
      })
      .catch(function () {
        setButtonLoading(button, false, "", "Đổi mật khẩu");
        showMessage("Đã xảy ra lỗi khi đổi mật khẩu.");
      });
  }

  function handleAvatarChange() {
    var input = document.getElementById("avatar-input");
    var file = input.files && input.files[0];
    if (!file) {
      return;
    }
    if (["image/png", "image/jpeg"].indexOf(file.type) === -1) {
      showMessage("Chỉ chấp nhận ảnh PNG hoặc JPG.");
      input.value = "";
      return;
    }
    if (file.size > 2 * 1024 * 1024) {
      showMessage("Ảnh đại diện tối đa 2MB.");
      input.value = "";
      return;
    }

    var button = document.getElementById("change-avatar-button");
    setButtonLoading(button, true, "Đang tải...", "Đổi ảnh đại diện");

    API.uploadFile("uploadProfileAvatar", file)
      .then(function (res) {
        setButtonLoading(button, false, "", "Đổi ảnh đại diện");
        if (!res.ok) {
          if (isMissing(res)) {
            var reader = new FileReader();
            reader.onload = function () {
              var avatarEl = document.getElementById("profile-avatar");
              if (avatarEl) {
                avatarEl.src = reader.result;
              }
            };
            reader.readAsDataURL(file);
            document.getElementById("mock-banner").hidden = false;
            showMessage("Backend chưa có API upload ảnh — ảnh chỉ hiển thị tạm, chưa lưu thật.", "alert-warning");
            return;
          }
          showMessage(res.message);
          return;
        }
        var avatarUrl = res.data && (res.data.avatar_url || res.data.avatarUrl);
        if (avatarUrl) {
          var avatarEl = document.getElementById("profile-avatar");
          if (avatarEl) {
            avatarEl.src = avatarUrl;
          }
        }
        showMessage("Đã cập nhật ảnh đại diện.", "alert-success");
      })
      .catch(function () {
        setButtonLoading(button, false, "", "Đổi ảnh đại diện");
        showMessage("Đã xảy ra lỗi khi tải ảnh đại diện.");
      })
      .finally(function () {
        input.value = "";
      });
  }

  function init() {
    if (!Auth.requireAuth()) {
      return;
    }
    Auth.applyRoleUI();

    var changeAvatarButton = document.getElementById("change-avatar-button");
    var avatarInput = document.getElementById("avatar-input");
    if (changeAvatarButton && avatarInput) {
      changeAvatarButton.addEventListener("click", function () {
        avatarInput.click();
      });
      avatarInput.addEventListener("change", handleAvatarChange);
    }

    var profileForm = document.getElementById("profile-form");
    if (profileForm) {
      profileForm.addEventListener("submit", updateProfile);
    }

    var passwordForm = document.getElementById("password-form");
    if (passwordForm) {
      passwordForm.addEventListener("submit", changePassword);
    }

    loadProfile();
  }

  document.addEventListener("DOMContentLoaded", init);
})();
