/* Đăng nhập, phiên đăng nhập và ẩn/hiện giao diện theo vai trò. */
window.Auth = (function () {
  var SESSION_KEY = "thuvien_session";
  var loginMessageTimer = null;

  var ROLE_LABELS = {
    admin: "Quản trị viên",
    librarian: "Thủ thư",
    reader: "Độc giả"
  };

  function roleLabel(role) {
    return ROLE_LABELS[role] || role || "";
  }

  function currentUser() {
    try {
      var raw = sessionStorage.getItem(SESSION_KEY) || localStorage.getItem(SESSION_KEY);
      if (raw && !sessionStorage.getItem(SESSION_KEY)) {
        sessionStorage.setItem(SESSION_KEY, raw);
      }
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
      localStorage.setItem(SESSION_KEY, JSON.stringify(session));
      return { ok: true, data: session };
    });
  }

  function logout() {
    sessionStorage.removeItem(SESSION_KEY);
    localStorage.removeItem(SESSION_KEY);
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
      var roleLabelText = ROLE_LABELS[user.role];
      nameEl.hidden = !user.name || user.name === roleLabelText;
      nameEl.classList.add("user-name-link");
      nameEl.setAttribute("role", "link");
      nameEl.setAttribute("tabindex", "0");
      nameEl.setAttribute("title", "Mở hồ sơ cá nhân");
      nameEl.addEventListener("click", function () {
        window.location.href = "profile.html";
      });
      nameEl.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          window.location.href = "profile.html";
        }
      });
    }
    if (roleEl) {
      roleEl.textContent = roleLabel(user.role);
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

    var nav = document.querySelector(".admin-nav");
    if (nav && !nav.querySelector('a[href="profile.html"]')) {
      var profileLink = document.createElement("a");
      profileLink.href = "profile.html";
      profileLink.setAttribute("data-roles", "admin,librarian,reader");
      profileLink.textContent = "Hồ sơ";
      nav.appendChild(profileLink);
    }
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
