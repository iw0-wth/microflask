"""
MicroFlask Flask移植演示
演示如何将Flask应用移植到MicroFlask
展示常见Flask功能的MicroFlask实现
"""
#一般路由处理
#Flask:
@app.route("/hello/")
def hello():
    return f"<h1>Hello!</h1>"
#MicroFlask:
@app.route("/hello/")
def hello(req):
    return f"<h1>Hello!</h1>"

#动态路由处理
#Flask:
@app.route("/hello/<name>")
def hello(name):
    """动态路由参数"""
    return f"<h1>Hello, {name}!</h1>"
#MicroFlask:
@app.route("/hello/<name>")
def hello(req):
    """动态路由参数"""
    name = req.view_args.get("name")
    return f"<h1>Hello, {name}!</h1>"

#GET
#Flask:
@app.route("/hello/")
def hello(name):
    """动态路由参数"""
    return f"<h1>Hello, {name}!</h1>"
#MicroFlask:
@app.route("/hello/")
def hello(req):
    """动态路由参数"""
    name = req.view_args.get("name")
    return f"<h1>Hello, {name}!</h1>"

#模板渲染可以同Flask
render_template('template.html', name='User')
#也可以：
render_template('template.html', {"name":'User'})
    

#表单处理
def form(req):req.form.get()

# 4. JSON API（Flask风格）
@app.route("/api/data", methods=["GET", "POST"])
def api_data():
    """API端点演示"""
    if request.method == "GET":
        # 模拟Flask的jsonify
        data = {
            "message": "Data retrieved successfully",
            "items": [
                {"id": 1, "name": "Item 1"},
                {"id": 2, "name": "Item 2"},
                {"id": 3, "name": "Item 3"}
            ],
            "timestamp": time.time()
        }
        return data  # 自动转换为JSON
    
    elif request.method == "POST":
        # 模拟Flask的request.get_json()
        try:
            data = request.json
            if not data:
                return {"error": "Invalid JSON"}, 400
            
            # 处理提交的数据
            result = {
                "message": "Data processed successfully",
                "received": data,
                "processed_at": time.time()
            }
            return result, 201
            
        except Exception as e:
            return {"error": f"Processing error: {str(e)}"}, 500

#重定向同Flask，目前版本不支持url_for()
return redirect(target)

#中间件暂不支持

#Session暂不支持，部分功能用Cookie手搓也行，示例如下
@app.route("/session")
def session_demo():
    """Session演示"""
    # 在Flask中：session['key'] = value
    # 在MicroFlask中，我们使用Cookie模拟
    
    session_data = request.cookies.get("session_data", "{}")
    try:
        session = json.loads(session_data)
    except:
        session = {}
    
    # 更新访问次数
    visit_count = session.get("visit_count", 0) + 1
    session["visit_count"] = visit_count
    session["last_visit"] = time.time()
    
    resp = Response(f"""
    <h1>Session Demo</h1>
    <p>Visit count: {visit_count}</p>
    <p>Last visit: {session['last_visit']}</p>
    <p><a href="/session">Refresh</a></p>
    """)
    
    # 保存session到Cookie
    resp.set_cookie("session_data", json.dumps(session))
    return resp

# 9. 文件上传模拟
@app.route("/upload", methods=["GET", "POST"])
def upload_demo():
    """文件上传演示（模拟）"""
    if request.method == "POST":
        # 在真实Flask中：request.files['file']
        # 在MicroFlask中，我们模拟文件上传通过JSON
        
        try:
            data = request.json
            if not data or "filename" not in data:
                return {"error": "No file data provided"}, 400
            
            filename = data["filename"]
            content = data.get("content", "")
            content_type = data.get("content_type", "text/plain")
            
            # 模拟文件处理
            file_info = {
                "filename": filename,
                "size": len(content),
                "content_type": content_type,
                "uploaded_at": time.time()
            }
            
            return {
                "message": "File uploaded successfully",
                "file": file_info
            }
            
        except Exception as e:
            return {"error": f"Upload failed: {str(e)}"}, 500
    
    # GET请求 - 显示上传表单
    return """
    <h1>File Upload Demo</h1>
    <p>This simulates file upload (MicroFlask doesn't support multipart yet)</p>
    <form id="uploadForm">
        <div>
            <label>Filename:</label><br>
            <input type="text" id="filename" required>
        </div><br>
        <div>
            <label>Content:</label><br>
            <textarea id="content" rows="6"></textarea>
        </div><br>
        <button type="button" onclick="uploadFile()">Upload</button>
    </form>
    
    <script>
    function uploadFile() {
        const filename = document.getElementById('filename').value;
        const content = document.getElementById('content').value;
        
        fetch('/upload', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                filename: filename,
                content: content,
                content_type: 'text/plain'
            })
        })
        .then(response => response.json())
        .then(data => {
            alert(JSON.stringify(data, null, 2));
        })
        .catch(error => {
            alert('Upload failed: ' + error);
        });
    }
    </script>
    """



#WebSocket替代方案
@app.route("/websocket-alt")
def websocket_alternative():
    """WebSocket替代方案（长轮询）"""
    return """
    <h1>WebSocket Alternative Demo</h1>
    <p>This demonstrates real-time updates using long polling</p>
    <button onclick="startPolling()">Start Polling</button>
    <button onclick="stopPolling()">Stop Polling</button>
    <div id="messages" style="border: 1px solid #ccc; padding: 10px; margin-top: 10px; height: 200px; overflow-y: auto;"></div>
    
    <script>
        let polling = false;
        let pollInterval;
        
        function startPolling() {
            if (polling) return;
            polling = true;
            
            pollInterval = setInterval(() => {
                fetch('/api/messages')
                .then(response => response.json())
                .then(data => {
                    const messages = document.getElementById('messages');
                    const message = document.createElement('div');
                    message.textContent = new Date().toLocaleTimeString() + ': ' + data.message;
                    messages.appendChild(message);
                    messages.scrollTop = messages.scrollHeight;
                })
                .catch(error => console.error('Polling error:', error));
            }, 1000);
        }
        
        function stopPolling() {
            polling = false;
            clearInterval(pollInterval);
        }
    </script>
    """

@app.route("/api/messages")
def api_messages():
    """消息API（用于长轮询）"""
    messages = [
        "Server is running",
        "New data available",
        "Processing request",
        "Operation completed",
        "Ready for next task"
    ]
    
    message = random.choice(messages)
    return {"message": message, "timestamp": time.time()}

# 12. CORS支持
@app.route("/cors-demo")
def cors_demo():
    """CORS支持演示"""
    # 设置CORS头
    resp = Response({
        "message": "CORS demo",
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "headers": ["Content-Type", "Authorization"],
        "origin": request.headers.get("Origin", "unknown")
    })
    
    # 在生产环境中应该更安全
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    
    return resp

@app.route("/cors-demo", methods=["POST", "PUT", "DELETE", "OPTIONS"])
def cors_demo_methods():
    """CORS其他方法演示"""
    if request.method == "OPTIONS":
        # 预检请求
        resp = Response("")
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return resp
    
    # 实际请求
    resp = Response({
        "method": request.method,
        "message": "CORS request successful"
    })
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp

# 13. 静态文件服务
@app.route("/static-demo")
def static_demo():
    """静态文件服务演示"""
    return """
    <h1>Static Files Demo</h1>
    <p>MicroFlask serves static files from the /static directory</p>
    <ul>
        <li><a href="/static/test.txt">Test Text File</a></li>
        <li><a href="/static/style.css">CSS File</a></li>
        <li><a href="/static/script.js">JavaScript File</a></li>
    </ul>
    <p>Make sure these files exist in the static directory</p>
    """

# 14. 生产环境配置
@app.route("/production-config")
def production_config():
    """生产环境配置演示"""
    is_production = not app.config.DEBUG
    
    config_info = {
        "debug_mode": app.config.DEBUG,
        "environment": "production" if is_production else "development",
        "secret_key": "***HIDDEN***" if is_production else app.config.SECRET_KEY,
        "items_per_page": app.config.ITEMS_PER_PAGE,
        "server_time": time.time()
    }
    
    return f"""
    <h1>Production Configuration</h1>
    <pre>{json.dumps(config_info, indent=2)}</pre>
    <p>Debug mode: {'ON' if app.config.DEBUG else 'OFF'}</p>
    """



# 创建request全局对象（模拟Flask的request）
@app.before_request
def create_request_global():
    """创建request全局对象"""
    # 这是一个概念演示，实际MicroFlask没有before_request装饰器
    # 在真实应用中，request会作为参数传递给视图函数
    pass

