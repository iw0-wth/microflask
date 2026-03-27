"""
MicroFlask Cookie和Session演示
演示Cookie的设置、读取、删除等操作
"""
import sys
import os
import time
import hashlib
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from microflask import Flask, Response

# 创建Flask应用实例
app = Flask(__name__)

# 简单的内存Session存储（生产环境应该使用数据库）
sessions = {}

def generate_session_id():
    """生成唯一的Session ID"""
    return hashlib.md5(f"{time.time()}{random.random()}".encode()).hexdigest()

def get_session_id(cookies):
    """从Cookie中获取Session ID"""
    session_cookie = cookies.get("session_id")
    return session_cookie if session_cookie else None

def get_session_data(session_id):
    """获取Session数据"""
    return sessions.get(session_id, {})

def set_session_data(session_id, data):
    """设置Session数据"""
    sessions[session_id] = data

def delete_session(session_id):
    """删除Session"""
    if session_id in sessions:
        del sessions[session_id]

# 1. 设置基础Cookie
@app.route("/set-cookie")
def set_cookie(req):
    """演示设置基础Cookie"""
    resp = Response("Cookie has been set!")
    
    # 设置不同类型的Cookie
    resp.set_cookie("username", "alice")
    resp.set_cookie("user_id", "12345")
    resp.set_cookie("theme", "dark")
    
    return resp

# 2. 读取Cookie
@app.route("/read-cookie")
def read_cookie(req):
    """演示读取Cookie"""
    username = req.cookies.get("username", "Guest")
    user_id = req.cookies.get("user_id", "unknown")
    theme = req.cookies.get("theme", "light")
    
    html = f"""
    <html>
    <head><title>Read Cookie Demo</title></head>
    <body>
        <h1>Cookie Values</h1>
        <p>Username: {username}</p>
        <p>User ID: {user_id}</p>
        <p>Theme: {theme}</p>
        <p>All cookies: {dict(req.cookies) if req.cookies else {}}</p>
        <p><a href="/set-cookie">Set Cookie</a></p>
    </body>
    </html>
    """
    
    return html

# 3. Cookie过期时间演示
@app.route("/set-expiring-cookie")
def set_expiring_cookie(req):
    """演示设置带过期时间的Cookie"""
    resp = Response("Expiring cookie set! It will expire in 60 seconds.")
    
    # 设置1分钟后过期的Cookie
    resp.set_cookie("temp_data", "will_expire_soon", max_age=60)
    
    # 设置10分钟后过期的Cookie
    resp.set_cookie("long_term", "will_expire_in_10_min", max_age=600)
    
    return resp

# 4. 删除Cookie演示
@app.route("/delete-cookie")
def delete_cookie(req):
    """演示删除Cookie"""
    resp = Response("Cookie has been deleted!")
    
    # 删除Cookie的方法：设置过期时间为0
    resp.set_cookie("username", "", max_age=0)
    resp.set_cookie("user_id", "", max_age=0)
    
    return resp

# 5. Session创建演示
@app.route("/session/create")
def session_create(req):
    """创建新Session"""
    session_id = generate_session_id()
    session_data = {
        "user_id": random.randint(1000, 9999),
        "username": f"user{random.randint(1, 100)}",
        "login_time": time.time(),
        "page_views": 0
    }
    
    set_session_data(session_id, session_data)
    
    resp = Response(f"Session created! Session ID: {session_id}")
    resp.set_cookie("session_id", session_id, max_age=3600)  # 1小时过期
    
    return resp

# 6. Session读取演示
@app.route("/session/read")
def session_read(req):
    """读取Session数据"""
    session_id = get_session_id(req.cookies)
    
    if not session_id:
        return "No session found. <a href='/session/create'>Create session</a>"
    
    session_data = get_session_data(session_id)
    
    if not session_data:
        return "Invalid or expired session. <a href='/session/create'>Create new session</a>"
    
    # 增加页面访问计数
    session_data["page_views"] += 1
    set_session_data(session_id, session_data)
    
    html = f"""
    <html>
    <head><title>Session Data</title></head>
    <body>
        <h1>Session Information</h1>
        <p>Session ID: {session_id}</p>
        <p>User ID: {session_data['user_id']}</p>
        <p>Username: {session_data['username']}</p>
        <p>Login Time: {time.ctime(session_data['login_time'])}</p>
        <p>Page Views: {session_data['page_views']}</p>
        <p>
            <a href="/session/read">Refresh (increase page views)</a> |
            <a href="/session/update">Update Session</a> |
            <a href="/session/delete">Delete Session</a>
        </p>
    </body>
    </html>
    """
    
    return html

# 7. Session更新演示
@app.route("/session/update")
def session_update(req):
    """更新Session数据"""
    session_id = get_session_id(req.cookies)
    
    if not session_id:
        return "No session found. <a href='/session/create'>Create session</a>"
    
    session_data = get_session_data(session_id)
    
    if not session_data:
        return "Invalid session. <a href='/session/create'>Create new session</a>"
    
    # 更新Session数据
    session_data["last_activity"] = time.time()
    session_data["updated_count"] = session_data.get("updated_count", 0) + 1
    
    set_session_data(session_id, session_data)
    
    html = f"""
    <html>
    <head><title>Session Updated</title></head>
    <body>
        <h1>Session Updated</h1>
        <p>Last Activity: {time.ctime(session_data['last_activity'])}</p>
        <p>Updated Count: {session_data['updated_count']}</p>
        <p><a href="/session/read">Back to Session</a></p>
    </body>
    </html>
    """
    
    return html

# 8. Session删除演示
@app.route("/session/delete")
def session_delete(req):
    """删除Session"""
    session_id = get_session_id(req.cookies)
    
    if session_id:
        delete_session(session_id)
    
    resp = Response("Session has been deleted! <a href='/session/read'>Check session</a>")
    resp.set_cookie("session_id", "", max_age=0)
    
    return resp

# 9. Cookie计数器演示
@app.route("/counter")
def counter(req):
    """Cookie计数器"""
    current_count = int(req.cookies.get("visit_count", "0"))
    current_count += 1
    
    first_visit = req.cookies.get("first_visit")
    if not first_visit:
        first_visit = time.ctime(time.time())
    
    resp = Response(f"""
    <html>
    <head><title>Cookie Counter</title></head>
    <body>
        <h1>Visit Counter</h1>
        <p>This is visit number: {current_count}</p>
        <p>First visit: {first_visit}</p>
        <p>Last visit: {time.ctime(time.time())}</p>
        <p><a href="/counter">Refresh</a> | <a href="/counter/reset">Reset Counter</a></p>
    </body>
    </html>
    """)
    
    resp.set_cookie("visit_count", str(current_count))
    resp.set_cookie("first_visit", first_visit)
    
    return resp

# 10. 重置计数器
@app.route("/counter/reset")
def counter_reset(req):
    """重置Cookie计数器"""
    resp = Response("Counter has been reset! <a href='/counter'>Start counting</a>")
    resp.set_cookie("visit_count", "0", max_age=0)
    resp.set_cookie("first_visit", "", max_age=0)
    
    return resp

# 11. 用户偏好设置演示
@app.route("/preferences")
def preferences(req):
    """用户偏好设置"""
    # 获取当前偏好
    theme = req.cookies.get("theme", "light")
    language = req.cookies.get("language", "en")
    font_size = req.cookies.get("font_size", "medium")
    
    action = req.args.get("action")
    
    if action == "save":
        # 保存新偏好
        new_theme = req.args.get("theme", theme)
        new_language = req.args.get("language", language)
        new_font_size = req.args.get("font_size", font_size)
        
        resp = Response("Preferences saved! <a href='/preferences'>View preferences</a>")
        resp.set_cookie("theme", new_theme, max_age=86400 * 30)  # 30天
        resp.set_cookie("language", new_language, max_age=86400 * 30)
        resp.set_cookie("font_size", new_font_size, max_age=86400 * 30)
        
        return resp
    
    html = f"""
    <html>
    <head><title>User Preferences</title></head>
    <body>
        <h1>User Preferences</h1>
        
        <h2>Current Preferences</h2>
        <p>Theme: {theme}</p>
        <p>Language: {language}</p>
        <p>Font Size: {font_size}</p>
        
        <h2>Update Preferences</h2>
        <form method="GET" action="/preferences">
            <input type="hidden" name="action" value="save">
            
            <label for="theme">Theme:</label>
            <select name="theme" id="theme">
                <option value="light" {'selected' if theme == 'light' else ''}>Light</option>
                <option value="dark" {'selected' if theme == 'dark' else ''}>Dark</option>
                <option value="auto" {'selected' if theme == 'auto' else ''}>Auto</option>
            </select>
            <br><br>
            
            <label for="language">Language:</label>
            <select name="language" id="language">
                <option value="en" {'selected' if language == 'en' else ''}>English</option>
                <option value="zh" {'selected' if language == 'zh' else ''}>中文</option>
                <option value="es" {'selected' if language == 'es' else ''}>Español</option>
            </select>
            <br><br>
            
            <label for="font_size">Font Size:</label>
            <select name="font_size" id="font_size">
                <option value="small" {'selected' if font_size == 'small' else ''}>Small</option>
                <option value="medium" {'selected' if font_size == 'medium' else ''}>Medium</option>
                <option value="large" {'selected' if font_size == 'large' else ''}>Large</option>
            </select>
            <br><br>
            
            <button type="submit">Save Preferences</button>
        </form>
        
        <p><a href="/counter">Cookie Counter Demo</a> | <a href="/session/read">Session Demo</a></p>
    </body>
    </html>
    """
    
    return html

# 12. Cookie安全演示
@app.route("/secure-cookie")
def secure_cookie(req):
    """演示安全Cookie设置"""
    resp = Response("Secure cookie demo")
    
    # HttpOnly Cookie (不能被JavaScript访问)
    resp.set_cookie("http_only", "http_only_value", max_age=3600)
    # Note: MicroFlask目前不支持Secure和HttpOnly标志，但这里演示概念
    
    # 敏感数据应该加密存储
    sensitive_data = "secret_information"
    # 简单的编码示例（生产环境应该使用更强的加密）
    encoded_data = sensitive_data.encode().hex()
    resp.set_cookie("session_token", encoded_data, max_age=3600)
    
    html = f"""
    <html>
    <head><title>Secure Cookie Demo</title></head>
    <body>
        <h1>Secure Cookie Demo</h1>
        <p>Secure cookie has been set.</p>
        <p>Encoded session token: {encoded_data[:20]}...</p>
        <p>Note: In production, use proper encryption and security flags.</p>
        <p><a href="/secure-cookie/read">Read secure cookies</a></p>
    </body>
    </html>
    """
    
    return html

@app.route("/secure-cookie/read")
def read_secure_cookie(req):
    """读取安全Cookie"""
    session_token = req.cookies.get("session_token", "")
    
    try:
        decoded_data = bytes.fromhex(session_token).decode()
    except:
        decoded_data = "Invalid token"
    
    return f"""
    <html>
    <head><title>Secure Cookie Read</title></head>
    <body>
        <h1>Secure Cookie Data</h1>
        <p>Session Token (raw): {session_token}</p>
        <p>Decoded Data: {decoded_data}</p>
        <p><a href="/secure-cookie">Back to demo</a></p>
    </body>
    </html>
    """

if __name__ == "__main__":
    print("=== MicroFlask Cookie和Session演示 ===")
    print("可用路由:")
    print("  GET  /set-cookie          - 设置基础Cookie")
    print("  GET  /read-cookie         - 读取Cookie")
    print("  GET  /set-expiring-cookie - 设置过期Cookie")
    print("  GET  /delete-cookie       - 删除Cookie")
    print("  GET  /session/create      - 创建Session")
    print("  GET  /session/read        - 读取Session")
    print("  GET  /session/update      - 更新Session")
    print("  GET  /session/delete      - 删除Session")
    print("  GET  /counter             - Cookie计数器")
    print("  GET  /counter/reset       - 重置计数器")
    print("  GET  /preferences         - 用户偏好设置")
    print("  GET  /secure-cookie       - 安全Cookie演示")
    print("  GET  /secure-cookie/read  - 读取安全Cookie")
    print()
    app.run(host="0.0.0.0", port=8082, debug=True)