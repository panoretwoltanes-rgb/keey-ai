import os
import socket
from flask import Flask
from config import APP_NAME, VERSION, HOST, PORT, DEBUG, SECRET_KEY, OUTPUT_DIR, LOG_DIR, UPLOAD_DIR, TEMP_DIR


def get_lan_ip():
    """自动获取本机局域网 IPv4 地址。"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        if ip and ip != "127.0.0.1":
            return ip
    except:
        pass
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ip = info[4][0]
            if ip and not ip.startswith("127."):
                return ip
    except:
        pass
    return "127.0.0.1"


def create_app():
    app = Flask(__name__)
    app.config.from_object("config")
    app.secret_key = SECRET_KEY

    for d in [OUTPUT_DIR, LOG_DIR, UPLOAD_DIR, TEMP_DIR]:
        os.makedirs(d, exist_ok=True)

    # 初始化 SQLite 数据库（幂等，重复启动安全）
    from services.database_service import init_db
    init_db()

    from routes.quote import quote_bp
    app.register_blueprint(quote_bp)

    return app


app = create_app()

if __name__ == "__main__":
    lan_ip = get_lan_ip()
    print("=" * 50)
    print(f"  {APP_NAME} 已启动")
    print()
    print(f"  本机访问:  http://127.0.0.1:{PORT}")
    print(f"  局域网访问: http://{lan_ip}:{PORT}")
    print()
    print("  请确保手机与电脑连接同一 WiFi。")
    print("=" * 50)
    app.run(
        host="0.0.0.0",
        port=PORT,
        debug=DEBUG,
        threaded=True,
        use_reloader=False,
    )
