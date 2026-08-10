/*
 * MainLayout dùng chung (vanilla JS) — banner cố định + navbar theo role.
 * Các trang sau login chỉ cần: <header class="app-header" id="app-header-root"></header>
 * rồi gọi window.Layout.init("<pageKey>") sau khi load js/layout.js.
 */
window.Layout = (function () {
  var Auth = window.Auth;

  var ROLE_LABELS = {
    admin: "Quản trị viên",
    librarian: "Thủ thư",
    reader: "Độc giả"
  };

  var MENUS = {
    reader: [
      { key: "search", href: "search.html", label: "Tra cứu sách" },
      { key: "reservations", href: "reservations.html", label: "Đặt trước" },
      { key: "my-borrows", href: "my-borrows.html", label: "Lịch sử mượn" },
      { key: "requests", href: "requests.html", label: "Yêu cầu" },
      { key: "notifications", href: "notifications.html", label: "Thông báo", badge: true },
      { key: "profile", href: "profile.html", label: "Hồ sơ" }
    ],
    librarian: [
      { key: "search", href: "search.html", label: "Tra cứu sách" },
      { key: "reservations", href: "reservations.html", label: "Đặt trước" },
      { key: "requests", href: "requests.html", label: "Yêu cầu" },
      { key: "borrow", href: "borrow.html", label: "Mượn / Trả sách" },
      { key: "books", href: "books.html", label: "Quản lý sách" },
      { key: "readers", href: "readers.html", label: "Quản lý độc giả" },
      { key: "stats", href: "stats.html", label: "Thống kê" },
      { key: "profile", href: "profile.html", label: "Hồ sơ" }
    ],
    admin: [
      { key: "search", href: "search.html", label: "Tra cứu sách" },
      { key: "stats", href: "stats.html", label: "Thống kê" },
      { key: "admin-accounts", href: "admin-accounts.html", label: "Tài khoản" },
      { key: "admin-catalog", href: "admin-catalog.html", label: "Danh mục" },
      { key: "admin-config", href: "admin-config.html", label: "Cấu hình" },
      { key: "profile", href: "profile.html", label: "Hồ sơ" }
    ]
  };

  function banner() {
    var div = document.createElement("div");
    div.className = "app-banner";

    var img = document.createElement("img");
    img.className = "logo";
    img.src = "assets/logo-ictu-round.png";
    img.alt = "Logo ICTU";
    img.onerror = function () {
      img.style.display = "none";
    };

    var text = document.createElement("div");
    text.className = "app-banner__text";
    var strong = document.createElement("strong");
    strong.textContent = "TRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN VÀ TRUYỀN THÔNG";
    var span = document.createElement("span");
    span.textContent = "ĐẠI HỌC THÁI NGUYÊN — HỆ THỐNG QUẢN LÝ THƯ VIỆN TÍCH HỢP AI";
    text.appendChild(strong);
    text.appendChild(span);

    div.appendChild(img);
    div.appendChild(text);
    return div;
  }

  function navRow(user, pageKey) {
    var row = document.createElement("div");
    row.className = "app-header__nav-row";

    var toggle = document.createElement("button");
    toggle.type = "button";
    toggle.id = "nav-toggle";
    toggle.className = "nav-toggle";
    toggle.setAttribute("aria-label", "Mở menu");
    toggle.setAttribute("aria-expanded", "false");
    var bar1 = document.createElement("span");
    var bar2 = document.createElement("span");
    var bar3 = document.createElement("span");
    toggle.appendChild(bar1);
    toggle.appendChild(bar2);
    toggle.appendChild(bar3);

    var nav = document.createElement("nav");
    nav.className = "admin-nav";
    (MENUS[user.role] || []).forEach(function (item) {
      var a = document.createElement("a");
      a.href = item.href;
      a.textContent = item.label;
      a.className = item.key === pageKey ? "nav-item active" : "nav-item";
      if (item.badge) {
        var badge = document.createElement("span");
        badge.className = "notif-badge";
        badge.id = "notif-badge";
        badge.textContent = "0";
        badge.hidden = true;
        a.appendChild(document.createTextNode(" "));
        a.appendChild(badge);
      }
      nav.appendChild(a);
    });

    var userInfo = document.createElement("div");
    userInfo.className = "user-info";

    var nameSpan = document.createElement("span");
    nameSpan.id = "user-name";
    nameSpan.textContent = user.name || "";
    if (!user.name || user.name === ROLE_LABELS[user.role]) {
      nameSpan.hidden = true;
    }

    var roleSpan = document.createElement("span");
    roleSpan.id = "user-role";
    roleSpan.className = "role-badge";
    roleSpan.textContent = ROLE_LABELS[user.role] || user.role || "";

    var logout = document.createElement("button");
    logout.type = "button";
    logout.id = "logout-button";
    logout.className = "btn btn-secondary";
    logout.textContent = "Đăng xuất";

    userInfo.appendChild(nameSpan);
    userInfo.appendChild(roleSpan);
    userInfo.appendChild(logout);

    row.appendChild(nav);
    row.insertBefore(toggle, nav);
    row.appendChild(userInfo);
    initNavToggle(row);
    return row;
  }

  function initNavToggle(row) {
    var toggle = row.querySelector(".nav-toggle");
    if (!toggle) {
      return;
    }
    function closeMenu() {
      row.classList.remove("nav-open");
      toggle.setAttribute("aria-expanded", "false");
      toggle.setAttribute("aria-label", "Mở menu");
    }
    toggle.addEventListener("click", function (e) {
      e.stopPropagation();
      var open = row.classList.toggle("nav-open");
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", open ? "Đóng menu" : "Mở menu");
    });
    row.querySelectorAll(".admin-nav a").forEach(function (a) {
      a.addEventListener("click", closeMenu);
    });
    document.addEventListener("click", function (e) {
      if (!row.contains(e.target)) {
        closeMenu();
      }
    });
  }

  function init(pageKey) {
    var root = document.getElementById("app-header-root");
    var user = Auth ? Auth.currentUser() : null;
    if (!root || !user) {
      return;
    }
    root.innerHTML = "";
    root.appendChild(banner());
    root.appendChild(navRow(user, pageKey));
    if (Auth.applyRoleUI) {
      Auth.applyRoleUI();
    }
  }

  return {
    init: init
  };
})();
