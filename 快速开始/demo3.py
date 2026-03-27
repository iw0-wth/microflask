#本demo演示注册自定义路由

import gc,time
gc.collect()
import network
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
ap = setup_ap('某某饭店_5G', '12345678', '192.168.4.1')
sta = setup_sta("ssid", "pwd")












from microflask import*


#一般式
class EvenNumberConverter(BaseConverter):
    regex = r'[02468]'  # 简化，只匹配一位偶数
    
    def to_python(self, value):
        return int(value)

#传参式
class CustomConverter(BaseConverter):
    regex = '\d\d\d\d-\d\d-\d\d'
    def __init__(self, map, arg):
        super().__init__(map)
        self.arg = arg
        print(f"初始化转换器，参数值: {self.arg}")

    def to_python(self, value):
        print(f"value={value}, 传入参数={self.arg}")
        return value


# 判断函数式
def is_valid_date(value):
    """验证日期格式是否为 YYYY-MM-DD"""
    parts = value.split('-')
    return len(parts) == 3 and all(part.isdigit() for part in parts)
class BoolValidatorConverter(BaseConverter):
    def to_python(self, value):
        # 调用验证函数判断
        if not is_valid_date(value):
            raise ValueError("日期格式无效")
        return value  # 返回原始值
app = Flask()
# 注册自定义转换器
app.url_map.converters['even'] = EvenNumberConverter
app.url_map.converters['bool_valid'] = BoolValidatorConverter
app.url_map.converters['a'] = CustomConverter


@app.route("/")
def index(req):
    return render_template_string("{{a}}",a=1)
@app.route("/<int:a>")
def a(req):
    a=req.view_args.get("a")
    return render_template_string("{{a}}",a=a)
@app.route("/user/<int:user_id>")
def show_user(req):
    return f'User ID: {req.view_args["user_id"]}'
@app.route('/static/<path:filename>')
def static_file(req):
    return f'File: {req.view_args["filename"]}'
@app.route('/even/<even:num>')
def even_number(req):
        return f'Even number: {req.view_args["num"]}'
@app.route('/<a(1):a>/<path:b>')
def test_route(req):
    return f'a: {req.view_args["a"]}, b: {req.view_args["b"]}'
@app.route('/re/<re(r"\d\d\d\d-\d\d-\d\d"):date>/<part:slug>')
def blog_post(req):
    return f'Date: {req.view_args["date"]}, Slug: {req.view_args["slug"]}'
@app.route('/time/<bool_valid:date>')
def date_route(req):
    return f"有效日期: {req.view_args['date']}"
app.run()






