/*
 * Đặt trước sách (chức năng 6) — Frontend làm trước khi Backend có API.
 * Mọi hàm đều thử gọi API thật trước; nếu Backend chưa có endpoint
 * (API_CHUA_CO_TAI_LIEU / 404 / 405) thì tự fallback sang dữ liệu mẫu
 * (mock) để giao diện chạy được. Khi Backend cấp API, phần mock tự bỏ qua.
 */
window.Reservation = (function () {
  var API = window.API;
  var Auth = window.Auth;
  var mock = [];
  var seeded = false;

  function seed() {
    if (seeded) {
      return;
    }
    seeded = true;
    var now = Date.now();
    var mine = currentDocGia();
    mock.push({
      ma_dat: "RV001",
      ma_sach: "S004",
      ten_sach: "Người xa lạ",
      ma_doc_gia: mine,
      ngay_dat: new Date(now - 86400000).toISOString(),
      trang_thai: "CHO_XU_LY"
    });
    mock.push({
      ma_dat: "RV002",
      ma_sach: "S002",
      ten_sach: "Lập trình Python cơ bản",
      ma_doc_gia: mine,
      ngay_dat: new Date(now - 172800000).toISOString(),
      trang_thai: "SAN_SANG"
    });
    mock.push({
      ma_dat: "RV003",
      ma_sach: "S005",
      ten_sach: "Lịch sử Việt Nam hiện đại",
      ma_doc_gia: "DG_khac",
      ngay_dat: new Date(now - 3600000).toISOString(),
      trang_thai: "CHO_XU_LY"
    });
  }

  function isMissing(res) {
    return res && (res.code === "API_CHUA_CO_TAI_LIEU" || res.status === 404 || res.status === 405);
  }

  function currentDocGia() {
    var user = Auth.currentUser();
    if (user && user.role === "reader") {
      return "DG_" + (user.username || user.name || user.role);
    }
    return "DG_khac";
  }

  function dataForCurrentUser() {
    var user = Auth.currentUser();
    if (user && user.role === "reader") {
      var mine = currentDocGia();
      return mock.filter(function (r) {
        return r.ma_doc_gia === mine;
      });
    }
    return mock.slice();
  }

  function find(maDat) {
    for (var i = 0; i < mock.length; i++) {
      if (mock[i].ma_dat === maDat) {
        return mock[i];
      }
    }
    return null;
  }

  function list() {
    return API.call("reservations").then(function (res) {
      if (!res.ok) {
        if (isMissing(res)) {
          seed();
          return { ok: true, mock: true, data: dataForCurrentUser() };
        }
        return res;
      }
      return { ok: true, mock: false, data: res.data || [] };
    });
  }

  function create(book) {
    var payload = { ma_sach: book.ma, ma_doc_gia: currentDocGia() };
    return API.call("createReservation", payload, "POST").then(function (res) {
      if (!res.ok) {
        if (isMissing(res)) {
          seed();
          var item = {
            ma_dat: "RV" + Date.now().toString().slice(-8),
            ma_sach: book.ma,
            ten_sach: book.ten,
            ma_doc_gia: currentDocGia(),
            ngay_dat: new Date().toISOString(),
            trang_thai: "CHO_XU_LY"
          };
          mock.push(item);
          return { ok: true, mock: true, data: item };
        }
        return res;
      }
      return { ok: true, mock: false, data: res.data };
    });
  }

  function cancel(maDat) {
    return API.call("cancelReservation", undefined, "PUT", { id: maDat }).then(function (res) {
      if (!res.ok) {
        if (isMissing(res)) {
          seed();
          var item = find(maDat);
          if (item) {
            item.trang_thai = "HUY";
          }
          return { ok: true, mock: true, data: item };
        }
        return res;
      }
      return { ok: true, mock: false, data: res.data };
    });
  }

  function fulfill(maDat) {
    return API.call("fulfillReservation", undefined, "PUT", { id: maDat }).then(function (res) {
      if (!res.ok) {
        if (isMissing(res)) {
          seed();
          var item = find(maDat);
          if (item) {
            item.trang_thai = "SAN_SANG";
          }
          return { ok: true, mock: true, data: item };
        }
        return res;
      }
      return { ok: true, mock: false, data: res.data };
    });
  }

  function borrow(maDat) {
    return API.call("confirmReservation", undefined, "PUT", { id: maDat }).then(function (res) {
      if (!res.ok) {
        if (isMissing(res)) {
          seed();
          var item = find(maDat);
          if (item) {
            item.trang_thai = "DA_MUON";
          }
          return { ok: true, mock: true, data: item };
        }
        return res;
      }
      return { ok: true, mock: false, data: res.data };
    });
  }

  return {
    list: list,
    create: create,
    cancel: cancel,
    fulfill: fulfill,
    borrow: borrow
  };
})();
