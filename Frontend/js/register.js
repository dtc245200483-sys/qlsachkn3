/* Trang đăng ký độc giả (UC01) — sau khi đăng ký chuyển về đăng nhập. */
(function () {
  var messageTimer = null;

  function showMessage(text, type) {
    var el = document.getElementById("register-message");
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

  function validate(form) {
    var username = form.elements.username.value.trim();
    var hoTen = form.elements.hoTen.value.trim();
    var email = form.elements.email.value.trim();
    var sdt = form.elements.soDienThoai.value.trim();
    var password = form.elements.password.value;
    var confirm = document.getElementById("reg-password-confirm").value;

    if (!username) {
      return "Chưa nhập tên đăng nhập.";
    }
    if (username.length < 6) {
      return "Tên đăng nhập phải từ 6 ký tự trở lên.";
    }
    if (!hoTen) {
      return "Chưa nhập họ tên.";
    }
    if (!email) {
      return "Chưa nhập email.";
    }
    if (!/^[^@\s]+@ictu\.edu\.vn$/i.test(email)) {
      return "Email sai định dạng — phải là email @ictu.edu.vn.";
    }
    if (!sdt) {
      return "Chưa nhập số điện thoại.";
    }
    if (!/^0\d{9}$/.test(sdt)) {
      return "Số điện thoại phải là 10 chữ số và bắt đầu bằng 0.";
    }
    if (!password) {
      return "Chưa nhập mật khẩu.";
    }
    if (password.length < 6) {
      return "Mật khẩu phải từ 6 ký tự trở lên.";
    }
    if (confirm !== password) {
      return "Xác nhận mật khẩu không khớp.";
    }
    return "";
  }

  function submit(e) {
    e.preventDefault();
    var form = document.getElementById("register-form");
    var button = document.getElementById("register-button");
    var error = validate(form);
    if (error) {
      showMessage(error);
      return;
    }
    var built = window.API.serializeForm(form, "register");
    if (!built.ok) {
      showMessage(built.message);
      return;
    }
    button.disabled = true;
    button.textContent = "Đang đăng ký...";

    window.API.call("register", built.payload, "POST")
      .then(function (res) {
        button.disabled = false;
        button.textContent = "Đăng ký";
        if (!res.ok) {
          showMessage(res.message);
          return;
        }
        showMessage("Đăng ký thành công! Chuyển về trang đăng nhập...", "alert-success");
        setTimeout(function () {
          window.location.href = "index.html";
        }, 1600);
      })
      .catch(function () {
        button.disabled = false;
        button.textContent = "Đăng ký";
        showMessage("Đã xảy ra lỗi không xác định khi đăng ký.");
      });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var form = document.getElementById("register-form");
    if (form) {
      form.addEventListener("submit", submit);
    }
  });
})();
