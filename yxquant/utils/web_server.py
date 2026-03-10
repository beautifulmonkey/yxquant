"""
Web服务器工具模块
提供简单的静态文件服务器功能
"""
import os
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler

def start_static_server(
    directory: str,
    port: int = 2918,
    auto_open: bool = True,
    host: str = "localhost"
) -> HTTPServer:
    """
    Args:
        directory: 静态文件目录路径
        port: 端口号，默认2918
        auto_open: 是否自动打开浏览器，默认True
        host: 主机地址，默认localhost
    Returns:
        HTTPServer: 服务器实例
    """
    directory += "/dist"
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Directory not found: {directory}")
    
    os.chdir(directory)
    url = f"http://{host}:{port}"
    print(f"Static file server started: {url}")
    print(f"Serving directory: {directory}")

    if auto_open:
        webbrowser.open(url)

    httpd = HTTPServer((host, port), SimpleHTTPRequestHandler)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.shutdown()
        print("Closed")
    return httpd

