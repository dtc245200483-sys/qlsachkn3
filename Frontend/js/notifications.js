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
    title.textContent = item.title;
    card.appendChild(title);

    var text = document.createElement("p");
    text.textContent = item.text;
    card.appendChild(text);

    var meta = document.createElement("p");
    meta.className = "hint";
    meta.textContent = item.date ? item.date.toLocaleString("vi-VN") : "";
    card.appendChild(meta);

    var actions = document.createElement("div");
    actions.className = "row-actions";
    if (item.read) {
      var done = document.createElement("span");
      done.className = "status-badge status-badge--active";
      done.textContent = "Đã đọc";
      actions.appendChild(done);
    } else {
      var mark = document.createElement("button");
      mark.type = "button";
      mark.className = "btn btn-secondary";
      mark.textContent = "Đánh dấu đã đọc";
      mark.addEventListener("click", function () {
        mark.disabled = true;
        window.Notif.markRead(item)
          .then(function (res) {
            if (!res.ok) {
              mark.disabled = false;
              showMessage(res.message || "Không thể đánh dấu đã đọc.");
              return;
            }
            load();
          })
          .catch(function () {
            mark.disabled = false;
            showMessage("Đã xảy ra lỗi khi đánh dấu đã đọc.");
          });
      });
      actions.appendChild(mark);
    }
    var del = document.createElement("button");
    del.type = "button";
    del.className = "btn btn-danger btn-sm";
    del.textContent = "Xoá";
    del.addEventListener("click", function () {
      window.Notif.remove(item)
        .then(function (res) {
          if (!res.ok) {
            showMessage("Không thể xoá thông báo.");
            return;
          }
          load();
        })
        .catch(function () {
          showMessage("Không thể xoá thông báo.");
        });
    });
    actions.appendChild(del);
    card.appendChild(actions);
    return card;
  }

  document.addEventListener("DOMContentLoaded", function () {
    if (!Auth.requireReader()) {
      return;
    }
    Auth.applyRoleUI();
    document.getElementById("mark-all-button").addEventListener("click", function () {
      window.Notif.markAllRead().then(function (res) {
        if (res && !res.ok) {
          showMessage(res.message || "Không thể đánh dấu tất cả.");
          return;
        }
        load();
      });
    });
    load();
  });
})();
