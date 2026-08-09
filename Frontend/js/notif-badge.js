/* Ô đếm thông báo chưa đọc trên menu (chỉ reader). */
document.addEventListener("DOMContentLoaded", function () {
  var user = window.Auth ? window.Auth.currentUser() : null;
  if (!user || user.role !== "reader") {
    return;
  }
  window.Notif.build()
    .then(function (res) {
      var badge = document.getElementById("notif-badge");
      if (!badge) {
        return;
      }
      if (res.unreadCount > 0) {
        badge.textContent = res.unreadCount > 99 ? "99+" : String(res.unreadCount);
        badge.hidden = false;
      }
    })
    .catch(function () {});
});
