/* Trang thông báo của độc giả (UC11) — chỉ reader. */
(function () {
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

  function load() {
    setLoading(true);
    window.Notif.build()
      .then(function (res) {
        setLoading(false);
        if (!res.ok) {
          showMessage("Không thể tải thông báo.");
          return;
        }
        render(res.items);
      })
      .catch(function () {
        setLoading(false);
        showMessage("Đã xảy ra lỗi khi tải thông báo.");
      });
  }

  function render(items) {
    var list = document.getElementById("notif-list");
    list.innerHTML = "";
    if (items.length === 0) {
      var empty = document.createElement("div");
      empty.className = "card";
      empty.className = "card notif-empty";
      empty.innerHTML = '<p class="hint">Không có thông báo nào.</p>';
      list.appendChild(empty);
      return;
    }
    items.forEach(function (item) {
      list.appendChild(itemCard(item));
    });
  }

  function itemCard(item) {
    var card = document.createElement("div");
    card.className = "card notif-item" + (item.read ? " notif-item--read" : " notif-item--unread");

    var title = document.createElement("h3");
    title.textContent = item.title + (item.read ? " (đã đọc)" : "");
    card.appendChild(title);

    var text = document.createElement("p");
    text.textContent = item.text;
    card.appendChild(text);

    var meta = document.createElement("p");
    meta.className = "hint";
    meta.textContent = item.date ? item.date.toLocaleString("vi-VN") : "";
    card.appendChild(meta);

    if (!item.read) {
      var mark = document.createElement("button");
      mark.type = "button";
      mark.className = "btn btn-secondary";
      mark.textContent = "Đánh dấu đã đọc";
      mark.addEventListener("click", function () {
        window.Notif.markRead(item);
        load();
      });
      card.appendChild(mark);
    }
    return card;
  }

  document.addEventListener("DOMContentLoaded", function () {
    if (!Auth.requireReader()) {
      return;
    }
    Auth.applyRoleUI();
    document.getElementById("mark-all-button").addEventListener("click", function () {
      window.Notif.build().then(function (res) {
        window.Notif.markAllRead(res.items);
        load();
      });
    });
    load();
  });
})();
