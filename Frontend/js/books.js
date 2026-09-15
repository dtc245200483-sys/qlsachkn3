/* Màn hình quản lý sách: danh sách + thêm/sửa/xoá.
   Mọi dữ liệu hiển thị đều lấy từ API; không tự sinh dữ liệu giả. */
(function () {
  var API = window.API;
  var Auth = window.Auth;
  var state = {
    editId: null
  };
  var allFetchedBooks = [];
  var currentPage = 1;
  var itemsPerPage = 6;
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

  function canManage() {
    var role = (Auth.currentUser() || {}).role || "";
    return role === "librarian" || role === "admin";
  }

  function parseSort(value) {
    if (!value) {
      return { sort: "", order: "" };
    }
    var parts = String(value).split("_");
    return { sort: parts[0] || "", order: parts[1] || "asc" };
  }

  function loadBooks(opts) {
    if (!opts || opts.clear !== false) {
      clearMessage();
    }
    setLoading(true);
    var sortParsed = parseSort(document.getElementById("book-sort").value);
    var built = API.buildQuery("books", {
      sort: sortParsed.sort,
      order: sortParsed.order
    });
    API.call("books", undefined, "GET", undefined, built.query)
      .then(function (res) {
        setLoading(false);
        if (!res.ok) {
          showMessage(res.message);
          return;
        }
        if (!Array.isArray(res.data)) {
          showMessage(
            "API trả về dữ liệu sách không đúng định dạng danh sách. Cần xác nhận lại tài liệu API."
          );
          return;
        }
        var list = res.data;
        allFetchedBooks = list;
        currentPage = 1;
        renderCurrentPage();
      })
      .catch(function () {
        setLoading(false);
        showMessage("Đã xảy ra lỗi không xác định khi tải danh sách sách.");
      });
  }

  function renderCurrentPage() {
    var start = (currentPage - 1) * itemsPerPage;
    var end = start + itemsPerPage;
    var pageItems = allFetchedBooks.slice(start, end);
    renderBooks(pageItems);
    renderPagination();
  }

  function renderPagination() {
    var container = document.getElementById("pagination-controls");
    if (!container) return;
    container.innerHTML = "";

    var totalPages = Math.ceil(allFetchedBooks.length / itemsPerPage);
    if (totalPages <= 1) return;

    var prevBtn = document.createElement("button");
    prevBtn.textContent = "Trước";
    prevBtn.disabled = currentPage === 1;
    prevBtn.addEventListener("click", function() {
      if (currentPage > 1) {
        currentPage--;
        renderCurrentPage();
      }
    });
    container.appendChild(prevBtn);

    for (var i = 1; i <= totalPages; i++) {
      (function(page) {
        var btn = document.createElement("button");
        btn.textContent = page;
        if (page === currentPage) {
          btn.className = "active";
        }
        btn.addEventListener("click", function() {
          currentPage = page;
          renderCurrentPage();
        });
        container.appendChild(btn);
      })(i);
    }

    var nextBtn = document.createElement("button");
    nextBtn.textContent = "Sau";
    nextBtn.disabled = currentPage === totalPages;
    nextBtn.addEventListener("click", function() {
      if (currentPage < totalPages) {
        currentPage++;
        renderCurrentPage();
      }
    });
    container.appendChild(nextBtn);
  }

  function renderBooks(list) {
    var tbody = document.getElementById("book-list-container");
    if (!tbody) {
      return;
    }
    tbody.innerHTML = "";

    if (list.length === 0) {
      var emptyRow = document.createElement("tr");
      var emptyCell = document.createElement("td");
      emptyCell.className = "empty-row";
      emptyCell.colSpan = 8;
      emptyCell.textContent = "Chưa có dữ liệu sách.";
      emptyRow.appendChild(emptyCell);
      tbody.appendChild(emptyRow);
      return;
    }

    var mappedList = list
      .map(function (item) {
        var mapped = API.mapResponse("book", item);
        if (!mapped) {
          showMessage(
            "Chưa có cấu hình field sách trong api.js nên chưa thể hiển thị dữ liệu."
          );
          return null;
        }
        return mapped;
      })
      .filter(Boolean);

    mappedList.forEach(function (book) {
      tbody.appendChild(bookRow(book));
    });
  }

  function bookRow(book) {
    var item = document.createElement("div");
    item.className = "book-list-item";

    var coverDiv = document.createElement("div");
    coverDiv.className = "book-cover-wrap";
    
    var coverImg = document.createElement("img");
    coverImg.className = "book-cover-placeholder";
    coverImg.loading = "lazy";
    if (book.anhBia) {
      coverImg.src = book.anhBia;
    } else {
      coverImg.src = "https://ui-avatars.com/api/?name=" + encodeURIComponent(book.ten ? book.ten : "Book") + "&background=random&size=120";
    }
    coverImg.style.width = "65px";
    coverImg.style.height = "90px";
    coverImg.style.objectFit = "cover";
    coverImg.style.borderRadius = "4px";
    coverImg.style.marginBottom = "8px";

    coverDiv.appendChild(coverImg);
    item.appendChild(coverDiv);

    var infoDiv = document.createElement("div");
    infoDiv.className = "book-info-wrap";

    var title = document.createElement("h3");
    title.className = "book-title";
    title.innerHTML = book.ten + " <span style='font-size: 14px; color: #64748b; font-weight: normal;'>(Mã: " + book.ma + ")</span>";
    infoDiv.appendChild(title);

    var details = document.createElement("div");
    details.className = "book-details-row";
    
    var props = [
        { label: "Tác giả:", value: book.tacGia },
        { label: "Thể loại:", value: book.theLoai },
        { label: "NXB:", value: book.nxb + (book.namXb ? " (" + book.namXb + ")" : "") },
        { label: "Số lượng:", value: book.soLuong }
    ];
    
    props.forEach(function(p) {
        var span = document.createElement("span");
        span.className = "book-detail-item";
        span.innerHTML = "<strong>" + p.label + "</strong> " + (p.value || "—");
        details.appendChild(span);
    });
    
    infoDiv.appendChild(details);

    // === TÓM TẮT SÁCH ===
    if (book.tomTat) {
      var summaryWrap = document.createElement("div");
      summaryWrap.className = "book-summary-wrap";

      var summaryToggle = document.createElement("button");
      summaryToggle.type = "button";
      summaryToggle.className = "book-summary-toggle";
      summaryToggle.innerHTML = "<span class=\"summary-icon\">📖</span> <span class=\"summary-label\">Tóm tắt nội dung</span> <span class=\"summary-arrow\">▼</span>";

      var summaryBody = document.createElement("div");
      summaryBody.className = "book-summary-body";
      summaryBody.hidden = true;

      var summaryText = document.createElement("p");
      summaryText.className = "book-summary-text";
      summaryText.textContent = book.tomTat;

      summaryBody.appendChild(summaryText);
      summaryWrap.appendChild(summaryToggle);
      summaryWrap.appendChild(summaryBody);
      infoDiv.appendChild(summaryWrap);

      summaryToggle.addEventListener("click", function () {
        var isOpen = !summaryBody.hidden;
        summaryBody.hidden = isOpen;
        summaryWrap.classList.toggle("open", !isOpen);
        summaryToggle.querySelector(".summary-arrow").textContent = isOpen ? "▼" : "▲";
      });
    }

    item.appendChild(infoDiv);


    if (canManage()) {
      var actions = document.createElement("div");
      actions.className = "book-actions";

      var editBtn = document.createElement("button");
      editBtn.type = "button";
      editBtn.className = "btn btn-secondary btn-sm";
      editBtn.textContent = "Sửa";
      editBtn.addEventListener("click", function () {
        openForm(book);
      });

      var deleteBtn = document.createElement("button");
      deleteBtn.type = "button";
      deleteBtn.className = "btn btn-danger btn-sm";
      deleteBtn.textContent = "Xoá";
      deleteBtn.addEventListener("click", function () {
        deleteBook(book);
      });

      actions.appendChild(editBtn);
      actions.appendChild(deleteBtn);
      item.appendChild(actions);
    }
    return item;
  }

  function openForm(book) {
    state.editId = book ? book.ma : null;
    var form = document.getElementById("book-form");
    var title = document.getElementById("book-form-title");
    var modal = document.getElementById("book-modal");

    if (title) {
      title.textContent = book ? "Sửa sách" : "Thêm sách";
    }
    if (form) {
      form.reset();
      clearInlineErrors(form);
      if (book) {
        ["ma", "ten", "tacGia", "theLoai", "nxb", "namXb", "soLuong", "anhBia", "tomTat"].forEach(
          function (key) {
            var input = form.elements[key];
            if (input) {
              input.value = (book[key] === null || book[key] === undefined) ? "" : book[key];
            }
          }
        );
      }
    }
    if (modal) {
      modal.hidden = false;
    }
  }

  function loadCategoriesAndPublishers() {
    if (!canManage()) return;

    API.call("categories", undefined, "GET")
      .then(function(res) {
        if (res.ok && Array.isArray(res.data)) {
          var select = document.getElementById("book-theloai");
          if (select) {
            select.innerHTML = '<option value="">-- Chọn thể loại --</option>';
            res.data.forEach(function(cat) {
              var opt = document.createElement("option");
              opt.value = cat.ten;
              opt.textContent = cat.ten;
              select.appendChild(opt);
            });
          }
        }
      });

    API.call("publishers", undefined, "GET")
      .then(function(res) {
        if (res.ok && Array.isArray(res.data)) {
          var select = document.getElementById("book-nxb");
          if (select) {
            select.innerHTML = '<option value="">-- Chọn NXB --</option>';
            res.data.forEach(function(pub) {
              var opt = document.createElement("option");
              opt.value = pub.ten;
              opt.textContent = pub.ten;
              select.appendChild(opt);
            });
          }
        }
      });
  }

  function closeForm() {
    var modal = document.getElementById("book-modal");
    if (modal) {
      modal.hidden = true;
    }
    state.editId = null;
  }

  function clearInlineErrors(form) {
    var errs = form.querySelectorAll(".inline-error");
    for (var i = 0; i < errs.length; i++) {
      errs[i].remove();
    }
    var inputs = form.querySelectorAll(".input-error");
    for (var i = 0; i < inputs.length; i++) {
      inputs[i].classList.remove("input-error");
    }
  }

  function showInlineErrors(form, errors) {
    var unhandled = [];
    Object.keys(errors).forEach(function (key) {
      var input = form.elements[key];
      if (input) {
        input.classList.add("input-error");
        var errDiv = document.createElement("div");
        errDiv.className = "inline-error";
        errDiv.textContent = errors[key];
        input.parentNode.appendChild(errDiv);
      } else {
        unhandled.push(errors[key]);
      }
    });
    if (unhandled.length > 0) {
      showMessage(unhandled.join("; "));
    }
  }

  function saveBook(e) {
    e.preventDefault();
    var form = document.getElementById("book-form");
    clearInlineErrors(form);

    var built = API.serializeForm(form, "book");
    if (!built.ok) {
      showMessage(built.message);
      return;
    }

    var isEdit = state.editId !== null;
    var name = isEdit ? "updateBook" : "createBook";
    var pathParams = isEdit ? { ma: state.editId } : undefined;

    var button = document.getElementById("save-book-button");
    if (button) {
      button.disabled = true;
      button.textContent = "Đang lưu...";
    }

    API.call(name, built.payload, isEdit ? "PUT" : "POST", pathParams)
      .then(function (res) {
        if (button) {
          button.disabled = false;
          button.textContent = "Lưu";
        }
        if (!res.ok) {
          if (res.fieldErrors && Object.keys(res.fieldErrors).length > 0) {
            showInlineErrors(form, res.fieldErrors);
          } else {
            showMessage(res.message);
          }
          return;
        }
        closeForm();
        showMessage(isEdit ? "Đã cập nhật sách." : "Đã thêm sách.", "alert-success");
        loadBooks({ clear: false });
      })
      .catch(function () {
        if (button) {
          button.disabled = false;
          button.textContent = "Lưu";
        }
        showMessage("Đã xảy ra lỗi không xác định khi lưu sách.");
      });
  }

  function deleteBook(book) {
    var ok = window.confirm('Xoá sách "' + (book.ten || book.ma || "") + '"?');
    if (!ok) {
      return;
    }
    API.call("deleteBook", undefined, "DELETE", { ma: book.ma })
      .then(function (res) {
        if (!res.ok) {
          showMessage(res.message);
          return;
        }
        showMessage("Đã xoá sách.", "alert-success");
        loadBooks({ clear: false });
      })
      .catch(function () {
        showMessage("Đã xảy ra lỗi không xác định khi xoá sách.");
      });
  }

  function init() {
    Auth.requireAuth();
    Auth.applyRoleUI();

    var addButton = document.getElementById("add-book-button");
    if (addButton) {
      addButton.addEventListener("click", function () {
        openForm(null);
      });
    }
    var form = document.getElementById("book-form");
    if (form) {
      form.addEventListener("submit", saveBook);
    }

    var cancelButton = document.getElementById("cancel-book-button");
    if (cancelButton) {
      cancelButton.addEventListener("click", closeForm);
    }

    var modal = document.getElementById("book-modal");
    if (modal) {
      modal.addEventListener("click", function (e) {
        if (e.target === modal) {
          closeForm();
        }
      });
    }

    var sortSelect = document.getElementById("book-sort");
    if (sortSelect) {
      sortSelect.addEventListener("change", function () {
        loadBooks({ clear: false });
      });
    }

    var coverDropZone = document.getElementById("cover-drop-zone");
    var coverFileInput = document.getElementById("book-anhbia-file");
    var coverStatus = document.getElementById("cover-upload-status");
    var coverUrlInput = document.getElementById("book-anhbia");

    if (coverDropZone && coverFileInput) {
      coverDropZone.addEventListener("click", function () {
        coverFileInput.click();
      });

      coverDropZone.addEventListener("dragover", function (e) {
        e.preventDefault();
        coverDropZone.style.backgroundColor = "#e2e8f0";
      });

      coverDropZone.addEventListener("dragleave", function (e) {
        e.preventDefault();
        coverDropZone.style.backgroundColor = "#f8fafc";
      });

      coverDropZone.addEventListener("drop", function (e) {
        e.preventDefault();
        coverDropZone.style.backgroundColor = "#f8fafc";
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
          handleCoverUpload(e.dataTransfer.files[0]);
        }
      });

      coverFileInput.addEventListener("change", function () {
        if (coverFileInput.files && coverFileInput.files.length > 0) {
          handleCoverUpload(coverFileInput.files[0]);
        }
      });
    }

    function handleCoverUpload(file) {
      if (!file.type.match("image.*")) {
        coverStatus.textContent = "Vui lòng chọn một tệp hình ảnh.";
        coverStatus.style.color = "#ef4444";
        return;
      }
      coverStatus.textContent = "Đang tải lên...";
      coverStatus.style.color = "#3b82f6";

      API.uploadFile("uploadBookCover", file)
        .then(function (res) {
          if (!res.ok) {
            coverStatus.textContent = "Lỗi tải lên: " + (res.message || "Không xác định");
            coverStatus.style.color = "#ef4444";
            return;
          }
          if (res.data && res.data.url) {
            coverUrlInput.value = res.data.url;
            coverStatus.textContent = "Tải lên thành công!";
            coverStatus.style.color = "#10b981";
          } else {
            coverStatus.textContent = "Không nhận được URL từ máy chủ.";
            coverStatus.style.color = "#ef4444";
          }
        })
        .catch(function () {
          coverStatus.textContent = "Lỗi kết nối khi tải lên.";
          coverStatus.style.color = "#ef4444";
        });
    }

    loadBooks();
    loadCategoriesAndPublishers();
  }

  document.addEventListener("DOMContentLoaded", init);
})();
