/* ============================================================
   chatbot.js — Logic tương tác Chatbot AI V3 cho Web App Thư viện ICTU
   Gọi Backend qua API.call("chatbot", ...)
   ============================================================ */

(function () {
  var chatMessages = document.getElementById("chat-messages");
  var chatInput = document.getElementById("chat-input");
  var btnSend = document.getElementById("btn-send");
  var btnClear = document.getElementById("btn-clear-chat");
  var lblLatency = document.getElementById("chat-latency");

  var SESSION_STORAGE_KEY = "ictu_ai_chat_history";

  function loadSession() {
    try {
      var raw = sessionStorage.getItem(SESSION_STORAGE_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch (e) {
      return [];
    }
  }

  function saveSession(history) {
    try {
      sessionStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(history));
    } catch (e) {
      console.warn("Không thể lưu sessionStorage:", e);
    }
  }

  var getHistory = loadSession;
  var saveHistory = saveSession;

  function appendToHistory(item) {
    var list = loadSession();
    list.push(item);
    saveSession(list);
  }

  function scrollBottom() {
    if (chatMessages) {
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }
  }

  function formatTime() {
    var d = new Date();
    var h = String(d.getHours()).padStart(2, "0");
    var m = String(d.getMinutes()).padStart(2, "0");
    return h + ":" + m;
  }

  function appendUserMessage(text, customTime, isRestoring) {
    var wrap = document.createElement("div");
    wrap.className = "chat-msg chat-msg--user";

    var avatar = document.createElement("div");
    avatar.className = "chat-msg__avatar";
    avatar.textContent = "👤";

    var bubble = document.createElement("div");
    bubble.className = "chat-msg__bubble";

    var p = document.createElement("p");
    p.style.margin = "0";
    p.textContent = text;

    var time = document.createElement("div");
    time.className = "chat-msg__time";
    var msgTime = customTime || formatTime();
    time.textContent = msgTime;

    bubble.appendChild(p);
    bubble.appendChild(time);
    wrap.appendChild(avatar);
    wrap.appendChild(bubble);

    chatMessages.appendChild(wrap);
    scrollBottom();

    if (!isRestoring) {
      appendToHistory({ role: "user", text: text, time: msgTime });
    }
  }

  function showTypingIndicator() {
    var wrap = document.createElement("div");
    wrap.className = "chat-msg chat-msg--assistant";
    wrap.id = "typing-indicator-msg";

    var avatar = document.createElement("div");
    avatar.className = "chat-msg__avatar";
    avatar.textContent = "🤖";

    var indicator = document.createElement("div");
    indicator.className = "typing-indicator";
    indicator.innerHTML = '<span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>';

    wrap.appendChild(avatar);
    wrap.appendChild(indicator);
    chatMessages.appendChild(wrap);
    scrollBottom();
  }

  function removeTypingIndicator() {
    var el = document.getElementById("typing-indicator-msg");
    if (el) {
      el.remove();
    }
  }

  function appendAssistantResponse(data, customTime, isRestoring) {
    removeTypingIndicator();

    var wrap = document.createElement("div");
    wrap.className = "chat-msg chat-msg--assistant";

    var avatar = document.createElement("div");
    avatar.className = "chat-msg__avatar";
    avatar.textContent = "🤖";

    var bubble = document.createElement("div");
    bubble.className = "chat-msg__bubble";

    // 1. Thông báo từ AI (nếu có)
    if (data.thong_bao) {
      var notice = document.createElement("div");
      // Nếu là câu từ chối lạc đề hoặc không tìm thấy
      if (data.thong_bao.indexOf("chỉ hỗ trợ tra cứu sách") !== -1 || data.thong_bao.indexOf("không liên quan") !== -1) {
        notice.className = "ai-notice-box";
        notice.innerHTML = "🛡️ <span>" + escapeHtml(data.thong_bao) + "</span>";
      } else if (data.tong_so_ket_qua === 0) {
        notice.className = "ai-notice-box";
        notice.innerHTML = "ℹ️ <span>" + escapeHtml(data.thong_bao) + "</span>";
      } else {
        notice.style.marginBottom = "8px";
        notice.textContent = data.thong_bao;
      }
      bubble.appendChild(notice);
    }

    // 2. Trích xuất từ khóa nhấn mạnh từ người dùng (nếu có)
    var keywords = data.tu_khoa_nhan_manh || [];
    if (keywords.length > 0) {
      var kwBox = document.createElement("div");
      kwBox.className = "ai-extracted-keywords";
      kwBox.innerHTML = '<span class="ai-keywords-label">🎯 Trọng tâm tìm kiếm:</span> ' +
        keywords.map(function (k) {
          return '<span class="ai-keyword-tag">#' + escapeHtml(k) + '</span>';
        }).join(" ");
      bubble.appendChild(kwBox);
    }

    // 3. Danh sách sách gợi ý
    var books = data.ket_qua || [];
    if (books.length > 0) {
      var headerP = document.createElement("p");
      headerP.style.margin = "8px 0 6px 0";
      headerP.innerHTML = "<strong>📚 Dưới đây là " + books.length + " cuốn sách phù hợp nhất được đối chiếu từ tóm tắt nội dung:</strong>";
      bubble.appendChild(headerP);

      var grid = document.createElement("div");
      grid.className = "book-cards-grid";

      books.forEach(function (b) {
        var card = document.createElement("div");
        card.className = "ai-book-card";

        var isAvailable = b.con_hang !== false;
        var badgeClass = isAvailable ? "badge-stock badge-stock--in" : "badge-stock badge-stock--out";
        var badgeText = isAvailable ? "✓ Còn sách" : "✕ Đã hết (Đặt trước)";

        var title = escapeHtml(b.ten_sach || "Sách không tên");
        var author = escapeHtml(b.tac_gia || "Chưa rõ tác giả");
        var reason = escapeHtml(b.ly_do_goi_y || "Phù hợp với chủ đề tìm kiếm");
        var genre = escapeHtml(b.the_loai || "Chung");

        var matchTagsHtml = "";
        var kws = b.khop_voi_tu_khoa || [];
        if (kws.length > 0) {
          matchTagsHtml = '<div class="ai-book-card__matches">' +
            kws.map(function (k) {
              return '<span class="badge-match">✨ Khớp: #' + escapeHtml(k) + '</span>';
            }).join(" ") +
            '</div>';
        }

        var searchUrl = "search.html?q=" + encodeURIComponent(b.ten_sach || "");

        card.innerHTML = [
          '<div>',
          '  <div class="ai-book-card__title" title="Bấm để xem chi tiết tóm tắt">📖 ' + title + '</div>',
          '  <div class="ai-book-card__meta">Tác giả: ' + author + ' • Thể loại: ' + genre + '</div>',
          matchTagsHtml,
          '  <div class="ai-book-card__reason">"' + reason + '"</div>',
          '</div>',
          '<div class="ai-book-card__footer">',
          '  <span class="' + badgeClass + '">' + badgeText + '</span>',
          '  <div class="ai-card-actions">',
          '    <button type="button" class="btn-book-action btn-book-detail">📖 Xem tóm tắt</button>',
          '    <a href="' + searchUrl + '" class="btn-book-action btn-book-action--primary" title="Xem và tra cứu sách này trong thư viện">Xem sách →</a>',
          '  </div>',
          '</div>'
        ].join("");

        // Bấm nút hoặc tiêu đề để mở modal xem tóm tắt
        var btnDetail = card.querySelector(".btn-book-detail");
        if (btnDetail) {
          btnDetail.addEventListener("click", function () {
            openBookModal(b);
          });
        }
        var titleEl = card.querySelector(".ai-book-card__title");
        if (titleEl) {
          titleEl.style.cursor = "pointer";
          titleEl.addEventListener("click", function () {
            openBookModal(b);
          });
        }

        grid.appendChild(card);
      });

      bubble.appendChild(grid);
    }

    // Thời gian
    var time = document.createElement("div");
    time.className = "chat-msg__time";
    var msgTime = customTime || (formatTime() + (data.thoi_gian_ms ? " (" + data.thoi_gian_ms + "ms)" : ""));
    time.textContent = msgTime;
    bubble.appendChild(time);

    wrap.appendChild(avatar);
    wrap.appendChild(bubble);
    chatMessages.appendChild(wrap);
    scrollBottom();

    if (!isRestoring) {
      appendToHistory({ role: "assistant", data: data, time: msgTime });
    }

    if (lblLatency && data.thoi_gian_ms) {
      lblLatency.textContent = "Thời gian phản hồi: " + data.thoi_gian_ms + "ms";
    }
  }

  // ── Xử lý Modal Xem Chi Tiết & Tóm Tắt Sách ──────────────────────────────
  function openBookModal(book) {
    var modal = document.getElementById("ai-book-modal");
    if (!modal) return;

    var elTitle = document.getElementById("modal-book-title");
    var elAuthor = document.getElementById("modal-book-author");
    var elCat = document.getElementById("modal-book-category");
    var elStatus = document.getElementById("modal-book-status");
    var elReason = document.getElementById("modal-book-reason");
    var elKeywords = document.getElementById("modal-book-keywords");
    var elSummary = document.getElementById("modal-book-summary");
    var elLink = document.getElementById("btn-modal-search-link");

    if (elTitle) elTitle.textContent = book.ten_sach || "Sách không tên";
    if (elAuthor) elAuthor.textContent = "✍️ Tác giả: " + (book.tac_gia || "Chưa rõ");
    if (elCat) elCat.textContent = "📂 Thể loại: " + (book.the_loai || "Chung");

    var isAvailable = book.con_hang !== false;
    if (elStatus) {
      elStatus.className = isAvailable ? "badge-stock badge-stock--in" : "badge-stock badge-stock--out";
      elStatus.textContent = isAvailable ? "✓ Còn sách trong kho" : "✕ Đã hết (Đặt mượn trước)";
    }

    if (elReason) {
      elReason.textContent = book.ly_do_goi_y || "Phù hợp với chủ đề tìm kiếm của bạn.";
    }

    if (elKeywords) {
      elKeywords.innerHTML = "";
      var kws = book.khop_voi_tu_khoa || [];
      if (kws.length > 0) {
        var lbl = document.createElement("span");
        lbl.className = "modal-kw-label";
        lbl.textContent = "Khớp từ khóa:";
        elKeywords.appendChild(lbl);
        kws.forEach(function (kw) {
          var tag = document.createElement("span");
          tag.className = "modal-kw-tag";
          tag.textContent = "#" + kw;
          elKeywords.appendChild(tag);
        });
      }
    }

    if (elSummary) {
      var summaryText = (book.tom_tat || "").trim();
      elSummary.textContent = summaryText || "Cuốn sách này hiện chưa có nội dung tóm tắt chi tiết trong hệ thống.";
    }

    if (elLink) {
      elLink.href = "search.html?q=" + encodeURIComponent(book.ten_sach || "");
    }

    modal.hidden = false;
  }

  function closeBookModal() {
    var modal = document.getElementById("ai-book-modal");
    if (modal) {
      modal.hidden = true;
    }
  }

  var btnCloseModal = document.getElementById("btn-close-modal");
  var btnModalCancel = document.getElementById("btn-modal-cancel");
  var modalBackdrop = document.getElementById("ai-book-modal");

  if (btnCloseModal) btnCloseModal.addEventListener("click", closeBookModal);
  if (btnModalCancel) btnModalCancel.addEventListener("click", closeBookModal);
  if (modalBackdrop) {
    modalBackdrop.addEventListener("click", function (e) {
      if (e.target === modalBackdrop) closeBookModal();
    });
  }
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeBookModal();
  });

  function appendErrorMessage(err, customTime, isRestoring) {
    removeTypingIndicator();

    var wrap = document.createElement("div");
    wrap.className = "chat-msg chat-msg--assistant";

    var avatar = document.createElement("div");
    avatar.className = "chat-msg__avatar";
    avatar.textContent = "⚠️";

    var bubble = document.createElement("div");
    bubble.className = "chat-msg__bubble";
    bubble.style.borderColor = "#FCA5A5";
    bubble.style.background = "#FEF2F2";
    bubble.style.color = "#991B1B";
    bubble.innerHTML = "<strong>Đã xảy ra lỗi khi trao đổi với AI:</strong> " + escapeHtml(String(err));

    var time = document.createElement("div");
    time.className = "chat-msg__time";
    var msgTime = customTime || formatTime();
    time.textContent = msgTime;
    bubble.appendChild(time);

    wrap.appendChild(avatar);
    wrap.appendChild(bubble);
    chatMessages.appendChild(wrap);
    scrollBottom();

    if (!isRestoring) {
      appendToHistory({ role: "error", message: String(err), time: msgTime });
    }
  }

  function escapeHtml(str) {
    if (!str) return "";
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  var isSending = false;

  async function guiCauHoi() {
    if (isSending) return;
    var q = chatInput.value.trim();
    if (!q) return;

    isSending = true;
    chatInput.value = "";
    chatInput.style.height = "44px";
    btnSend.disabled = true;
    chatInput.disabled = true;

    var quickBtns = document.querySelectorAll(".btn-pill-prompt");
    quickBtns.forEach(function (btn) {
      btn.disabled = true;
      btn.style.opacity = "0.6";
      btn.style.cursor = "not-allowed";
    });

    appendUserMessage(q);
    showTypingIndicator();

    try {
      var res = await window.API.call("chatbot", { cau_hoi: q }, "POST");

      if (!res.ok) {
        appendErrorMessage(res.message || res.detail || "Không thể kết nối đến máy chủ");
      } else {
        appendAssistantResponse(res.data);
      }
    } catch (err) {
      appendErrorMessage(err && err.message ? err.message : err);
    } finally {
      isSending = false;
      btnSend.disabled = false;
      chatInput.disabled = false;
      quickBtns.forEach(function (btn) {
        btn.disabled = false;
        btn.style.opacity = "";
        btn.style.cursor = "";
      });
      chatInput.focus();
    }
  }

  // Hộp thoại xác nhận chuyển trang bằng Tiếng Việt chuẩn giao diện ICTU
  function showLeaveConfirmModal(targetUrl) {
    var modalId = "ictu-leave-confirm-modal";
    var existing = document.getElementById(modalId);
    if (existing) existing.remove();

    var modal = document.createElement("div");
    modal.id = modalId;
    modal.style.cssText = "position:fixed; top:0; left:0; right:0; bottom:0; background:rgba(15,23,42,0.65); backdrop-filter:blur(4px); z-index:999999; display:flex; align-items:center; justify-content:center; padding:16px; font-family:'Be Vietnam Pro',system-ui,sans-serif;";

    modal.innerHTML = [
      '<div style="background:#ffffff; border-radius:14px; max-width:440px; width:100%; box-shadow:0 20px 30px rgba(0,0,0,0.25); overflow:hidden; border:1px solid #e2e8f0;">',
      '  <div style="background:linear-gradient(135deg, #0a2e5c 0%, #1e4b8c 100%); color:#ffffff; padding:14px 18px; display:flex; align-items:center; gap:10px;">',
      '    <span style="font-size:22px;">⚠️</span>',
      '    <h4 style="margin:0; font-size:16px; font-weight:700; color:#ffffff;">Cảnh báo gián đoạn tra cứu sách</h4>',
      '  </div>',
      '  <div style="padding:18px; color:#334155; font-size:14.5px; line-height:1.55;">',
      '    <p style="margin:0 0 8px 0; font-weight:600; color:#0f172a;">🤖 Trợ lý AI đang tìm sách cho bạn...</p>',
      '    <p style="margin:0; color:#475569;">Nếu bạn chuyển trang lúc này, quá trình tìm kiếm sẽ bị gián đoạn và câu trả lời chưa kịp lưu lại.</p>',
      '    <p style="margin:10px 0 0 0; font-size:13.5px; color:#64748b;">Bạn có muốn ở lại chờ AI trả lời xong không?</p>',
      '  </div>',
      '  <div style="padding:12px 18px; background:#f8fafc; border-top:1px solid #e2e8f0; display:flex; justify-content:flex-end; gap:10px;">',
      '    <button type="button" id="btn-leave-modal-stay" style="padding:9px 18px; background:linear-gradient(135deg, #0a2e5c 0%, #1e4b8c 100%); color:#ffffff; border:none; border-radius:8px; font-weight:600; cursor:pointer; font-size:14px;">Ở lại chờ kết quả</button>',
      '    <button type="button" id="btn-leave-modal-go" style="padding:9px 16px; background:#ffffff; color:#dc2626; border:1px solid #fca5a5; border-radius:8px; font-weight:600; cursor:pointer; font-size:13.5px;">Vẫn rời đi</button>',
      '  </div>',
      '</div>'
    ].join("");

    document.body.appendChild(modal);

    document.getElementById("btn-leave-modal-stay").addEventListener("click", function () {
      modal.remove();
    });

    document.getElementById("btn-leave-modal-go").addEventListener("click", function () {
      modal.remove();
      isSending = false; // Tắt cờ để không kích hoạt beforeunload trình duyệt
      window.location.href = targetUrl;
    });
  }

  // Bắt sự kiện click vào các liên kết chuyển trang khi đang gửi
  document.addEventListener("click", function (e) {
    if (!isSending) return;
    var link = e.target.closest("a");
    if (!link) return;
    var href = link.getAttribute("href");
    if (!href || href.startsWith("#") || href.startsWith("javascript:")) return;
    if (link.target === "_blank") return;

    e.preventDefault();
    e.stopPropagation();
    showLeaveConfirmModal(link.href);
  }, true);

  // Cảnh báo người dùng khi đóng tab hoặc reload trang (F5) trong lúc đang chờ AI phản hồi
  window.addEventListener("beforeunload", function (e) {
    if (isSending) {
      e.preventDefault();
      e.returnValue = "";
      return "";
    }
  });

  window.chonCauHoiMau = function (q) {
    if (isSending) return;
    if (chatInput) {
      chatInput.value = q;
      chatInput.focus();
      guiCauHoi();
    }
  };

  if (btnSend) {
    btnSend.addEventListener("click", guiCauHoi);
  }

  if (chatInput) {
    chatInput.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        guiCauHoi();
      }
    });

    // Auto resize
    chatInput.addEventListener("input", function () {
      this.style.height = "44px";
      this.style.height = Math.min(this.scrollHeight, 120) + "px";
    });
  }

  function restoreHistory() {
    var history = getHistory();
    if (!history || history.length === 0) return;

    history.forEach(function (item) {
      if (item.role === "user") {
        appendUserMessage(item.text, item.time, true);
      } else if (item.role === "assistant" && item.data) {
        appendAssistantResponse(item.data, item.time, true);
      } else if (item.role === "error") {
        appendErrorMessage(item.message, item.time, true);
      }
    });
  }

  if (btnClear) {
    btnClear.addEventListener("click", function () {
      if (confirm("Bạn có chắc chắn muốn xóa toàn bộ lịch sử trò chuyện hiện tại?")) {
        try {
          sessionStorage.removeItem(SESSION_STORAGE_KEY);
        } catch (e) {}
        chatMessages.innerHTML = [
          '<div class="chat-msg chat-msg--assistant">',
          '  <div class="chat-msg__avatar">🤖</div>',
          '  <div class="chat-msg__bubble">',
          '    <p style="margin:0 0 6px 0;"><strong>Đã làm mới cuộc hội thoại.</strong></p>',
          '    <p style="margin:0;">Hãy nhập câu hỏi tra cứu sách hoặc chọn một chủ đề gợi ý phía trên để tiếp tục.</p>',
          '  </div>',
          '</div>'
        ].join("");
      }
    });
  }

  // Tự động khôi phục lịch sử chat từ sessionStorage khi nạp trang
  restoreHistory();
})();
