import gc
gc.collect()
import os
import re
import sys
import time
import json
import hashlib

# 导入网络模块
try:
    import network
except ImportError:
    print("警告: network模块不可用，网络功能将被禁用")

# 从提供的文件中导入框架
from microflask import *

# 创建Flask应用
app = Flask(
    static_folder="static/",
    static_url_path="/static/",
)

# ========== 网络配置函数 ==========
def setup_ap(ssid, pwd, ip):
    """设置ESP32为AP模式"""
    try:
        ap = network.WLAN(network.AP_IF)
        ap.active(True)
        # 注意：authmode配置需要在password之前
        ap.config(essid=str(ssid), authmode=network.AUTH_WPA_WPA2_PSK, password=str(pwd))
        
        # 设置静态IP
        ap.ifconfig((str(ip), '255.255.255.0', str(ip), '8.8.8.8'))
        
        print("AP模式已启动")
        print("SSID: " + str(ssid))
        print("密码: " + str(pwd))
        print("IP地址: " + ap.ifconfig()[0])
        
        return ap
    except Exception as e:
        print("AP设置失败: " + str(e))
        return None

def setup_sta(ssid, pwd):
    """设置STA模式连接WiFi"""
    try:
        sta = network.WLAN(network.STA_IF)
        sta.active(True)
        if not sta.isconnected():
            print("正在连接WiFi: " + str(ssid))
            sta.connect(str(ssid), str(pwd))
            
            # 等待连接，最多30秒
            for i in range(30):
                if sta.isconnected():
                    break
                time.sleep(1)
                print(".", end='')
            print()
        
        if sta.isconnected():
            print("WiFi连接成功!")
            print("IP地址: " + sta.ifconfig()[0])
        else:
            print("WiFi连接失败!")
        
        return sta
    except Exception as e:
        print("STA设置失败: " + str(e))
        return None







# ================== Cookie 测试路由 ==================

@app.route("/set_cookie", methods=["GET"])
def set_cookie(req):
    """设置Cookie的测试端点"""
    resp = Response("Cookie设置成功！")
    
    # 设置多个测试Cookie
    resp.set_cookie("user", "李四", max_age=3600, path="/")
    resp.set_cookie("session_id", "abc123xyz", max_age=7200, path="/")
    resp.set_cookie("theme", "dark", max_age=86400, path="/")
    resp.set_cookie("preference", "zh-CN", path="/api")
    
    return resp

@app.route("/get_cookie", methods=["GET"])
def get_cookie(req):
    """获取并显示所有Cookie"""
    cookies = req.cookies
    cookie_list = []
    
    for name, value in cookies.items():
        cookie_list.append(f"{name}: {value}")
    
    html = f"""
    <html>
    <head><title>Cookie测试</title></head>
    <body>
        <h1>当前Cookie ({len(cookie_list)}个)</h1>
        <ul>
    """
    
    for cookie in cookie_list:
        html += f"<li>{cookie}</li>"
    
    html += """
        </ul>
        <p>
            <a href="/set_cookie">设置Cookie</a> | 
            <a href="/clear_cookie">清除Cookie</a> | 
            <a href="/stream">测试流式响应</a>
        </p>
    </body>
    </html>
    """
    
    return Response(html, content_type="text/html")

@app.route("/clear_cookie", methods=["GET"])
def clear_cookie(req):
    """清除所有Cookie（通过设置过期时间）"""
    resp = Response("Cookie已清除！")
    
    # 清除Cookie
    resp.set_cookie("user", "", max_age=0, path="/")
    resp.set_cookie("session_id", "", max_age=0, path="/")
    resp.set_cookie("theme", "", max_age=0, path="/")
    resp.set_cookie("preference", "", max_age=0, path="/api")
    
    return resp

@app.route("/cookie_counter", methods=["GET"])
def cookie_counter(req):
    """Cookie计数器示例"""
    count = int(req.cookies.get("visit_count", "0"))
    count += 1
    
    resp = Response(f"""
    <html>
    <body>
        <h1>欢迎！</h1>
        <p>这是您第 {count} 次访问本页面。</p>
        <p><a href="/">返回首页</a></p>
    </body>
    </html>
    """)
    
    resp.set_cookie("visit_count", str(count), max_age=31536000, path="/")
    return resp

# ================== 流式响应测试路由 ==================

@app.route("/stream", methods=["GET"])
def stream_test(req):
    """基本的流式响应示例"""
    def generate():
        # 第一个yield可以是header patch
        yield {"Content-Type": "text/plain; charset=utf-8", "X-Streaming": "true"}
        
        # 生成流式内容
        for i in range(5):
            yield f"这是第 {i+1} 条流式数据\n"
            time.sleep(0.5)  # 模拟延迟
    
    return Response(generate())

@app.route("/stream_json", methods=["GET"])
def stream_json(req):
    """流式JSON数据"""
    def generate():
        # 设置Content-Type为JSON
        yield {"Content-Type": "application/json", "X-Streaming": "true"}
        
        # 开始数组
        yield "[\n"
        
        for i in range(5):
            item = json.dumps({
                "id": i + 1,
                "timestamp": time.time(),
                "message": f"数据块 {i+1}"
            })
            
            if i < 4:
                yield f"  {item},\n"
            else:
                yield f"  {item}\n"
            
            time.sleep(0.3)
        
        # 结束数组
        yield "]\n"
    
    return Response(generate())

@app.route("/stream_sse", methods=["GET"])
def stream_sse(req):
    """Server-Sent Events (SSE) 示例"""
    def generate():
        # SSE需要特定的Content-Type
        yield {
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
        
        for i in range(10):
            # SSE格式：event: message\ndata: {...}\n\n
            data = json.dumps({
                "count": i + 1,
                "time": time.time(),
                "message": f"实时更新 {i+1}"
            })
            
            yield f"event: message\ndata: {data}\n\n"
            time.sleep(1)  # 每秒推送一次
    
    return Response(generate())

@app.route("/stream_large", methods=["GET"])
def stream_large_data(req):
    """生成大型数据的流式响应（模拟大数据传输）"""
    def generate():
        # 先返回headers
        yield {"Content-Type": "text/plain; charset=utf-8"}
        
        # 生成1000行数据
        for i in range(1000):
            yield f"行 {i+1}: " + "x" * 100 + "\n"
            if i % 100 == 0:  # 每100行刷新一次
                time.sleep(0.1)
    
    return Response(generate())

# ================== 混合测试路由 ==================

@app.route("/chat_stream", methods=["GET"])
def chat_stream(req):
    """模拟聊天机器人流式响应（同时设置Cookie）"""
    def generate():
        # 设置SSE headers
        yield {
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
        
        # 生成流式聊天响应
        messages = [
            "你好！我是AI助手。",
            "我可以在流式响应中逐步显示回答。",
            "这样你可以看到实时的回复过程。",
            "同时，我也设置了会话Cookie。",
            "再见！期待下次为你服务。"
        ]
        
        for i, msg in enumerate(messages):
            data = json.dumps({
                "index": i + 1,
                "message": msg,
                "timestamp": time.time(),
                "complete": i == len(messages) - 1
            })
            
            yield f"data: {data}\n\n"
            time.sleep(1.5)
    
    resp = Response(generate())
    # 设置会话Cookie
    resp.set_cookie("chat_session", f"sess_{int(time.time())}", max_age=3600, path="/")
    return resp

@app.route("/progress", methods=["GET"])
def progress_stream(req):
    """进度条流式更新示例"""
    def generate():
        yield {"Content-Type": "text/html; charset=utf-8"}
        
        yield """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>进度流式示例</title>
            <style>
                .progress-bar {
                    width: 300px;
                    height: 20px;
                    border: 1px solid #ccc;
                    margin: 20px 0;
                }
                .progress-fill {
                    height: 100%;
                    background: #4CAF50;
                    width: 0%;
                    transition: width 0.3s;
                }
                .status {
                    font-family: monospace;
                }
            </style>
        </head>
        <body>
            <h1>流式进度更新</h1>
            <div class="progress-bar">
                <div class="progress-fill" id="progress"></div>
            </div>
            <div class="status" id="status">准备开始...</div>
        """
        
        # 流式更新进度
        for progress in range(0, 101, 10):
            if progress == 0:
                continue
                
            yield f"""
            <script>
                document.getElementById('progress').style.width = '{progress}%';
                document.getElementById('status').innerHTML = '当前进度: {progress}%';
            </script>
            """
            time.sleep(0.5)
        
        yield """
            <script>
                document.getElementById('status').innerHTML = '✅ 完成！';
            </script>
            <p>进度更新完成！<a href="/">返回首页</a></p>
        </body>
        </html>
        """
    
    return Response(generate())

# ================== 首页和测试页面 ==================

@app.route("/", methods=["GET"])
def index(req):
    """首页，显示所有测试链接"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>流式与Cookie测试框架</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1 { color: #333; }
            .test-section { margin: 30px 0; padding: 20px; border-left: 4px solid #4CAF50; background: #f9f9f9; }
            .test-list { list-style: none; padding: 0; }
            .test-list li { margin: 10px 0; }
            .test-list a { 
                display: inline-block; 
                padding: 8px 15px; 
                background: #4CAF50; 
                color: white; 
                text-decoration: none; 
                border-radius: 4px; 
                margin-right: 10px;
            }
            .test-list a:hover { background: #45a049; }
            .code { 
                background: #f4f4f4; 
                padding: 10px; 
                border-radius: 4px; 
                font-family: monospace; 
                margin: 10px 0; 
            }
        </style>
    </head>
    <body>
        <h1>🎯 流式与Cookie测试框架</h1>
        <p>这是一个用于测试你框架的流式响应和Cookie功能的后端。</p>
        
        <div class="test-section">
            <h2>🍪 Cookie 测试</h2>
            <ul class="test-list">
                <li><a href="/set_cookie">设置测试Cookie</a></li>
                <li><a href="/get_cookie">查看当前Cookie</a></li>
                <li><a href="/clear_cookie">清除所有Cookie</a></li>
                <li><a href="/cookie_counter">访问计数器（使用Cookie）</a></li>
            </ul>
        </div>
        
        <div class="test-section">
            <h2>🌊 流式响应测试</h2>
            <ul class="test-list">
                <li><a href="/stream">基本流式文本</a></li>
                <li><a href="/stream_json">流式JSON数据</a></li>
                <li><a href="/stream_sse">Server-Sent Events (SSE)</a></li>
                <li><a href="/stream_large">大文件流式传输</a></li>
                <li><a href="/chat_stream">模拟聊天流式响应</a></li>
                <li><a href="/progress">流式进度更新</a></li>
            </ul>
        </div>
        
        <div class="test-section">
            <h2>🛠️ 测试工具</h2>
            <p>使用curl测试：</p>
            <div class="code">
                # 测试Cookie<br>
                curl -c cookies.txt http://localhost:8080/set_cookie<br>
                curl -b cookies.txt http://localhost:8080/get_cookie<br><br>
                # 测试流式响应<br>
                curl -N http://localhost:8080/stream<br>
                curl -N http://localhost:8080/stream_sse
            </div>
        </div>
        
        <div class="test-section">
            <h2>📊 框架功能验证</h2>
            <p>你的框架支持以下功能：</p>
            <ul>
                <li>✅ Flask-like 路由装饰器</li>
                <li>✅ Cookie 设置和读取</li>
                <li>✅ 流式响应（生成器）</li>
                <li>✅ 响应头自动管理</li>
                <li>✅ 多种内容类型（HTML/JSON/SSE）</li>
            </ul>
        </div>
    </body>
    </html>
    """
    
    return Response(html, content_type="text/html")

# ================== API测试端点 ==================

@app.route("/api/data", methods=["GET"])
def api_data(req):
    """API端点测试"""
    data = {
        "status": "success",
        "data": {
            "framework": "Micropython Flask-like",
            "features": ["streaming", "cookies", "routing"],
            "timestamp": time.time(),
            "cookies_received": dict(req.cookies)
        }
    }
    return Response(data, content_type="application/json")

@app.route("/api/stream_data", methods=["GET"])
def api_stream_data(req):
    """流式API端点"""
    def generate():
        yield {"Content-Type": "application/json"}
        yield "{\n  \"data\": [\n"
        
        for i in range(5):
            item = {
                "id": i + 1,
                "value": f"item_{i+1}",
                "time": time.time()
            }
            
            if i < 4:
                yield f"    {json.dumps(item)},\n"
            else:
                yield f"    {json.dumps(item)}\n"
            
            time.sleep(0.5)
        
        yield "  ]\n}\n"
    
    return Response(generate())

# ================== 错误处理测试 ==================

@app.route("/slow_stream", methods=["GET"])
def slow_stream(req):
    """慢速流测试，测试客户端中断处理"""
    def generate():
        try:
            for i in range(10):
                yield f"数据块 {i+1}，时间: {time.time()}\n"
                time.sleep(2)  # 每2秒发送一次
        except Exception as e:
            print(f"流中断: {e}")
    
    return Response(generate())

@app.route("/error_stream", methods=["GET"])
def error_stream(req):
    """模拟流中发生错误"""
    def generate():
        for i in range(5):
            if i == 2:
                raise Exception("模拟流错误")
            yield f"数据 {i+1}\n"
            time.sleep(0.5)
    
    return Response(generate())

# ================== 启动服务器 ==================

if __name__ == "__main__":
    # 设置AP模式
    ap = setup_ap('某某饭店_5G', '12345678', '192.168.4.1')
    time.sleep(2)
    
    # 设置STA模式
    sta = setup_sta("ssid", "pwd")
    print("🎯 启动流式与Cookie测试服务器...")
    print("🔗 访问地址: http://localhost:8080")
    print("📁 Cookie测试: /set_cookie, /get_cookie, /clear_cookie")
    print("🌊 流式测试: /stream, /stream_sse, /chat_stream")
    print("🚀 按Ctrl+C停止服务器\n")
    
    # 启动服务器
    app.run(host="0.0.0.0", port=80)