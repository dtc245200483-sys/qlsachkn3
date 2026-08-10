/* Trang Cấu hình admin — thư viện (UC24), AI (UC26), backup/restore (UC27). */
(function () {
  var API = window.API;
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
    }, 7000);
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

  function loadLibraryConfig() {
    clearMessage();
    setLoading(true);
    API.call("libraryConfig")
      .then(function (res) {
        setLoading(false);
        if (!res.ok) {
          showMessage(res.message);
          return;
        }
        var cfg = API.mapResponse("libraryConfig", res.data);
        if (!cfg) {
          showMessage("Chưa có cấu hình field cấu hình thư viện.");
          return;
        }
        var form = document.getElementById("library-config-form");
        form.elements.maxBorrowDays.value = cfg.maxBorrowDays;
        form.elements.overdueFinePointsPerDay.value =
          cfg.overdueFinePointsPerDay !== "" ? cfg.overdueFinePointsPerDay : 2;
        form.elements.maxBooksAtOnce.value = cfg.maxBooksAtOnce;
      })
      .catch(function () {
        setLoading(false);
        showMessage("Đã xảy ra lỗi khi tải cấu hình thư viện.");
      });
  }

  function validateLibraryConfig(form) {
    var maxDays = form.elements.maxBorrowDays.value;
    var points = form.elements.overdueFinePointsPerDay.value;
    var maxBooks = form.elements.maxBooksAtOnce.value;

    if (maxDays === "") {
      return "Chưa nhập số ngày mượn tối đa.";
    }
    var nDays = Number(maxDays);
    if (isNaN(nDays) || nDays < 1 || nDays > 365) {
      return "Số ngày mượn tối đa phải từ 1 đến 365.";
    }
    if (points === "") {
      return "Chưa nhập điểm phạt quá hạn.";
    }
    var nPoints = Number(points);
    if (isNaN(nPoints) || nPoints < 0) {
      return "Điểm phạt quá hạn không được âm.";
    }
    if (maxBooks === "") {
      return "Chưa nhập giới hạn số sách mượn.";
    }
    var nBooks = Number(maxBooks);
    if (isNaN(nBooks) || nBooks < 1 || nBooks > 100) {
      return "Giới hạn số sách mượn phải từ 1 đến 100.";
    }
    return "";
  }

  function saveLibraryConfig(e) {
    e.preventDefault();
    var form = document.getElementById("library-config-form");
    var error = validateLibraryConfig(form);
    if (error) {
      showMessage(error);
      return;
    }
    var built = API.serializeForm(form, "libraryConfig");
    if (!built.ok) {
      showMessage(built.message);
      return;
    }
    API.call("updateLibraryConfig", built.payload, "PUT")
      .then(function (res) {
        if (!res.ok) {
          showMessage(res.message);
          return;
        }
        showMessage("Đã lưu cấu hình thư viện.", "alert-success");
        loadLibraryConfig();
      })
      .catch(function () {
        showMessage("Đã xảy ra lỗi khi lưu cấu hình thư viện.");
      });
  }

  function loadAiConfig() {
    clearMessage();
    setLoading(true);
    API.call("aiConfig")
      .then(function (res) {
        setLoading(false);
        if (!res.ok) {
          showMessage(res.message);
          return;
        }
        var cfg = API.mapResponse("aiConfigOut", res.data);
        if (!cfg) {
          showMessage("Chưa có cấu hình field cấu hình AI.");
          return;
        }
        var form = document.getElementById("ai-config-form");
        form.elements.provider.value = cfg.provider;
        form.elements.model.value = cfg.model;
        form.elements.promptTemplate.value = cfg.promptTemplate;
        form.elements.apiKey.value = "";
        form.elements.clearKey.checked = false;
        form.elements.apiKey.placeholder = cfg.hasApiKey
          ? cfg.apiKeyMasked + " — nhập key mới để thay"
          : "Chưa có API key";
        document.getElementById("ai-key-status").textContent = cfg.hasApiKey
          ? "API key hiện tại: " + cfg.apiKeyMasked
          : "Chưa có API key.";
      })
      .catch(function () {
        setLoading(false);
        showMessage("Đã xảy ra lỗi khi tải cấu hình AI.");
      });
  }

  function saveAiConfig(e) {
    e.preventDefault();
    var form = document.getElementById("ai-config-form");
    var payload = {
      provider: form.elements.provider.value,
      model: form.elements.model.value,
      prompt_template: form.elements.promptTemplate.value
    };
    if (form.elements.apiKey.value) {
      payload.api_key = form.elements.apiKey.value;
    }
    if (form.elements.clearKey.checked) {
      payload.api_key = "";
    }
    API.call("updateAiConfig", payload, "PUT")
      .then(function (res) {
        if (!res.ok) {
          showMessage(res.message);
          return;
        }
        showMessage("Đã lưu cấu hình AI.", "alert-success");
        loadAiConfig();
      })
      .catch(function () {
        showMessage("Đã xảy ra lỗi khi lưu cấu hình AI.");
      });
  }

  function backupDatabase() {
    var button = document.getElementById("backup-button");
    button.disabled = true;
    button.textContent = "Đang sao lưu...";
    API.call("backup", undefined, "POST")
      .then(function (res) {
        button.disabled = false;
        button.textContent = "Sao lưu CSDL";
        if (!res.ok) {
          showMessage(res.message);
          return;
        }
        var mapped = API.mapResponse("backupOut", res.data);
        var text = mapped && mapped.message ? mapped.message : "Đã sao lưu CSDL.";
        if (mapped && mapped.path) {
          text += " — " + mapped.path;
        }
        showMessage(text, "alert-success");
      })
      .catch(function () {
        button.disabled = false;
        button.textContent = "Sao lưu CSDL";
        showMessage("Đã xảy ra lỗi khi sao lưu CSDL.");
      });
  }

  function restoreDatabase() {
    var path = document.getElementById("restore-path").value.trim();
    if (!path) {
      showMessage("Vui lòng nhập đường dẫn file .bak.");
      return;
    }
    var ok = window.confirm("Phục hồi sẽ THAY THẾ toàn bộ dữ liệu hiện tại. Tiếp tục?");
    if (!ok) {
      return;
    }
    var button = document.getElementById("restore-button");
    button.disabled = true;
    button.textContent = "Đang phục hồi...";
    API.call("restore", { file_path: path }, "POST")
      .then(function (res) {
        button.disabled = false;
        button.textContent = "Phục hồi CSDL";
        if (!res.ok) {
          showMessage(res.message);
          return;
        }
        var mapped = API.mapResponse("restoreOut", res.data);
        showMessage(mapped && mapped.message ? mapped.message : "Đã phục hồi CSDL.", "alert-success");
      })
      .catch(function () {
        button.disabled = false;
        button.textContent = "Phục hồi CSDL";
        showMessage("Đã xảy ra lỗi khi phục hồi CSDL.");
      });
  }

  document.addEventListener("DOMContentLoaded", function () {
    if (!Auth.requireAdmin()) {
      return;
    }
    Auth.applyRoleUI();
    document.getElementById("library-config-form").addEventListener("submit", saveLibraryConfig);
    loadLibraryConfig();
  });
})();
