/* ============================================================
   chatbot-widget.js — Bong bóng chat nổi (Floating Chat Widget)
   Nhúng độc lập vào mọi trang HTML của hệ thống Thư viện ICTU
   Kết nối trực tiếp tới endpoint POST /api/chatbot/hoi
   ============================================================ */

(function () {
  // Tránh nhúng trùng lặp nếu trang đã có widget
  if (window.__ICTU_CHATBOT_WIDGET_LOADED__) return;
  window.__ICTU_CHATBOT_WIDGET_LOADED__ = true;

  var SESSION_STORAGE_KEY = "ictu_ai_chat_history";
  var isChatOpen = false;

  function loadSession() {
    try {
      var raw = sessionStorage.getItem(SESSION_STORAGE_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch (e) {
      return [];
    }
  }

  function saveSession(list) {
    try {
      sessionStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(list));
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

  // 4 Câu hỏi gợi ý nhanh ban đầu
  var QUICK_PROMPTS = [
    { label: "💻 Sách Lập trình & CNTT", query: "sách học lập trình phần mềm và công nghệ thông tin" },
    { label: "🤖 Sách Trí tuệ nhân tạo (AI)", query: "sách về trí tuệ nhân tạo AI và ChatGPT" },
    { label: "📚 Sách Kinh tế & Quản trị", query: "sách kinh tế quản trị kinh doanh và tư duy làm giàu" },
    { label: "⭐ Sách hay nên đọc", query: "gợi ý những cuốn sách hay và đáng đọc nhất trong thư viện" }
  ];

  function escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function formatTime() {
    var d = new Date();
    var h = String(d.getHours()).padStart(2, "0");
    var m = String(d.getMinutes()).padStart(2, "0");
    return h + ":" + m;
  }

  // Khởi tạo HTML cho Widget
  function initWidget() {
    // 1. Tạo nút bong bóng tròn nổi
    var bubbleBtn = document.createElement("button");
    bubbleBtn.type = "button";
    bubbleBtn.className = "cb-widget-bubble";
    bubbleBtn.id = "cb-widget-bubble-btn";
    bubbleBtn.setAttribute("aria-label", "Mở Trợ lý AI Thư viện");
    bubbleBtn.title = "Hỏi Trợ lý AI (Tra cứu sách thông minh)";
    bubbleBtn.innerHTML = [
      '<span class="cb-widget-bubble__icon" id="cb-bubble-icon">🤖</span>',
      '<span class="cb-widget-badge">AI</span>'
    ].join("");

    // 2. Tạo khung chat
    var chatWindow = document.createElement("div");
    chatWindow.className = "cb-widget-window cb-widget--hidden";
    chatWindow.id = "cb-widget-chat-window";
    chatWindow.setAttribute("role", "dialog");
    chatWindow.setAttribute("aria-label", "Khung trò chuyện với Trợ lý thư viện");

    chatWindow.innerHTML = [
      '<!-- Header -->',
      '<div class="cb-widget-header">',
      '  <div class="cb-widget-header__info">',
      '    <div class="cb-widget-header__avatar">🤖</div>',
      '    <div>',
      '      <h4 class="cb-widget-header__title">🤖 Trợ lý AI Thư viện</h4>',
      '      <div class="cb-widget-header__status">',
      '        <span class="cb-widget-status-dot"></span>',
      '        <span>Trực tuyến • Hỗ trợ tra cứu sách thư viện</span>',
      '      </div>',
      '    </div>',
      '  </div>',
      '  <div class="cb-widget-header__actions">',
      '    <button type="button" class="cb-widget-btn-close" id="cb-btn-clear-chat" title="Xóa lịch sử trò chuyện" aria-label="Xóa lịch sử" style="font-size: 13px;">🧹</button>',
      '    <button type="button" class="cb-widget-btn-close" id="cb-btn-close-window" title="Thu nhỏ khung chat" aria-label="Đóng">&times;</button>',
      '  </div>',
      '</div>',
      '',
      '<!-- Danh sách tin nhắn -->',
      '<div class="cb-widget-messages" id="cb-widget-msg-list"></div>',
      '',
      '<!-- Khung nhập câu hỏi -->',
      '<div class="cb-widget-input-area">',
      '  <input type="text" class="cb-widget-input" id="cb-widget-input" placeholder="Hỏi tìm sách (VD: Sách Python, tài chính...)" autocomplete="off">',
      '  <button type="button" class="cb-widget-btn-send" id="cb-widget-btn-send" title="Gửi câu hỏi" aria-label="Gửi">',
      '    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">',
      '      <line x1="22" y1="2" x2="11" y2="13"></line>',
      '      <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>',
      '    </svg>',
      '  </button>',
      '</div>'
    ].join("");

    document.body.appendChild(bubbleBtn);
    document.body.appendChild(chatWindow);

    // Gắn sự kiện
    var btnClose = document.getElementById("cb-btn-close-window");
    var btnClear = document.getElementById("cb-btn-clear-chat");
    var inputEl = document.getElementById("cb-widget-input");
    var sendBtn = document.getElementById("cb-widget-btn-send");

    bubbleBtn.addEventListener("click", toggleChat);
    if (btnClose) btnClose.addEventListener("click", toggleChat);

    if (btnClear) {
      btnClear.addEventListener("click", function () {
        if (confirm("Bạn có chắc chắn muốn xóa toàn bộ lịch sử trò chuyện hiện tại?")) {
          try {
            sessionStorage.removeItem(SESSION_STORAGE_KEY);
          } catch (e) {}
          var list = document.getElementById("cb-widget-msg-list");
          if (list) {
            list.innerHTML = "";
            renderWelcomeMessage();
          }
        }
      });
    }

    if (sendBtn) {
      sendBtn.addEventListener("click", handleSend);
    }

    if (inputEl) {
      inputEl.addEventListener("keydown", function (e) {
        if (e.key === "Enter" && !e.shiftKey) {
          e.preventDefault();
          handleSend();
        }
      });
    }

    // Render tin nhắn chào mừng ban đầu
    renderWelcomeMessage();

    // Khôi phục lịch sử từ sessionStorage nếu có
    restoreHistory();
  }

  function toggleChat() {
    var chatWindow = document.getElementById("cb-widget-chat-window");
    var bubbleIcon = document.getElementById("cb-bubble-icon");
    if (!chatWindow) return;

    isChatOpen = !isChatOpen;
    if (isChatOpen) {
      chatWindow.classList.remove("cb-widget--hidden");
      if (bubbleIcon) bubbleIcon.textContent = "✕";
      var inputEl = document.getElementById("cb-widget-input");
      if (inputEl) {
        setTimeout(function () { inputEl.focus(); }, 100);
      }
      scrollToBottom();
    } else {
      chatWindow.classList.add("cb-widget--hidden");
      if (bubbleIcon) bubbleIcon.textContent = "🤖";
    }
  }

  function scrollToBottom() {
    var list = document.getElementById("cb-widget-msg-list");
    if (list) {
      list.scrollTop = list.scrollHeight;
    }
  }

  function renderWelcomeMessage() {
    var list = document.getElementById("cb-widget-msg-list");
    if (!list) return;

    var wrap = document.createElement("div");
    wrap.className = "cb-msg cb-msg--assistant";

    var avatar = document.createElement("div");
    avatar.className = "cb-msg__avatar";
    avatar.textContent = "🤖";

    var bubble = document.createElement("div");
    bubble.className = "cb-msg__bubble";

    var p = document.createElement("p");
    p.style.margin = "0 0 6px 0";
    p.innerHTML = "<strong>Xin chào!</strong> Tôi là Trợ lý AI Thư viện. Tôi có thể đọc tóm tắt và giúp bạn tìm cuốn sách phù hợp nhất.";
    bubble.appendChild(p);

    // Gợi ý nhanh
    var quickWrap = document.createElement("div");
    quickWrap.className = "cb-widget-quick-prompts";

    QUICK_PROMPTS.forEach(function (item) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "cb-quick-btn";
      btn.textContent = item.label;
      btn.addEventListener("click", function () {
        submitQuestion(item.query);
      });
      quickWrap.appendChild(btn);
    });

    bubble.appendChild(quickWrap);

    var time = document.createElement("div");
    time.className = "cb-msg__time";
    time.textContent = formatTime();
    bubble.appendChild(time);

    wrap.appendChild(avatar);
    wrap.appendChild(bubble);
    list.appendChild(wrap);
  }

  function showTypingIndicator() {
    var list = document.getElementById("cb-widget-msg-list");
    if (!list) return;

    var wrap = document.createElement("div");
    wrap.className = "cb-msg cb-msg--assistant";
    wrap.id = "cb-typing-msg";

    var avatar = document.createElement("div");
    avatar.className = "cb-msg__avatar";
    avatar.textContent = "🤖";

    var bubble = document.createElement("div");
    bubble.className = "cb-msg__bubble cb-typing";
    bubble.innerHTML = '<span class="cb-typing-dot"></span><span class="cb-typing-dot"></span><span class="cb-typing-dot"></span>';

    wrap.appendChild(avatar);
    wrap.appendChild(bubble);
    list.appendChild(wrap);
    scrollToBottom();
  }

  function removeTypingIndicator() {
    var el = document.getElementById("cb-typing-msg");
    if (el) el.remove();
  }

  function appendUserMessage(text, customTime, isRestoring) {
    var list = document.getElementById("cb-widget-msg-list");
    if (!list) return;

    var wrap = document.createElement("div");
    wrap.className = "cb-msg cb-msg--user";

    var avatar = document.createElement("div");
    avatar.className = "cb-msg__avatar";
    avatar.textContent = "👤";

    var bubble = document.createElement("div");
    bubble.className = "cb-msg__bubble";

    var p = document.createElement("p");
    p.style.margin = "0";
    p.textContent = text;
    bubble.appendChild(p);

    var time = document.createElement("div");
    time.className = "cb-msg__time";
    var msgTime = customTime || formatTime();
    time.textContent = msgTime;
    bubble.appendChild(time);

    wrap.appendChild(avatar);
    wrap.appendChild(bubble);
    list.appendChild(wrap);
    scrollToBottom();

    if (!isRestoring) {
      appendToHistory({ role: "user", text: text, time: msgTime });
    }
  }

  function appendAssistantResponse(data, customTime, isRestoring) {
    removeTypingIndicator();
    var list = document.getElementById("cb-widget-msg-list");
    if (!list) return;

    var wrap = document.createElement("div");
    wrap.className = "cb-msg cb-msg--assistant";

    var avatar = document.createElement("div");
    avatar.className = "cb-msg__avatar";
    avatar.textContent = "🤖";

    var bubble = document.createElement("div");
    bubble.className = "cb-msg__bubble";

    // 1. Từ khóa trích xuất từ người dùng (nếu có)
    var kws = data.tu_khoa_nhan_manh || [];
    if (kws.length > 0) {
      var kwBox = document.createElement("div");
      kwBox.className = "cb-extracted-kws";
      kwBox.innerHTML = '<span>🎯 Trọng tâm:</span> ' +
        kws.map(function (k) {
          return '<span class="cb-kw-tag">#' + escapeHtml(k) + '</span>';
        }).join(" ");
      bubble.appendChild(kwBox);
    }

    // 2. Thông báo chính
    if (data.thong_bao) {
      var pMsg = document.createElement("p");
      pMsg.style.margin = "0 0 6px 0";
      pMsg.textContent = data.thong_bao;
      bubble.appendChild(pMsg);
    }

    // 3. Danh sách sách gợi ý
    var books = data.ket_qua || [];
    if (books.length > 0) {
      if (!data.thong_bao) {
        var pIntro = document.createElement("p");
        pIntro.style.margin = "0 0 4px 0";
        pIntro.innerHTML = "<strong>📚 Gợi ý sách phù hợp từ thư viện:</strong>";
        bubble.appendChild(pIntro);
      }

      books.forEach(function (b) {
        var card = document.createElement("div");
        card.className = "cb-book-card";

        var isAvailable = b.con_hang !== false;
        var badgeClass = isAvailable ? "cb-badge-stock cb-badge-stock--in" : "cb-badge-stock cb-badge-stock--out";
        var badgeText = isAvailable ? "✓ Còn sách" : "✕ Đã hết";

        var title = escapeHtml(b.ten_sach || "Sách không tên");
        var author = escapeHtml(b.tac_gia || "Chưa rõ tác giả");
        var reason = escapeHtml(b.ly_do_goi_y || "Phù hợp với chủ đề tìm kiếm");
        var searchUrl = "search.html?q=" + encodeURIComponent(b.ten_sach || "");

        var matchHtml = "";
        var bookKws = b.khop_voi_tu_khoa || [];
        if (bookKws.length > 0) {
          matchHtml = '<div class="cb-book-card__matches">' +
            bookKws.map(function (k) {
              return '<span class="cb-badge-match">✨ #' + escapeHtml(k) + '</span>';
            }).join(" ") +
            '</div>';
        }

        card.innerHTML = [
          '<div class="cb-book-card__title">📖 ' + title + '</div>',
          '<div class="cb-book-card__author">Tác giả: ' + author + '</div>',
          matchHtml,
          '<div class="cb-book-card__reason">"' + reason + '"</div>',
          '<div class="cb-book-card__footer">',
          '  <span class="' + badgeClass + '">' + badgeText + '</span>',
          '  <a href="' + searchUrl + '" class="cb-btn-view" title="Xem và tra cứu sách này">Xem sách →</a>',
          '</div>'
        ].join("");

        var btnView = card.querySelector(".cb-btn-view");
        if (btnView) {
          btnView.addEventListener("click", function (e) {
            var targetTitle = b.ten_sach || "";
            var qInput = document.getElementById("search-q");
            var searchBtn = document.getElementById("search-button");
            if (qInput && searchBtn) {
              e.preventDefault();
              qInput.value = targetTitle;
              searchBtn.click();
              toggleChat();
              var container = document.getElementById("book-list-container");
              if (container) {
                setTimeout(function () {
                  container.scrollIntoView({ behavior: "smooth", block: "start" });
                }, 150);
              }
            }
          });
        }

        bubble.appendChild(card);
      });
    }

    // Thời gian
    var time = document.createElement("div");
    time.className = "cb-msg__time";
    var msgTime = customTime || formatTime();
    time.textContent = msgTime;
    bubble.appendChild(time);

    wrap.appendChild(avatar);
    wrap.appendChild(bubble);
    list.appendChild(wrap);
    scrollToBottom();

    if (!isRestoring) {
      appendToHistory({ role: "assistant", data: data, time: msgTime });
    }
  }

  function appendErrorMessage(errorText, customTime, isRestoring) {
    removeTypingIndicator();
    var list = document.getElementById("cb-widget-msg-list");
    if (!list) return;

    var wrap = document.createElement("div");
    wrap.className = "cb-msg cb-msg--assistant";

    var avatar = document.createElement("div");
    avatar.className = "cb-msg__avatar";
    avatar.textContent = "🤖";

    var bubble = document.createElement("div");
    bubble.className = "cb-msg__bubble";
    bubble.style.background = "#FEF2F2";
    bubble.style.color = "#991B1B";
    bubble.style.borderColor = "#FCA5A5";

    var p = document.createElement("p");
    p.style.margin = "0";
    p.textContent = errorText || "Xin lỗi, hệ thống đang gặp sự cố, bạn thử lại sau nhé!";
    bubble.appendChild(p);

    var time = document.createElement("div");
    time.className = "cb-msg__time";
    var msgTime = customTime || formatTime();
    time.textContent = msgTime;
    bubble.appendChild(time);

    wrap.appendChild(avatar);
    wrap.appendChild(bubble);
    list.appendChild(wrap);
    scrollToBottom();

    if (!isRestoring) {
      appendToHistory({ role: "error", message: errorText || "Xin lỗi, hệ thống đang gặp sự cố, bạn thử lại sau nhé!", time: msgTime });
    }
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

  var isSending = false;

  async function submitQuestion(questionText) {
    if (isSending) return;
    var text = (questionText || "").trim();
    if (!text) return;

    isSending = true;
    var sendBtn = document.getElementById("cb-widget-btn-send");
    var inputEl = document.getElementById("cb-widget-input");
    if (sendBtn) sendBtn.disabled = true;
    if (inputEl) inputEl.disabled = true;

    var quickBtns = document.querySelectorAll(".cb-quick-btn");
    quickBtns.forEach(function (btn) {
      btn.disabled = true;
      btn.style.opacity = "0.6";
      btn.style.cursor = "not-allowed";
    });

    appendUserMessage(text);
    showTypingIndicator();

    try {
      var response = await fetch("/api/chatbot/hoi", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ cau_hoi: text })
      });

      if (!response.ok) {
        throw new Error("HTTP " + response.status);
      }

      var data = await response.json();
      appendAssistantResponse(data);
    } catch (err) {
      appendErrorMessage("Xin lỗi, hệ thống đang gặp sự cố, bạn thử lại sau nhé!");
    } finally {
      isSending = false;
      if (sendBtn) sendBtn.disabled = false;
      if (inputEl) {
        inputEl.disabled = false;
        inputEl.focus();
      }
      quickBtns.forEach(function (btn) {
        btn.disabled = false;
        btn.style.opacity = "";
        btn.style.cursor = "";
      });
    }
  }

  // Hộp thoại xác nhận chuyển trang bằng Tiếng Việt chuẩn giao diện ICTU
  function showLeaveConfirmModal(targetUrl) {
    var modalId = "ictu-widget-leave-confirm-modal";
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
      '    <button type="button" id="btn-widget-modal-stay" style="padding:9px 18px; background:linear-gradient(135deg, #0a2e5c 0%, #1e4b8c 100%); color:#ffffff; border:none; border-radius:8px; font-weight:600; cursor:pointer; font-size:14px;">Ở lại chờ kết quả</button>',
      '    <button type="button" id="btn-widget-modal-leave" style="padding:9px 16px; background:#ffffff; color:#dc2626; border:1px solid #fca5a5; border-radius:8px; font-weight:600; cursor:pointer; font-size:13.5px;">Vẫn rời đi</button>',
      '  </div>',
      '</div>'
    ].join("");

    document.body.appendChild(modal);

    document.getElementById("btn-widget-modal-stay").addEventListener("click", function () {
      modal.remove();
    });

    document.getElementById("btn-widget-modal-leave").addEventListener("click", function () {
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

  function handleSend() {
    var inputEl = document.getElementById("cb-widget-input");
    if (!inputEl) return;
    var q = inputEl.value.trim();
    if (!q) return;

    inputEl.value = "";
    submitQuestion(q);
  }

  // Khởi chạy khi DOM sẵn sàng
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initWidget);
  } else {
    initWidget();
  }
})();
