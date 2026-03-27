# -*- coding: utf-8 -*-
"""
Created on Sat Feb  7 22:30:54 2026

@author: wth090714
"""

# test_client.py
# 用于测试流式和Cookie的客户端

import requests,sys
import time
import json
from threading import Thread

def test_cookie():
    """测试Cookie功能"""
    print("🍪 测试Cookie功能...")
    
    session = requests.Session()
    
    # 设置Cookie
    print("1. 设置Cookie...")
    resp = session.get("http://192.168.2.24/set_cookie")
    print(f"   状态码: {resp.status_code}")
    
    # 读取Cookie
    print("\n2. 读取Cookie...")
    resp = session.get("http://192.168.2.24/get_cookie")
    print(f"   状态码: {resp.status_code}")
    print(f"   响应: {resp.text[:200]}...")
    
    # 计数器测试
    print("\n3. 测试Cookie计数器...")
    for i in range(3):
        resp = session.get("http://192.168.2.24/cookie_counter")
        print(f"   第{i+1}次访问: {resp.status_code}")
    
    print("✅ Cookie测试完成\n")

def test_stream():
    """测试流式响应"""
    print("🌊 测试流式响应...")
    
    try:
        print("1. 测试基本流式文本...")
        resp = requests.get("http://192.168.2.24/stream", stream=True)
        print(f"   状态码: {resp.status_code}")
        print(f"   响应头: {resp.headers}")
        
        print("   接收数据:")
        for chunk in resp.iter_content(chunk_size=None, decode_unicode=True):
            if chunk:
                print(f"   → {chunk.strip()}")
        
        print("\n2. 测试SSE流...")
        resp = requests.get("http://192.168.2.24/stream_sse", stream=True)
        
        print("   接收SSE事件:")
        for line in resp.iter_lines():
            if line:
                print(f"   → {line.decode('utf-8')}")
        
        print("✅ 流式测试完成\n")
        
    except Exception as e:
        print(f"❌ 流式测试失败: {e}")

def test_api():
    """测试API端点"""
    print("🔧 测试API端点...")
    
    try:
        # 普通API
        resp = requests.get("http://192.168.2.24/api/data")
        print(f"1. API响应: {resp.status_code}")
        data = resp.json()
        print(f"   数据: {json.dumps(data, indent=2)}")
        
        # 流式API
        print("\n2. 测试流式API...")
        resp = requests.get("http://192.168.2.24/api/stream_data", stream=True)
        
        print("   接收流式JSON:")
        full_data = ""
        for chunk in resp.iter_content(chunk_size=None):
            if chunk:
                print(f"   → {chunk.decode('utf-8').strip()}")
                full_data += chunk.decode('utf-8')
        
        try:
            parsed = json.loads(full_data)
            print(f"   解析成功，数据条数: {len(parsed.get('data', []))}")
        except:
            print("   解析失败")
        
        print("✅ API测试完成\n")
        
    except Exception as e:
        print(f"❌ API测试失败: {e}")

def test_chat():
    """测试聊天流式响应"""
    print("💬 测试聊天流式...")
    
    try:
        resp = requests.get("http://192.168.2.24/chat_stream", stream=True)
        print(f"   状态码: {resp.status_code}")
        print(f"   Cookie: {resp.cookies}")
        
        print("   接收聊天消息:")
        for line in resp.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data:'):
                    try:
                        data = json.loads(line_str[5:].strip())
                        print(f"   💬 {data.get('message')}")
                    except:
                        print(f"   📦 {line_str}")
        
        print("✅ 聊天测试完成\n")
        
    except Exception as e:
        print(f"❌ 聊天测试失败: {e}")

def test_concurrent():
    """测试并发请求"""
    print("⚡ 测试并发请求...")
    
    def make_request(url, name):
        try:
            resp = requests.get(url, timeout=10)
            print(f"   {name}: {resp.status_code}")
        except Exception as e:
            print(f"   {name}: 失败 - {e}")
    
    urls = [
        ("http://192.168.2.24/", "首页"),
        ("http://192.168.2.24/stream", "流式"),
        ("http://192.168.2.24/get_cookie", "Cookie"),
        ("http://192.168.2.24/api/data", "API"),
    ]
    
    threads = []
    for url, name in urls:
        t = Thread(target=make_request, args=(url, name))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    print("✅ 并发测试完成\n")

if __name__ == "__main__":
    print("🚀 开始测试流式与Cookie框架...")
    print("=" * 50)
    
    # 检查服务器是否运行
    try:
        resp = requests.get("http://192.168.2.24/", timeout=10)
        print(f"✅ 服务器运行正常: {resp.status_code}")
    except:
        print("❌ 服务器未运行，请先启动服务器")
        print("   运行: python test_stream_cookie.py")
        sys.exit(0)
    
    # 运行测试
    test_cookie()
    test_stream()
    test_api()
    test_chat()
    test_concurrent()
    
    print("🎉 所有测试完成！")
    print("=" * 50)
    print("访问 http://192.168.2.24 查看完整测试页面")