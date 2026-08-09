/*
 * Cấu hình kết nối API — theo Backend/api_docs.md 0.6.0:
 * chức năng 1–5 + đăng ký, yêu cầu mượn/trả/gia hạn, lịch sử độc giả,
 * quản lý tài khoản, danh mục thể loại/NXB. API key AI do Backend giữ.
 */
window.API = (function () {
  var config = {
    baseUrl: "http://localhost:8000",
    endpoints: {
      login: "/api/auth/login",
      books: "/api/books",
      createBook: "/api/books",
      updateBook: "/api/books/{id}",
      deleteBook: "/api/books/{id}",
      readers: "/api/readers",
      createReader: "/api/readers",
      updateReader: "/api/readers/{id}",
      deleteReader: "/api/readers/{id}",
      createBorrow: "/api/borrows",
      borrows: "/api/borrows",
      returnBorrow: "/api/borrows/{id}/return",
      renewBorrow: "/api/borrows/{id}/renew",
      register: "/api/auth/register",
      myBorrows: "/api/borrows/me",
      deleteMyBorrow: "/api/borrows/me/{id}",
      deleteMyBorrows: "/api/borrows/me",
      reservations: "/api/reservations",
      createReservation: "/api/reservations",
      cancelReservation: "/api/reservations/{id}/cancel",
      fulfillReservation: "/api/reservations/{id}/fulfill",
      /*
       * UC11 — Thông báo: Backend chưa có endpoint riêng nên Frontend hiện
       * TỰ TỔNG HỢP từ /api/borrows/me + /api/reservations. Khi Backend cấp,
       * chuyển notifications.html sang gọi endpoint này.
       */
      notifications: "/api/notifications",
      /*
       * Chức năng 7 — Thống kê: Backend chưa có API, Frontend dùng mock
       * tạm. Endpoint dự kiến khi Backend cấp:
       *   statsTopBooks    -> GET /api/stats/top-books
       *   statsTopReaders  -> GET /api/stats/top-readers
       *   statsOverdueBooks-> GET /api/stats/overdue-books
       */
      statsTopBooks: "/api/stats/top-books",
      statsTopReaders: "/api/stats/top-readers",
      statsOverdueBooks: "/api/stats/overdue-books",
      /*
       * Chức năng 8 — Xuất dữ liệu (CSV). Backend chưa có endpoint,
       * gọi sẽ báo "chưa sẵn sàng". Endpoint dự kiến:
       *   exportBooks   -> GET /api/export/books.csv
       *   exportBorrows -> GET /api/export/borrows.csv
       *   exportReport  -> GET /api/export/report.csv
       */
      exportBooks: "/api/export/books.csv",
      exportBorrows: "/api/export/borrows.csv",
      exportReport: "/api/export/report.csv",
      aiConfig: "/api/admin/config/ai",
      updateAiConfig: "/api/admin/config/ai",
      backup: "/api/admin/backup",
      restore: "/api/admin/restore",
      /*
       * UC19 — Thu phạt: Backend chưa có API. Endpoint dự kiến:
       *   collectFine -> POST /api/borrows/{id}/collect-fine
       * (danh sách phạt chưa thu hiện đang dùng dữ liệu mẫu ở borrow.html)
       */
      collectFine: "/api/borrows/{id}/collect-fine",
      /*
       * Reader xoá lịch sử yêu cầu — Backend chưa có API (config chờ):
       *   deleteMyRequest  -> DELETE /api/requests/me/{ma_yeu_cau}
       *   deleteMyRequests -> DELETE /api/requests/me
       */
      deleteMyRequest: "/api/requests/me/{id}",
      deleteMyRequests: "/api/requests/me",
      requests: "/api/requests",
      createRequest: "/api/requests",
      approveRequest: "/api/requests/{id}/approve",
      rejectRequest: "/api/requests/{id}/reject",
      accounts: "/api/admin/accounts",
      createAccount: "/api/admin/accounts",
      updateAccount: "/api/admin/accounts/{id}",
      deleteAccount: "/api/admin/accounts/{id}",
      categories: "/api/admin/categories",
      createCategory: "/api/admin/categories",
      updateCategory: "/api/admin/categories/{id}",
      deleteCategory: "/api/admin/categories/{id}",
      publishers: "/api/admin/publishers",
      createPublisher: "/api/admin/publishers",
      updatePublisher: "/api/admin/publishers/{id}",
      deletePublisher: "/api/admin/publishers/{id}",
      libraryConfig: "/api/admin/config/library",
      updateLibraryConfig: "/api/admin/config/library"
    },
    fieldMap: {
      login: {
        username: "username",
        password: "password"
      },
      loginResponse: {
        token: "token",
        role: "role",
        name: "name"
      },
      book: {
        ma: "ma",
        ten: "ten",
        tacGia: "tacGia",
        theLoai: "theLoai",
        nxb: "nxb",
        namXb: "namXb",
        soLuong: "soLuong"
      },
      readerCreate: {
        ma: "ma",
        hoTen: "hoTen",
        email: "email",
        soDienThoai: "soDienThoai",
        loaiDocGia: "loaiDocGia",
        trangThaiThe: "trangThaiThe"
      },
      readerOut: {
        ma: "ma",
        hoTen: "hoTen",
        email: "email",
        soDienThoai: "soDienThoai",
        loaiDocGia: "loaiDocGia",
        trangThaiThe: "trangThaiThe",
        ngayTao: "ngayTao"
      },
      borrowSlipOut: {
        maPhieu: "ma_phieu",
        maDocGia: "ma_doc_gia",
        ngayMuon: "ngay_muon",
        hanTra: "han_tra",
        ngayTra: "ngay_tra",
        trangThai: "trang_thai",
        soLanGiaHan: "so_lan_gia_han",
        details: "details"
      },
      borrowDetailOut: {
        maSach: "ma_sach",
        soLuong: "so_luong",
        ngayTraChiTiet: "ngay_tra_chi_tiet"
      },
      borrowReturnOut: {
        message: "message",
        ngayTra: "ngay_tra",
        fine: "fine"
      },
      borrowRenewOut: {
        message: "message",
        hanTraMoi: "han_tra_moi",
        soLanGiaHan: "so_lan_gia_han",
        fine: "fine"
      },
      fineOut: {
        soNgayQuaHan: "so_ngay_qua_han",
        soTien: "so_tien"
      },
      register: {
        username: "username",
        password: "password",
        hoTen: "hoTen",
        email: "email",
        soDienThoai: "soDienThoai",
        loaiDocGia: "loaiDocGia"
      },
      registerResponse: {
        token: "token",
        role: "role",
        name: "name",
        readerMa: "reader_ma"
      },
      borrowHistoryOut: {
        maPhieu: "ma_phieu",
        maDocGia: "ma_doc_gia",
        ngayMuon: "ngay_muon",
        hanTra: "han_tra",
        ngayTra: "ngay_tra",
        trangThai: "trang_thai",
        soLanGiaHan: "so_lan_gia_han",
        details: "details",
        fines: "fines"
      },
      requestOut: {
        maYeuCau: "ma_yeu_cau",
        loai: "loai",
        maDocGia: "ma_doc_gia",
        maPhieu: "ma_phieu",
        items: "items",
        soNgayMuon: "so_ngay_muon",
        trangThai: "trang_thai",
        ngayTao: "ngay_tao"
      },
      accountCreate: {
        username: "username",
        password: "password",
        hoTen: "ho_ten",
        role: "role",
        readerId: "reader_id"
      },
      accountOut: {
        id: "id",
        username: "username",
        hoTen: "ho_ten",
        role: "role",
        isActive: "is_active",
        readerId: "reader_id",
        createdAt: "created_at"
      },
      catalogItem: {
        ma: "ma",
        ten: "ten"
      },
      libraryConfig: {
        maxBorrowDays: "max_borrow_days",
        overdueFinePerDay: "overdue_fine_per_day",
        maxBooksAtOnce: "max_books_at_once"
      },
      reservationCreate: {
        maSach: "ma_sach",
        maDocGia: "ma_doc_gia"
      },
      reservationOut: {
        maDat: "ma_dat",
        maSach: "ma_sach",
        tenSach: "ten_sach",
        maDocGia: "ma_doc_gia",
        ngayDat: "ngay_dat",
        trangThai: "trang_thai"
      },
      statsBookOut: {
        maSach: "ma_sach",
        tenSach: "ten_sach",
        soLanMuon: "so_lan_muon"
      },
      statsReaderOut: {
        maDocGia: "ma_doc_gia",
        hoTen: "ho_ten",
        soPhieuMuon: "so_phieu_muon"
      },
      statsOverdueOut: {
        maPhieu: "ma_phieu",
        maSach: "ma_sach",
        tenSach: "ten_sach",
        maDocGia: "ma_doc_gia",
        hoTen: "ho_ten",
        soNgayQuaHan: "so_ngay_qua_han"
      },
      aiConfigOut: {
        provider: "provider",
        model: "model",
        apiKeyMasked: "api_key_masked",
        hasApiKey: "has_api_key",
        promptTemplate: "prompt_template"
      },
      backupOut: {
        message: "message",
        path: "path"
      },
      restoreOut: {
        message: "message"
      }
    },
    roleMap: {
      admin: "admin",
      librarian: "librarian",
      reader: "reader"
    },
    queryMap: {
      books: {
        q: "q",
        theLoai: "theLoai",
        trangThai: "trangThai"
      },
      borrows: {
        docGia: "docGia",
        trangThai: "trangThai"
      },
      requests: {
        maDocGia: "maDocGia",
        trangThai: "trangThai"
      },
      accounts: {
        role: "role"
      }
    },
  };

  function missingConfig(name) {
    return {
      ok: false,
      code: "API_CHUA_CO_TAI_LIEU",
      message:
        'Chưa có tài liệu API từ Backend nên chưa thể gọi "' + name + '". ' +
        "Cập nhật Frontend/js/api.js khi có tài liệu từ Thư Ký."
    };
  }

  function call(name, payload, method, pathParams, query) {
    var endpoint = config.endpoints[name];
    if (!config.baseUrl || !endpoint) {
      return Promise.resolve(missingConfig(name));
    }

    var url = config.baseUrl + endpoint;
    if (pathParams) {
      Object.keys(pathParams).forEach(function (key) {
        url = url.split("{" + key + "}").join(encodeURIComponent(pathParams[key]));
      });
    }
    if (query) {
      var parts = [];
      Object.keys(query).forEach(function (key) {
        var value = query[key];
        if (value !== undefined && value !== null && value !== "") {
          parts.push(encodeURIComponent(key) + "=" + encodeURIComponent(value));
        }
      });
      if (parts.length > 0) {
        url += (url.indexOf("?") === -1 ? "?" : "&") + parts.join("&");
      }
    }

    var options = {
      method: method || "GET",
      headers: { Accept: "application/json" }
    };

    if (payload !== undefined) {
      options.headers["Content-Type"] = "application/json";
      options.body = JSON.stringify(payload);
    }

    var session = null;
    try {
      var raw = sessionStorage.getItem("thuvien_session");
      session = raw ? JSON.parse(raw) : null;
    } catch (e) {
      session = null;
    }
    if (session && session.token) {
      options.headers.Authorization = "Bearer " + session.token;
    }

    return fetch(url, options)
      .then(function (res) {
        var textPromise = res.text();
        return textPromise.then(function (text) {
          var data = null;
          if (text) {
            try {
              data = JSON.parse(text);
            } catch (e) {
              data = text;
            }
          }
          if (!res.ok) {
            var rawDetail = data && (data.message || data.detail);
            var message;
            if (Array.isArray(rawDetail)) {
              message = rawDetail
                .map(function (d) {
                  return d && d.msg ? d.msg : JSON.stringify(d);
                })
                .join("; ");
            } else if (rawDetail && typeof rawDetail === "object") {
              message = JSON.stringify(rawDetail);
            } else {
              message = rawDetail ? String(rawDetail) : "Lỗi máy chủ: HTTP " + res.status;
            }
            return {
              ok: false,
              code: "HTTP_" + res.status,
              status: res.status,
              message: message,
              data: data
            };
          }
          return { ok: true, status: res.status, data: data };
        });
      })
      .catch(function (err) {
        return {
          ok: false,
          code: "NETWORK_ERROR",
          message:
            "Không kết nối được máy chủ. Kiểm tra baseUrl trong api.js và cấu hình CORS của Backend.",
          error: err
        };
      });
  }

  function serializeForm(form, section) {
    var map = config.fieldMap[section];
    if (!map || Object.keys(map).length === 0) {
      return {
        ok: false,
        message:
          'Chưa có cấu hình field cho "' + section + '" trong api.js nên chưa thể gửi dữ liệu.'
      };
    }
    var payload = {};
    Object.keys(map).forEach(function (internalKey) {
      var input = form.elements[internalKey];
      var value = "";
      if (input) {
        if (input.type === "checkbox") {
          value = input.checked;
        } else if (input.type === "number") {
          value = input.value === "" ? "" : Number(input.value);
        } else {
          value = input.value;
        }
      }
      payload[map[internalKey]] = value;
    });
    return { ok: true, payload: payload };
  }

  function mapResponse(section, item) {
    var map = config.fieldMap[section];
    if (!map || Object.keys(map).length === 0) {
      return null;
    }
    var out = {};
    Object.keys(map).forEach(function (internalKey) {
      var apiKey = map[internalKey];
      out[internalKey] = item && item[apiKey] !== undefined ? item[apiKey] : "";
    });
    return out;
  }

  function canonicalRole(rawRole) {
    var map = config.roleMap || {};
    if (map[rawRole]) {
      return map[rawRole];
    }
    if (["admin", "librarian", "reader"].indexOf(rawRole) !== -1) {
      return rawRole;
    }
    return "";
  }

  function buildQuery(name, params) {
    var map = config.queryMap[name];
    if (!map) {
      return { ok: false, query: {} };
    }
    var query = {};
    Object.keys(map).forEach(function (internalKey) {
      var value = params ? params[internalKey] : undefined;
      if (value !== undefined && value !== null && value !== "") {
        query[map[internalKey]] = value;
      }
    });
    return { ok: true, query: query };
  }

  function downloadFile(name, filename) {
    var endpoint = config.endpoints[name];
    if (!config.baseUrl || !endpoint) {
      return Promise.resolve({
        ok: false,
        code: "API_CHUA_CO_TAI_LIEU",
        message: 'Chưa có cấu hình endpoint export "' + name + '" trong api.js.'
      });
    }
    var session = null;
    try {
      var raw = sessionStorage.getItem("thuvien_session");
      session = raw ? JSON.parse(raw) : null;
    } catch (e) {
      session = null;
    }
    var headers = { Accept: "text/csv, application/octet-stream" };
    if (session && session.token) {
      headers.Authorization = "Bearer " + session.token;
    }
    return fetch(config.baseUrl + endpoint, { headers: headers })
      .then(function (res) {
        if (!res.ok) {
          return res.text().then(function (text) {
            var message = text && text.indexOf("{") === 0 ? text : "Lỗi khi tải file: HTTP " + res.status;
            return { ok: false, status: res.status, message: message };
          });
        }
        return res.blob().then(function (blob) {
          var url = URL.createObjectURL(blob);
          var a = document.createElement("a");
          a.href = url;
          a.download = filename;
          document.body.appendChild(a);
          a.click();
          a.remove();
          URL.revokeObjectURL(url);
          return { ok: true };
        });
      })
      .catch(function (err) {
        return {
          ok: false,
          code: "NETWORK_ERROR",
          message: "Không tải được file xuất dữ liệu.",
          error: err
        };
      });
  }

  return {
    config: config,
    call: call,
    serializeForm: serializeForm,
    mapResponse: mapResponse,
    canonicalRole: canonicalRole,
    buildQuery: buildQuery,
    downloadFile: downloadFile
  };
})();
