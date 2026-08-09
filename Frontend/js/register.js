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

  function submit(e) {
    e.preventDefault();
    var form = document.getElementById("register-form");
    var button = document.getElementById("register-button");
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
