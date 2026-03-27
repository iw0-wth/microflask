# MicroPython兼容性报告

## 概述
本报告说明各个demo文件在MicroPython环境中的兼容性状态。

## ✅ 完全兼容的演示

### 核心演示
- **demo_index.py** - ✅ 完全兼容
- **demo_basic_functions.py** - ✅ 完全兼容
- **demo_template_rendering.py** - ✅ 完全兼容
- **demo_cookie_session.py** - ✅ 完全兼容
- **demo_json_api.py** - ✅ 完全兼容
- **demo_streaming.py** - ✅ 完全兼容
- **demo_utemplate.py** - ✅ 完全兼容
- **demo_dynamic_routing.py** - ✅ 完全兼容
- **demo_error_handling.py** - ✅ 完全兼容
- **demo_ncsi_spoofing.py** - ✅ 完全兼容


## ⚠️ CPython专用的演示

### 高级功能演示
- **demo_third_party_engines.py** - ⚠️ CPython专用，需要外部模板引擎库
- **demo_flask_migration.py** - ⚠️ 部分功能依赖CPython库

## 📋 MicroPython环境要求

### 必需模块
- `microflask.py` - 核心框架
- `microdns.py` - DNS服务器 (可选)
- `_thread` - 线程支持

### 可选模块  
- `json` - JSON处理 (MicroPython内置)
- `time` - 时间函数 (MicroPython内置)
- `socket` - 网络功能 (MicroPython内置)
- `re` - 正则表达式 (MicroPython内置)

## 🚀 MicroPython部署指南

### 1. 基础部署
```python
# 在MicroPython环境中运行单个演示
import demo_basic_functions
```


## 📊 功能限制说明

### MicroPython
1. **正则表达式**: 不支持高级量词如`{n,m}`
2. **模板引擎**: 无法使用Jinja2等第三方引擎
3. **线程**: 线程支持有限，建议单线程运行
4. **内存**: 内存限制较大，适合简单演示

### CPython
1. **高级模板引擎**: Jinja2、Mako、Cheetah等(自己适配)
2. **复杂路由**: 需要高级正则表达式的路由
3. **多线程**: 复杂的并发处理
4. **Flask迁移**: 无法使用某些Flask特有功能

## 🎯 推荐使用场景

### MicroPython环境 (ESP32、ESP8266等)
- `demo_basic_functions.py` - 基础路由和响应
- `demo_template_rendering.py` - 简单模板渲染
- `demo_cookie_session.py` - 会话管理
- `demo_json_api.py` - JSON API
- `demo_utemplate.py` - 轻量级模板引擎
- `demo_ncsi_spoofing.py` - 简化NCSI功能
- 推荐参考`demo_flask_migration.py`进行项目迁移

### CPython环境 (PC、服务器)
- 所有演示都支持
- 推荐使用`demo_third_party_engines.py`体验高级功能
- 推荐参考`demo_flask_migration.py`进行项目迁移

## 🔧 故障排除

### 常见问题
1. **内存不足**: 重启设备，适当使用gc
2. **模块导入失败**: 确保MicroFlask核心文件在路径中
3. **正则表达式错误**: 检查是否使用了MicroPython不支持的语法


---

*最后更新: 2026-02-26*  
