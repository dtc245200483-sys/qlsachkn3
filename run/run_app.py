import subprocess
import webbrowser
import time
from pathlib import Path

def main():
    # Lấy thư mục gốc (thư mục cha của thư mục 'run')
    current_dir = Path(__file__).parent.absolute()
    app_dir = current_dir.parent
    
    backend_dir = app_dir / "Backend"
    frontend_index = app_dir / "frontend" / "index.html"
    
    print("===========================================")
    print("🚀 Đang khởi động Backend FastAPI...")
    print("===========================================")
    
    try:
        # Chạy uvicorn trong thư mục Backend
        backend_process = subprocess.Popen(
            ["uvicorn", "app.main:app", "--reload", "--port", "8000"],
            cwd=str(backend_dir)
        )
    except FileNotFoundError:
        print("❌ Lỗi: Không tìm thấy 'uvicorn'. Hãy chắc chắn bạn đã cài đặt FastAPI và Uvicorn.")
        return
    
    print("⏳ Vui lòng chờ 3 giây để máy chủ khởi động...")
    time.sleep(3)
    
    if frontend_index.exists():
        url = "http://localhost:8000/"
        print(f"🌐 Đang mở trang giao diện web tại: {url}")
        webbrowser.open(url)
    else:
        print(f"❌ Không tìm thấy file Frontend tại: {frontend_index}")
        
    print("✅ Ứng dụng đã chạy thành công!")
    print("⚠️ Nhấn Ctrl + C ở cửa sổ này để tắt máy chủ khi dùng xong.")
    
    # Giữ script chạy để duy trì Backend
    try:
        backend_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Đang tắt Backend...")
        backend_process.terminate()
        backend_process.wait()
        print("Tắt hoàn tất.")

if __name__ == "__main__":
    main()
