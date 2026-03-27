"""
MicroFlask动态路由演示
演示各种动态路由规则和自定义转换器
参考Pro版本的扩展路由功能
"""
import sys
import os
import time
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from microflask import *

# 创建Flask应用实例
app = Flask(__name__)

# 1. 基础动态路由
@app.route("/user/<username>")
def user_profile(req):
    """基础动态路由 - 字符串参数"""
    username = req.view_args.get("username")
    return f"""
    <h1>User Profile</h1>
    <p>Username: {username}</p>
    <p><a href="/user/{username}/posts">View posts</a></p>
    """

# 2. 整数类型转换器
@app.route("/post/<int:post_id>")
def show_post(req):
    """整数类型转换器"""
    post_id = req.view_args.get("post_id")
    return f"""
    <h1>Post #{post_id}</h1>
    <p>This is post number {post_id}</p>
    <p>Type of post_id: {type(post_id).__name__}</p>
    <p><a href="/post/{post_id}/edit">Edit this post</a></p>
    """

# 3. 浮点数类型转换器
@app.route("/price/<float:amount>")
def show_price(req):
    """浮点数类型转换器"""
    amount = req.view_args.get("amount")
    return f"""
    <h1>Price Display</h1>
    <p>Amount: ${amount}</p>
    <p>Type: {type(amount).__name__}</p>
    <p>With tax (8%): ${amount * 1.08:.2f}</p>
    """

# 4. 布尔类型转换器
@app.route("/settings/<bool:feature>")
def toggle_feature(req):
    """布尔类型转换器"""
    feature_enabled = req.view_args.get("feature")
    return f"""
    <h1>Feature Settings</h1>
    <p>Feature is: {'Enabled' if feature_enabled else 'Disabled'}</p>
    <p>Type: {type(feature_enabled).__name__}</p>
    <p><a href="/settings/true">Enable</a> | <a href="/settings/false">Disable</a></p>
    """

# 5. 路径类型转换器（匹配包含斜杠的路径）
@app.route("/files/<path:filepath>")
def serve_file(req):
    """路径类型转换器"""
    filepath = req.view_args.get("filepath")
    return f"""
    <h1>File Path</h1>
    <p>Requested file: {filepath}</p>
    <p>Full path would be: /var/www/{filepath}</p>
    <p>Type: {type(filepath).__name__}</p>
    """

# 6. Part类型转换器（非贪婪匹配）
@app.route("/search/<part:query>")
def search(req):
    """Part类型转换器"""
    query = req.view_args.get("query")
    return f"""
    <h1>Search Results</h1>
    <p>Searching for: {query}</p>
    <p>Type: {type(query).__name__}</p>
    <p>Results for "{query}" would appear here</p>
    """

# 7. 多参数动态路由
@app.route("/user/<int:user_id>/post/<int:post_id>")
def user_post(req):
    """多参数动态路由"""
    user_id = req.view_args.get("user_id")
    post_id = req.view_args.get("post_id")
    return f"""
    <h1>User Post</h1>
    <p>User ID: {user_id} (Type: {type(user_id).__name__})</p>
    <p>Post ID: {post_id} (Type: {type(post_id).__name__})</p>
    <p>Viewing post {post_id} by user {user_id}</p>
    """

# 8. 复杂多段路由
@app.route("/api/v<int:version>/user/<int:user_id>/profile/<section>")
def api_user_profile(req):
    """复杂多段路由"""
    version = req.view_args.get("version")
    user_id = req.view_args.get("user_id")
    section = req.view_args.get("section")
    
    return f"""
    <h1>API User Profile</h1>
    <p>API Version: {version}</p>
    <p>User ID: {user_id}</p>
    <p>Profile Section: {section}</p>
    <p>Endpoint: /api/v{version}/user/{user_id}/profile/{section}</p>
    """

# 9. 可选参数路由（使用多个路由）
@app.route("/category/")
@app.route("/category/<category>")
@app.route("/category/<category>/<subcategory>")
def category(req):
    """可选参数路由"""
    category = req.view_args.get("category")
    subcategory = req.view_args.get("subcategory")
    
    if not category:
        return "<h1>All Categories</h1><p>Browse all categories</p>"
    elif not subcategory:
        return f"<h1>Category: {category}</h1><p>Browse items in {category}</p>"
    else:
        return f"<h1>{subcategory} in {category}</h1><p>Browse {subcategory} items</p>"

# 10. 自定义正则表达式路由 (MicroPython兼容)
@app.route("/product/<re(r'^[A-Z][A-Z]-\\d\\d\\d\\d$'):product_code>")
def product_detail(req):
    """自定义正则表达式路由"""
    product_code = req.view_args.get("product_code")
    return f"""
    <h1>Product Details</h1>
    <p>Product Code: {product_code}</p>
    <p>Format: XX-0000 (2 letters, 4 digits)</p>
    <p>Type: {type(product_code).__name__}</p>
    """

# 11. 日期格式路由 (MicroPython兼容)
@app.route("/archive/<re(r'^\\d\\d\\d\\d-\\d\\d-\\d\\d$'):date>")
def archive_by_date(req):
    """日期格式路由"""
    date_str = req.view_args.get("date")
    return f"""
    <h1>Archive for {date_str}</h1>
    <p>Date format: YYYY-MM-DD</p>
    <p>Type: {type(date_str).__name__}</p>
    <p>Showing posts from {date_str}</p>
    """

# 12. 邮箱格式验证路由 (MicroPython兼容)
@app.route("/email/<re(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z][a-zA-Z]$'):email>")
def email_info(req):
    """邮箱格式验证路由"""
    email = req.view_args.get("email")
    domain = email.split('@')[1] if '@' in email else 'unknown'
    return f"""
    <h1>Email Information</h1>
    <p>Email: {email}</p>
    <p>Domain: {domain}</p>
    <p>Valid email format</p>
    <p>Type: {type(email).__name__}</p>
    """

# 13. 复杂URL模式
@app.route("/docs/<re(r'^v(\\d+)\\.(\\d+)$'):version>/page/<int:page>")
def documentation(req):
    """复杂URL模式"""
    version = req.view_args.get("version")
    page = req.view_args.get("page")
    
    return f"""
    <h1>Documentation</h1>
    <p>Version: {version}</p>
    <p>Page: {page}</p>
    <p>URL pattern: docs/vX.Y/page/N</p>
    """

# 14. 文件扩展名路由
@app.route("/download/<re(r'^[^/]+\\.(txt|pdf|docx)$'):filename>")
def download_file(req):
    """文件扩展名路由"""
    filename = req.view_args.get("filename")
    extension = filename.split('.')[-1] if '.' in filename else 'unknown'
    
    return f"""
    <h1>File Download</h1>
    <p>Filename: {filename}</p>
    <p>Extension: {extension}</p>
    <p>Allowed: .txt, .pdf, .docx</p>
    """

# 15. 混合类型转换器 (MicroPython兼容)
@app.route("/mixed/<int:id>/<float:ratio>/<bool:active>/<re(r'^COL_[A-Z][A-Z][A-Z]$'):code>")
def mixed_types(req):
    """混合类型转换器"""
    args = req.view_args
    return f"""
    <h1>Mixed Type Converters</h1>
    <ul>
        <li>ID: {args.get('id')} (Type: {type(args.get('id')).__name__})</li>
        <li>Ratio: {args.get('ratio')} (Type: {type(args.get('ratio')).__name__})</li>
        <li>Active: {args.get('active')} (Type: {type(args.get('active')).__name__})</li>
        <li>Code: {args.get('code')} (Type: {type(args.get('code')).__name__})</li>
    </ul>
    """

# 16. 路由优先级演示
@app.route("/priority/<string:name>")
def priority_string(req):
    """字符串类型路由（较低优先级）"""
    name = req.view_args.get("name")
    return f"<h1>String Route: {name}</h1>"

@app.route("/priority/<int:num>")
def priority_int(req):
    """整数类型路由（较高优先级）"""
    num = req.view_args.get("num")
    return f"<h1>Integer Route: {num}</h1>"

# 17. 路由测试页面
@app.route("/routing-test")
def routing_test(req):
    """路由测试页面"""
    return """
    <h1>Dynamic Routing Tests</h1>
    
    <h2>Basic Converters</h2>
    <ul>
        <li><a href="/user/alice">String: /user/alice</a></li>
        <li><a href="/post/123">Integer: /post/123</a></li>
        <li><a href="/price/19.99">Float: /price/19.99</a></li>
        <li><a href="/settings/true">Boolean: /settings/true</a></li>
        <li><a href="/files/documents/reports/2024/report.pdf">Path: /files/documents/reports/2024/report.pdf</a></li>
        <li><a href="/search/python+tutorial">Part: /search/python+tutorial</a></li>
    </ul>
    
    <h2>Multi-parameter Routes</h2>
    <ul>
        <li><a href="/user/456/post/789">User Post: /user/456/post/789</a></li>
        <li><a href="/api/v2/user/123/profile/basic">API: /api/v2/user/123/profile/basic</a></li>
    </ul>
    
    <h2>Custom Regex Routes</h2>
    <ul>
        <li><a href="/product/AB-1234">Product: /product/AB-1234</a></li>
        <li><a href="/archive/2024-01-15">Archive: /archive/2024-01-15</a></li>
        <li><a href="/email/user@example.com">Email: /email/user@example.com</a></li>
        <li><a href="/docs/v1.2/page/5">Documentation: /docs/v1.2/page/5</a></li>
        <li><a href="/download/document.pdf">Download: /download/document.pdf</a></li>
    </ul>
    
    <h2>Optional Parameters</h2>
    <ul>
        <li><a href="/category/">Category: /category/</a></li>
        <li><a href="/category/electronics">Category: /category/electronics</a></li>
        <li><a href="/category/electronics/phones">Category: /category/electronics/phones</a></li>
    </ul>
    
    <h2>Priority Tests</h2>
    <ul>
        <li><a href="/priority/123">Should match integer route</a></li>
        <li><a href="/priority/abc">Should match string route</a></li>
    </ul>
    
    <h2>Mixed Types</h2>
    <ul>
        <li><a href="/mixed/42/3.14/true/COL_USA">Mixed: /mixed/42/3.14/true/COL_USA</a></li>
    </ul>
    """

# 18. 路由参数信息
@app.route("/route-info")
def route_info(req):
    """显示当前路由信息"""
    import inspect
    
    info = {
        "method": req.method,
        "path": req.path,
        "full_path": req.full_path,
        "url": req.url,
        "view_args": dict(req.view_args) if req.view_args else {},
        "args": dict(req.args) if req.args else {},
        "headers": dict(req.headers) if req.headers else {}
    }
    
    html = "<h1>Route Information</h1><pre>" + str(info) + "</pre>"
    return html

if __name__ == "__main__":
    print("=== MicroFlask动态路由演示 ===")
    print("可用路由:")
    print("  GET  /user/username           - 字符串参数")
    print("  GET  /post/123               - 整数转换器")
    print("  GET  /price/19.99            - 浮点数转换器")
    print("  GET  /settings/true          - 布尔转换器")
    print("  GET  /files/path/to/file     - 路径转换器")
    print("  GET  /search/query            - Part转换器")
    print("  GET  /user/123/post/456      - 多参数路由")
    print("  GET  /api/v2/user/123/profile/basic - 复杂路由")
    print("  GET  /category/               - 可选参数")
    print("  GET  /category/electronics     - 可选参数")
    print("  GET  /category/electronics/phones - 可选参数")
    print("  GET  /product/AB-1234         - 自定义正则")
    print("  GET  /archive/2024-01-15      - 日期格式")
    print("  GET  /email/user@domain.com    - 邮箱格式")
    print("  GET  /docs/v1.2/page/5        - 复杂模式")
    print("  GET  /download/file.pdf        - 文件扩展名")
    print("  GET  /mixed/42/3.14/true/COL_USA - 混合类型")
    print("  GET  /priority/123            - 优先级测试")
    print("  GET  /routing-test            - 测试页面")
    print("  GET  /route-info              - 路由信息")
    print()
    app.run(host="0.0.0.0", port=8086, debug=True)