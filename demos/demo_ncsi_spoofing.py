#!/usr/bin/env python3
"""
NCSI欺骗演示
仅使用 /ncsi.txt 和 /connecttest.txt 两个路由
启动DNS服务器线程模拟网络连接检查
"""
from microflask import*
import network
import socket
import time
from machine import Pin
import gc
import _thread
from microdns import DNSServer

gc.enable()
wlan = network.WLAN(network.STA_IF)
wlan.active(False) # 先禁用接口
wlan.active(True)

app = Flask(__name__)

@app.route('/')
def index(request):
    dic={"None":"None"} if len(request.args)==0 else request.args
    html_content = render_template('index.html')
    print(f'[web]GET:{str(dic)}')
    return html_content

@app.route('/ncsi.txt')
def r(request):
    print('[web]NCSI')
    return "Microsoft NCSI"

@app.route('/connecttest.txt')
def r(request):
    print('[web]NCSI')
    return "Microsoft Connect Test"

# 配置AP模式
def setup_ap(ssid,pwd,ip):
    """设置ESP32为AP模式"""
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=str(ssid), password=str(pwd), authmode=network.AUTH_WPA_WPA2_PSK)
    
    # 设置静态IP
    ap.ifconfig((str(ip), '255.255.255.0', '192.168.4.1', '8.8.8.8'))
    
    print("AP模式已启动")
    print(f"SSID: {str(ssid)}")
    print(f"密码: {str(pwd)}")
    print(f"IP地址: {ap.ifconfig()[0]}")
    
    return ap

def start_dns_server():
    """启动DNS服务器"""
    dns_server = DNSServer()
    dns_server.start()


def main():
    """主函数"""
    print("启动服务器...")
    ap = setup_ap('AP','12345678','192.168.4.1')
    time.sleep(2)
    
    
    try:
        _thread.start_new_thread(start_dns_server, ())
        app.run(host='0.0.0.0', port=80)
    except KeyboardInterrupt:
        print("正在停止服务器...")
        ap.active(False)
        print("服务器已停止")
    except Exception as e:
        print(f"运行错误: {e}")
        import sys
        sys.print_exception(e)
    finally:
        print("程序已退出")

if __name__ == '__main__':
    main()