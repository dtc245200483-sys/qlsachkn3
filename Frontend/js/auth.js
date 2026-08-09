/* Đăng nhập, phiên đăng nhập và ẩn/hiện giao diện theo vai trò. */
window.Auth = (function () {
  var SESSION_KEY = "thuvien_session";
  var loginMessageTimer = null;

  function currentUser() {
    try {
      var raw = sessionStorage.getItem(SESSION_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  }

  function login(form) {
    var built = window.API.serializeForm(form, "login");
    if (!built.ok) {
      return Promise.resolve(built);
    }
    return window.API.call("login", built.payload, "POST").then(function (res) {
      if (!res.ok) {
        return res;
      }
      var mapped = window.API.mapResponse("loginResponse", res.data);
      if (!mapped) {
        return {
          ok: false,
          code: "API_CHUA_CO_TAI_LIEU",
          message:
            "API đăng nhập trả về nhưng chưa có cấu hình field token/role trong api.js."
        };
      }
      var session = {
        token: mapped.token || "",
        role: window.API.canonicalRole(mapped.role),
        name: mapped.name || ""
      };
      sessionStorage.setItem(SESSION_KEY, JSON.stringify(session));
      return { ok: true, data: session };
    });
  }

  function logout() {
    sessionStorage.removeItem(SESSION_KEY);
    window.location.href = "index.html";
  }

  function requireAuth() {
    if (!currentUser()) {
      window.location.replace("index.html");
      return false;
    }
    return true;
  }

  function requireAdmin() {
    var user = currentUser();
    if (!user) {
      window.location.replace("index.html");
      return false;
    }
    if (user.role !== "admin") {
      window.location.replace("search.html");
      return false;
    }
    return true;
  }

  function requireStaff() {
    var user = currentUser();
    if (!user) {
      window.location.replace("index.html");
      return false;
    }
    if (user.role !== "admin" && user.role !== "librarian") {
      window.location.replace("search.html");
      return false;
    }
    return true;
  }

  function requireLibrarian() {
    var user = currentUser();
    if (!user) {
      window.location.replace("index.html");
      return false;
    }
    if (user.role !== "librarian") {
      window.location.replace("search.html");
      return false;
    }
    return true;
  }

  function requireReader() {
    var user = currentUser();
    if (!user) {
      window.location.replace("index.html");
      return false;
    }
    if (user.role !== "reader") {
      window.location.replace("search.html");
      return false;
    }
    return true;
  }

  function applyRoleUI() {
    var user = currentUser();
    if (!user) {
      return;
    }
    var nameEl = document.getElementById("user-name");
    var roleEl = document.getElementById("user-role");
    if (nameEl) {
      nameEl.textContent = user.name || "";
    }
    if (roleEl) {
      roleEl.textContent = user.role || "";
    }

    var role = user.role || "";
    document.body.dataset.role = role;
    document.querySelectorAll("[data-roles]").forEach(function (el) {
      var allowed = (el.getAttribute("data-roles") || "")
        .split(",")
        .map(function (s) {
          return s.trim();
        });
      el.hidden = allowed.indexOf(role) === -1;
    });
  }

  function initLoginPage() {
    var form = document.getElementById("login-form");
    if (!form) {
      return;
    }
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var messageEl = document.getElementById("login-message");
      var button = document.getElementById("login-button");
      if (messageEl) {
        if (loginMessageTimer) {
          clearTimeout(loginMessageTimer);
          loginMessageTimer = null;
        }
        messageEl.hidden = true;
        messageEl.className = "alert";
      }
      if (button) {
        button.disabled = true;
        button.textContent = "Đang đăng nhập...";
      }
      login(form).then(function (res) {
        if (button) {
          button.disabled = false;
          button.textContent = "Đăng nhập";
        }
        if (res.ok) {
          window.location.href = "search.html";
          return;
        }
        if (messageEl) {
          messageEl.className = "alert alert-error";
          messageEl.textContent = res.message || "Đăng nhập thất bại.";
          messageEl.hidden = false;
          if (loginMessageTimer) {
            clearTimeout(loginMessageTimer);
          }
          loginMessageTimer = setTimeout(function () {
            messageEl.hidden = true;
            loginMessageTimer = null;
          }, 5000);
        }
      });
    });
  }

  function init() {
    if (document.body.classList.contains("login-body")) {
      initLoginPage();
    }
    var logoutButton = document.getElementById("logout-button");
    if (logoutButton) {
      logoutButton.addEventListener("click", logout);
    }
  }

  document.addEventListener("DOMContentLoaded", init);

  return {
    currentUser: currentUser,
    login: login,
    logout: logout,
    requireAuth: requireAuth,
    requireAdmin: requireAdmin,
    requireStaff: requireStaff,
    requireLibrarian: requireLibrarian,
    requireReader: requireReader,
    applyRoleUI: applyRoleUI
  };
})();
