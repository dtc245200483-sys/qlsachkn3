/* Danh mục thể loại + NXB (UC25) — chỉ admin. */
(function () {
  var API = window.API;
  var Auth = window.Auth;
  var messageTimer = null;
  var state = { kind: "category", editId: null };

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

  function listEndpoint(kind) {
    return kind === "category" ? "categories" : "publishers";
  }

  function load(kind) {
    var name = listEndpoint(kind);
    API.call(name)
      .then(function (res) {
        if (!res.ok) {
          showMessage(res.message);
          return;
        }
        render(kind, res.data || []);
      })
      .catch(function () {
        showMessage("Đã xảy ra lỗi khi tải danh mục.");
      });
  }

  function render(kind, list) {
    var tbodyId = kind === "category" ? "category-tbody" : "publisher-tbody";
    var tbody = document.getElementById(tbodyId);
    tbody.innerHTML = "";
    if (list.length === 0) {
      var emptyRow = document.createElement("tr");
      var emptyCell = document.createElement("td");
      emptyCell.className = "empty-row";
      emptyCell.colSpan = 3;
      emptyCell.textContent = "Chưa có dữ liệu.";
      emptyRow.appendChild(emptyCell);
      tbody.appendChild(emptyRow);
      return;
    }
    list.forEach(function (item) {
      var mapped = API.mapResponse("catalogItem", item);
      if (!mapped) {
        return;
      }
      var tr = document.createElement("tr");
      var maTd = document.createElement("td");
      maTd.textContent = mapped.ma;
      var tenTd = document.createElement("td");
      tenTd.textContent = mapped.ten;
      var actionsTd = document.createElement("td");
      var actions = document.createElement("div");
      actions.className = "row-actions";
      var edit = document.createElement("button");
      edit.type = "button";
      edit.className = "btn btn-secondary";
      edit.textContent = "Sửa";
      edit.addEventListener("click", function () {
        openForm(kind, mapped);
      });
      var del = document.createElement("button");
      del.type = "button";
      del.className = "btn btn-danger";
      del.textContent = "Xoá";
      del.addEventListener("click", function () {
        remove(kind, mapped);
      });
      actions.appendChild(edit);
      actions.appendChild(del);
      actionsTd.appendChild(actions);
      tr.appendChild(maTd);
      tr.appendChild(tenTd);
      tr.appendChild(actionsTd);
      tbody.appendChild(tr);
    });
  }

  function openForm(kind, item) {
    state.kind = kind;
    state.editId = item ? item.ma : null;
    document.getElementById("catalog-form-title").textContent =
      (kind === "category" ? "Thể loại" : "NXB") + (item ? " — sửa" : " — thêm");
    document.getElementById("catalog-form").reset();
    document.getElementById("catalog-ma").value = item ? item.ma : "";
    document.getElementById("catalog-ma").disabled = !!item;
    document.getElementById("catalog-ten").value = item ? item.ten : "";
    document.getElementById("catalog-modal").hidden = false;
  }

  function closeForm() {
    document.getElementById("catalog-modal").hidden = true;
    state.editId = null;
  }

  function save(e) {
    e.preventDefault();
    var kind = state.kind;
    var name = listEndpoint(kind);
    var ma = document.getElementById("catalog-ma").value.trim();
    var ten = document.getElementById("catalog-ten").value.trim();
    if (!ten) {
      showMessage("Vui lòng nhập tên.");
      return;
    }
    var request;
    if (state.editId !== null) {
      request = API.call("update" + (kind === "category" ? "Category" : "Publisher"), { ten: ten }, "PUT", { id: state.editId });
    } else {
      if (!ma) {
        showMessage("Vui lòng nhập mã.");
        return;
      }
      request = API.call("create" + (kind === "category" ? "Category" : "Publisher"), { ma: ma, ten: ten }, "POST");
    }
    request
      .then(function (res) {
        if (!res.ok) {
          showMessage(res.message);
          return;
        }
        closeForm();
        showMessage("Đã lưu danh mục.", "alert-success");
        clearMessage();
        load(kind);
      })
      .catch(function () {
        showMessage("Đã xảy ra lỗi khi lưu danh mục.");
      });
  }

  function remove(kind, item) {
    var ok = window.confirm('Xoá "' + item.ten + '"?');
    if (!ok) {
      return;
    }
    var name = listEndpoint(kind);
    API.call("delete" + (kind === "category" ? "Category" : "Publisher"), undefined, "DELETE", { id: item.ma })
      .then(function (res) {
        if (!res.ok) {
          showMessage(res.message);
          return;
        }
        showMessage("Đã xoá.", "alert-success");
        load(kind);
      })
      .catch(function () {
        showMessage("Đã xảy ra lỗi khi xoá.");
      });
  }

  document.addEventListener("DOMContentLoaded", function () {
    if (!Auth.requireAdmin()) {
      return;
    }
    Auth.applyRoleUI();
    document.getElementById("add-category-button").addEventListener("click", function () {
      openForm("category", null);
    });
    document.getElementById("add-publisher-button").addEventListener("click", function () {
      openForm("publisher", null);
    });
    document.getElementById("cancel-catalog-button").addEventListener("click", closeForm);
    document.getElementById("catalog-form").addEventListener("submit", save);
    load("category");
    load("publisher");
  });
})();
