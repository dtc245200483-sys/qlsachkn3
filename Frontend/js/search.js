/* Trang tra cứu sách — mọi vai trò đã đăng nhập đều dùng được. */
(function () {
  var API = window.API;
  var Auth = window.Auth;
  var messageTimer = null;
  var theLoaiSet = {};

  var allFetchedBooks = [];
  var currentPage = 1;
  var itemsPerPage = 6;

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

  /*
   * Backend đã hỗ trợ q/theLoai/trangThai/sort/order (api_docs 0.13+).
   * Lọc sách "hết" (soLuong <= 0) client-side.
   */
  function clientFilter(list, filters) {
    return list.filter(function (book) {
      if (filters.trangThai === "het" && book.soLuong > 0) {
        return false;
      }
      return true;
    });
  }

  function loadCategories() {
    API.call("categories", undefined, "GET")
      .then(function(res) {
        if (res.ok && Array.isArray(res.data)) {
          var select = document.getElementById("search-theloai");
          if (select) {
            var current = select.value;
            select.innerHTML = '<option value="">Tất cả thể loại</option>';
            res.data.forEach(function(cat) {
              var opt = document.createElement("option");
              opt.value = cat.ten;
              opt.textContent = cat.ten;
              select.appendChild(opt);
            });
            select.value = current;
          }
        }
      });
  }

  function parseSort(value) {
    if (!value) {
      return { sort: "", order: "" };
    }
    var parts = String(value).split("_");
    return { sort: parts[0] || "", order: parts[1] || "asc" };
  }

  function loadBooks() {
    clearMessage();
    setLoading(true);
    var q = document.getElementById("search-q").value.trim();
    var theLoai = document.getElementById("search-theloai").value;
    var trangThai = document.getElementById("search-trangthai").value;
    var sortParsed = parseSort(document.getElementById("search-sort").value);
    // "het" không phải giá trị hợp lệ của Backend -> lấy tất cả rồi lọc client-side
    var apiTrangThai = trangThai === "het" ? "" : trangThai;
    var built = API.buildQuery("books", {
      q: q,
      theLoai: theLoai,
      trangThai: apiTrangThai,
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
          showMessage("API trả về danh sách sách không đúng định dạng.");
          return;
        }
        var list = clientFilter(res.data, { q: q, theLoai: theLoai, trangThai: trangThai });
        if (!API.config.sortBooksBackend) {
          list = API.sortBooks(list, sortParsed.sort, sortParsed.order);
        }
        allFetchedBooks = list;
        currentPage = 1;
        renderCurrentPage();
      })
      .catch(function () {
        setLoading(false);
        showMessage("Đã xảy ra lỗi không xác định khi tra cứu sách.");
      });
  }

  function renderCurrentPage() {
    var start = (currentPage - 1) * itemsPerPage;
    var end = start + itemsPerPage;
    var pageItems = allFetchedBooks.slice(start, end);
    render(pageItems);
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

  function render(list) {
    var tbody = document.getElementById("book-list-container");
    if (!tbody) {
      return;
    }
    tbody.innerHTML = "";

    if (list.length === 0) {
      var emptyRow = document.createElement("div");
      emptyRow.className = "empty-list";
      emptyRow.style.padding = "20px";
      emptyRow.style.textAlign = "center";
      emptyRow.textContent = "Không tìm thấy sách nào phù hợp.";
      tbody.appendChild(emptyRow);
      return;
    }

    list.forEach(function (book) {
      var mapped = API.mapResponse("book", book);
      if (!mapped) {
        return;
      }
      tbody.appendChild(row(mapped));
    });
  }

  function row(book) {
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
        span.innerHTML = "<strong>" + p.label + "</strong> " + (p.value !== null && p.value !== undefined && p.value !== "" ? p.value : "—");
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

      (function(toggle, body, wrap) {
        toggle.addEventListener("click", function () {
          var isOpen = !body.hidden;
          body.hidden = isOpen;
          wrap.classList.toggle("open", !isOpen);
          toggle.querySelector(".summary-arrow").textContent = isOpen ? "▼" : "▲";
        });
      })(summaryToggle, summaryBody, summaryWrap);
    }

    item.appendChild(infoDiv);


    var available = Number(book.soLuong) > 0;
    var statusText = available ? "Còn sách" : "Hết sách";
    if (book.trangThai === "dang_muon") statusText = "Đang mượn";
    
    var statusSpan = document.createElement("span");
    statusSpan.style.marginLeft = "auto";
    if (available) {
      statusSpan.style.padding = "4px 10px";
      statusSpan.style.backgroundColor = "#f3f4f6"; // light gray
      statusSpan.style.color = "#4b5563";
      statusSpan.style.borderRadius = "4px";
      statusSpan.style.fontSize = "13px";
      statusSpan.style.fontWeight = "600";
    } else {
      statusSpan.style.fontWeight = "bold";
      statusSpan.style.color = "#ef4444";
    }
    statusSpan.textContent = statusText;
    
    var actions = document.createElement("div");
    actions.className = "book-actions";
    actions.appendChild(statusSpan);

    var user = Auth.currentUser();
    if (user && user.role === "reader") {
      if (!available) {
        var reserveBtn = document.createElement("button");
        reserveBtn.className = "btn btn-primary btn-sm";
        reserveBtn.style.marginLeft = "10px";
        reserveBtn.textContent = "Đặt trước";
        reserveBtn.onclick = function() {
          reserveBtn.disabled = true;
          reserveBtn.textContent = "Đã gửi...";
          API.call("createReservation", { ma_sach: book.ma }, "POST").then(function (res) {
            if (!res.ok) {
              reserveBtn.disabled = false;
              reserveBtn.textContent = "Đặt trước";
              showMessage(res.message);
              return;
            }
            reserveBtn.textContent = "Đã đặt trước";
            var pos = res.data.queue_position ? " Bạn đang ở vị trí thứ " + res.data.queue_position + " trong hàng đợi." : "";
            showMessage("Đã gửi yêu cầu đặt trước sách " + book.ten + "." + pos, "alert-success");
          });
        };
        actions.appendChild(reserveBtn);
      } else {
        var borrowBtn = document.createElement("button");
        borrowBtn.className = "btn btn-primary btn-sm";
        borrowBtn.style.marginLeft = "10px";
        borrowBtn.textContent = "Mượn sách";
        borrowBtn.onclick = function() {
          borrowBtn.disabled = true;
          borrowBtn.textContent = "Đang gửi...";
          
          var d = new Date();
          var y = d.getFullYear();
          var m = String(d.getMonth() + 1).padStart(2, "0");
          var a = String(d.getDate()).padStart(2, "0");
          var r = String(Math.floor(Math.random() * 10000)).padStart(4, "0");
          var reqMa = "YC" + y + m + a + r;
          
          var payload = {
            ma_yeu_cau: reqMa,
            loai: "MUON",
            items: [{ ma_sach: book.ma, so_luong: 1 }],
            so_ngay_muon: 14
          };
          
          API.call("createRequest", payload, "POST").then(function (res) {
            if (!res.ok) {
              borrowBtn.disabled = false;
              borrowBtn.textContent = "Mượn sách";
              showMessage(res.message);
              return;
            }
            borrowBtn.textContent = "Đã gửi Y/C";
            showMessage("Đã gửi yêu cầu mượn sách " + book.ten + " thành công.", "alert-success");
          });
        };
        actions.appendChild(borrowBtn);
      }
    }
    item.appendChild(actions);
    
    return item;
  }

  function init() {
    if (!Auth.requireAuth()) {
      return;
    }
    Auth.applyRoleUI();

    var searchButton = document.getElementById("search-button");
    if (searchButton) {
      searchButton.addEventListener("click", loadBooks);
    }
    var clearButton = document.getElementById("clear-search-button");
    if (clearButton) {
      clearButton.addEventListener("click", function () {
        document.getElementById("search-q").value = "";
        document.getElementById("search-theloai").value = "";
        document.getElementById("search-trangthai").value = "";
        document.getElementById("search-sort").value = "";
        loadBooks();
      });
    }
    var sortSelect = document.getElementById("search-sort");
    if (sortSelect) {
      sortSelect.addEventListener("change", loadBooks);
    }
    var qInput = document.getElementById("search-q");
    if (qInput) {
      qInput.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
          loadBooks();
        }
      });
    }

    loadCategories();
    loadBooks();

    var accessMsg = sessionStorage.getItem("thuvien_access_msg");
    if (accessMsg) {
      sessionStorage.removeItem("thuvien_access_msg");
      showMessage(accessMsg);
    }
  }

  document.addEventListener("DOMContentLoaded", init);
})();
