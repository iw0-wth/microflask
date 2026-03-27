# MicroFlask

- MicroFlask是一个为提升flask项目迁移和web界面开发的速度的类flask的web框架，以开放和可扩展为宗旨，兼容micropython和cpython并主要为micropython服务
- MicroFlask is a Flask-like web framework designed to facilitate the migration of Flask-based projects and accelerate development. With a focus on openness and extensibility, it provides compatibility with both MicroPython and CPython while prioritizing support for MicroPython environments.

# MicroFlask_Async
- MicroFlask_Async是一个为提升flask项目迁移和web界面开发的速度的类flask的异步web框架，以开放和可扩展为宗旨，兼容micropython和cpython并主要为micropython服务
- MicroFlask_Async is a Flask-like asynchronous web framework designed to facilitate the migration of Flask-based projects and accelerate web interface development. With a focus on openness and extensibility, it provides compatibility with both MicroPython and CPython while prioritizing support for MicroPython environments.

# MicroFlask
## 版本说明
- microflask.py 同步版本
- microflask_async.py 异步版本

## 特性

- Flask-like API 设计，便于项目迁移
- 同时支持 MicroPython 和 CPython 环境
- 轻量级设计，适合资源受限环境
- 支持同步和异步处理模式
- 模块化架构，易于扩展
- 定义模板引擎基类，可自定义接入模板引擎
- 自定义动态路由语法高度兼容flask


## 快速开始(使用前请先让您的开发板联网)
### 基础同步应用
```python
from microflask import *

app = Flask(__name__)

@app.route('/')
def hello(request):
    return "Hello, MicroFlask!"

@app.route('/user/<name>')
def user(request):
    name=request.view_args.get("name")
    return f"Hello, {name}!"

if __name__ == '__main__':
    app.run()
```

### 异步应用
```python
from microflask_async import *

app = Flask(__name__)

@app.route('/')
def hello(request):
    return "Hello, Async MicroFlask!"

@app.route('/api/data')
def get_data(request):
    return {"message": "Async data response"}

if __name__ == '__main__':
    app.run()
```

## 路由系统
### 基本路由
```python
@app.route('/')
def index(request):
    return "Home Page"

@app.route('/about')
def about(request):
    return "About Page"
```

### 动态路由
```python
@app.route('/user/<username>')
def show_user(req):
    username=req.view_args.get("username")
    return f"User: {username}"

@app.route('/post/<int:post_id>')
def show_post(req):
    post_id=req.view_args.get("post_id")
    return f"Post ID: {post_id}"
```

### HTTP 方法
```python
@app.route('/login', methods=['GET', 'POST'])
def login(request):
    if request.method == 'POST':
        return do_login()
    else:
        return show_login_form()
```
## 项目结构
设计同flask
```bash
根目录
 ├── main.py
 ├── microflask.py
 ├── static #默认静态文件夹
 └── templates/ #默认模板文件夹
       └── index.html #放置模板文件
```
静态文件夹可以通过Flask()设置
```python
app = Flask(
    static_folder="static/",
    static_url_path="/static/",
)
```

## 请求处理
### 获取请求数据
```python
from microflask import *

@app.route("/form", methods=["POST"])
def form(request):
    return request.form.get("b")
@app.route("/json", methods=["POST"])
def j(request):
    return request.json.get("a")
```

### 文件上传
**目前版本没有解析multipart/form-data，下个版本一定改**
```python
from microflask import*
import binascii
max_request_length=8192
# 创建一个应用实例
app = Flask(__name__)

def parse_multipart_form_data(body, boundary):
    """
    一个简化的 multipart/form-data 解析器，用于在 ESP32 等资源受限环境。
    它提取第一个文件的文件名和内容。
    注意：这是一个简化实现，对于复杂表单可能需要增强。
    """
    parts = body.split(b'--' + boundary.encode())
    result = {}

    for part in parts:
        if b'Content-Disposition: form-data;' in part:
            # 找到头部和正文的分隔处
            header_end = part.find(b'\r\n\r\n')
            if header_end == -1:
                continue
            headers = part[:header_end]
            file_content = part[header_end+4:]  # 跳过 \r\n\r\n

            # 解析头部，寻找文件名
            lines = headers.split(b'\r\n')
            filename = None
            field_name = None
            for line in lines:
                if b'name=' in line and b'filename=' in line:
                    # 处理文件字段
                    try:
                        # 简单解析，查找 filename="..."
                        name_start = line.find(b'name="') + 6
                        name_end = line.find(b'"', name_start)
                        field_name = line[name_start:name_end].decode()

                        filename_start = line.find(b'filename="', name_end) + 10
                        filename_end = line.find(b'"', filename_start)
                        filename = line[filename_start:filename_end].decode()
                    except:
                        pass
                    if filename and field_name:
                        # 移除末尾可能存在的 \r\n (正文部分后的分隔符)
                        if file_content.endswith(b'\r\n'):
                            file_content = file_content[:-2]
                        result[field_name] = {'filename': filename, 'content': file_content}
                        break
    return result

@app.route('/upload', methods=['GET'])
def upload_form(request):
    """提供一个简单的文件上传HTML表单页面"""
    html_form = '''
    <!DOCTYPE html>
    <html>
    <head><title>Upload File</title></head>
    <body>
        <h2>Upload a .txt file to ESP32</h2>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <label for="file">Select file (max 8KB):</label><br><br>
            <input type="file" id="file" name="file" accept=".txt"><br><br>
            <input type="submit" value="Upload">
        </form>
    </body>
    </html>
    '''
    return Response(html_form, content_type="text/html")

@app.route('/upload', methods=['POST'])
def handle_upload(request):
    """处理文件上传的POST请求"""
    content_type = request.headers.get('Content-Type', '')

    # 检查是否为multipart表单数据
    if 'multipart/form-data' not in content_type:
        return Response('Invalid content type. Expected multipart/form-data.', status=400)

    # 从Content-Type头中提取边界字符串
    try:
        boundary = content_type.split('boundary=')[1].strip()
    except IndexError:
        return Response('Could not find boundary in Content-Type.', status=400)

    # 限制文件大小（框架默认限制为max_request_length=8192，但是可以从run修改，此处再次检查）
    if len(request.body) > max_request_length:
        return Response(f'File too large. Maximum size is {max_request_length/1024}KB.', status=413)

    # 解析multipart数据
    uploaded_files = parse_multipart_form_data(request.body, boundary)

    if 'file' not in uploaded_files:
        return Response('No file uploaded or field name is not "file".', status=400)

    file_info = uploaded_files['file']
    filename = file_info['filename']
    file_content = file_info['content']

    # 检查是否为文本文件（简单通过扩展名）
    if not filename.lower().endswith('.txt'):
        return Response('Only .txt files are allowed.', status=400)

    # 将文件保存到ESP32的文件系统 (例如命名为 uploaded.txt)
    try:
        save_path = 'uploaded.txt'
        with open(save_path, 'wb') as f:
            f.write(file_content)
        save_message = f"File saved successfully to '{save_path}'."
    except Exception as e:
        return Response(f"Failed to save file: {e}", status=500)

    # 尝试将文件内容解码为UTF-8文本并输出
    try:
        text_content = file_content.decode('utf-8')
        content_preview = text_content[:500]  # 预览前500个字符，避免响应过大
        if len(text_content) > 500:
            content_preview += "\n... (truncated for display)"
    except UnicodeDecodeError:
        content_preview = "[File contains binary data, cannot display as text]"

    # 构建响应HTML，显示上传结果和文件内容
    result_html = f'''
    <!DOCTYPE html>
    <html>
    <head><title>Upload Result</title></head>
    <body>
        <h2>Upload Successful!</h2>
        <p><strong>Original Filename:</strong> {filename}</p>
        <p><strong>Save Status:</strong> {save_message}</p>
        <p><strong>File Size:</strong> {len(file_content)} bytes</p>
        <hr>
        <h3>Content of the uploaded file:</h3>
        <pre>{content_preview}</pre>
        <hr>
        <a href="/upload">Upload another file</a>
    </body>
    </html>
    '''
    return Response(result_html, content_type="text/html")

if __name__ == '__main__':
    # 注意：对于文件上传，根据文件大小调整 max_request_length 参数。
    app.run(port=80,max_request_length=max_request_length)
```

## 响应处理
### 返回JSON
**对于list和dict类型数据，会自动转为json**
```python
@app.route('/api/users')
def get_users(request):
    users = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    return users
 
```

### 设置状态码和头部
```python
@app.route('/create', methods=['POST'])
def create_resource(request):
    # 创建资源逻辑
    return "Created", 201, {'X-Custom-Header': 'Value'}
    #或者像这样不设置头部
    return "Created", 201
    #还可以
    resp = Response(
        content="Hello World", 
        status=201, 
        headers={'X-Custom-Header': 'Value'}
    )
    # 也可以单独设置头部
    resp.headers['Another-Header'] = 'AnotherValue'
    return resp
    #或者这样
    #make_response直接传递内容、状态码、头部
    return make_response("Created", 201, {'X-Custom-Header': 'Value'})    
    #make_response修改一个已存在的Response对象
    resp = Response("Hello")
    resp = make_response(resp, 201, {'X-Custom-Header': 'Value'})
    return resp
 
```

### 重定向
**url_for()得等下，做这个还得构造一个新类映射路由和函数，好累QwQ**
```python
@app.route('/old')
def old_endpoint(request):
    return redirect('/new')
@app.route('/external')
def external_redirect(request):
    # 重定向到外部网址
    return redirect('https://example.com')
```

## 模板渲染
### 基本模板使用
```python
from microflask import render_template

@app.route('/')
def index(request):
    return render_template('index.html')
```
### 模板引擎使用
```python
@app.route('/')
def index(request):
    return render_template('index.html',template_engine=SimpleTemplateEngine())
```
### 设置默认模板引擎
**使用UTemplateEngine()，需要确定已经下载了utemplate库并可导入**
```python
utemplate_engine = UTemplateEngine(pkg=None, dir="demo_templates", loader_type="source")
Response.set_default_template_engine(utemplate_engine)
@app.route('/')
def index(request):
    return render_template('index.html')
```

## 扩展
**中间件目前是没有的，我感觉这不纯浪费资源吗QwQ**
### 自定义动态路由规则
```python
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
```
### 自定义模板引擎

```python
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
```
utemplate可以看作一个demo:
```python
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
```
**更多功能看demo吧，不想写了QwQ呜呜呜呜呜呜呜**
**反正SSE，流式，cookie，json...都是支持的，自己琢磨去吧§(*￣▽￣*)§**

## demo
**有点多，有点乱，我梳理下QwQ，ai连demo都写不明白，淦**
不过目前已经写了不少了，慢慢来吧，后面更新版本的时候会更新readme的，到时候会给

## 兼容性测试
### microflask.py
```bash
ESP系列 已测试 无兼容性问题
K230 可能存在问题 使用硬件勘智CanMV-K230-V1.0固件"CanMV_K230_V1P0_P1_micropython_v1.5-legacy-27-g274b82f_nncase_v2.9.0.img" 初步判断为该固件socket库存在问题
```

### microflask_async.py
```bash
ESP系列 已测试 无兼容性问题
K230 已测试 无兼容性问题
```

## 版本说明
### 0.0.20260321
1. 从工程文件中选取了一个兼容版本并进行了测试和发布前检查
2. 编写了README.md
3. 开始整理demo
4. 编写了package.json并修改urls为绝对地址以允许老版本mip抓取

### 0.0.20260324
1. 修改了部分README.md中的问题并添加条目
2. 进行了K230的兼容性测试
3. 项目文件未修改因而仍使用0.0.20260321作为文件内版本号

## 贡献指南
1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request
## 许可证
MIT License

## 支持
如有问题请提交 Issue 或联系开发团队。

## 联系
 EMAIL:tianqi2021_001@163.com