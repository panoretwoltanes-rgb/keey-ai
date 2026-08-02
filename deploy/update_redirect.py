"""Generate docs/index.html that redirects to the latest KEEY tunnel URL."""
import html
import os
import sys

DEPLOY_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(DEPLOY_DIR)
URL_FILE = os.path.join(PROJECT_DIR, "output", "tunnel_url.txt")
DOCS_DIR = os.path.join(PROJECT_DIR, "docs")
INDEX_PATH = os.path.join(DOCS_DIR, "index.html")


def read_tunnel_url():
    if not os.path.exists(URL_FILE):
        print("[redirect] output/tunnel_url.txt not found")
        sys.exit(1)
    with open(URL_FILE, "r", encoding="utf-8") as f:
        url = f.read().strip()
    if not url:
        print("[redirect] output/tunnel_url.txt is empty")
        sys.exit(1)
    return url


def build_index_html(url):
    escaped = html.escape(url, quote=True)
    return (
        "<!DOCTYPE html>\n"
        '<html lang="zh-CN">\n'
        "<head>\n"
        '  <meta charset="UTF-8">\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '  <meta http-equiv="refresh" content="0; url=' + escaped + '">\n'
        "  <title>KEEY AI 报价系统</title>\n"
        "  <script>\n"
        "    window.location.replace(\"" + escaped + "\");\n"
        "  </script>\n"
        "</head>\n"
        "<body>\n"
        "  <p>正在跳转到 KEEY AI 报价系统...</p>\n"
        '  <p><a href="' + escaped + '">如果未自动跳转，请点击这里</a></p>\n'
        "</body>\n"
        "</html>\n"
    )


def main():
    url = read_tunnel_url()
    os.makedirs(DOCS_DIR, exist_ok=True)
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(build_index_html(url))
    print("[redirect] docs/index.html updated")
    print("[redirect] target: " + url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
