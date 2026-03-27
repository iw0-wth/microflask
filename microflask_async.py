#Author : iw0雨渊(Gitee:@wth_iw0 GitHub:@iw0_wth)
#Date : 2026.3.21
#Description : MicroFlask_async is a Flask-like async web framework engineered to streamline the migration of Flask-based projects.
#Copyright © 2026 iw0雨渊. All rights reserved.
#Version : 0.0.20260321
#License : MIT License
#Contact : EMAIL:tianqi2021_001@163.com
#Github : https://github.com/iw0-wth
__version__ = '0.0.20260321'

"""
MicroFlask Async Web Framework
异步版的MicroFlask，可在mpy,py双环境运行，支持自定义动态路由规则

This project uses micropython-easyweb as reference: https://github.com/funnygeeker/micropython-easyweb
This project integrates utemplate as third-party engine: https://github.com/pfalcon/utemplate/
"""
import os
import re
import sys
import binascii
try:
    from utemplate import source, compiled, recompile
    UTEMPLATE_AVAILABLE = True
except ImportError:
    UTEMPLATE_AVAILABLE = False

try:
    import ujson as json  # MicroPython
except Exception:  # pragma: no cover
    import json  # type: ignore

try:
    import uasyncio as asyncio  # MicroPython
except Exception:  # pragma: no cover
    import asyncio  # type: ignore





STRICT_MODE = True








#兼容函数
def _schedule(func, arg):
    """兼容 micropython.schedule；在 CPython 下直接调用。"""
    if micropython is not None and hasattr(micropython, "schedule"):
        micropython.schedule(func, arg)
    else:  # pragma: no cover
        func(arg)


def groups(match):
    i = 1
    return_tuple = tuple()
    while True:
        try:
            return_tuple += (match.group(i),)
            i += 1
        except Exception:
            break
    return return_tuple


def escape(text):
    """替代 re.escape 的手动实现"""
    special_chars = r"\^$*+?.()|{}[]"
    return "".join(["\\" + char if char in special_chars else char for char in text])


class ImmutableMultiDict(dict):
    """兼容低版本mpy"""
    def get(self, key, default=None):
        if key in self:
            return super().get(key)
        return default







#外置的可扩展的渲染引擎
class TemplateEngine:
    """模板引擎基类，定义统一的渲染接口"""    
    def render(self, template_content: str, context: dict) -> str:
        """
        渲染模板的核心方法
        Args:
            template_content: 模板内容字符串
            context: 上下文变量字典
            
        Returns:
            渲染后的字符串
        """
        raise NotImplementedError("子类必须实现此方法")
    
    def render_file(self, template_path: str, context: dict) -> str:
        """
        从文件渲染模板的便捷方法
        
        Args:
            template_path: 模板文件路径
            context: 上下文变量字典
            
        Returns:
            渲染后的字符串
        """
        try:
            # 尝试从templates目录读取
            with open(f"templates/{template_path}", "rb") as f:
                content = f.read().decode("utf-8")
        except OSError:
            # 尝试直接路径读取
            with open(template_path, "rb") as f:
                content = f.read().decode("utf-8")
        
        return self.render(content, context)

class ExpressionTemplateEngine(TemplateEngine):
    """支持表达式求值的模板引擎"""
    
    def render(self, template_content: str, context: dict) -> str:
        def eval_expression(match):
            expression = match.group(1).strip()
            try:
                env = globals()
                env.update(context)
                result = eval(expression, {"__builtins__": {}}, env)
                return str(result)
            except Exception:
                # 求值失败时返回原表达式
                return match.group(0)
        
        # 使用正则替换所有 {{ 表达式 }}
        return re.sub(r'{{\s*(.*?)\s*}}', eval_expression, template_content)

class SimpleTemplateEngine(TemplateEngine):
    """简单字符串替换的模板引擎"""
    
    def render(self, template_content: str, context: dict) -> str:
        """使用字符串替换方式渲染模板"""
        result = template_content
        
        for key, value in context.items():
            placeholder = "{{ %s }}" % key
            result = result.replace(placeholder, str(value))
        
        return result

class ThirdPartyTemplateAdapter(TemplateEngine):
    """第三方模板引擎适配器模板"""
    
    def __init__(self, engine_instance, render_method_name="render"):
        """
        初始化适配器
        Args:
            engine_instance: 第三方模板引擎实例
            render_method_name: 渲染方法名，默认为'render'
        """
        self.engine = engine_instance
        self.render_method = getattr(engine_instance, render_method_name)
    
    def render(self, template_content: str, context: dict) -> str:
        """调用第三方引擎的渲染方法"""
        return self.render_method(template_content, **context)
    
    def render_file(self, template_path: str, context: dict) -> str:
        """重写文件渲染方法以适配第三方引擎的文件加载方式"""
        # 某些第三方引擎可能自带文件加载逻辑
        if hasattr(self.engine, 'render_file'):
            return self.engine.render_file(template_path, **context)
        # 否则使用基类的默认实现
        return super().render_file(template_path, context)

def create_template_adapter(render_func, file_render_func=None):
    """创建函数式模板引擎适配器"""
    
    class FunctionalTemplateEngine(TemplateEngine):
        def render(self, template_content: str, context: dict) -> str:
            return render_func(template_content, **context)
        
        def render_file(self, template_path: str, context: dict) -> str:
            if file_render_func:
                return file_render_func(template_path, **context)
            # 回退到默认文件加载+渲染
            with open(template_path, "r", encoding="utf-8") as f:
                content = f.read()
            return render_func(content, **context)
    
    return FunctionalTemplateEngine()

class UTemplateEngine(TemplateEngine):
    """utemplate模板引擎适配器"""
    
    def __init__(self, pkg=None, dir="templates", loader_type="source", auto_recompile=True):
        """
        初始化utemplate引擎
        
        Args:
            pkg: 包名，通常为__name__
            dir: 模板目录
            loader_type: 加载器类型，可选"source"、"compiled"、"recompile"
            auto_recompile: 是否自动重新编译（仅对recompile有效）
        """
        if not UTEMPLATE_AVAILABLE:
            raise ImportError("utemplate is not installed. ")  
        self.pkg = pkg
        self.dir = dir
        #由于mpy导入从根目录开始，会导致模板文件导入失败，遂加入相对目录
        if self.dir not in sys.path:
            sys.path.append(self.dir)
        # 根据loader_type创建相应的加载器
        if loader_type == "compiled":
            self.loader = compiled.Loader(pkg, dir)
        elif loader_type == "recompile":
            self.loader = recompile.Loader(pkg, dir)
        else:  # source是默认的
            self.loader = source.Loader(pkg, dir)
        
        # 缓存已加载的模板函数
        self._template_cache = {}
    
    def _get_template(self, template_name):
        """获取模板函数，支持缓存"""
        # 移除扩展名中的点，用下划线替换
        cache_key = template_name.replace(".", "_")
        
        if cache_key not in self._template_cache:
            # 从加载器获取模板函数
            render_func = self.loader.load(template_name)
            self._template_cache[cache_key] = render_func
        
        return self._template_cache[cache_key]
    
    def render(self, template_content: str, context: dict) -> str:
        """
        渲染模板内容字符串
        
        注意：utemplate主要设计用于文件模板，这里提供一个基本实现
        但utemplate的优势在于编译文件模板，所以这个方法可能不是最优的
        """
        # 由于utemplate主要设计用于文件模板，对于字符串渲染我们使用简单的回退方案
        result = template_content
        
        # 简单的变量替换
        for key, value in context.items():
            placeholder = "{{ " + str(key) + " }}"
            result = result.replace(placeholder, str(value))
        
        return result
    
    def render_file(self, template_path: str, context: dict) -> str:
        """
        从文件渲染模板 - 这是utemplate的主要使用方式
        """
        # 获取模板函数
        render_func = self._get_template(template_path)
        
        try:
            # 调用模板函数，它会返回一个生成器
            generator = render_func(**context)
            
            # 从生成器收集所有片段
            parts = []
            for chunk in generator:
                if chunk is not None:
                    parts.append(str(chunk))
            
            return "".join(parts)
            
        except Exception as e:
            # 如果渲染出错，提供详细错误信息
            error_msg = f"UTemplate渲染错误: {e}\n"
            error_msg += f"模板: {template_path}\n"
            error_msg += f"上下文键: {list(context.keys())}"
            raise RuntimeError(error_msg) from e
    
    def clear_cache(self):
        """清除模板缓存"""
        self._template_cache.clear()




















#外置的可扩展的动态路由规则
class BaseConverter:
    """路由转换器基类，模仿 Flask 的 werkzeug.routing.BaseConverter"""
    
    # 转换器匹配变量时使用的正则表达式部分
    # 子类可以覆盖这个属性
    regex = "[^/]+"
    
    # 转换器在URL中可接受的参数（例如 <int:num> 中的 “int” 就是名字，没有参数）
    # 对于 <re(r"\d+"):var>，名字是“re”，参数是 (r"\d+",)
    def __init__(self, map, *args, **kwargs):
        """
        Args:
            map: 保留参数，为了与Flask API兼容，这里传入的是 url_map
            *args: 来自路由定义中括号内的参数，如 <re(r"\d+"):id> 中的 r"\d+"
        """
        self.map = map
        self.args = args
        self.kwargs = kwargs
    
    def to_python(self, value: str):
        """
        将URL中的字符串值转换为Python对象（传递给视图函数）。
        默认返回字符串，子类可覆盖以进行类型转换。
        """
        return value
    
    def to_url(self, value) -> str:
        """
        将Python对象转换回URL中的字符串。
        默认使用 str()，子类可覆盖。
        """
        return str(value)


# ---------------- 默认转换器定义 ----------------
class StringConverter(BaseConverter):
    """字符串转换器，默认类型"""
    pass  # 使用基类的 regex 和 to_python


class IntConverter(BaseConverter):
    """整数转换器"""
    regex = r"[-+]?\d+"
    if STRICT_MODE:
        regex = r"-?\d+"
    
    def to_python(self, value: str):
        return int(value)


class FloatConverter(BaseConverter):
    """浮点数转换器"""
    regex = r"[-+]?\d+\.\d+|[+-]?\d+"
    if STRICT_MODE:
        regex = r"-?\d+\.\d+"
    
    def to_python(self, value: str):
        return float(value)


class PathConverter(BaseConverter):
    """路径转换器，匹配包括斜杠的剩余部分"""
    regex = ".+"
    
    def to_python(self, value: str):
        return value


class PartConverter(BaseConverter):
    """part 转换器，匹配非空路径段，但不包括斜杠"""
    regex = ".+?"


class ReConverter(BaseConverter):    
    def __init__(self, map, reg):
        super().__init__(map)
        self.regex = reg 
        


class BoolConverter(BaseConverter):
    """bool转换器"""
    regex = r"[tT][rR][uU][eE]|[fF][aA][lL][sS][eE]|[yY][eE][sS]|[nN][oO]|1|0"
    if STRICT_MODE:
        regex = r"[tT]rue|[fF]alse|[yY]es|[nN]o|1|0"
    
    def to_python(self, value: str):
        return str(value).lower() in ("true", "1", "yes")















#对照列表
FILE_TYPE = ImmutableMultiDict(
    {
        ".txt": "text/plain",
        ".htm": "text/html",
        ".html": "text/html",
        ".css": "text/css",
        ".csv": "text/csv",
        ".js": "application/javascript",
        ".xml": "application/xml",
        ".xhtml": "application/xhtml+xml",
        ".json": "application/json",
        ".zip": "application/zip",
        ".pdf": "application/pdf",
        ".ts": "application/typescript",
        ".woff": "font/woff",
        ".woff2": "font/woff2",
        ".ttf": "font/ttf",
        ".otf": "font/otf",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".svg": "image/svg+xml",
        ".ico": "image/x-icon",
    }
)


STATUS_CODE = ImmutableMultiDict(
    {
        100: "Continue",
        101: "Switching Protocols",
        102: "Processing",
        200: "OK",
        201: "Created",
        202: "Accepted",
        203: "Non-Authoritative Information",
        204: "No Content",
        205: "Reset Content",
        206: "Partial Content",
        207: "Multi-Status",
        208: "Already Reported",
        226: "IM Used",
        300: "Multiple Choices",
        301: "Moved Permanently",
        302: "Found",
        303: "See Other",
        304: "Not Modified",
        305: "Use Proxy",
        307: "Temporary Redirect",
        308: "Permanent Redirect",
        400: "Bad Request",
        401: "Unauthorized",
        402: "Payment Required",
        403: "Forbidden",
        404: "Not Found",
        405: "Method Not Allowed",
        406: "Not Acceptable",
        407: "Proxy Authentication Required",
        408: "Request Timeout",
        409: "Conflict",
        410: "Gone",
        411: "Length Required",
        412: "Precondition Failed",
        413: "Payload Too Large",
        414: "URI Too Long",
        415: "Unsupported Media Type",
        416: "Range Not Satisfiable",
        417: "Expectation Failed",
        418: "I'm a teapot",
        422: "Unprocessable Entity",
        423: "Locked",
        424: "Failed Dependency",
        426: "Upgrade Required",
        428: "Precondition Required",
        429: "Too Many Requests",
        431: "Request Header Fields Too Large",
        451: "Unavailable For Legal Reasons",
        500: "Internal Server Error",
        501: "Not Implemented",
        502: "Bad Gateway",
        503: "Service Unavailable",
        504: "Gateway Timeout",
        505: "HTTP Version Not Supported",
        506: "Variant Also Negotiates",
        507: "Insufficient Storage",
        508: "Loop Detected",
        510: "Not Extended",
        511: "Network Authentication Required",
    }
)


# ========= URL 编码/解码（照搬 easyweb.py） =========
def url_encode(url):
    """URL 编码"""
    encoded_url = ""
    for char in url:
        if char.isalpha() or char.isdigit() or char in ("-", ".", "_", "~"):
            encoded_url += char
        else:
            encoded_url += (
                "%" + binascii.hexlify(char.encode("utf-8")).decode("utf-8").upper()
            )
    return encoded_url


def url_decode(encoded_url):
    """URL 解码"""
    encoded_url = encoded_url.replace("+", " ")
    if "%" not in encoded_url:
        return encoded_url
    blocks = encoded_url.split("%")
    decoded_url = blocks[0]
    buffer = ""
    for b in blocks[1:]:
        if len(b) == 2:
            buffer += b[:2]
        else:
            decoded_url += binascii.unhexlify(buffer + b[:2]).decode("utf-8")
            buffer = ""
            decoded_url += b[2:]
    if buffer:
        decoded_url += binascii.unhexlify(buffer).decode("utf-8")
    return decoded_url


def _is_generator(obj):
    def _g():
        yield 0

    return isinstance(obj, type(_g()))


def _is_streaming_body(body):
    if body is None:
        return False
    if isinstance(body, (bytes, str, dict)):
        return False
    return _is_generator(body) or hasattr(body, "__iter__")


def _to_bytes(x, charset="utf-8"):
    if x is None:
        return b""
    if isinstance(x, bytes):
        return x
    if isinstance(x, str):
        return x.encode(charset)
    return str(x).encode(charset)


class Request:
    def __init__(self, method="GET", full_path="/", protocol="HTTP/1.1", headers=None, body=b""):
        self.method = method or "GET"
        self.full_path = full_path or "/"
        self.protocol = protocol or "HTTP/1.1"
        self.headers = ImmutableMultiDict(headers or {})
        self.body = body if body is not None else b""

        raw_path = self.full_path.split("?", 1)[0]
        self.path = url_decode(raw_path)

        self.view_args = ImmutableMultiDict({})

        self._url = None
        self._args = None
        self._form = None
        self._json = None
        self._cookies = None

    @property
    def host(self):
        return self.headers.get("Host")

    @property
    def url(self):
        if self._url is None:
            host = self.host
            if host:
                self._url = "http://{}{}".format(host, self.full_path)
        return self._url

    @property
    def args(self):
        if self._args is None:
            args = {}
            try:
                if "?" in self.full_path:
                    query_str = self.full_path.split("?", 1)[1].rstrip("&")
                else:
                    query_str = ""
                if query_str:
                    for arg_pair in query_str.split("&"):
                        if not arg_pair:
                            continue
                        if "=" in arg_pair:
                            key, value = arg_pair.split("=", 1)
                        else:
                            key, value = arg_pair, ""
                        args[url_decode(key)] = url_decode(value)
            except Exception:
                args = {}
            self._args = ImmutableMultiDict(args)
        return self._args

    @property
    def json(self):
        if self._json is None:
            try:
                self._json = json.loads(self.body)
            except Exception:
                self._json = None
        return self._json

    @property
    def form(self):
        if self._form is None:
            try:
                ct = self.headers.get("Content-Type", "") or ""
                if "application/x-www-form-urlencoded" not in ct:
                    self._form = None
                    return None
                items = (self.body or b"").decode("utf-8").split("&")
                form = {}
                for item in items:
                    if not item:
                        continue
                    if "=" in item:
                        k, v = item.split("=", 1)
                    else:
                        k, v = item, ""
                    k = url_decode(k)
                    v = None if v == "" else url_decode(v)
                    form[k] = v
                self._form = ImmutableMultiDict(form)
            except Exception:
                self._form = None
        return self._form

    @property
    def cookies(self):
        if self._cookies is None:
            cookies = {}
            try:
                raw = self.headers.get("Cookie")
                if raw:
                    for item in raw.split(";"):
                        item = item.strip()
                        if "=" in item:
                            k, v = item.split("=", 1)
                            cookies[url_decode(k)] = url_decode(v)
            except Exception:
                cookies = {}
            self._cookies = ImmutableMultiDict(cookies)
        return self._cookies


class Response:
    _default_template_engine = None
    
    def __init__(self, content=b"", status=200, headers=None, mimetype=None, content_type=None):
        self.status = int(status or 200)
        self.reason = STATUS_CODE.get(self.status, "Undefined")

        self.headers = {}
        if headers:
            if isinstance(headers, dict):
                self.headers.update(headers)
            else:
                for k, v in headers:
                    self.headers[k] = v

        self._cookies = []

        if mimetype and not content_type:
            content_type = mimetype
        self._explicit_content_type = content_type

        self.content = content

    def set_cookie(self, name, value="", max_age=None, path="/"):
        if max_age is None:
            max_age_part = ""
        else:
            max_age_part = "; Max-Age={}".format(int(max_age))
        path_part = "" if path is None else "; Path={}".format(path)
        line = "Set-Cookie: {}={}{}{}".format(
            url_encode(str(name)), url_encode(str(value)), max_age_part, path_part
        )
        self._cookies.append(line)

    @classmethod
    def set_default_template_engine(cls, engine):
        """设置默认模板引擎"""
        cls._default_template_engine = engine
    
    @classmethod
    def render_template(cls, template_path, *args, 
                       template_engine=None,  # 可传入特定引擎
                       **kwargs):
        """增强的模板渲染方法，支持多种引擎"""
        
        # 确定上下文
        def _ctx(*args, **kwargs):
            if args and isinstance(args[0], dict):
                return args[0]
            return kwargs
        context = _ctx(*args, **kwargs)
        
        # 确定使用的引擎
        engine = template_engine or cls._default_template_engine
        
        # 如果没有设置引擎，使用表达式引擎作为默认
        if engine is None:
            engine = ExpressionTemplateEngine()
            # 可以缓存默认引擎实例
            cls._default_template_engine = engine
        
        try:
            # 使用引擎渲染
            content = engine.render_file(template_path, context)
            return cls(content, content_type="text/html; charset=utf-8")
        except Exception as e:
            return cls(f"Template Error: {e}", status=500)
    
    # 添加直接使用字符串模板的方法
    @classmethod
    def render_string(cls, template_string, *args, 
                     template_engine=None, **kwargs):
        """渲染字符串模板"""
        # 确定上下文
        def _ctx(*args, **kwargs):
            if args and isinstance(args[0], dict):
                return args[0]
            return kwargs
        
        context = _ctx(*args, **kwargs) if args and isinstance(args[0], dict) else kwargs
        
        engine = template_engine or cls._default_template_engine
        if engine is None:
            engine = ExpressionTemplateEngine()
            cls._default_template_engine = engine
        
        try:
            content = engine.render(template_string, context)
            return cls(content, content_type="text/html; charset=utf-8")
        except Exception as e:
            return cls(f"Template Error: {e}", status=500)

    def _finalize_headers(self, body_bytes=None, streaming=False):
        # Content-Type 默认策略
        if self._explicit_content_type:
            # 如果用户明确指定了Content-Type，但没指定charset且是文本类型，则加上
            ct = self._explicit_content_type.lower()
            if ct.startswith('text/') and 'charset=' not in ct:
                self._explicit_content_type = f"{self._explicit_content_type}; charset=utf-8"
            self.headers.setdefault("Content-Type", self._explicit_content_type)
        else:
            # 没有明确指定，则根据内容类型设置默认值
            if isinstance(self.content, str):
                # 字符串默认使用HTML，强制指定UTF-8
                self.headers.setdefault("Content-Type", "text/html; charset=utf-8")
            elif isinstance(self.content, dict):
                # JSON响应
                self.headers.setdefault("Content-Type", "application/json")
            elif isinstance(self.content, list):
                # JSON响应
                self.headers.setdefault("Content-Type", "application/json")
            else:
                # 其他文本内容
                self.headers.setdefault("Content-Type", "text/plain; charset=utf-8")

        self.headers.setdefault("Connection", "close")

        if (not streaming) and (body_bytes is not None):
            self.headers.setdefault("Content-Length", str(len(body_bytes)))
        
        # 添加UTF-8编码相关的其他header
        self.headers.setdefault("Content-Encoding", "identity")

    def _status_line(self):
        return "HTTP/1.1 {} {}\r\n".format(self.status, self.reason).encode("utf-8")

    def _headers_bytes(self):
        lines = []
        for k, v in self.headers.items():
            lines.append("{}: {}".format(k, v))
        for c in self._cookies:
            lines.append(c)
        return ("\r\n".join(lines) + "\r\n\r\n").encode("utf-8")

    def iter_chunks(self):
        """
        统一的“响应字节流”迭代器：
        - 非流式：status_line + headers + body
        - 流式：status_line + headers + (chunks...)
          其中 generator 首个 yield 若为 dict，会用于补充 headers（easyweb 风格）。
        """
        streaming = _is_streaming_body(self.content)

        if not streaming:
            body = self.content
            if isinstance(body, dict):
                body = json.dumps(body)
            if isinstance(body, list):
                body = json.dumps(body)
            body_bytes = _to_bytes(body)
            self._finalize_headers(body_bytes=body_bytes, streaming=False)
            yield self._status_line()
            yield self._headers_bytes()
            if body_bytes:
                yield body_bytes
            return

        it = iter(self.content)
        first_item = None
        has_first = False
        try:
            first_item = next(it)
            has_first = True
        except Exception:
            has_first = False

        if has_first and isinstance(first_item, dict):
            self.headers.update(first_item)
            first_item = None
            has_first = False

        self._finalize_headers(body_bytes=None, streaming=True)
        yield self._status_line()
        yield self._headers_bytes()

        if has_first and first_item is not None:
            b = _to_bytes(first_item)
            if b:
                yield b

        for item in it:
            if item is None:
                continue
            b = _to_bytes(item)
            if b:
                yield b

    def build(self):
        data = b"".join([chunk for chunk in self.iter_chunks()])
        return data


def make_response(content=b"", status=200, headers=None):
    if isinstance(content, Response):
        if status is not None:
            content.status = int(status)
            content.reason = STATUS_CODE.get(content.status, "Undefined")
        if headers:
            if isinstance(headers, dict):
                content.headers.update(headers)
            else:
                for k, v in headers:
                    content.headers[k] = v
        return content

    if isinstance(content, tuple):
        if len(content) == 2:
            return Response(content[0], status=content[1])
        if len(content) >= 3:
            return Response(content[0], status=content[1], headers=content[2])
    return Response(content, status=status, headers=headers)


class Application:
    def __init__(self, static_folder="static/", static_url_path="/static/"):
        self.routes = []
        self.static_routes = {}
        self.static_folder = static_folder
        self.static_url_path = static_url_path
        
        # 初始化URL映射和转换器字典
        # 模拟 Flask 的 url_map
        class UrlMap:
            def __init__(self):
                self.converters = {}
        
        self.url_map = UrlMap()
        self._register_default_converters()

    def _register_default_converters(self):
        """注册所有默认的转换器"""
        self.url_map.converters.update({
            'string': StringConverter,
            'int': IntConverter,
            'float': FloatConverter,
            'path': PathConverter,
            'part': PartConverter,   
            're': ReConverter,      # 重构后的 re 转换器
            'bool': BoolConverter
        })

    def _compile_route(self, path: str):
        """
        编译路由路径，支持Flask风格的 <转换器名(参数):变量名> 语法。
        
        返回: (compiled_regex_pattern, converters_dict, param_names_list)
        """
        # 修改后的正则表达式，使用普通捕获组替代命名捕获组
        # 组1: 转换器名
        # 组2: 括号内的参数
        # 组3: 变量名
        route_param_pattern = re.compile(
            r'<(?:([a-zA-Z_][a-zA-Z0-9_]*)(?:\(([^)]*)\))?:)?([a-zA-Z_][a-zA-Z0-9_]*)>'
        )
        
        param_names = []
        converters = {}  # 存放 {变量名: 转换器实例}
        regex_parts = []
        
        # 按斜杠分割路径，但注意 path 转换器会吃掉后面的所有部分
        segments = path.split('/')
        for segment in segments:
            if not segment:
                regex_parts.append('')  # 用于开头的空段
                continue
            
            # 尝试匹配动态段
            match = route_param_pattern.match(segment)
            if match:
                # 获取匹配的完整字符串
                matched_str = match.group(0)
                # 检查是否匹配了整个段（MicroPython兼容的方法）
                if matched_str == segment:
                    # 这是一个动态参数段
                    converter_name = match.group(1)  # 索引1对应转换器名
                    args_string = match.group(2)     # 索引2对应参数
                    variable_name = match.group(3)   # 索引3对应变量名
                    if variable_name in param_names:
                        raise ValueError(f"Duplicate variable name '{variable_name}' in route '{path}'")
                    
                    param_names.append(variable_name)
                    
                    # 1. 确定转换器类
                    if converter_name is None:
                        converter_name = 'string'  # 默认转换器
                    
                    converter_class = self.url_map.converters.get(converter_name)
                    if converter_class is None:
                        raise ValueError(f"Unknown converter '{converter_name}' in route '{path}'. "+
                                       f"Available converters: {list(self.url_map.converters.keys())}")
                    
                    # 2. 解析参数（如果存在）
                    args = ()
                    kwargs = {}
                    if args_string:
                        # 这是一个简化的参数解析，主要处理 re(r'...') 这种单字符串参数
                        try:
                            # 尝试用 eval 解析元组，但在受控环境下（参数来自开发者定义的路由）
                            parsed_args = eval(f'({args_string},)', {}, {})
                            if isinstance(parsed_args, tuple):
                                args = parsed_args
                        except Exception:
                            # 如果 eval 失败，将整个 args_string 作为单个字符串参数
                            args = (args_string.strip(),)
                    
                    # 3. 创建转换器实例
                    converter_instance = converter_class(self.url_map, *args, **kwargs)
                    converters[variable_name] = converter_instance
                    
                    # 4. 获取该转换器的正则部分并添加到路径
                    regex_part = f"({converter_instance.regex})"
                    regex_parts.append(regex_part)
                    
                    # 5. 如果遇到 'path' 转换器，它是最后一部分，跳出循环
                    if converter_name == 'path':
                        # 确保 path 是最后一个转换器
                        if segments.index(segment) != len(segments) - 1:
                            raise ValueError(f"Path converter '{segment}' must be the last part in route '{path}'")
                        # 对于 path 转换器，我们不再连接剩余的硬编码部分
                        break
                    
                    continue  # 动态段处理完毕，继续下一个段
            
            # 如果到达这里，说明不是动态参数段，是静态文本段
            regex_parts.append(escape(segment))
        
        # 构建完整的正则表达式
        regex_pattern = "^" + "/".join(regex_parts) + "$"
        # 清理双斜杠（当有空段时可能产生）
        regex_pattern = regex_pattern.replace("//", "/")
        
        try:
            compiled_pattern = re.compile(regex_pattern)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern for route '{path}': {e}") from e
        
        return compiled_pattern, converters, param_names

    def route(self, path, methods=None):
        if methods is None:
            methods = ["GET"]
        compiled_pattern, param_types, param_names = self._compile_route(path)

        def decorator(func):
            for method in methods:
                m = (method or "GET").upper()
                if "<" in path:
                    self.routes.append((m, compiled_pattern, param_types, param_names, func))
                else:
                    self.static_routes[(m, path)] = func
            return func

        return decorator

    def add_route(self, path, handler, methods=None):
        if methods is None:
            methods = ["GET"]
        compiled_pattern, param_types, param_names = self._compile_route(path)
        for method in methods:
            m = (method or "GET").upper()
            if "<" in path:
                self.routes.append((m, compiled_pattern, param_types, param_names, handler))
            else:
                self.static_routes[(m, path)] = handler

    def _call_view(self, view_func, req):
        try:
            argc = view_func.__code__.co_argcount
        except Exception:
            argc = 1
        if argc == 0:
            return view_func()
        return view_func(req)

    def _serve_static_file(self, req):
        if not req.path.startswith(self.static_url_path):
            return None
        rel = req.path[len(self.static_url_path) :]
        if rel.startswith("/"):
            rel = rel[1:]
        if ".." in rel:
            return Response("Forbidden", status=403)
        file_path = self.static_folder + rel
        try:
            content_type = "application/octet-stream"
            for ext, ct in FILE_TYPE.items():
                if file_path.endswith(ext):
                    content_type = ct
                    break
            with open(file_path, "rb") as f:
                return Response(f.read(), content_type=content_type)
        except Exception:
            return None

    def handle_request(self, req):
        # 静态文件
        static_resp = self._serve_static_file(req)
        if static_resp is not None:
            return static_resp

        # 静态路由
        handler = self.static_routes.get((req.method, req.path))

        # 动态路由
        if not handler:
            for method, pattern, converters, param_names, view_func in self.routes:  # 注意：这里解包的内容变了
                if method != req.method:
                    continue
                match = pattern.match(req.path)
                if match:
                    # 提取匹配的字符串组
                    matched_values = groups(match)
                    view_args_dict = {}
                    
                    # 使用转换器将字符串转换为Python值
                    for var_name, raw_value in zip(param_names, matched_values):
                        converter = converters.get(var_name)
                        if converter:
                            try:
                                view_args_dict[var_name] = converter.to_python(raw_value)
                            except Exception as e:
                                # 转换失败，例如 int(‘abc‘)
                                # 可以选择记录日志或跳过此路由
                                print(f"[web] Converter error for '{var_name}': {e}")
                                view_args_dict = None
                                break
                        else:
                            # 没有转换器，保持字符串
                            view_args_dict[var_name] = raw_value
                    
                    if view_args_dict is None:
                        continue  # 转换失败，尝试下一个路由
                    
                    req.view_args = ImmutableMultiDict(view_args_dict)
                    handler = view_func
                    break

        if not handler:
            return Response("Not Found", status=404)

        try:
            res = self._call_view(handler, req)
            if isinstance(res, Response):
                return res
            if isinstance(res, tuple):
                return make_response(res)
            return Response(res)
        except Exception as e:
            return Response("Error1: {}".format(e), status=500)

    async def _awrite(self, writer, data):
        if hasattr(writer, "awrite"):
            await writer.awrite(data)
            return
        # CPython asyncio StreamWriter
        writer.write(data)
        if hasattr(writer, "drain"):
            await writer.drain()

    async def _aclose(self, writer):
        if hasattr(writer, "aclose"):
            await writer.aclose()
            return
        writer.close()
        if hasattr(writer, "wait_closed"):
            try:
                await writer.wait_closed()
            except Exception:
                pass

    async def _handle(self, reader, writer):
        try:
            raw = await reader.readline()
            if not raw:
                await self._aclose(writer)
                return
            try:
                line = raw.decode("utf-8").rstrip("\r\n")
            except Exception:
                line = str(raw).rstrip("\r\n")
            parts = line.split(" ")
            if len(parts) < 3:
                await self._aclose(writer)
                return
            method, full_path, protocol = parts[0].upper(), parts[1], parts[2]

            headers = {}
            while True:
                h = await reader.readline()
                if not h:
                    break
                h = h.decode("utf-8").rstrip("\r\n")
                if h == "":
                    break
                if ": " in h:
                    k, v = h.split(": ", 1)
                elif ":" in h:
                    k, v = h.split(":", 1)
                else:
                    continue
                headers[k.strip()] = v.strip()

            size = 0
            try:
                size = int(headers.get("Content-Length", "0") or "0")
            except Exception:
                size = 0
            body = b""
            if size > 0:
                try:
                    body = await reader.read(size)
                except Exception:
                    body = b""

            req = Request(method=method, full_path=full_path, protocol=protocol, headers=headers, body=body)
            resp = self.handle_request(req)
            if not isinstance(resp, Response):
                resp = Response(resp)

            for chunk in resp.iter_chunks():
                if chunk:
                    await self._awrite(writer, chunk)
        except Exception as e:
            try:
                resp = Response("Internal Server Error", status=500)
                await self._awrite(writer, resp.build())
            except Exception:
                pass
        finally:
            try:
                await self._aclose(writer)
            except Exception:
                pass

    async def serve(self, host="0.0.0.0", port=80):
        """创建 server（协程），由调用者决定如何 run_forever。"""
        return await asyncio.start_server(self._handle, host, port)

    def run(self, host="0.0.0.0", port=80, **kwargs):
        """MicroPython 风格：创建 task 并 run_forever。"""
        loop = asyncio.get_event_loop()

        async def _runner():
            await asyncio.start_server(self._handle, host, port)

        loop.create_task(_runner())
        print("[web]Server running on {}:{}".format(host, int(port)))
        if sys.implementation.name == 'micropython':
            print("[web]If you have enabled AP or STA mode, you can access the server with the corresponding IP address.")
            print("[web]In AP mode, it is recommended to use the 'microdns' library to enable accessing by any website address.")
        loop.run_forever()


def Flask(import_name=None, **kwargs):
    return Application(**kwargs)

def render_template(template_path, *args, **kwargs):
    return Response.render_template(template_path, *args, **kwargs)

def render_template_string(template_string, *args, **kwargs):
    return Response.render_string(template_string, *args, **kwargs)

def redirect(url):
    resp = Response("", status=302)
    resp.headers["Location"] = url
    return resp

def _self_test():
    req = Request(method="GET", full_path="/hello?name=%E4%B8%AD%E6%96%87&x=1+2", headers={"Host": "a"})
    assert req.path == "/hello"
    assert req.args.get("name") == "中文"
    assert req.args.get("x") == "1 2"
    assert req.url == "http://a/hello?name=%E4%B8%AD%E6%96%87&x=1+2"

    req2 = Request(headers={"Cookie": "a=1; b=%E4%B8%AD%E6%96%87"})
    assert req2.cookies.get("b") == "中文"

    r = Response("ok")
    r.set_cookie("b", "中文", max_age=10)
    bs = b"".join(r.iter_chunks())
    assert b"Set-Cookie:" in bs

    def gen():
        yield {"Content-Type": "text/plain"}
        yield b"1"
        yield b"2"

    r2 = Response(gen())
    out = b"".join(r2.iter_chunks())
    assert b"Content-Type: text/plain" in out
    assert out.endswith(b"12")

    # 5) dynamic route + type conversion
    app = Flask(__name__)

    @app.route("/u/<int:uid>", methods=["GET"])
    def u(req):
        return req.view_args.get("uid")

    resp = app.handle_request(Request(method="GET", full_path="/u/12"))
    assert b"".join(resp.iter_chunks()).endswith(b"12")

    # 6) POST form
    @app.route("/form", methods=["POST"])
    def form(req):
        return req.form.get("b")

    body = b"a=1&b=%E4%B8%AD"
    resp2 = app.handle_request(
        Request(
            method="POST",
            full_path="/form",
            headers={"Content-Type": "application/x-www-form-urlencoded", "Content-Length": str(len(body))},
            body=body,
        )
    )
    assert b"".join(resp2.iter_chunks()).endswith("中".encode("utf-8"))

    # 7) POST JSON
    @app.route("/json", methods=["POST"])
    def j(req):
        return req.json.get("a")

    bodyj = b'{"a":1}'
    resp3 = app.handle_request(
        Request(
            method="POST",
            full_path="/json",
            headers={"Content-Type": "application/json", "Content-Length": str(len(bodyj))},
            body=bodyj,
        )
    )
    assert b"".join(resp3.iter_chunks()).endswith(b"1")

    # 8) static file
    try:
        os.mkdir("static")
    except Exception:
        pass
    try:
        with open("static/_t.txt", "wb") as f:
            f.write(b"hi")
        resp4 = app.handle_request(Request(method="GET", full_path="/static/_t.txt"))
        data4 = b"".join(resp4.iter_chunks())
        assert data4.endswith(b"hi")
    finally:
        try:
            os.remove("static/_t.txt")
        except Exception:
            pass
    return True


if __name__ == "__main__":  # pragma: no cover
    print(_self_test())

