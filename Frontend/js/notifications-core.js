/*
 * UC11 — Thông báo cho độc giả (Frontend tổng hợp trước khi Backend có API):
 *  (a) Nhắc hạn trả: phiếu đang mượn còn <= 3 ngày hoặc đã quá hạn (borrows/me).
 *  (b) Sách đặt trước sẵn sàng: reservation trang_thai = SAN_SANG (reservations).
 * Đánh dấu đã đọc lưu tạm ở localStorage (chờ Backend /api/notifications).
 */
window.Notif = (function () {
  var API = window.API;
  var READ_KEY = "thuvien_notif_read";

  function readSet() {
    try {
      return JSON.parse(localStorage.getItem(READ_KEY) || "[]");
    } catch (e) {
      return [];
    }
  }

  function saveSet(set) {
    localStorage.setItem(READ_KEY, JSON.stringify(set));
  }

  function idFor(item) {
    return item.kind === "duedate" ? "BORROW:" + item.ref : "RES:" + item.ref;
  }

  function build() {
    return Promise.all([API.call("myBorrows"), loadReservations()]).then(
      function (results) {
        var items = [];
        var borrowRes = results[0];
        var resvRes = results[1];

        if (borrowRes.ok && Array.isArray(borrowRes.data)) {
          borrowRes.data.forEach(function (raw) {
            var slip = API.mapResponse("borrowHistoryOut", raw) || raw;
            if (slip.trangThai !== "dang_muon" || !slip.hanTra) {
              return;
            }
            var now = new Date();
            var han = new Date(slip.hanTra);
            var daysLeft = Math.ceil((han.getTime() - now.getTime()) / 86400000);
            if (daysLeft <= 3) {
              items.push({
                kind: "duedate",
                ref: slip.maPhieu,
                title: "Nhắc hạn trả",
                text:
                  "Phiếu " +
                  slip.maPhieu +
                  " hạn trả " +
                  han.toLocaleDateString("vi-VN") +
                  (daysLeft < 0
                    ? " — đã quá hạn " + -daysLeft + " ngày"
                    : " — còn " + daysLeft + " ngày"),
                date: han
              });
            }
          });
        }

        if (resvRes.ok && Array.isArray(resvRes.data)) {
          resvRes.data.forEach(function (raw) {
            var r = API.mapResponse("reservationOut", raw) || raw;
            if (r.trangThai === "SAN_SANG") {
              items.push({
                kind: "ready",
                ref: r.maDat,
                title: "Sách sẵn sàng",
                text:
                  "Đặt trước " +
                  r.maDat +
                  " — " +
                  (r.tenSach || r.maSach || "") +
                  " đã sẵn sàng",
                date: r.ngayDat ? new Date(r.ngayDat) : new Date()
              });
            }
          });
        }

        var set = readSet();
        items.forEach(function (it) {
          it.read = set.indexOf(idFor(it)) !== -1;
        });
        items.sort(function (a, b) {
          return b.date.getTime() - a.date.getTime();
        });
        return {
          ok: true,
          items: items,
          unreadCount: items.filter(function (it) {
            return !it.read;
          }).length,
          reservationsMock: !!(resvRes && resvRes.mock)
        };
      }
    ).catch(function () {
      return { ok: false, items: [], unreadCount: 0, reservationsMock: false };
    });
  }

  function loadReservations() {
    if (typeof window.Reservation !== "undefined") {
      return window.Reservation.list();
    }
    return Promise.resolve({ ok: false, data: [] });
  }

  function markRead(item) {
    var set = readSet();
    var id = idFor(item);
    if (set.indexOf(id) === -1) {
      set.push(id);
      saveSet(set);
    }
  }

  function markAllRead(items) {
    var set = readSet();
    items.forEach(function (it) {
      var id = idFor(it);
      if (set.indexOf(id) === -1) {
        set.push(id);
      }
    });
    saveSet(set);
  }

  return {
    build: build,
    markRead: markRead,
    markAllRead: markAllRead
  };
})();
