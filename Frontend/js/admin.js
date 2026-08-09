/* Tiện ích dùng chung cho các trang admin (chỉ admin). */
window.Admin = (function () {
  var messageTimer = null;

  function initShared() {
    if (!window.Auth.requireAdmin()) {
      return false;
    }
    window.Auth.applyRoleUI();
    return true;
  }

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
    }, 5000);
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

  return {
    initShared: initShared,
    showMessage: showMessage,
    clearMessage: clearMessage,
    setLoading: setLoading
  };
})();
