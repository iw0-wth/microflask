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



# ========== 网络状态监控路由 ==========
@app.route("/")
def index(request):
    """主页 - 显示网络状态和测试链接"""
    network_info = {}
    
    try:
        # 获取AP模式信息
        ap = network.WLAN(network.AP_IF)
        if ap.active():
            ap_config = ap.ifconfig()
            network_info['ap'] = {
                'active': True,
                'ip': ap_config[0],
                'ssid': '某某饭店_5G' if hasattr(ap, 'config') else '未知'
            }
        else:
            network_info['ap'] = {'active': False}
        
        # 获取STA模式信息
        sta = network.WLAN(network.STA_IF)
        if sta.active():
            sta_config = sta.ifconfig()
            network_info['sta'] = {
                'active': True,
                'connected': sta.isconnected(),
                'ip': sta_config[0] if sta.isconnected() else '未连接'
            }
        else:
            network_info['sta'] = {'active': False}
            
    except Exception as e:
        network_info['error'] = str(e)
    
    
    current_time = time.ticks_ms()  # 使用ticks_ms获取时间戳
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MicroPython网络测试服务器</title>
        <meta charset="utf-8">
        </head>
    <body>
        <div class="container">
            <h1>MicroPython网络测试服务器</h1>
            
            <div class="network-status">
                <h2>📡 网络状态</h2>
                <div class="status-item {ap_status}">
                    <strong>AP模式:</strong> {ap_info}
                </div>
                <div class="status-item {sta_status}">
                    <strong>STA模式:</strong> {sta_info}
                </div>
                <div class="status-item">
                    <strong>服务器时间:</strong> {current_time}ms
                </div>
            </div>
            
            <div class="test-section">
                <h2>🔧 网络测试工具</h2>
                <a class="test-link" href="/network/scan">WiFi网络扫描</a>
                <a class="test-link" href="/network/status">详细网络状态</a>
                <a class="test-link" href="/network/config">网络配置信息</a>
            </div>
            
            <div class="test-section">
                <h2>🌐 Web服务测试</h2>
                <a class="test-link" href="/api/hello">基础API测试</a>
                <a class="test-link" href="/api/system">系统信息</a>
                <a class="test-link" href="/static/network_test.html">静态文件测试</a>
            </div>
            
            <div class="test-section">
                <h2>📊 实时数据测试</h2>
                <a class="test-link" href="/sensor/simulate">传感器数据模拟</a>
                <a class="test-link" href="/data/live">实时数据流</a>
            </div>
            
            <div class="api-test">
                <h3>快速API测试</h3>
                <button onclick="testAPI()">测试网络连接</button>
                <div id="api-result"></div>
                <script>
                    function testAPI() {{
                        fetch('/api/hello')
                            .then(r => r.text())
                            .then(text => {{
                                document.getElementById('api-result').innerHTML = '响应: ' + text;
                            }})
                            .catch(e => {{
                                document.getElementById('api-result').innerHTML = '错误: ' + e;
                            }});
                    }}
                </script>
            </div>
        </div>
    </body>
    </html>
    """.format(
        ap_status='status-on' if network_info.get('ap', {}).get('active') else 'status-off',
        ap_info=network_info.get('ap', {}).get('ip', '未知') if network_info.get('ap', {}).get('active') else '未启用',
        sta_status='status-on' if network_info.get('sta', {}).get('connected') else 'status-off',
        sta_info=network_info.get('sta', {}).get('ip', '未知') if network_info.get('sta', {}).get('connected') else '未连接',
        current_time=current_time
    )
    return html

# ========== 网络相关路由 ==========
@app.route("/network/scan")
def network_scan(request):
    """扫描可用WiFi网络"""
    try:
        sta = network.WLAN(network.STA_IF)
        sta.active(True)
        networks = sta.scan()
        
        result = {
            "status": "success",
            "networks": []
        }
        
        for net in networks:
            result["networks"].append({
                "ssid": net[0].decode('utf-8') if isinstance(net[0], bytes) else net[0],
                "bssid": net[1],
                "channel": net[2],
                "rssi": net[3],
                "authmode": net[4]
            })
        
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

@app.route('/test/get', methods=['GET'])
def test_get(request):
    """测试GET请求"""
    print("\n" + "="*50)
    print(f"📨 收到GET请求 - {time.ticks_ms()}")
    print("="*50)
    #print(f"客户端IP: {request.remote_addr}")
    print(f"请求路径: {request.path}")
    print(f"完整URL: {request.url}")
    print(f"查询参数: {request.args}")
    print(f"请求头: {request.headers}")
    
    return {
        "status": "GET请求成功",
        "message": "服务器已收到GET请求",
        "your_params": request._args if request.args else {}
        
    }

@app.route("/test/basic")
def test_basic_vars(request):
    context = {
        "username": "张三",
        "message": "Hello, MicroPython!",
        "age": 25,
        "price": 99.99,
        "score": 4.5,
        "is_active": True,
        "is_admin": False,
        "null_value": None,
        "number1": 10,
        "number2": 20,
        "str1": "Hello",
        "str2": "World"
    }
    return render_template("var_basic.html", **context)

@app.route("/test/complex")
def test_complex_vars(request):
    a = request.args.get("a", "0")
    
    # 根据条件选择模板引擎
    if a == "1":
        template_engine = SimpleTemplateEngine()
    else:
        template_engine = None  # 使用默认引擎
    
    context = {
        "user": {
            "name": "李四",
            "age": 30,
            "email": "lisi@example.com"
        },
        "address": {
            "province": "广东省",
            "city": "深圳市"
        },
        "fruits": ["苹果", "香蕉", "橙子", "葡萄"],
        "numbers": [1, 2, 3, 4, 5],
        "company": {
            "name": "测试公司",
            "departments": [
                {
                    "name": "技术部",
                    "manager": {"name": "王经理"}
                }
            ]
        },
        "product": {
            "title": "笔记本电脑",
            "price": 5999,
            "in_stock": True
        }
    }
    return render_template("var_complex.html", template_engine=template_engine, **context)

@app.route("/test/advanced")
def test_advanced_vars(request):
    context = {
        "a": 5,
        "b": 3, 
        "c": 10,
        "x": 15,
        "y": 8,
        "age": 20,
        "greeting": "欢迎",
        "user_info": {
            "name": "测试用户",
            "level": "VIP"
        },
        "product_info": {
            "name": "无线鼠标",
            "price": 89.9
        },
        "normal_text": "这是一段普通文本",
        "html_content": "<div>测试div标签</div>",
        "json_data": '{"key": "value", "number": 123}'
    }
    return render_template("var_advanced.html", **context)

@app.route("/squares")
def page1(request):
    return render_template("squares.tpl", template_engine=UTemplateEngine())

@app.route("/squares_compiled")
def page1(request):
    return render_template("squares.tpl", template_engine=UTemplateEngine(loader_type="compiled"))

@app.route("/include_args")
def page1(request):
    return render_template("include_args.tpl", template_engine=UTemplateEngine())

@app.route('/path/<path:a>')
def r(request):
    dic={}
    for a,b in request.view_args.items():
        dic[a]=b
    for a,b in request.args.items():
        dic[a]=b
    html_content = render_template('index.html',dic)
    return html_content

@app.route("/squares/b/<int:n>")
def show_squares_n(request):
    """动态参数版本"""
    # 可以创建动态模板内容
    n = request.view_args.get('n')
    n = request.args.get('n') if 'n' in request.args else n
    dynamic_template = f"""
    = Table of Squares (1-{n}) =
    {{% include "squares.tpl" {n} %}}
    ====================
    """
    
    #这里无效，因为UTemplateEngine()未适配render_template_string()
    return render_template_string(dynamic_template,template_engine=UTemplateEngine())

@app.route("/squares/a/<int:n>")
def show_squares_n(request):
    """动态参数版本"""
    # 可以创建动态模板内容
    n = request.view_args.get('n')
    n = request.args.get('n') if 'n' in request.args and bool(re.match(r'^\s*[-+]?\d+\s*$',n)) else n
    dynamic_template = """
    = Table of Squares (1-{{n}}) =
    {{n**2}}
    ====================
    """
    
    # 使用render_template_string方法
    # 使用默认渲染引擎就可以
    return render_template_string(dynamic_template,{'n':n})

@app.route("/test/simple")
def simple(request):
    return render_template("simple.tpl",template_engine=UTemplateEngine(),message=str(time.ticks_ms()))

@app.route("/test/greeting")
def greeting(request):
    return render_template("greeting.tpl",template_engine=UTemplateEngine())

@app.route("/test/include")
def test_include(request):
    """测试include功能的主入口"""
    
    context = {
        "title": "UTemplate Include功能测试",
        "show_squares": True,
        "n": 7,  # 传递给squares.tpl的参数
        "time": time  # 传递time模块用于格式化时间
    }
    
    return render_template("include_test.tpl",template_engine=UTemplateEngine(loader_type="recompiled"),**context)

@app.route("/form", methods=["POST"])
def form(request):
    return request.form.get("b")
@app.route("/json", methods=["POST"])
def j(request):
    return request.json.get("a")
    
@app.route("/network/status")
def network_status(request):
    """获取详细网络状态"""
    try:
        status = {}
        
        # AP模式状态
        ap = network.WLAN(network.AP_IF)
        status['ap'] = {
            'active': ap.active(),
            'connected': ap.isconnected() if hasattr(ap, 'isconnected') else False,
            'ifconfig': ap.ifconfig() if ap.active() else None
        }
        
        # STA模式状态
        sta = network.WLAN(network.STA_IF)
        status['sta'] = {
            'active': sta.active(),
            'connected': sta.isconnected(),
            'ifconfig': sta.ifconfig() if sta.active() else None
        }
        
        return status
    except Exception as e:
        return {"error": str(e)}

@app.route("/network/config")
def network_config(request):
    """网络配置信息"""
    return {
        "ap_config": {
            "ssid": "某某饭店_5G",
            "ip": "192.168.4.1"
        },
        "sta_config": {
            "ssid": "wangtaohan"
        }
    }

# ========== API测试路由 ==========
@app.route("/api/hello")
def api_hello(request):
    """基础API测试"""
    return {
        "message": "Hello from MicroPython Server!",
        "timestamp": time.ticks_ms(),
        "status": "active"
    }

@app.route("/api/system")
def api_system(request):
    """系统信息API"""
    try:
        import gc
        
        return {
            "platform": sys.platform,
            "version": sys.version,
            "memory_free": gc.mem_free() if hasattr(gc, 'mem_free') else None,
            "memory_alloc": gc.mem_alloc() if hasattr(gc, 'mem_alloc') else None,
        }
    except Exception as e:
        return {"error": str(e)}

# ========== 传感器数据模拟 ==========
@app.route("/sensor/simulate")
def sensor_simulate(request):
    """模拟传感器数据"""
    import random
    
    sensors = {
        "temperature": round(20 + random.random() * 15, 2),  # 20-35°C
        "humidity": round(30 + random.random() * 50, 2),    # 30-80%
        "pressure": round(1000 + random.random() * 100, 2), # 1000-1100 hPa
        "light_level": random.randint(0, 1000),            # 0-1000 lux
        "timestamp": time.ticks_ms()
    }
    
    return sensors

@app.route("/data/live")
def data_live(request):
    """实时数据流（模拟）"""
    def generate():
        yield {"Content-Type": "text/plain; charset=utf-8"}
        for i in range(10):
            data = {
                "sequence": i + 1,
                "value": i * 10,
                "timestamp": time.ticks_ms()
            }
            yield json.dumps(data) + "\n"
            time.sleep(0.5)
    
    return Response(generate())

@app.route("/time/current")
def get_current_time(request):
    """返回当前时间戳的JSON API"""
    import time
    
    # 返回JSON格式的时间
    time_data = {
        "ticks_ms": time.ticks_ms(),
        "uptime": time.ticks_ms(),  # 运行时间
        "timestamp": time.time()  # 如果支持的话
    }
    
    return Response(
        json.dumps(time_data),
        content_type="application/json"
    )

@app.route("/time/dynamic")
def dynamic_time_page(request):
    """返回包含JavaScript的HTML页面，自动更新时间"""
    html = """
<!DOCTYPE html>
<html>
<head>
    <title>动态时间显示</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            text-align: center; 
            margin-top: 50px; 
        }
        .time-display { 
            font-size: 3em; 
            color: #333; 
            margin: 20px 0; 
        }
        .control-btn { 
            padding: 10px 20px; 
            font-size: 1em; 
            margin: 5px; 
            cursor: pointer; 
        }
    </style>
</head>
<body>
    <h1>MicroPython 动态时间</h1>
    <div class="time-display" id="timeDisplay">正在加载...</div>
    <div>
        <button class="control-btn" onclick="startUpdate()">开始更新</button>
        <button class="control-btn" onclick="stopUpdate()">停止更新</button>
        <button class="control-btn" onclick="changeInterval(100)">快速(100ms)</button>
        <button class="control-btn" onclick="changeInterval(1000)">慢速(1s)</button>
    </div>
    <div id="status">状态: 就绪</div>
    
    <script>
        let updateInterval = null;
        let currentInterval = 1000; // 默认1秒
        
        function updateTime() {
            fetch('/time/current')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('timeDisplay').innerHTML = 
                        'ticks_ms: ' + data.ticks_ms + ' ms';
                })
                .catch(error => {
                    document.getElementById('status').innerHTML = 
                        '状态: 获取失败 - ' + error;
                });
        }
        
        function startUpdate() {
            if (!updateInterval) {
                updateInterval = setInterval(updateTime, currentInterval);
                document.getElementById('status').innerHTML = 
                    '状态: 更新中 (' + currentInterval + 'ms间隔)';
                updateTime(); // 立即更新一次
            }
        }
        
        function stopUpdate() {
            if (updateInterval) {
                clearInterval(updateInterval);
                updateInterval = null;
                document.getElementById('status').innerHTML = '状态: 已停止';
            }
        }
        
        function changeInterval(interval) {
            currentInterval = interval;
            if (updateInterval) {
                // 如果正在更新，重启定时器
                stopUpdate();
                startUpdate();
            }
        }
        
        // 页面加载完成后自动开始
        window.onload = function() {
            startUpdate();
        };
    </script>
</body>
</html>
    """
    return Response(html, content_type="text/html; charset=utf-8")


# ========== 主函数 ==========
def main():
    """主函数"""
    print("启动MicroPython网络服务器...")
    print("=" * 50)
    
    # 创建静态文件
    
    # 设置AP模式
    ap = setup_ap('某某饭店_5G', '12345678', '192.168.4.1')
    time.sleep(2)
    
    # 设置STA模式
    sta = setup_sta("ssid", "pwd")
    
    print("=" * 50)
    print("服务器启动中...")
    
    # 显示访问信息
    if ap and ap.active():
        print("AP模式访问地址: http://192.168.4.1")
    if sta and sta.isconnected():
        sta_ip = sta.ifconfig()[0]
        print("STA模式访问地址: http://" + sta_ip)
    
    print("=" * 50)
    
    try:
        # 启动Web服务器
        app.run(host='0.0.0.0', port=80)
    except KeyboardInterrupt:
        print("\n正在停止服务器...")
        if ap:
            ap.active(False)
        print("服务器已安全停止")
    except Exception as e:
        print("运行错误: " + str(e))
        import sys
        sys.print_exception(e)
    finally:
        print("程序已退出")

if __name__ == '__main__':
    main()