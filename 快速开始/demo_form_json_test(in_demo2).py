# -*- coding: utf-8 -*-
"""
Created on Sat Feb  7 02:00:55 2026

@author: wth090714
"""

import requests

# 配置服务器地址（根据实际情况修改）
BASE_URL = "http://192.168.2.24"  # 替换为实际地址

def test_form_endpoint():
    """测试表单数据处理端点 /form"""
    url = f"{BASE_URL}/form"
    form_data = {"b": "form_test_value"}  # 表单数据
    
    try:
        response = requests.post(url, data=form_data)
        print(f"测试 /form 端点 [状态码: {response.status_code}]")
        print(f"响应内容: {response.text}\n")
    except Exception as e:
        print(f"/form 测试失败: {str(e)}")

def test_json_endpoint():
    """测试JSON数据处理端点 /json"""
    url = f"{BASE_URL}/json"
    json_data = {"a": "json_test_value"}  # JSON数据
    
    try:
        response = requests.post(url, json=json_data)
        print(f"测试 /json 端点 [状态码: {response.status_code}]")
        print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"/json 测试失败: {str(e)}")

if __name__ == "__main__":
    test_form_endpoint()  # 测试表单端点
    test_json_endpoint()  # 测试JSON端点