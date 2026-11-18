# -*- coding: utf-8 -*-
"""
前后端分离学习示例 · 后端服务
------------------------------------------------
目录约定：
  backend/api_server.py   本文件（后端 API + 静态文件服务）
  frontend/               前端静态资源（index.html / style.css / script.js）

运行（在任意目录执行都可以，路径基于本文件自动定位）：
  D:\PythonRuntimes\pythoncore-3.15-64\python.exe D:\code\demo\backend\api_server.py

浏览器访问：
  http://127.0.0.1:8000          -> 前端首页（frontend/index.html）
  http://127.0.0.1:8000/api-docs -> API 测试页（可点击体验各接口）

知识点：
  * 同一个服务既能返回静态文件（HTML/CSS/JS），也能返回动态 API（JSON）
  * 静态文件从 frontend 文件夹读取，API 接口由 Python 计算得出
"""

import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

HOST = "127.0.0.1"
PORT = 8000

# 关键：用 __file__ 定位项目根目录，这样从哪个目录启动都能找到 frontend
BASE_DIR = Path(__file__).resolve().parent.parent        # D:/code/demo
FRONTEND_DIR = BASE_DIR / "frontend"                     # D:/code/demo/frontend

# 浏览器打开 /api-docs 时看到的 API 测试首页（点链接即可体验各个接口）
API_DOCS_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>HTTP API 学习示例</title>
<style>
  body { font-family: system-ui, sans-serif; max-width: 760px; margin: 40px auto;
         padding: 0 20px; color: #222; line-height: 1.7; }
  h1 { color: #2b6cb0; }
  code { background: #f2f4f7; padding: 2px 6px; border-radius: 4px; }
  a { color: #2b6cb0; }
  li { margin: 8px 0; }
  button { padding: 8px 16px; cursor: pointer; background:#2b6cb0; color:#fff;
           border:0; border-radius:5px; }
  pre { background:#f7f9fc; padding:12px; border-radius:6px; overflow:auto; }
</style>
</head>
<body>
  <h1>HTTP API 学习示例</h1>
  <p>这是后端提供的接口测试页。你正在访问 <code>backend/api_server.py</code> 提供的动态内容。</p>
  <p><a href="/">← 返回前端首页（frontend/index.html）</a></p>

  <h2>可以点击测试的 GET 接口</h2>
  <ul>
    <li><a href="/hello?name=小明">GET /hello?name=小明</a> —— 查询参数（query string）</li>
    <li><a href="/time">GET /time</a> —— 返回当前时间（JSON）</li>
    <li><a href="/user/42">GET /user/42</a> —— 路径参数（path param）</li>
    <li><a href="/notfound">GET /notfound</a> —— 故意返回 404 状态码</li>
  </ul>

  <h2>POST 接口（地址栏只能发 GET，用按钮通过 JS 发 POST）</h2>
  <button onclick="postEcho()">发送 POST /echo</button>
  <pre id="out">点击按钮后结果会显示在这里…</pre>

<script>
function postEcho() {
  fetch('/echo', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({message: '你好，这是 POST 请求', from: '浏览器'})
  })
  .then(r => r.json())
  .then(data => document.getElementById('out').textContent = JSON.stringify(data, null, 2));
}
</script>
</body>
</html>"""

# 常见静态文件的 Content-Type
MIME_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".ico": "image/x-icon",
}


class APIHandler(BaseHTTPRequestHandler):
    """GET/POST 请求分别由 do_GET / do_POST 处理。"""

    server_version = "LearningAPI/1.0"

    # ---------- 通用响应工具 ----------
    def _send(self, status, body, content_type="application/json; charset=utf-8"):
        """统一发送响应：状态行 + 响应头 + 空行 + 响应体。"""
        if isinstance(body, (dict, list)):
            data = json.dumps(body, ensure_ascii=False, indent=2).encode("utf-8")
        elif isinstance(body, bytes):
            data = body
        else:
            data = str(body).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _json(self, obj, status=200):
        self._send(status, obj)

    # ---------- 静态文件服务 ----------
    def _serve_file(self, rel_name):
        """从 frontend 文件夹读取一个静态文件并返回。"""
        # 只允许纯文件名，杜绝 ../ 之类的路径穿越
        if Path(rel_name).name != rel_name:
            self._json({"error": "非法路径"}, 400)
            return
        file_path = FRONTEND_DIR / rel_name
        if not file_path.is_file():
            self._json({"error": f"静态文件不存在: {rel_name}"}, 404)
            return
        content_type = MIME_TYPES.get(file_path.suffix.lower(), "application/octet-stream")
        self._send(200, file_path.read_bytes(), content_type)

    # ---------- GET 路由 ----------
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        # 前端静态页面
        if path == "/":
            self._serve_file("index.html")

        # 前端依赖的资源（浏览器请求 style.css / script.js 时会走到这里）
        elif path in ("/index.html", "/style.css", "/script.js"):
            self._serve_file(path.lstrip("/"))

        # API 测试页
        elif path == "/api-docs":
            self._send(200, API_DOCS_HTML, "text/html; charset=utf-8")

        # 浏览器自动请求图标，直接回 204 避免 404 噪音
        elif path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()

        # 以下是动态 API 接口
        elif path == "/hello":
            name = query.get("name", ["世界"])[0]
            self._json({
                "message": f"你好，{name}！",
                "method": "GET",
                "your_query": query,
            })

        elif path == "/time":
            self._json({
                "timestamp": int(time.time()),
                "datetime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            })

        elif path.startswith("/user/"):
            user_id = path[len("/user/"):].strip("/")
            self._json({"user_id": user_id, "name": f"用户{user_id}"})

        elif path == "/notfound":
            self._json({"error": "这是一个故意返回的 404 示例"}, 404)

        else:
            self._json({"error": "页面不存在", "path": path}, 404)

    # ---------- POST 路由 ----------
    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)

        try:
            payload = json.loads(raw.decode("utf-8")) if raw else {}
        except Exception:
            payload = {"raw": raw.decode("utf-8", "ignore")}

        if parsed.path == "/echo":
            self._json({
                "message": "收到你的 POST 请求",
                "you_posted": payload,
                "content_type": self.headers.get("Content-Type"),
            })
        else:
            self._json({"error": "页面不存在"}, 404)


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), APIHandler)
    print(f"前后端学习服务已启动：http://{HOST}:{PORT}")
    print(f"  前端首页   http://{HOST}:{PORT}/")
    print(f"  API 测试页 http://{HOST}:{PORT}/api-docs")
    print("按 Ctrl+C 停止服务")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已停止")
        server.server_close()
