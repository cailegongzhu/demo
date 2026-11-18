# -*- coding: utf-8 -*-
"""
纯后端 API 服务（前后端分离）
------------------------------------------------
只做一件事：接收 POST 请求，把收到的内容原样返回。
【不提供任何前端页面】—— 前端是独立文件，可以单独打开或放到静态服务器上。

运行：
  D:\code\demo\backend\.venv\Scripts\python.exe D:\code\demo\backend\main.py

接口：
  POST http://127.0.0.1:8001/
  请求体：任意文本
  响应体：原样返回请求体内容

跨域（CORS）：
  前端和后端不在同一个地址时（例如前端是 file:// 打开、或放在别的域名），
  浏览器会拦截请求。本服务通过 Access-Control-Allow-Origin 等响应头放行跨域请求，
  并处理浏览器自动发出的 OPTIONS 预检请求。

按 Ctrl+C 停止。
"""

import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = "127.0.0.1"
PORT = 8001


class ApiHandler(BaseHTTPRequestHandler):
    """纯 API：只处理 POST，外加跨域预检 OPTIONS。"""

    def _cors_headers(self):
        """放行跨域请求的响应头。"""
        self.send_header("Access-Control-Allow-Origin", "*")            # 允许任意来源
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        """预检请求：浏览器发真正的 POST 之前，先来问服务器允许什么。"""
        self.send_response(204)             # 204 = 成功，但无响应体
        self._cors_headers()
        self.end_headers()

    def do_POST(self):
        """读取请求体，打印信息，并把内容原样返回。"""
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)              # 原始请求体（bytes）
        text = raw.decode("utf-8", "replace")      # 解码成文本，仅用于打印
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        # 打印到控制台
        print("=" * 48, flush=True)
        print(f"[{now}] 收到一个 POST 请求", flush=True)
        print(f"  来访 IP : {self.client_address[0]}", flush=True)
        print(f"  来源 Origin: {self.headers.get('Origin', '无')}", flush=True)
        print(f"  Content-Type: {self.headers.get('Content-Type', '未知')}", flush=True)
        print(f"  收到内容: {text}", flush=True)
        print("=" * 48, flush=True)

        # 原样返回收到的字节内容（带上 CORS 头，浏览器才允许前端读取）
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self._cors_headers()
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        """后端不提供网页，只给一句提示。"""
        body = "这是一个纯 API 服务，只接受 POST 请求。前端页面请单独打开 frontend/index.html。".encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        # 关闭默认日志，控制台只显示上面自定义的信息
        pass


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), ApiHandler)
    print(f"纯 API 服务已启动： POST http://{HOST}:{PORT}/", flush=True)
    print("前端页面是独立文件，可单独打开 frontend/index.html。", flush=True)
    print("按 Ctrl+C 停止服务。", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已停止", flush=True)
        server.server_close()
