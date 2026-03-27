"""
MicroFlask utemplate引擎演示
演示utemplate库的完整集成和使用
参考: https://github.com/pfalcon/utemplate
"""
#使用请检查
import time
import network


from microflask import Flask, Response, UTemplateEngine, render_template

# 创建Flask应用实例
app = Flask(__name__)

# 设置utemplate为默认模板引擎
try:
    utemplate_engine = UTemplateEngine(pkg=None, dir="demo_templates", loader_type="source")
    Response.set_default_template_engine(utemplate_engine)
    print("✓ UTemplate engine initialized successfully")
except:
    print("⚠ UTemplate not available, falling back to expression engine")
    from microflask_sync import ExpressionTemplateEngine
    Response.set_default_template_engine(ExpressionTemplateEngine())
#请检查squares.tpl是否存在于templates文件夹
@app.route("/squares")
def page1(request):
    return render_template("squares.tpl", template_engine=UTemplateEngine())

#请检查squares_tpl.py是否存在于templates文件夹
@app.route("/squares_compiled")
def page1(request):
    return render_template("squares.tpl", template_engine=UTemplateEngine(loader_type="compiled"))

#请检查include_args.tpl是否存在于templates文件夹
@app.route("/include_args")
def page1(request):
    return render_template("include_args.tpl", template_engine=UTemplateEngine())

@app.route("/test")
def test_complex_vars(request):
    m = request.args.get("m", "0")
    
    # 根据条件选择模板引擎
    if m == "1":
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
# ========== 主函数 ==========
def main():
    """主函数"""
    print("启动MicroPython网络服务器...")
    print("=" * 50)
    
    # 创建静态文件
    
    # 设置AP模式
    ap = setup_ap('AP', '12345678', '192.168.4.1')
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