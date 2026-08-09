/* Màn hình quản lý sách: danh sách + thêm/sửa/xoá.
   Mọi dữ liệu hiển thị đều lấy từ API; không tự sinh dữ liệu giả. */
(function () {
  var API = window.API;
  var Auth = window.Auth;
  var state = {
    editId: null
  };
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
        if (!API.config.sortBooksBackend) {
          list = API.sortBooks(list, sortParsed.sort, sortParsed.order);
        }
        renderBooks(list);
      })
      .catch(function () {
        setLoading(false);
        showMessage("Đã xảy ra lỗi không xác định khi tải danh sách sách.");
      });
  }

  function renderBooks(list) {
    var tbody = document.getElementById("book-tbody");
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
    var tr = document.createElement("tr");

    ["ma", "ten", "tacGia", "theLoai", "nxb", "namXb", "soLuong"].forEach(
      function (key) {
        var td = document.createElement("td");
        td.textContent = book[key] === "" || book[key] === null ? "—" : book[key];
        tr.appendChild(td);
      }
    );

    var actionsTd = document.createElement("td");
    if (canManage()) {
      var actions = document.createElement("div");
      actions.className = "row-actions";

      var editBtn = document.createElement("button");
      editBtn.type = "button";
      editBtn.className = "btn btn-secondary";
      editBtn.textContent = "Sửa";
      editBtn.addEventListener("click", function () {
        openForm(book);
      });

      var deleteBtn = document.createElement("button");
      deleteBtn.type = "button";
      deleteBtn.className = "btn btn-danger";
      deleteBtn.textContent = "Xoá";
      deleteBtn.addEventListener("click", function () {
        deleteBook(book);
      });

      actions.appendChild(editBtn);
      actions.appendChild(deleteBtn);
      actionsTd.appendChild(actions);
    } else {
      actionsTd.textContent = "—";
    }
    tr.appendChild(actionsTd);
    return tr;
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
      if (book) {
        ["ma", "ten", "tacGia", "theLoai", "nxb", "namXb", "soLuong"].forEach(
          function (key) {
            var input = form.elements[key];
            if (input) {
              input.value = book[key] === null ? "" : book[key];
            }
          }
        );
      }
    }
    if (modal) {
      modal.hidden = false;
    }
  }

  function closeForm() {
    var modal = document.getElementById("book-modal");
    if (modal) {
      modal.hidden = true;
    }
    state.editId = null;
  }

  function saveBook(e) {
    e.preventDefault();
    var form = document.getElementById("book-form");
    var built = API.serializeForm(form, "book");
    if (!built.ok) {
      showMessage(built.message);
      return;
    }

    var isEdit = state.editId !== null;
    var name = isEdit ? "updateBook" : "createBook";
    var pathParams = isEdit ? { id: state.editId } : undefined;

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
          showMessage(res.message);
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
    API.call("deleteBook", undefined, "DELETE", { id: book.ma })
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

    loadBooks();
  }

  document.addEventListener("DOMContentLoaded", init);
})();
