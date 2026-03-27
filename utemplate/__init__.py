"""
uTemplate - 一个非常轻量级、内存高效、无依赖的模板引擎（编译为Python源码）。
适用于 MicroPython 和标准 CPython。

主要组件:
- source: 基于源码的模板加载与编译
- compiled: 基于预编译模板的加载
- recompile: 重新编译模板的工具
"""
# 公开主要的子模块，使其可以通过 `utemplate.source` 和 `utemplate.compiled` 访问
# 在MicroPython环境中，这种显式导入有助于确保模块被正确加载并建立模块命名空间。
import utemplate.source
import utemplate.compiled
# 通常`recompile`是内部工具，可根据需要决定是否公开
import utemplate.recompile

# 可选：将最常用的类或函数提升到包顶级，方便快速访问。
# 注意：在内存受限的mpy环境中，通常不建议这样做，以保持最小化导入。
# from utemplate.source import Loader, Compiler
# from utemplate.compiled import Loader as CompiledLoader

# 定义包的版本（可选，可从setup.py同步）
__version__ = "1.4.1"
__author__ = "Paul Sokolovsky"

# 清理命名空间，仅导出指定的名称（在MicroPython中通常非必需，但更规范）
# __all__ = ['source', 'compiled', '__version__', '__author__']