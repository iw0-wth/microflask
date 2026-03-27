"""
MicroFlask错误处理和API测试演示
演示全面的错误处理机制和API端点测试
"""
import sys
import os
import time
import json
import traceback
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from microflask import Flask, Response

# 创建Flask应用实例
app = Flask(__name__)

# 全局错误日志
error_log = []

# 1. 404错误处理演示
@app.route("/error/404")
def trigger_404():
    """触发404错误"""
    return Response("This page will show 404", status=404)

@app.route("/error/not-found")
def trigger_not_found():
    """另一种404触发方式"""
    return Response("Resource not found", status=404)

# 2. 500错误处理演示
@app.route("/error/500")
def trigger_500():
    """触发500错误"""
    # 故意引发错误
    raise ValueError("This is a test error to trigger 500")

@app.route("/error/internal-server")
def trigger_internal_server():
    """另一种500错误"""
    raise RuntimeError("Internal server error occurred")

# 3. 403禁止访问错误
@app.route("/error/403")
def trigger_403():
    """触发403禁止访问"""
    return Response("Access forbidden", status=403)

@app.route("/error/forbidden")
def trigger_forbidden():
    """另一种403错误"""
    return Response("You don't have permission", status=403)

# 4. 400错误处理
@app.route("/error/400")
def trigger_400():
    """触发400错误"""
    return Response("Bad request", status=400)

@app.route("/error/bad-request")
def trigger_bad_request():
    """另一种400错误"""
    return Response("Invalid parameters", status=400)

# 5. 自定义错误页面
@app.route("/error/custom/<int:code>")
def custom_error(code):
    """自定义错误页面"""
    error_pages = {
        400: {"title": "Bad Request", "message": "Your request is invalid", "color": "#ff6b6b"},
        401: {"title": "Unauthorized", "message": "Authentication required", "color": "#ff9800"},
        403: {"title": "Forbidden", "message": "Access denied", "color": "#f44336"},
        404: {"title": "Not Found", "message": "Page not found", "color": "#9e9e9e"},
        500: {"title": "Server Error", "message": "Internal server error", "color": "#f44336"},
        502: {"title": "Bad Gateway", "message": "Gateway error", "color": "#ff9800"},
        503: {"title": "Service Unavailable", "message": "Service temporarily unavailable", "color": "#ff9800"}
    }
    
    error_info = error_pages.get(code, {
        "title": "Unknown Error",
        "message": f"Error code {code}",
        "color": "#666666"
    })
    
    # 记录错误
    error_log.append({
        "code": code,
        "message": error_info["message"],
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "path": f"/error/custom/{code}"
    })
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Error {code}</title>
        <style>
            body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f5f5f5; }}
            .error-container {{ max-width: 500px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 5px 20px rgba(0,0,0,0.1); }}
            .error-code {{ font-size: 72px; font-weight: bold; color: {error_info['color']}; margin-bottom: 20px; }}
            .error-title {{ font-size: 24px; color: #333; margin-bottom: 10px; }}
            .error-message {{ color: #666; font-size: 16px; margin-bottom: 30px; }}
            .actions {{ margin-top: 30px; }}
            .btn {{ display: inline-block; padding: 10px 20px; margin: 0 10px; background: #007cba; color: white; text-decoration: none; border-radius: 5px; }}
            .btn:hover {{ background: #005a8b; }}
        </style>
    </head>
    <body>
        <div class="error-container">
            <div class="error-code">{code}</div>
            <div class="error-title">{error_info['title']}</div>
            <div class="error-message">{error_info['message']}</div>
            <div class="actions">
                <a href="/" class="btn">Go Home</a>
                <a href="javascript:history.back()" class="btn">Go Back</a>
                <a href="/error-test" class="btn">Test Other Errors</a>
            </div>
        </div>
    </body>
    </html>
    """, code

# 6. 异常处理演示
@app.route("/error/exception")
def trigger_exception():
    """触发各种异常"""
    exception_type = request.args.get("type", "value")
    
    try:
        if exception_type == "value":
            raise ValueError("Invalid value provided")
        elif exception_type == "type":
            raise TypeError("Wrong type conversion")
        elif exception_type == "index":
            raise IndexError("List index out of range")
        elif exception_type == "key":
            raise KeyError("Dictionary key not found")
        elif exception_type == "attribute":
            raise AttributeError("Object has no attribute")
        elif exception_type == "import":
            raise ImportError("Module not found")
        elif exception_type == "memory":
            raise MemoryError("Out of memory")
        elif exception_type == "io":
            raise IOError("File I/O error")
        else:
            raise Exception(f"Unknown exception type: {exception_type}")
    except Exception as e:
        # 记录异常
        error_log.append({
            "type": type(e).__name__,
            "message": str(e),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "traceback": traceback.format_exc()
        })
        
        return f"""
        <h1>Exception Caught</h1>
        <p><strong>Type:</strong> {type(e).__name__}</p>
        <p><strong>Message:</strong> {str(e)}</p>
        <p><strong>Time:</strong> {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <a href="/error-test">Back to Error Tests</a>
        """, 500

# 7. 超时错误演示
@app.route("/error/timeout")
def trigger_timeout():
    """触发超时错误"""
    timeout = int(request.args.get("timeout", 5))
    time.sleep(timeout)
    return "This should have timed out", 408  # Request Timeout

# 8. 请求过大错误
@app.route("/error/too-large")
def trigger_too_large():
    """触发请求过大错误"""
    # 模拟处理大请求
    return Response("Request entity too large", status=413)

# 9. 不支持的媒体类型
@app.route("/error/unsupported-media")
def trigger_unsupported_media():
    """触发不支持的媒体类型错误"""
    return Response("Unsupported media type", status=415)

# 10. 错误测试首页
@app.route("/error-test")
def error_test_home():
    """错误测试首页"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Error Handling Tests</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
            .error-section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
            .error-link { display: inline-block; margin: 5px 10px; padding: 8px 15px; background: #007cba; color: white; text-decoration: none; border-radius: 3px; }
            .error-link:hover { background: #005a8b; }
            .danger { background: #dc3545; }
            .warning { background: #ffc107; color: #333; }
            .info { background: #17a2b8; }
            .success { background: #28a745; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔧 MicroFlask Error Handling Tests</h1>
            <p>Test various error conditions and see how MicroFlask handles them.</p>
            
            <div class="error-section">
                <h3>HTTP Status Code Errors</h3>
                <a href="/error/400" class="error-link danger">400 Bad Request</a>
                <a href="/error/401" class="error-link warning">401 Unauthorized</a>
                <a href="/error/403" class="error-link danger">403 Forbidden</a>
                <a href="/error/404" class="error-link info">404 Not Found</a>
                <a href="/error/500" class="error-link danger">500 Internal Server</a>
                <a href="/error/502" class="error-link warning">502 Bad Gateway</a>
                <a href="/error/503" class="error-link warning">503 Service Unavailable</a>
            </div>
            
            <div class="error-section">
                <h3>Custom Error Pages</h3>
                <a href="/error/custom/400" class="error-link">Custom 400</a>
                <a href="/error/custom/404" class="error-link">Custom 404</a>
                <a href="/error/custom/500" class="error-link">Custom 500</a>
                <a href="/error/custom/503" class="error-link">Custom 503</a>
            </div>
            
            <div class="error-section">
                <h3>Exception Handling</h3>
                <a href="/error/exception?type=value" class="error-link">ValueError</a>
                <a href="/error/exception?type=index" class="error-link">IndexError</a>
                <a href="/error/exception?type=key" class="error-link">KeyError</a>
                <a href="/error/exception?type=type" class="error-link">TypeError</a>
                <a href="/error/exception?type=attribute" class="error-link">AttributeError</a>
                <a href="/error/exception?type=import" class="error-link">ImportError</a>
                <a href="/error/exception?type=memory" class="error-link">MemoryError</a>
                <a href="/error/exception?type=io" class="error-link">IOError</a>
            </div>
            
            <div class="error-section">
                <h3>Other Error Conditions</h3>
                <a href="/error/timeout?timeout=3" class="error-link warning">Timeout (3s)</a>
                <a href="/error/too-large" class="error-link danger">Request Too Large</a>
                <a href="/error/unsupported-media" class="error-link warning">Unsupported Media Type</a>
            </div>
            
            <div class="error-section">
                <h3>Error Monitoring</h3>
                <a href="/error-log" class="error-link info">View Error Log</a>
                <a href="/error-stats" class="error-link success">Error Statistics</a>
                <a href="/api-test" class="error-link">API Testing</a>
            </div>
        </div>
    </body>
    </html>
    """

# 11. 错误日志查看
@app.route("/error-log")
def view_error_log():
    """查看错误日志"""
    if not error_log:
        return "<h1>Error Log</h1><p>No errors recorded yet.</p>"
    
    html = "<h1>Error Log</h1><table border='1' style='border-collapse: collapse; width: 100%;'><tr><th>Time</th><th>Type</th><th>Message</th><th>Path</th></tr>"
    
    for error in error_log[-20:]:  # 显示最近20个错误
        html += f"<tr><td>{error['timestamp']}</td><td>{error.get('type', 'N/A')}</td><td>{error['message']}</td><td>{error.get('path', 'N/A')}</td></tr>"
    
    html += "</table><p><a href='/error-test'>Back to Tests</a></p>"
    return html

# 12. 错误统计
@app.route("/error-stats")
def error_stats():
    """错误统计"""
    if not error_log:
        return "<h1>Error Statistics</h1><p>No errors recorded yet.</p>"
    
    # 统计错误类型
    error_types = {}
    status_codes = {}
    
    for error in error_log:
        # 统计状态码
        code = error.get('code', 'unknown')
        status_codes[code] = status_codes.get(code, 0) + 1
        
        # 统计异常类型
        exc_type = error.get('type', 'N/A')
        error_types[exc_type] = error_types.get(exc_type, 0) + 1
    
    html = f"""
    <h1>Error Statistics</h1>
    <p>Total errors: {len(error_log)}</p>
    
    <h2>Status Code Distribution</h2>
    <table border='1' style='border-collapse: collapse;'>
        <tr><th>Status Code</th><th>Count</th><th>Percentage</th></tr>
    """
    
    for code, count in sorted(status_codes.items()):
        percentage = (count / len(error_log)) * 100
        html += f"<tr><td>{code}</td><td>{count}</td><td>{percentage:.1f}%</td></tr>"
    
    html += "</table>"
    
    html += "<h2>Exception Type Distribution</h2><table border='1' style='border-collapse: collapse;'><tr><th>Type</th><th>Count</th><th>Percentage</th></tr>"
    
    for exc_type, count in sorted(error_types.items()):
        percentage = (count / len(error_log)) * 100
        html += f"<tr><td>{exc_type}</td><td>{count}</td><td>{percentage:.1f}%</td></tr>"
    
    html += "</table><p><a href='/error-test'>Back to Tests</a></p>"
    return html

# 13. API端点测试
@app.route("/api-test")
def api_test_home():
    """API测试首页"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Endpoint Tests</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
            .test-section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
            .test-link { display: inline-block; margin: 5px; padding: 8px 15px; background: #007cba; color: white; text-decoration: none; border-radius: 3px; font-size: 12px; }
            .test-link:hover { background: #005a8b; }
            .response { background: #f8f9fa; padding: 10px; margin: 10px 0; border-radius: 3px; font-family: monospace; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔗 API Endpoint Testing</h1>
            <p>Test various API endpoints and response formats.</p>
            
            <div class="test-section">
                <h3>Basic API Endpoints</h3>
                <a href="/api/health" class="test-link">Health Check</a>
                <a href="/api/status" class="test-link">Server Status</a>
                <a href="/api/info" class="test-link">Server Info</a>
                <a href="/api/version" class="test-link">Version Info</a>
            </div>
            
            <div class="test-section">
                <h3>Data Endpoints</h3>
                <a href="/api/users" class="test-link">Users List</a>
                <a href="/api/users/1" class="test-link">User Detail</a>
                <a href="/api/posts" class="test-link">Posts List</a>
                <a href="/api/posts/1" class="test-link">Post Detail</a>
            </div>
            
            <div class="test-section">
                <h3>Method Testing</h3>
                <a href="/api/method-test" class="test-link">GET Test</a>
                <button onclick="testPost()" class="test-link">POST Test</button>
                <button onclick="testPut()" class="test-link">PUT Test</button>
                <button onclick="testDelete()" class="test-link">DELETE Test</button>
            </div>
            
            <div class="test-section">
                <h3>Response Format Tests</h3>
                <a href="/api/json" class="test-link">JSON Response</a>
                <a href="/api/xml" class="test-link">XML Response</a>
                <a href="/api/text" class="test-link">Text Response</a>
                <a href="/api/html" class="test-link">HTML Response</a>
            </div>
            
            <div class="test-section">
                <h3>Error Response Tests</h3>
                <a href="/api/error/400" class="test-link">400 Error</a>
                <a href="/api/error/404" class="test-link">404 Error</a>
                <a href="/api/error/500" class="test-link">500 Error</a>
                <a href="/api/error/timeout" class="test-link">Timeout Error</a>
            </div>
            
            <div id="response" class="response" style="display: none;"></div>
        </div>
        
        <script>
            function showResponse(text) {
                document.getElementById('response').style.display = 'block';
                document.getElementById('response').textContent = text;
            }
            
            function testPost() {
                fetch('/api/method-test', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({test: 'data'})
                })
                .then(response => response.json())
                .then(data => showResponse('POST Response: ' + JSON.stringify(data, null, 2)))
                .catch(error => showResponse('Error: ' + error));
            }
            
            function testPut() {
                fetch('/api/method-test', {
                    method: 'PUT',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({test: 'data'})
                })
                .then(response => response.json())
                .then(data => showResponse('PUT Response: ' + JSON.stringify(data, null, 2)))
                .catch(error => showResponse('Error: ' + error));
            }
            
            function testDelete() {
                fetch('/api/method-test', {
                    method: 'DELETE'
                })
                .then(response => response.json())
                .then(data => showResponse('DELETE Response: ' + JSON.stringify(data, null, 2)))
                .catch(error => showResponse('Error: ' + error));
            }
        </script>
    </body>
    </html>
    """

# 14. API健康检查
@app.route("/api/health")
def api_health():
    """API健康检查"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "uptime": "2h 34m 12s",
        "version": "1.0.0"
    }

@app.route("/api/status")
def api_status():
    """服务器状态"""
    return {
        "server": "MicroFlask",
        "status": "running",
        "environment": "development",
        "debug": True,
        "port": 8089,
        "endpoints_count": 25
    }

@app.route("/api/info")
def api_info():
    """服务器信息"""
    import sys
    return {
        "python_version": sys.version,
        "platform": sys.platform,
        "server": "MicroFlask",
        "api_version": "1.0.0",
        "features": [
            "Error Handling",
            "API Testing", 
            "JSON Responses",
            "Template Rendering",
            "Static Files"
        ]
    }

@app.route("/api/version")
def api_version():
    """版本信息"""
    return {
        "version": "1.0.0",
        "build": "2025.01.09",
        "api_version": "v1",
        "compatibility": "Flask-like"
    }

# 15. 数据API端点
@app.route("/api/users")
def api_users():
    """用户列表API"""
    users = [
        {"id": 1, "name": "Alice", "email": "alice@example.com"},
        {"id": 2, "name": "Bob", "email": "bob@example.com"},
        {"id": 3, "name": "Charlie", "email": "charlie@example.com"}
    ]
    return {"users": users, "count": len(users)}

@app.route("/api/users/<int:user_id>")
def api_user_detail(user_id):
    """用户详情API"""
    users = {
        1: {"id": 1, "name": "Alice", "email": "alice@example.com"},
        2: {"id": 2, "name": "Bob", "email": "bob@example.com"},
        3: {"id": 3, "name": "Charlie", "email": "charlie@example.com"}
    }
    
    user = users.get(user_id)
    if user:
        return user
    else:
        return {"error": "User not found"}, 404

@app.route("/api/posts")
def api_posts():
    """文章列表API"""
    posts = [
        {"id": 1, "title": "Post 1", "content": "Content of post 1"},
        {"id": 2, "title": "Post 2", "content": "Content of post 2"},
        {"id": 3, "title": "Post 3", "content": "Content of post 3"}
    ]
    return {"posts": posts, "count": len(posts)}

@app.route("/api/posts/<int:post_id>")
def api_post_detail(post_id):
    """文章详情API"""
    posts = {
        1: {"id": 1, "title": "Post 1", "content": "Content of post 1"},
        2: {"id": 2, "title": "Post 2", "content": "Content of post 2"},
        3: {"id": 3, "title": "Post 3", "content": "Content of post 3"}
    }
    
    post = posts.get(post_id)
    if post:
        return post
    else:
        return {"error": "Post not found"}, 404

# 16. HTTP方法测试
@app.route("/api/method-test", methods=["GET", "POST", "PUT", "DELETE"])
def api_method_test():
    """HTTP方法测试"""
    # 模拟request对象获取方法
    method = "GET"  # 在真实实现中从request对象获取
    
    return {
        "method": method,
        "message": f"HTTP {method} method test successful",
        "timestamp": time.time()
    }

# 17. 不同响应格式测试
@app.route("/api/json")
def api_json_response():
    """JSON响应测试"""
    return {"message": "This is a JSON response", "format": "json"}

@app.route("/api/xml")
def api_xml_response():
    """XML响应测试"""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <response>
        <message>This is an XML response</message>
        <format>xml</format>
    </response>"""
    return Response(xml, content_type="application/xml")

@app.route("/api/text")
def api_text_response():
    """文本响应测试"""
    return Response("This is a text response", content_type="text/plain")

@app.route("/api/html")
def api_html_response():
    """HTML响应测试"""
    html = "<h1>API HTML Response</h1><p>This is an HTML response from the API</p>"
    return Response(html, content_type="text/html")

# 18. API错误测试
@app.route("/api/error/<int:code>")
def api_error_test(code):
    """API错误测试"""
    error_responses = {
        400: {"error": "Bad Request", "code": 400},
        401: {"error": "Unauthorized", "code": 401},
        403: {"error": "Forbidden", "code": 403},
        404: {"error": "Not Found", "code": 404},
        500: {"error": "Internal Server Error", "code": 500}
    }
    
    error = error_responses.get(code)
    if error:
        return error, code
    else:
        return {"error": "Unknown error"}, 500

@app.route("/api/error/timeout")
def api_timeout():
    """API超时测试"""
    time.sleep(10)  # 模拟长时间处理
    return {"message": "This should have timed out"}, 408

# 添加request模拟（简化版）
class request:
    @staticmethod
    def args():
        return {"key": "value"}  # 模拟查询参数

if __name__ == "__main__":
    print("=== MicroFlask错误处理和API测试演示 ===")
    print("错误处理演示:")
    print("  GET  /error-test            - 错误测试首页")
    print("  GET  /error/400             - 400错误")
    print("  GET  /error/403             - 403错误")
    print("  GET  /error/404             - 404错误")
    print("  GET  /error/500             - 500错误")
    print("  GET  /error/custom/404      - 自定义404页面")
    print("  GET  /error/exception?type=value - 异常处理")
    print("  GET  /error/timeout?timeout=3 - 超时错误")
    print("  GET  /error-log             - 错误日志")
    print("  GET  /error-stats           - 错误统计")
    print()
    print("API测试演示:")
    print("  GET  /api-test              - API测试首页")
    print("  GET  /api/health             - 健康检查")
    print("  GET  /api/status             - 服务器状态")
    print("  GET  /api/info               - 服务器信息")
    print("  GET  /api/users              - 用户列表")
    print("  GET  /api/users/1           - 用户详情")
    print("  ANY  /api/method-test        - HTTP方法测试")
    print("  GET  /api/json              - JSON响应")
    print("  GET  /api/error/404         - API错误测试")
    print()
    print("启动服务器...")
    app.run(host="0.0.0.0", port=8089, debug=True)