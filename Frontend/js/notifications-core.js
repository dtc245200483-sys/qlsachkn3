/*
 * UC11 — Thông báo cho độc giả: lấy từ GET /api/notifications (Backend tổng hợp).
 * Trạng thái đã đọc lưu ở Backend (DocThongBao) qua PUT .../{id}/read và read-all.
 */
window.Notif = (function () {
  var API = window.API;

  var TITLES = {
    QUA_HAN: "Nhắc hạn trả",
    SAP_HET_HAN: "Nhắc hạn trả",
    SACH_SAN_SANG: "Sách sẵn sàng",
    YEU_CAU_DA_DUYET: "Yêu cầu đã duyệt",
    DAT_TRUOC_DA_MUON: "Đặt trước đã xác nhận"
  };

  function build() {
    return API.call("notifications")
      .then(function (res) {
        if (!res.ok || !Array.isArray(res.data)) {
          return { ok: false, items: [], unreadCount: 0 };
        }
        var items = res.data.map(function (n) {
          return {
            id: String(n.id || ""),
            loai: n.loai || "",
            title: TITLES[n.loai] || "Thông báo",
            text: n.noi_dung || "",
            date: n.ngay ? new Date(n.ngay) : new Date(),
            read: !!n.da_doc
          };
        });
        items.sort(function (a, b) {
          return b.date.getTime() - a.date.getTime();
        });
        return {
          ok: true,
          items: items,
          unreadCount: items.filter(function (it) {
            return !it.read;
          }).length
        };
      })
      .catch(function () {
        return { ok: false, items: [], unreadCount: 0 };
      });
  }

  function markRead(item) {
    return API.call("markNotificationRead", undefined, "PUT", { source_id: item.id });
  }

  function markAllRead() {
    return API.call("markAllNotificationsRead", undefined, "PUT");
  }

  function remove(item) {
    return API.call("deleteNotification", undefined, "DELETE", { source_id: item.id });
  }

  return {
    build: build,
    markRead: markRead,
    markAllRead: markAllRead,
    remove: remove
  };
})();
