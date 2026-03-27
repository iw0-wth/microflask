"""
MicroFlask基础功能演示
演示所有对外API函数的基本用法
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from microflask import Flask, Response, Request, make_response

# 创建Flask应用实例
app = Flask(__name__)

# 1. 基础路由演示
@app.route("/")
def home(req):
    """首页 - 基础字符串响应"""
    return "Welcome to MicroFlask Demo!"

# 2. make_response函数演示
@app.route("/make-response")
def make_response_demo(req):
    """演示make_response函数的不同用法"""
    # 方式1: 直接返回字符串
    # return "Simple response"
    
    # 方式2: 返回(status, body)元组
    # return (200, "Response with status")
    
    # 方式3: 返回(body, status, headers)元组
    return ("Response with headers", 200, {"X-Custom-Header": "demo-value"})

# 3. Response对象直接使用
@app.route("/response-object")
def response_object_demo(req):
    """演示Response对象的直接使用"""
    resp = Response("Direct Response object", status=200)
    resp.set_cookie("demo_cookie", "cookie_value", max_age=3600)
    resp.headers["X-Response-Type"] = "direct-object"
    return resp

# 4. Request对象属性演示
@app.route("/request-info")
def request_info_demo(req):
    """演示Request对象的各个属性"""
    info = {
        "method": req.method,
        "path": req.path,
        "full_path": req.full_path,
        "url": req.url,
        "host": req.host,
        "user_agent": req.headers.get("User-Agent", "Unknown"),
        "args": dict(req.args) if req.args else {},
        "cookies": dict(req.cookies) if req.cookies else {}
    }
    return info

# 5. 请求参数处理演示
@app.route("/args")
def args_demo(req):
    """演示查询参数的处理"""
    name = req.args.get("name", "Guest")
    age = req.args.get("age", "unknown")
    return f"Hello {name}, you are {age} years old!"

# 6. JSON响应演示
@app.route("/json")
def json_demo(req):
    """演示JSON响应"""
    data = {
        "message": "This is a JSON response",
        "status": "success",
        "data": [1, 2, 3, 4, 5]
    }
    return data  # 自动转换为JSON

# 7. 不同HTTP状态码演示
@app.route("/status/<int:code>")
def status_demo(req):
    """演示不同HTTP状态码"""
    status_messages = {
        200: "OK",
        201: "Created",
        400: "Bad Request",
        404: "Not Found",
        500: "Internal Server Error"
    }
    message = status_messages.get(req.view_args.get("code"), "Unknown Status")
    return message, req.view_args.get("code")

# 8. 自定义响应头演示
@app.route("/headers")
def headers_demo(req):
    """演示自定义响应头"""
    resp = Response("Headers demo")
    resp.headers["X-Custom-Header"] = "Custom-Value"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    return resp

# 9. 路由参数演示
@app.route("/user/<username>")
def user_profile(req):
    """演示路由参数"""
    username = req.view_args.get("username")
    return f"User profile: {username}"

# 10. 多方法路由演示
@app.route("/api/data", methods=["GET", "POST", "PUT", "DELETE"])
def api_data(req):
    """演示多方法路由"""
    if req.method == "GET":
        return {"action": "get", "data": []}
    elif req.method == "POST":
        return {"action": "create", "status": "success"}
    elif req.method == "PUT":
        return {"action": "update", "status": "success"}
    elif req.method == "DELETE":
        return {"action": "delete", "status": "success"}

# 11. 错误处理演示
@app.route("/error")
def error_demo(req):
    """演示错误处理"""
    # 故意引发一个错误来演示错误处理
    raise ValueError("This is a demo error")

# 12. 静态文件访问演示（需要在static目录下放置文件）
@app.route("/static-demo")
def static_demo(req):
    """静态文件访问演示"""
    return """
    <h1>Static Files Demo</h1>
    <p>Try accessing these static files:</p>
    <ul>
        <li><a href="/static/test.txt">/static/test.txt</a></li>
        <li><a href="/static/style.css">/static/style.css</a></li>
        <li><a href="/static/script.js">/static/script.js</a></li>
    </ul>
    """

# 13. 重定向演示（使用302状态码和Location头）
@app.route("/redirect")
def redirect_demo(req):
    """演示重定向"""
    resp = Response("", status=302)
    resp.headers["Location"] = "/"
    return resp

# 14. 内容类型演示
@app.route("/content-types")
def content_types_demo(req):
    """演示不同的内容类型"""
    content_type = req.args.get("type", "html")
    
    if content_type == "html":
        return Response("<h1>HTML Content</h1>", content_type="text/html")
    elif content_type == "json":
        return Response('{"message": "JSON Content"}', content_type="application/json")
    elif content_type == "text":
        return Response("Plain text content", content_type="text/plain")
    elif content_type == "xml":
        return Response('<?xml version="1.0"?><root><item>XML Content</item></root>', content_type="application/xml")
    else:
        return Response("Unknown content type", status=400)

# 15. 环境信息演示
@app.route("/env")
def env_demo(req):
    """演示环境信息"""
    import sys
    return {
        "python_version": sys.version,
        "platform": sys.platform,
        "implementation": sys.implementation.name if hasattr(sys, 'implementation') else 'unknown'
    }

if __name__ == "__main__":
    print("=== MicroFlask基础功能演示 ===")
    print("可用路由:")
    print("  GET  /                    - 首页")
    print("  GET  /make-response        - make_response函数演示")
    print("  GET  /response-object     - Response对象演示")
    print("  GET  /request-info        - Request对象属性演示")
    print("  GET  /args?name=xxx&age=20 - 查询参数演示")
    print("  GET  /json                - JSON响应演示")
    print("  GET  /status/200          - 状态码演示")
    print("  GET  /headers             - 自定义响应头演示")
    print("  GET  /user/username       - 路由参数演示")
    print("  GET|POST|PUT|DELETE /api/data - 多方法路由演示")
    print("  GET  /error               - 错误处理演示")
    print("  GET  /static-demo         - 静态文件演示")
    print("  GET  /redirect            - 重定向演示")
    print("  GET  /content-types?type=json - 内容类型演示")
    print("  GET  /env                 - 环境信息演示")
    print()
    app.run(host="0.0.0.0", port=8080, debug=True)