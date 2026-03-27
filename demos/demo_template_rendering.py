"""
MicroFlask模板渲染演示
演示各种模板引擎的使用方法
"""
from microflask import *
import network,time
# 创建Flask应用实例
app = Flask(__name__)
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

# 设置默认模板引擎为表达式引擎
#Response.set_default_template_engine(ExpressionTemplateEngine())此为默认设置

# 1. 表达式模板引擎演示（字符串渲染）
@app.route("/string-expression")
def string_expression_demo(req):
    """演示表达式模板引擎的字符串渲染"""
    template_string = """
    <html>
    <head><title>Expression Template Demo</title></head>
    <body>
        <h1>Hello {{ name }}!</h1>
        <p>You are {{ age }} years old.</p>
        <p>Today is {{ date }}.</p>
        <p>2 + 3 = {{ 2 + 3 }}</p>
        <p>Upper case: {{ name.upper() }}</p>
    </body>
    </html>
    """
    
    context = {
        "name": "Alice",
        "age": 25,
        "date": "2025-01-09"
    }
    
    return render_template_string(template_string, context)

# 2. 简单字符串替换模板演示
@app.route("/string-simple")
def string_simple_demo(req):
    """演示简单字符串替换模板"""
    template_string = """
    <html>
    <head><title>Simple Template Demo</title></head>
    <body>
        <h1>Hello {{ name }}!</h1>
        <p>Message: {{ message }}</p>
        <p>Status: {{ status }}</p>
    </body>
    </html>
    """
    
    context = {
        "name": "Bob",
        "message": "Welcome to MicroFlask!",
        "status": "Active"
    }
    
    engine = SimpleTemplateEngine()
    return render_template_string(template_string, context, template_engine=engine)

# 3. 文件模板演示（需要创建templates目录）
@app.route("/file-template")
def file_template_demo(req):
    return render_template("1.html")

# 4. 自定义函数模板演示
@app.route("/custom-function")
def custom_function_demo(req):
    """演示自定义函数作为模板引擎"""
    def custom_renderer(template_content, **context):
        """自定义模板渲染函数"""
        result = template_content
        # 简单的变量替换，支持{{变量名}}格式
        for key, value in context.items():
            result = result.replace(f"{{ {key} }}", str(value))
            result = result.replace(f"{{{key}}}", str(value))
        return result
    
    # 创建自定义模板引擎
    from microflask_sync_pro import create_template_adapter
    custom_engine = create_template_adapter(custom_renderer)
    
    template_string = """
    <html>
    <head><title>Custom Function Template</title></head>
    <body>
        <h1>Title: {{ title }}</h1>
        <p>Author: {{ author }}</p>
        <p>Content: {{ content }}</p>
        <p>Tags: {{ tags }}</p>
    </body>
    </html>
    """
    
    context = {
        "title": "Custom Template Demo",
        "author": "MicroFlask Team",
        "content": "This is rendered using a custom template function.",
        "tags": "python, microflask, template"
    }
    
    return render_template_string(template_string, context, template_engine=custom_engine)

# 5. 条件渲染演示
@app.route("/conditional")
def conditional_demo(req):
    """演示条件渲染"""
    user_logged_in = req.args.get("login", "false").lower() == "true"
    user_role = req.args.get("role", "guest")
    
    template_string = """
    <html>
    <head><title>Conditional Rendering Demo</title></head>
    <body>
        <h1>Conditional Rendering</h1>
        {% if logged_in %}
            <p>Welcome back, {{ user }}!</p>
            {% if role == 'admin' %}
                <p>You have admin privileges.</p>
            {% elif role == 'user' %}
                <p>You have regular user privileges.</p>
            {% else %}
                <p>You have guest privileges.</p>
            {% endif %}
        {% else %}
            <p>Please log in to continue.</p>
        {% endif %}
        
        <p>Visit with different parameters:</p>
        <ul>
            <li><a href="/conditional?login=true&role=admin">Admin View</a></li>
            <li><a href="/conditional?login=true&role=user">User View</a></li>
            <li><a href="/conditional?login=false">Guest View</a></li>
        </ul>
    </body>
    </html>
    """
    
    # 由于表达式引擎不支持if语句，我们用Python处理逻辑
    context = {
        "logged_in": user_logged_in,
        "user": "DemoUser",
        "role": user_role
    }
    
    if user_logged_in:
        if user_role == 'admin':
            role_message = "You have admin privileges."
        elif user_role == 'user':
            role_message = "You have regular user privileges."
        else:
            role_message = "You have guest privileges."
        
        content = f"""
        <html>
        <head><title>Conditional Rendering Demo</title></head>
        <body>
            <h1>Conditional Rendering</h1>
            <p>Welcome back, {context['user']}!</p>
            <p>{role_message}</p>
            <p>Visit with different parameters:</p>
            <ul>
                <li><a href="/conditional?login=true&role=admin">Admin View</a></li>
                <li><a href="/conditional?login=true&role=user">User View</a></li>
                <li><a href="/conditional?login=false">Guest View</a></li>
            </ul>
        </body>
        </html>
        """
    else:
        content = f"""
        <html>
        <head><title>Conditional Rendering Demo</title></head>
        <body>
            <h1>Conditional Rendering</h1>
            <p>Please log in to continue.</p>
            <p>Visit with different parameters:</p>
            <ul>
                <li><a href="/conditional?login=true&role=admin">Admin View</a></li>
                <li><a href="/conditional?login=true&role=user">User View</a></li>
                <li><a href="/conditional?login=false">Guest View</a></li>
            </ul>
        </body>
        </html>
        """
    
    return content

# 6. 循环渲染演示
@app.route("/loop")
def loop_demo(req):
    """演示循环渲染"""
    items = [
        {"name": "Item 1", "price": 10.99, "in_stock": True},
        {"name": "Item 2", "price": 25.50, "in_stock": False},
        {"name": "Item 3", "price": 5.75, "in_stock": True},
        {"name": "Item 4", "price": 99.99, "in_stock": True}
    ]
    
    template_string = """
    <html>
    <head><title>Loop Rendering Demo</title></head>
    <body>
        <h1>Product List</h1>
        <table border="1">
            <tr>
                <th>Name</th>
                <th>Price</th>
                <th>Status</th>
            </tr>
            {items_html}
        </table>
        <p>Total items: {{ total_items }}</p>
        <p>Total value: ${{ total_value }}</p>
    </body>
    </html>
    """
    
    # 生成表格行HTML
    items_html = ""
    total_value = 0
    for item in items:
        status = "In Stock" if item["in_stock"] else "Out of Stock"
        items_html += f"""
        <tr>
            <td>{item['name']}</td>
            <td>${item['price']}</td>
            <td>{status}</td>
        </tr>
        """
        if item["in_stock"]:
            total_value += item["price"]
    
    context = {
        "items_html": items_html,
        "total_items": len(items),
        "total_value": round(total_value, 2)
    }
    
    return render_template_string(template_string, context)

# 7. 模板继承演示（简单实现）
@app.route("/inheritance")
def inheritance_demo(req):
    """演示模板继承概念"""
    page = req.args.get("page", "home")
    
    # 基础模板
    base_template = """
    <html>
    <head>
        <title>{{ title }} - MicroFlask Demo</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background: #f0f0f0; padding: 10px; }}
            .content {{ margin: 20px 0; }}
            .footer {{ background: #f0f0f0; padding: 10px; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{{ site_name }}</h1>
        </div>
        <div class="content">
            {{ content }}
        </div>
        <div class="footer">
            <p>&copy; 2025 {{ site_name }}. All rights reserved.</p>
        </div>
    </body>
    </html>
    """
    
    # 根据页面生成内容
    if page == "home":
        content = "<h2>Welcome Home</h2><p>This is the home page content.</p>"
        title = "Home"
    elif page == "about":
        content = "<h2>About Us</h2><p>This is the about page content.</p>"
        title = "About"
    elif page == "contact":
        content = "<h2>Contact</h2><p>Email: info@microflask.com</p>"
        title = "Contact"
    else:
        content = "<h2>Page Not Found</h2><p>The requested page does not exist.</p>"
        title = "404"
    
    context = {
        "site_name": "MicroFlask Demo",
        "title": title,
        "content": content
    }
    
    return render_template_string(base_template, context)

# 8. 模板缓存演示
@app.route("/cache")
def cache_demo(req):
    """演示模板缓存功能"""
    import time
    
    template_string = """
    <html>
    <head><title>Template Cache Demo</title></head>
    <body>
        <h1>Template Cache Demo</h1>
        <p>Generated at: {{ timestamp }}</p>
        <p>Random number: {{ random_number }}</p>
        <p><a href="/cache">Refresh this page</a></p>
    </body>
    </html>
    """
    
    context = {
        "timestamp": time.time(),
        "random_number": hash(time.time()) % 1000
    }
    
    return render_template_string(template_string, context)

if __name__ == "__main__":
    print("=== MicroFlask模板渲染演示 ===")
    print("可用路由:")
    print("  GET  /string-expression  - 表达式模板引擎（字符串渲染）")
    print("  GET  /string-simple      - 简单字符串替换模板")
    print("  GET  /file-template      - 文件模板渲染")
    print("  GET  /custom-function    - 自定义函数模板")
    print("  GET  /conditional        - 条件渲染演示")
    print("  GET  /loop               - 循环渲染演示")
    print("  GET  /inheritance        - 模板继承演示")
    print("  GET  /cache              - 模板缓存演示")
    print()
    print("注意：文件模板需要在templates目录下创建相应的模板文件")
    print()
    app.run(host="0.0.0.0", port=80, debug=True)