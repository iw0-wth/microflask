#Author : iw0雨渊(Gitee:@wth_iw0 GitHub:@iw0_wth)
#Date : 2025.8.8
#Description : Basic HTTP GET Request Demo using MicroFlask
#Copyright © 2025 iw0雨渊. All rights reserved.
#Version : 1.0.0
#License : MIT License
#Contact : EMAIL
#Contact : tianqi2021_001@163.com
#Github : https://github.com/iw0-wth

"""
MicroFlask Web Framework - Basic GET Request Demo
This demo demonstrates basic GET request handling with MicroFlask.
Compatible with both MicroPython and CPython environments.

This project uses micropython-easyweb as reference: https://github.com/funnygeeker/micropython-easyweb
This project integrates utemplate as third-party engine: https://github.com/pfalcon/utemplate/
"""

import gc
import time
import sys

# Try to import network module for MicroPython
try:
    import network
except ImportError:
    print("Warning: network module not available, network features will be disabled")

# Import MicroFlask framework
from microflask import Flask, Response

# Create Flask application
app = Flask(__name__)

# Network configuration functions
def setup_ap(ssid, pwd, ip):
    """Setup ESP32 in AP mode"""
    try:
        ap = network.WLAN(network.AP_IF)
        ap.active(True)
        ap.config(essid=str(ssid), authmode=network.AUTH_WPA_WPA2_PSK, password=str(pwd))
        ap.ifconfig((str(ip), '255.255.255.0', str(ip), '8.8.8.8'))
        
        print("AP mode started")
        print(f"SSID: {str(ssid)}")
        print(f"Password: {str(pwd)}")
        print(f"IP Address: {ap.ifconfig()[0]}")
        
        return ap
    except Exception as e:
        print(f"AP setup failed: {str(e)}")
        return None

def setup_sta(ssid, pwd):
    """Setup ESP32 in STA mode"""
    try:
        sta = network.WLAN(network.STA_IF)
        sta.active(True)
        if not sta.isconnected():
            print(f"Connecting to WiFi: {str(ssid)}")
            sta.connect(str(ssid), str(pwd))
            
            # Wait for connection, max 30 seconds
            for i in range(30):
                if sta.isconnected():
                    break
                time.sleep(1)
                print(".", end='')
            print()
        
        if sta.isconnected():
            print("WiFi connected successfully!")
            print(f"IP Address: {sta.ifconfig()[0]}")
        else:
            print("WiFi connection failed!")
        
        return sta
    except Exception as e:
        print(f"STA setup failed: {str(e)}")
        return None

# Basic routes for demonstrating different GET request scenarios

@app.route("/")
def index(request):
    """Homepage - Welcome message and basic info"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MicroFlask Basic Demo</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .demo-section { margin: 30px 0; padding: 20px; border-left: 4px solid #007acc; background: #f9f9f9; }
            .demo-list { list-style: none; padding: 0; }
            .demo-list li { margin: 10px 0; }
            .demo-list a { 
                display: inline-block; 
                padding: 8px 15px; 
                background: #007acc; 
                color: white; 
                text-decoration: none; 
                border-radius: 4px; 
            }
            .demo-list a:hover { background: #005999; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌟 MicroFlask Basic GET Demo</h1>
            <p>This demo showcases basic HTTP GET request handling with MicroFlask framework.</p>
            
            <div class="demo-section">
                <h2>📋 Available Routes</h2>
                <ul class="demo-list">
                    <li><a href="/hello">Simple Hello</a></li>
                    <li><a href="/time">Current Time</a></li>
                    <li><a href="/info">System Info</a></li>
                    <li><a href="/query?name=John&age=25">Query Parameters</a></li>
                    <li><a href="/json">JSON Response</a></li>
                </ul>
            </div>
            
            <div class="demo-section">
                <h2>🔧 Test Commands</h2>
                <p>Use curl to test endpoints:</p>
                <pre>
curl http://192.168.4.1/hello
curl http://192.168.4.1/query?name=Alice&age=30
curl -H "Accept: application/json" http://192.168.4.1/json
                </pre>
            </div>
        </div>
    </body>
    </html>
    """
    return Response(html, content_type="text/html; charset=utf-8")

@app.route("/hello")
def hello(request):
    """Simple hello endpoint"""
    return "Hello from MicroFlask! 🎉"

@app.route("/time")
def current_time(request):
    """Return current timestamp"""
    current_ms = time.ticks_ms()
    return f"Current time: {current_ms} ms"

@app.route("/info")
def system_info(request):
    """Basic system information"""
    info = {
        "platform": sys.platform,
        "implementation": sys.implementation.name if hasattr(sys.implementation, 'name') else 'unknown',
        "free_memory": gc.mem_free() if hasattr(gc, 'mem_free') else 'N/A',
        "allocated_memory": gc.mem_alloc() if hasattr(gc, 'mem_alloc') else 'N/A',
        "uptime_ms": time.ticks_ms()
    }
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>System Info</title>
        <meta charset="utf-8">
    </head>
    <body>
        <h1>System Information</h1>
        <ul>
            <li><strong>Platform:</strong> {info['platform']}</li>
            <li><strong>Implementation:</strong> {info['implementation']}</li>
            <li><strong>Free Memory:</strong> {info['free_memory']}</li>
            <li><strong>Allocated Memory:</strong> {info['allocated_memory']}</li>
            <li><strong>Uptime:</strong> {info['uptime_ms']} ms</li>
        </ul>
        <p><a href="/">← Back to Home</a></p>
    </body>
    </html>
    """
    return Response(html, content_type="text/html; charset=utf-8")

@app.route("/query")
def query_params(request):
    """Demonstrate query parameter handling"""
    name = request.args.get("name", "Anonymous")
    age = request.args.get("age", "Unknown")
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Query Parameters</title>
        <meta charset="utf-8">
    </head>
    <body>
        <h1>Query Parameters Demo</h1>
        <p><strong>Name:</strong> {name}</p>
        <p><strong>Age:</strong> {age}</p>
        <p><strong>All Parameters:</strong> {dict(request.args)}</p>
        
        <h3>Try different parameters:</h3>
        <ul>
            <li><a href="/query?name=Alice&age=25">Alice, 25</a></li>
            <li><a href="/query?name=Bob&age=30&city=Beijing">Bob, 30, Beijing</a></li>
            <li><a href="/query">No parameters</a></li>
        </ul>
        
        <p><a href="/">← Back to Home</a></p>
    </body>
    </html>
    """
    return Response(html, content_type="text/html; charset=utf-8")

@app.route("/json")
def json_response(request):
    """JSON response example"""
    data = {
        "message": "This is a JSON response from MicroFlask",
        "timestamp": time.ticks_ms(),
        "status": "success",
        "framework": "MicroFlask",
        "version": "1.0.0"
    }
    
    # Return JSON based on Accept header
    accept_header = request.headers.get("Accept", "")
    if "application/json" in accept_header:
        return Response(data, content_type="application/json")
    else:
        # HTML with formatted JSON
        import json
        json_str = json.dumps(data, indent=2)
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>JSON Response</title>
            <meta charset="utf-8">
            <style>
                pre {{ background: #f4f4f4; padding: 15px; border-radius: 4px; }}
            </style>
        </head>
        <body>
            <h1>JSON Response Demo</h1>
            <p>This endpoint returns JSON data. To get raw JSON, use curl with appropriate headers:</p>
            <pre>curl -H "Accept: application/json" {request.url}</pre>
            
            <h3>Response Data:</h3>
            <pre>{json_str}</pre>
            
            <p><a href="/">← Back to Home</a></p>
        </body>
        </html>
        """
        return Response(html, content_type="text/html; charset=utf-8")

def main():
    """Main function"""
    print("🚀 Starting MicroFlask Basic GET Demo...")
    print("=" * 50)
    
    # Setup network (optional - for testing without network)
    try:
        # AP mode setup
        ap = setup_ap('MicroFlaskDemo', '12345678', '192.168.4.1')
        time.sleep(2)
        
        # STA mode setup (optional)
        # sta = setup_sta("YourWiFi", "YourPassword")
        
        print("=" * 50)
        print("Server starting...")
        
        # Show access information
        if ap and ap.active():
            print("AP Mode Access: http://192.168.4.1")
        
        print("=" * 50)
        print("🎯 Demo Features:")
        print("  ✅ Basic GET requests")
        print("  ✅ Query parameter handling")
        print("  ✅ JSON responses")
        print("  ✅ HTML templating")
        print("  ✅ Request logging")
        print("=" * 50)
        
        # Start server with debug mode
        app.run(host='0.0.0.0', port=80, debug=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping server...")
        if 'ap' in locals() and ap:
            ap.active(False)
        print("Server stopped gracefully")
    except Exception as e:
        print(f"❌ Runtime error: {str(e)}")
        if 'ap' in locals() and ap:
            ap.active(False)
    finally:
        print("🏁 Demo ended")

if __name__ == '__main__':
    main()