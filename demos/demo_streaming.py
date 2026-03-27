"""
MicroFlask流式响应演示
演示各种流式响应技术
"""
import sys
import os
import time
import json
import random


from microflask import Flask, Response

# 创建Flask应用实例
app = Flask(__name__)
import network,time
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
ap = setup_ap('AP', '12345678', '192.168.4.1')
sta = setup_sta("ssid", "pwd")
# 1. 基础流式响应
@app.route("/stream/basic")
def stream_basic(req):
    """基础流式响应演示"""
    def generate():
        yield {"Content-Type": "text/plain; charset=utf-8"}
        yield "Starting stream...\n"
        for i in range(5):
            yield f"Chunk {i + 1}\n"
            time.sleep(0.5)
        yield "Stream completed!\n"
    
    return Response(generate())

# 2. JSON流式响应
@app.route("/stream/json")
def stream_json(req):
    """JSON流式响应"""
    def generate():
        yield {"Content-Type": "application/json; charset=utf-8"}
        yield "[\n"
        for i in range(5):
            data = {
                "id": i + 1,
                "message": f"Item {i + 1}",
                "timestamp": time.time()
            }
            if i < 4:
                yield json.dumps(data) + ",\n"
            else:
                yield json.dumps(data) + "\n"
            time.sleep(0.3)
        yield "]\n"
    
    return Response(generate())

# 3. 生成大型数据流
@app.route("/stream/large-data")
def stream_large_data(req):
    """生成大型数据的流式响应"""
    size = int(req.args.get("size", 1000))  # 默认1000行
    
    def generate():
        yield {"Content-Type": "text/plain; charset=utf-8"}
        yield "Large data stream generation\n"
        yield "=" * 50 + "\n"
        
        for i in range(size):
            line = f"Line {i + 1}: This is a sample line of data with random number {random.randint(1, 1000)}\n"
            yield line
            
            if i % 100 == 0:  # 每100行稍微暂停一下
                time.sleep(0.01)
        
        yield "\n" + "=" * 50 + "\n"
        yield f"Generated {size} lines\n"
    
    return Response(generate())

# 4. 模拟聊天机器人流式响应
@app.route("/stream/chat")
def stream_chat(req):
    """模拟聊天机器人的流式响应"""
    message = req.args.get("message", "Hello!")
    
    def generate():
        # 设置Cookie来记录对话
        yield {"Content-Type": "text/plain; charset=utf-8"}
        yield {"Set-Cookie": "chat_session=active; Path=/; Max-Age=3600"}
        
        yield f"You: {message}\n"
        yield "Bot: "
        
        # 模拟打字效果
        bot_response = f"I received your message: '{message}'. Let me think about it... This is a simulated streaming response that appears character by character!"
        
        for char in bot_response:
            yield char
            time.sleep(0.05)  # 每个字符延迟50ms
    
    return Response(generate())

# 5. 进度条流式更新
@app.route("/stream/progress")
def stream_progress(req):
    """进度条流式更新演示"""
    steps = int(req.args.get("steps", 10))
    duration = float(req.args.get("duration", 5.0))
    
    def generate():
        yield {"Content-Type": "text/html; charset=utf-8"}
        yield """
        <html>
        <head>
            <title>Progress Stream Demo</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                .progress-container { width: 300px; border: 1px solid #ccc; margin: 10px 0; }
                .progress-bar { height: 20px; background: #4CAF50; width: 0%; transition: width 0.3s; }
                .progress-text { margin: 5px 0; }
            </style>
        </head>
        <body>
            <h1>Progress Stream Demo</h1>
            <div class="progress-container">
                <div class="progress-bar" id="progress"></div>
            </div>
            <div class="progress-text" id="status">Starting...</div>
            <div id="log"></div>
            
            <script>
                function updateProgress(percent, message) {
                    document.getElementById('progress').style.width = percent + '%';
                    document.getElementById('status').textContent = message;
                    
                    const log = document.getElementById('log');
                    log.innerHTML += '<div>' + message + ' (' + percent + '%)</div>';
                }
            </script>
        """
        
        step_duration = duration / steps
        for i in range(steps + 1):
            progress = (i / steps) * 100
            message = f"Processing step {i}/{steps}"
            
            yield f"<script>updateProgress({progress:.1f}, '{message}');</script>\n"
            
            # 强制浏览器立即显示更新
            yield " " * 1000  # 添加一些空白字符强制缓冲
            
            if i < steps:
                time.sleep(step_duration)
        
        yield """
            <script>
                updateProgress(100, 'Completed!');
                document.getElementById('progress').style.background = '#2196F3';
            </script>
        </body>
        </html>
        """
    
    return Response(generate())

# 6. Server-Sent Events (SSE) 演示
@app.route("/stream/sse")
def stream_sse(req):
    """Server-Sent Events演示"""
    def generate():
        yield {"Content-Type": "text/event-stream; charset=utf-8"}
        yield {"Cache-Control": "no-cache"}
        yield {"Connection": "keep-alive"}
        
        # 发送初始连接事件
        yield f"event: connect\ndata: Connected to SSE stream at {time.time()}\n\n"
        
        for i in range(10):
            event_type = "message" if i % 2 == 0 else "update"
            data = {
                "id": i + 1,
                "message": f"Server message {i + 1}",
                "timestamp": time.time()
            }
            
            yield f"event: {event_type}\n"
            yield f"data: {json.dumps(data)}\n\n"
            
            time.sleep(1)
        
        # 发送结束事件
        yield "event: end\ndata: Stream ended\n\n"
    
    return Response(generate())

# 7. 慢速流测试
@app.route("/stream/slow")
def stream_slow(req):
    """慢速流测试"""
    duration = int(req.args.get("duration", 30))  # 默认30秒
    interval = int(req.args.get("interval", 2))    # 默认2秒间隔
    
    def generate():
        yield {"Content-Type": "text/plain; charset=utf-8"}
        yield f"Slow stream test - Duration: {duration}s, Interval: {interval}s\n"
        yield "=" * 50 + "\n"
        
        start_time = time.time()
        count = 0
        
        while time.time() - start_time < duration:
            count += 1
            elapsed = time.time() - start_time
            remaining = duration - elapsed
            
            yield f"[{elapsed:.1f}s] Message {count}: {remaining:.1f}s remaining\n"
            
            time.sleep(interval)
        
        yield "=" * 50 + "\n"
        yield f"Slow stream completed after {count} messages\n"
    
    return Response(generate())

# 8. 流式错误处理
@app.route("/stream/error")
def stream_error(req):
    """流式响应中的错误处理"""
    error_point = int(req.args.get("error_at", 5))  # 在第几个chunk引发错误
    
    def generate():
        yield {"Content-Type": "text/plain; charset=utf-8"}
        yield "Stream with error demo\n"
        
        for i in range(10):
            if i == error_point:
                raise ValueError(f"Intentional error at chunk {i + 1}")
            
            yield f"Chunk {i + 1}: Processing data...\n"
            time.sleep(0.5)
    
    return Response(generate())

# 9. 分块传输编码演示
@app.route("/stream/chunked")
def stream_chunked(req):
    """分块传输编码演示"""
    def generate():
        yield {"Content-Type": "text/plain; charset=utf-8"}
        yield {"Transfer-Encoding": "chunked"}
        
        # 发送不同大小的块
        chunks = [
            "Small chunk",
            "This is a medium-sized chunk of data",
            "This is a much larger chunk that contains more text and demonstrates how the server can send data in variable sized chunks to optimize performance",
            "Final chunk"
        ]
        
        for i, chunk in enumerate(chunks):
            yield f"Chunk {i + 1}: {chunk}\n"
            time.sleep(1)
    
    return Response(generate())

# 10. 实时数据流
@app.route("/stream/realtime")
def stream_realtime(req):
    """实时数据流演示"""
    def generate():
        yield {"Content-Type": "text/plain; charset=utf-8"}
        yield "Real-time data stream\n"
        yield "=" * 40 + "\n"
        
        # 模拟实时数据
        data_types = ["temperature", "humidity", "pressure", "light"]
        
        for i in range(20):
            data_type = random.choice(data_types)
            
            if data_type == "temperature":
                value = random.uniform(18.0, 28.0)
                unit = "°C"
            elif data_type == "humidity":
                value = random.uniform(30.0, 80.0)
                unit = "%"
            elif data_type == "pressure":
                value = random.uniform(990.0, 1020.0)
                unit = "hPa"
            else:  # light
                value = random.uniform(0, 1000)
                unit = "lux"
            
            timestamp = time.strftime("%H:%M:%S")
            yield f"[{timestamp}] {data_type}: {value:.2f} {unit}\n"
            
            time.sleep(0.5)
        
        yield "=" * 40 + "\n"
        yield "Real-time stream ended\n"
    
    return Response(generate())

# 11. 文件下载流
@app.route("/stream/download")
def stream_download(req):
    """文件下载流演示"""
    filename = req.args.get("filename", "sample.txt")
    size = int(req.args.get("size", 1000))  # 文件大小
    
    def generate():
        # 设置下载头
        yield {"Content-Type": "application/octet-stream"}
        yield {"Content-Disposition": f"attachment; filename=\"{filename}\""}
        
        # 生成文件内容
        for i in range(size):
            line = f"Line {i + 1}: This is sample content for the downloadable file.\n"
            yield line.encode('utf-8')
            
            if i % 100 == 0:
                time.sleep(0.01)  # 避免占用太多CPU
    
    return Response(generate())

# 12. WebSocket替代演示（长轮询）
@app.route("/stream/long-poll")
def stream_long_poll(req):
    """长轮询演示"""
    timeout = int(req.args.get("timeout", 10))  # 超时时间
    
    def generate():
        yield {"Content-Type": "text/plain; charset=utf-8"}
        yield "Long polling simulation\n"
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            # 检查是否有新数据（这里模拟随机产生数据）
            if random.random() < 0.1:  # 10%概率有新数据
                yield f"New data at {time.time()}\n"
                break
            
            time.sleep(0.5)
        else:
            yield f"Timeout after {timeout} seconds\n"
    
    return Response(generate())

# 13. 流式HTML页面
@app.route("/stream/html")
def stream_html(req):
    """流式HTML页面"""
    def generate():
        yield {"Content-Type": "text/html; charset=utf-8"}
        
        # 发送HTML头部
        yield """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Streaming HTML Demo</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                .chunk { margin: 10px 0; padding: 10px; border-left: 3px solid #007cba; background: #f5f5f5; }
            </style>
        </head>
        <body>
            <h1>Streaming HTML Content</h1>
            <div id="content">
        """
        
        # 逐步发送内容
        for i in range(5):
            yield f"""
                <div class="chunk">
                    <h3>Chunk {i + 1}</h3>
                    <p>This content was streamed at {time.time()}</p>
                    <p>Random number: {random.randint(1, 1000)}</p>
                </div>
            """
            time.sleep(1)
        
        # 发送HTML尾部
        yield """
            </div>
            <p>All chunks loaded!</p>
        </body>
        </html>
        """
    
    return Response(generate())

# 14. 流式数据处理管道
@app.route("/stream/pipeline")
def stream_pipeline(req):
    """流式数据处理管道演示"""
    def generate():
        yield {"Content-Type": "text/plain; charset=utf-8"}
        yield "Data processing pipeline\n"
        yield "=" * 40 + "\n"
        
        # 模拟数据处理阶段
        stages = [
            ("Data Collection", 2),
            ("Data Validation", 1),
            ("Data Transformation", 3),
            ("Data Analysis", 2),
            ("Report Generation", 1)
        ]
        
        for stage_name, duration in stages:
            yield f"Starting: {stage_name}\n"
            
            # 模拟处理过程
            for i in range(5):
                yield f"  {stage_name} - Step {i + 1}/5\n"
                time.sleep(duration / 5)
            
            yield f"Completed: {stage_name}\n\n"
        
        yield "Pipeline completed successfully!\n"
    
    return Response(generate())

if __name__ == "__main__":
    print("=== MicroFlask流式响应演示 ===")
    print("可用路由:")
    print("  GET  /stream/basic         - 基础流式响应")
    print("  GET  /stream/json          - JSON流式响应")
    print("  GET  /stream/large-data    - 大型数据流")
    print("  GET  /stream/chat?msg=hi   - 聊天机器人流式响应")
    print("  GET  /stream/progress      - 进度条流式更新")
    print("  GET  /stream/sse           - Server-Sent Events")
    print("  GET  /stream/slow?duration=20 - 慢速流测试")
    print("  GET  /stream/error?error_at=3 - 流式错误处理")
    print("  GET  /stream/chunked       - 分块传输编码")
    print("  GET  /stream/realtime      - 实时数据流")
    print("  GET  /stream/download      - 文件下载流")
    print("  GET  /stream/long-poll     - 长轮询演示")
    print("  GET  /stream/html          - 流式HTML页面")
    print("  GET  /stream/pipeline      - 数据处理管道")
    print()
    print("注意：流式响应适用于支持分块传输的客户端")
    print()
    app.run(host="0.0.0.0", port=80, debug=True)