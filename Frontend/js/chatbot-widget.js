/* ============================================================
   chatbot-widget.js — Floating AI Chat Widget cho mọi trang web thư viện
   Tự động hiển thị icon nổi ở góc dưới màn hình, bấm vào để mở chat mini.
   ============================================================ */

(function () {
  // Không hiển thị widget nổi nếu đang ở chính trang chatbot.html
  if (window.location.pathname.indexOf("chatbot.html") !== -1) {
    return;
  }

  function initWidget() {
    var style = document.createElement("style");
    style.textContent = [
      '#ictu-ai-widget-btn {',
      '  position: fixed;',
      '  bottom: 24px;',
      '  right: 24px;',
      '  width: 54px;',
      '  height: 54px;',
      '  background: linear-gradient(135deg, #0a2e5c 0%, #1e4b8c 100%);',
      '  color: #ffffff;',
      '  border-radius: 50%;',
      '  border: 2px solid #ffffff;',
      '  box-shadow: 0 4px 18px rgba(10, 46, 92, 0.35);',
      '  display: flex;',
      '  align-items: center;',
      '  justify-content: center;',
      '  font-size: 26px;',
      '  cursor: pointer;',
      '  z-index: 9999;',
      '  transition: transform 0.2s ease, box-shadow 0.2s ease;',
      '}',
      '#ictu-ai-widget-btn:hover {',
      '  transform: scale(1.08) translateY(-2px);',
      '  box-shadow: 0 6px 22px rgba(10, 46, 92, 0.45);',
      '}',
      '#ictu-ai-widget-box {',
      '  position: fixed;',
      '  bottom: 90px;',
      '  right: 24px;',
      '  width: 360px;',
      '  height: 480px;',
      '  max-height: calc(100vh - 120px);',
      '  background: #ffffff;',
      '  border: 1px solid #dce1ea;',
      '  border-radius: 14px;',
      '  box-shadow: 0 10px 30px rgba(10, 25, 48, 0.2);',
      '  display: none;',
      '  flex-direction: column;',
      '  overflow: hidden;',
      '  z-index: 9999;',
      '  animation: widgetSlideUp 0.25s ease-out;',
      '}',
      '@keyframes widgetSlideUp {',
      '  from { opacity: 0; transform: translateY(15px); }',
      '  to { opacity: 1; transform: translateY(0); }',
      '}',
      '.ai-w-header {',
      '  background: #0a2e5c;',
      '  color: #ffffff;',
      '  padding: 10px 14px;',
      '  display: flex;',
      '  align-items: center;',
      '  justify-content: space-between;',
      '}',
      '.ai-w-header__title {',
      '  font-size: 13.5px;',
      '  font-weight: 700;',
      '  display: flex;',
      '  align-items: center;',
      '  gap: 6px;',
      '}',
      '.ai-w-close {',
      '  background: none;',
      '  border: none;',
      '  color: #ffffff;',
      '  font-size: 18px;',
      '  cursor: pointer;',
      '  opacity: 0.8;',
      '}',
      '.ai-w-close:hover { opacity: 1; }',
      '.ai-w-body {',
      '  flex: 1;',
      '  padding: 12px;',
      '  overflow-y: auto;',
      '  display: flex;',
      '  flex-direction: column;',
      '  gap: 10px;',
      '  background: #f8fafc;',
      '  font-size: 13px;',
      '}',
      '.ai-w-msg-user {',
      '  align-self: flex-end;',
      '  background: #0a2e5c;',
      '  color: #ffffff;',
      '  padding: 8px 12px;',
      '  border-radius: 12px;',
      '  border-bottom-right-radius: 2px;',
      '  max-width: 85%;',
      '  word-break: break-word;',
      '}',
      '.ai-w-msg-bot {',
      '  align-self: flex-start;',
      '  background: #ffffff;',
      '  color: #1a1a1a;',
      '  border: 1px solid #e5e7eb;',
      '  padding: 8px 12px;',
      '  border-radius: 12px;',
      '  border-bottom-left-radius: 2px;',
      '  max-width: 90%;',
      '  box-shadow: 0 1px 3px rgba(0,0,0,0.05);',
      '}',
      '.ai-w-footer {',
      '  padding: 8px;',
      '  background: #ffffff;',
      '  border-top: 1px solid #e5e7eb;',
      '  display: flex;',
      '  gap: 6px;',
      '}',
      '.ai-w-input {',
      '  flex: 1;',
      '  border: 1px solid #dce1ea;',
      '  border-radius: 6px;',
      '  padding: 8px 10px;',
      '  font-size: 13px;',
      '  outline: none;',
      '}',
      '.ai-w-input:focus { border-color: #1e4b8c; }',
      '.ai-w-send {',
      '  background: #0a2e5c;',
      '  color: #ffffff;',
      '  border: none;',
      '  border-radius: 6px;',
      '  padding: 0 12px;',
      '  font-weight: 600;',
      '  cursor: pointer;',
      '}',
      '.ai-w-links {',
      '  font-size: 11px;',
      '  text-align: center;',
      '  padding: 4px;',
      '  background: #f1f5f9;',
      '  color: #64748b;',
      '}',
      '.ai-w-links a { color: #1e4b8c; text-decoration: none; font-weight: 600; }'
    ].join("\n");
    document.head.appendChild(style);

    // Nút tròn nổi
    var btn = document.createElement("div");
    btn.id = "ictu-ai-widget-btn";
    btn.title = "Hỏi Trợ lý AI Thư viện (V3)";
    btn.innerHTML = "🤖";

    // Khung chat nổi
    var box = document.createElement("div");
    box.id = "ictu-ai-widget-box";
    box.innerHTML = [
      '<div class="ai-w-header">',
      '  <div class="ai-w-header__title">🤖 Trợ lý AI Thư viện (V3)</div>',
      '  <button type="button" class="ai-w-close" id="ai-w-close-btn">&times;</button>',
      '</div>',
      '<div class="ai-w-body" id="ai-w-body">',
      '  <div class="ai-w-msg-bot">Xin chào! Tôi là Trợ lý AI V3 của thư viện. Bạn cần tìm sách gì hôm nay?</div>',
      '</div>',
      '<div class="ai-w-footer">',
      '  <input type="text" class="ai-w-input" id="ai-w-input" placeholder="Hỏi tìm sách..." />',
      '  <button type="button" class="ai-w-send" id="ai-w-send">Gửi</button>',
      '</div>',
      '<div class="ai-w-links">',
      '  <a href="chatbot.html">Mở giao diện chat đầy đủ ↗</a>',
      '</div>'
    ].join("");

    document.body.appendChild(btn);
    document.body.appendChild(box);

    var isOpen = false;
    btn.addEventListener("click", function () {
      isOpen = !isOpen;
      box.style.display = isOpen ? "flex" : "none";
      if (isOpen) {
        document.getElementById("ai-w-input").focus();
      }
    });

    document.getElementById("ai-w-close-btn").addEventListener("click", function () {
      isOpen = false;
      box.style.display = "none";
    });

    var body = document.getElementById("ai-w-body");
    var input = document.getElementById("ai-w-input");
    var sendBtn = document.getElementById("ai-w-send");

    async function sendQuery() {
      var q = input.value.trim();
      if (!q) return;
      input.value = "";

      // Add user msg
      var uDiv = document.createElement("div");
      uDiv.className = "ai-w-msg-user";
      uDiv.textContent = q;
      body.appendChild(uDiv);
      body.scrollTop = body.scrollHeight;

      // Add bot typing
      var tDiv = document.createElement("div");
      tDiv.className = "ai-w-msg-bot";
      tDiv.textContent = "⏳ Đang tra cứu sách...";
      body.appendChild(tDiv);
      body.scrollTop = body.scrollHeight;

      try {
        var res = await window.API.call("chatbot", {
          method: "POST",
          payload: { cau_hoi: q }
        });

        if (res.ok && res.data) {
          var d = res.data;
          var html = "";
          if (d.thong_bao) {
            html += "<p style='margin:0 0 6px 0;'>" + d.thong_bao + "</p>";
          }
          if (d.ket_qua && d.ket_qua.length > 0) {
            html += "<p style='margin:0 0 4px 0; font-weight:700;'>Gợi ý " + d.ket_qua.length + " sách:</p><ul style='margin:0; padding-left:18px;'>";
            d.ket_qua.forEach(function (b) {
              var stt = b.con_hang === false ? " <span style='color:#dc2626;'>(Hết)</span>" : " <span style='color:#16a34a;'>(Còn)</span>";
              html += "<li><strong>" + (b.ten_sach || "") + "</strong>" + stt + "<br><span style='font-size:11.5px; color:#475569;'>" + (b.ly_do_goi_y || "") + "</span></li>";
            });
            html += "</ul>";
          }
          tDiv.innerHTML = html || "Đã xử lý yêu cầu.";
        } else {
          tDiv.textContent = "⚠️ " + (res.message || "Lỗi máy chủ khi tra cứu");
        }
      } catch (err) {
        tDiv.textContent = "⚠️ Không thể kết nối Backend.";
      }
      body.scrollTop = body.scrollHeight;
    }

    sendBtn.addEventListener("click", sendQuery);
    input.addEventListener("keydown", function (e) {
      if (e.key === "Enter") {
        e.preventDefault();
        sendQuery();
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initWidget);
  } else {
    initWidget();
  }
})();
