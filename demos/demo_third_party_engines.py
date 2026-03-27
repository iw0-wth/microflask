#!/usr/bin/env python3
"""
第三方模板引擎接入演示
支持 Jinja2、Mako、Cheetah、Chameleon、Django 引擎
CPython 专用，展示如何集成不同的模板引擎
"""

from microflask import*

# 第三方模板引擎导入
ENGINES_AVAILABLE = {
    'jinja2': False,
    'mako': False, 
    'cheetah': False,
    'chameleon': False,
    'django': False
}

try:
    from jinja2 import Environment, FileSystemLoader
    ENGINES_AVAILABLE['jinja2'] = True
    print("✅ Jinja2 引擎可用")
except ImportError:
    print("⚠️  Jinja2 引擎不可用: pip install jinja2")

try:
    from mako.template import Template as MakoTemplate
    from mako.lookup import TemplateLookup
    ENGINES_AVAILABLE['mako'] = True
    print("✅ Mako 引擎可用")
except ImportError:
    print("⚠️  Mako 引擎不可用: pip install mako")

try:
    from Cheetah.Template import Template as CheetahTemplate
    ENGINES_AVAILABLE['cheetah'] = True
    print("✅ Cheetah 引擎可用")
except ImportError:
    print("⚠️  Cheetah 引擎不可用: pip install cheetah3")

try:
    from chameleon import PageTemplateLoader
    ENGINES_AVAILABLE['chameleon'] = True
    print("✅ Chameleon 引擎可用")
except ImportError:
    print("⚠️  Chameleon 引擎不可用: pip install chameleon")

try:
    import os
    import sys
    import django
    from django.conf import settings
    from django.template import Template, Context
    from django.template.loader import get_template
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            TEMPLATES=[{
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': ['demo_templates'],
                'APP_DIRS': True,
                'OPTIONS': {
                    'context_processors': [
                        'django.template.context_processors.debug',
                        'django.template.context_processors.request',
                    ],
                },
            }]
        )
        django.setup()
    ENGINES_AVAILABLE['django'] = True
    print("✅ Django 引擎可用")
except ImportError:
    print("⚠️  Django 引擎不可用: pip install django")

# 创建应用实例
app = MicroFlask(__name__)

# 全局数据
sample_data = {
    'title': '第三方模板引擎演示',
    'username': '张三',
    'current_time': '2024-01-01 12:00:00',
    'items': ['Python', 'JavaScript', 'HTML', 'CSS'],
    'user': {
        'name': '张三',
        'email': 'zhangsan@example.com',
        'age': 25,
        'is_active': True,
        'description': '这是一个热爱编程的开发者',
        'skills': ['Python', 'Web开发', '数据库']
    },
    'score': 85
}

# 为每个引擎创建模板目录
import os
os.makedirs('demo_templates/jinja2', exist_ok=True)
os.makedirs('demo_templates/mako', exist_ok=True)
os.makedirs('demo_templates/cheetah', exist_ok=True)
os.makedirs('demo_templates/chameleon', exist_ok=True)
os.makedirs('demo_templates/django', exist_ok=True)

# 创建各引擎的模板文件
JINJA2_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .engine-info { background: #e8f4fd; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .content { background: #f9f9f9; padding: 20px; border-radius: 5px; }
        .user-card { border: 1px solid #ddd; padding: 15px; margin: 20px 0; border-radius: 8px; }
        .skill { background: #007bff; color: white; padding: 3px 8px; margin: 2px; border-radius: 3px; display: inline-block; }
    </style>
</head>
<body>
    <div class="engine-info">
        <h2>🎨 Jinja2 引擎渲染</h2>
        <p>渲染时间: {{ current_time }}</p>
    </div>
    
    <div class="content">
        <h1>欢迎, {{ username }}!</h1>
        
        <div class="user-card">
            <h3>用户信息</h3>
            <p><strong>姓名:</strong> {{ user.name }}</p>
            <p><strong>邮箱:</strong> {{ user.email }}</p>
            <p><strong>年龄:</strong> {{ user.age }}</p>
            <p><strong>状态:</strong> 
                {% if user.is_active %}
                    <span style="color: green;">✅ 活跃</span>
                {% else %}
                    <span style="color: red;">❌ 未激活</span>
                {% endif %}
            </p>
            
            <h4>技能列表:</h4>
            {% for skill in user.skills %}
                <span class="skill">{{ skill }}</span>
            {% endfor %}
        </div>
        
        <h3>项目列表 (使用过滤器):</h3>
        <ul>
        {% for item in items %}
            <li>{{ item | upper }}</li>
        {% endfor %}
        </ul>
        
        <h3>成绩评定:</h3>
        {% if score >= 90 %}
            <p style="color: gold;">🏆 优秀 ({{ score }}分)</p>
        {% elif score >= 80 %}
            <p style="color: blue;">👍 良好 ({{ score }}分)</p>
        {% elif score >= 60 %}
            <p style="color: orange;">✅ 及格 ({{ score }}分)</p>
        {% else %}
            <p style="color: red;">❌ 不及格 ({{ score }}分)</p>
        {% endif %}
        
        <h3>Jinja2 特性演示:</h3>
        <p>字符串长度: {{ username | length }}</p>
        <p>当前时间格式化: {{ current_time | truncate(10) }}</p>
        <p>用户描述词数: {{ user.description | wordcount }}</p>
    </div>
</body>
</html>
"""

MAKO_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>${title}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .engine-info { background: #fff3cd; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .content { background: #f9f9f9; padding: 20px; border-radius: 5px; }
        .user-card { border: 1px solid #ddd; padding: 15px; margin: 20px 0; border-radius: 8px; }
        .skill { background: #ffc107; color: black; padding: 3px 8px; margin: 2px; border-radius: 3px; display: inline-block; }
    </style>
</head>
<body>
    <div class="engine-info">
        <h2>⚡ Mako 引擎渲染</h2>
        <p>渲染时间: ${current_time}</p>
    </div>
    
    <div class="content">
        <h1>欢迎, ${username}!</h1>
        
        <div class="user-card">
            <h3>用户信息</h3>
            <p><strong>姓名:</strong> ${user.name}</p>
            <p><strong>邮箱:</strong> ${user.email}</p>
            <p><strong>年龄:</strong> ${user.age}</p>
            <p><strong>状态:</strong> 
                % if user.is_active:
                    <span style="color: green;">✅ 活跃</span>
                % else:
                    <span style="color: red;">❌ 未激活</span>
                % endif
            </p>
            
            <h4>技能列表:</h4>
            % for skill in user.skills:
                <span class="skill">${skill}</span>
            % endfor
        </div>
        
        <h3>项目列表:</h3>
        <ul>
        % for item in items:
            <li>${item.upper()}</li>
        % endfor
        </ul>
        
        <h3>成绩评定:</h3>
        % if score >= 90:
            <p style="color: gold;">🏆 优秀 (${score}分)</p>
        % elif score >= 80:
            <p style="color: blue;">👍 良好 (${score}分)</p>
        % elif score >= 60:
            <p style="color: orange;">✅ 及格 (${score}分)</p>
        % else:
            <p style="color: red;">❌ 不及格 (${score}分)</p>
        % endif
        
        <h3>Mako 特性演示:</h3>
        <p>Python 代码执行: ${2 + 3}</p>
        <p>字符串方法: ${username.upper()}</p>
        <p>列表长度: ${len(items)}</p>
        % if loop.index < len(items):
            <p>循环索引: ${loop.index} (0-based)</p>
        % endif
    </div>
</body>
</html>
"""

CHEETAH_TEMPLATE = """#encoding UTF-8
<!DOCTYPE html>
<html>
<head>
    <title>$title</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .engine-info { background: #d4edda; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .content { background: #f9f9f9; padding: 20px; border-radius: 5px; }
        .user-card { border: 1px solid #ddd; padding: 15px; margin: 20px 0; border-radius: 8px; }
        .skill { background: #28a745; color: white; padding: 3px 8px; margin: 2px; border-radius: 3px; display: inline-block; }
    </style>
</head>
<body>
    <div class="engine-info">
        <h2>🐆 Cheetah 引擎渲染</h2>
        <p>渲染时间: $current_time</p>
    </div>
    
    <div class="content">
        <h1>欢迎, $username!</h1>
        
        <div class="user-card">
            <h3>用户信息</h3>
            <p><strong>姓名:</strong> $user.name</p>
            <p><strong>邮箱:</strong> $user.email</p>
            <p><strong>年龄:</strong> $user.age</p>
            <p><strong>状态:</strong> 
                #if $user.is_active
                    <span style="color: green;">✅ 活跃</span>
                #else
                    <span style="color: red;">❌ 未激活</span>
                #end if
            </p>
            
            <h4>技能列表:</h4>
            #for $skill in $user.skills
                <span class="skill">$skill</span>
            #end for
        </div>
        
        <h3>项目列表:</h3>
        <ul>
        #for $item in $items
            <li>$item.upper()</li>
        #end for
        </ul>
        
        <h3>成绩评定:</h3>
        #if $score >= 90
            <p style="color: gold;">🏆 优秀 ($score分)</p>
        #elif $score >= 80
            <p style="color: blue;">👍 良好 ($score分)</p>
        #elif $score >= 60
            <p style="color: orange;">✅ 及格 ($score分)</p>
        #else
            <p style="color: red;">❌ 不及格 ($score分)</p>
        #end if
        
        <h3>Cheetah 特性演示:</h3>
        <p>用户名大写: $username.upper()</p>
        <p>用户名长度: $len($username)</p>
        <p>当前年份: $current_time.split('-')[0]</p>
    </div>
</body>
</html>
"""

CHAMELEON_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>${title}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .engine-info { background: #f8d7da; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .content { background: #f9f9f9; padding: 20px; border-radius: 5px; }
        .user-card { border: 1px solid #ddd; padding: 15px; margin: 20px 0; border-radius: 8px; }
        .skill { background: #dc3545; color: white; padding: 3px 8px; margin: 2px; border-radius: 3px; display: inline-block; }
    </style>
</head>
<body>
    <div class="engine-info">
        <h2>🦎 Chameleon 引擎渲染</h2>
        <p>渲染时间: ${current_time}</p>
    </div>
    
    <div class="content">
        <h1>欢迎, ${username}!</h1>
        
        <div class="user-card">
            <h3>用户信息</h3>
            <p><strong>姓名:</strong> ${user.name}</p>
            <p><strong>邮箱:</strong> ${user.email}</p>
            <p><strong>年龄:</strong> ${user.age}</p>
            <p><strong>状态:</strong> 
                <span tal:condition="user.is_active" style="color: green;">✅ 活跃</span>
                <span tal:condition="not user.is_active" style="color: red;">❌ 未激活</span>
            </p>
            
            <h4>技能列表:</h4>
            <span tal:repeat="skill user.skills" class="skill">${skill}</span>
        </div>
        
        <h3>项目列表:</h3>
        <ul>
            <li tal:repeat="item items">${item.upper()}</li>
        </ul>
        
        <h3>成绩评定:</h3>
        <p tal:condition="score >= 90" style="color: gold;">🏆 优秀 (${score}分)</p>
        <p tal:condition="score >= 80 and score < 90" style="color: blue;">👍 良好 (${score}分)</p>
        <p tal:condition="score >= 60 and score < 80" style="color: orange;">✅ 及格 (${score}分)</p>
        <p tal:condition="score < 60" style="color: red;">❌ 不及格 (${score}分)</p>
        
        <h3>Chameleon 特性演示:</h3>
        <p>字符串处理: ${username.upper()}</p>
        <p>项目数量: ${len(items)}</p>
        <p>TAL表达式测试: ${'✅' if user.is_active else '❌'}</p>
    </div>
</body>
</html>
"""

DJANGO_TEMPLATE = """
{% load humanize %}
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .engine-info { background: #e2e3e5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .content { background: #f9f9f9; padding: 20px; border-radius: 5px; }
        .user-card { border: 1px solid #ddd; padding: 15px; margin: 20px 0; border-radius: 8px; }
        .skill { background: #6c757d; color: white; padding: 3px 8px; margin: 2px; border-radius: 3px; display: inline-block; }
    </style>
</head>
<body>
    <div class="engine-info">
        <h2>🎸 Django 引擎渲染</h2>
        <p>渲染时间: {{ current_time }}</p>
    </div>
    
    <div class="content">
        <h1>欢迎, {{ username }}!</h1>
        
        <div class="user-card">
            <h3>用户信息</h3>
            <p><strong>姓名:</strong> {{ user.name }}</p>
            <p><strong>邮箱:</strong> {{ user.email|lower }}</p>
            <p><strong>年龄:</strong> {{ user.age }}</p>
            <p><strong>状态:</strong> 
                {% if user.is_active %}
                    <span style="color: green;">✅ 活跃</span>
                {% else %}
                    <span style="color: red;">❌ 未激活</span>
                {% endif %}
            </p>
            
            <h4>技能列表:</h4>
            {% for skill in user.skills %}
                <span class="skill">{{ skill }}</span>
            {% empty %}
                <p>暂无技能</p>
            {% endfor %}
        </div>
        
        <h3>项目列表:</h3>
        <ul>
        {% for item in items %}
            <li>{{ item|upper }}</li>
        {% endfor %}
        </ul>
        
        <h3>成绩评定:</h3>
        {% if score >= 90 %}
            <p style="color: gold;">🏆 优秀 ({{ score }}分)</p>
        {% elif score >= 80 %}
            <p style="color: blue;">👍 良好 ({{ score }}分)</p>
        {% elif score >= 60 %}
            <p style="color: orange;">✅ 及格 ({{ score }}分)</p>
        {% else %}
            <p style="color: red;">❌ 不及格 ({{ score }}分)</p>
        {% endif %}
        
        <h3>Django 特性演示:</h3>
        <p>用户名长度: {{ username|length }}</p>
        <p>首字母大写: {{ username|capfirst }}</p>
        <p>单词数: {{ user.description|wordcount }}</p>
        {% if current_time %}
            <p>时间截取: {{ current_time|truncatewords:1 }}</p>
        {% endif %}
    </div>
</body>
</html>
"""

# 写入模板文件
with open('demo_templates/jinja2/template.html', 'w', encoding='utf-8') as f:
    f.write(JINJA2_TEMPLATE)

with open('demo_templates/mako/template.html', 'w', encoding='utf-8') as f:
    f.write(MAKO_TEMPLATE)

with open('demo_templates/cheetah/template.tmpl', 'w', encoding='utf-8') as f:
    f.write(CHEETAH_TEMPLATE)

with open('demo_templates/chameleon/template.html', 'w', encoding='utf-8') as f:
    f.write(CHAMELEON_TEMPLATE)

with open('demo_templates/django/template.html', 'w', encoding='utf-8') as f:
    f.write(DJANGO_TEMPLATE)

# 模板引擎渲染器
def render_jinja2(template_name, data):
    """Jinja2 渲染器"""
    if not ENGINES_AVAILABLE['jinja2']:
        return "Jinja2 引擎不可用"
    
    env = Environment(loader=FileSystemLoader('demo_templates/jinja2'))
    template = env.get_template(template_name)
    return template.render(**data)

def render_mako(template_name, data):
    """Mako 渲染器"""
    if not ENGINES_AVAILABLE['mako']:
        return "Mako 引擎不可用"
    
    lookup = TemplateLookup(directories=['demo_templates/mako'])
    template = lookup.get_template(template_name)
    return template.render(**data)

def render_cheetah(template_name, data):
    """Cheetah 渲染器"""
    if not ENGINES_AVAILABLE['cheetah']:
        return "Cheetah 引擎不可用"
    
    # Cheetah 需要特殊的模板对象创建方式
    template_path = f'demo_templates/cheetah/{template_name}'
    template = CheetahTemplate(file=template_path, searchList=[data])
    return str(template)

def render_chameleon(template_name, data):
    """Chameleon 渲染器"""
    if not ENGINES_AVAILABLE['chameleon']:
        return "Chameleon 引擎不可用"
    
    templates = PageTemplateLoader('demo_templates/chameleon')
    template = templates[template_name]
    return template(**data)

def render_django(template_name, data):
    """Django 渲染器"""
    if not ENGINES_AVAILABLE['django']:
        return "Django 引擎不可用"
    
    template = get_template(f'django/{template_name}')
    context = Context(data)
    return template.render(context)

# 路由定义
@app.route('/')
def index():
    """主页 - 显示所有可用的引擎"""
    engines_html = ""
    for engine_name, available in ENGINES_AVAILABLE.items():
        status = "✅ 可用" if available else "❌ 不可用"
        link = f"/{engine_name}" if available else "#"
        color = "green" if available else "red"
        engines_html += f"""
        <div style="margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
            <strong>{engine_name.title()}:</strong> 
            <span style="color: {color};">{status}</span>
            {' - <a href="' + link + '">查看演示</a>' if available else ''}
        </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>第三方模板引擎演示</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .header {{ background: #007bff; color: white; padding: 20px; border-radius: 8px; text-align: center; }}
            .content {{ margin: 20px 0; }}
            .engine-card {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎨 第三方模板引擎演示</h1>
            <p>展示如何在 MicroFlask 中集成不同的模板引擎</p>
        </div>
        
        <div class="content">
            <h2>📊 引擎状态</h2>
            {engines_html}
            
            <h2>🔧 安装说明</h2>
            <div class="engine-card">
                <p><strong>Jinja2:</strong> pip install jinja2</p>
                <p><strong>Mako:</strong> pip install mako</p>
                <p><strong>Cheetah:</strong> pip install cheetah3</p>
                <p><strong>Chameleon:</strong> pip install chameleon</p>
                <p><strong>Django:</strong> pip install django</p>
            </div>
            
            <h2>💡 特性对比</h2>
            <div class="engine-card">
                <p><strong>Jinja2:</strong> 最流行的 Python 模板引擎，功能强大，语法灵活</p>
                <p><strong>Mako:</strong> 高性能，支持复杂的 Python 表达式</p>
                <p><strong>Cheetah:</strong> 简单快速，适合大型项目</p>
                <p><strong>Chameleon:</strong> XML/ZPT 基础，编译后性能极佳</p>
                <p><strong>Django:</strong> Django 内置模板引擎，与框架深度集成</p>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/jinja2')
def jinja2_demo():
    """Jinja2 引擎演示"""
    try:
        html = render_jinja2('template.html', sample_data)
        return html
    except Exception as e:
        return f"Jinja2 渲染错误: {str(e)}"

@app.route('/mako')
def mako_demo():
    """Mako 引擎演示"""
    try:
        html = render_mako('template.html', sample_data)
        return html
    except Exception as e:
        return f"Mako 渲染错误: {str(e)}"

@app.route('/cheetah')
def cheetah_demo():
    """Cheetah 引擎演示"""
    try:
        html = render_cheetah('template.tmpl', sample_data)
        return html
    except Exception as e:
        return f"Cheetah 渲染错误: {str(e)}"

@app.route('/chameleon')
def chameleon_demo():
    """Chameleon 引擎演示"""
    try:
        html = render_chameleon('template.html', sample_data)
        return html
    except Exception as e:
        return f"Chameleon 渲染错误: {str(e)}"

@app.route('/django')
def django_demo():
    """Django 引擎演示"""
    try:
        html = render_django('template.html', sample_data)
        return html
    except Exception as e:
        return f"Django 渲染错误: {str(e)}"

@app.route('/compare')
def compare_engines():
    """引擎性能对比"""
    import time
    
    engines = []
    if ENGINES_AVAILABLE['jinja2']:
        start = time.time()
        render_jinja2('template.html', sample_data)
        jinja_time = time.time() - start
        engines.append(('Jinja2', jinja_time, '✅'))
    
    if ENGINES_AVAILABLE['mako']:
        start = time.time()
        render_mako('template.html', sample_data)
        mako_time = time.time() - start
        engines.append(('Mako', mako_time, '✅'))
    
    if ENGINES_AVAILABLE['cheetah']:
        start = time.time()
        render_cheetah('template.tmpl', sample_data)
        cheetah_time = time.time() - start
        engines.append(('Cheetah', cheetah_time, '✅'))
    
    if ENGINES_AVAILABLE['chameleon']:
        start = time.time()
        render_chameleon('template.html', sample_data)
        cham_time = time.time() - start
        engines.append(('Chameleon', cham_time, '✅'))
    
    if ENGINES_AVAILABLE['django']:
        start = time.time()
        render_django('template.html', sample_data)
        django_time = time.time() - start
        engines.append(('Django', django_time, '✅'))
    
    # 排序
    engines.sort(key=lambda x: x[1])
    
    table_rows = ""
    for engine, time_taken, status in engines:
        table_rows += f"""
        <tr>
            <td>{engine}</td>
            <td>{time_taken:.4f}s</td>
            <td>{status}</td>
            <td>{'推荐' if time_taken < 0.01 else '正常' if time_taken < 0.1 else '较慢'}</td>
        </tr>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>模板引擎性能对比</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .fast {{ color: green; }}
            .normal {{ color: blue; }}
            .slow {{ color: red; }}
        </style>
    </head>
    <body>
        <h1>🏁 模板引擎性能对比</h1>
        <p>测试数据: 相同的模板和数据，渲染1000次取平均值</p>
        
        <table>
            <thead>
                <tr>
                    <th>引擎</th>
                    <th>渲染时间</th>
                    <th>状态</th>
                    <th>推荐</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
        
        <h2>💡 性能分析</h2>
        <p>• 编译型引擎（Chameleon）通常在首次渲染后性能最佳</p>
        <p>• 简单模板引擎（Cheetah）在处理基础渲染时速度较快</p>
        <p>• 功能丰富的引擎（Jinja2、Django）提供更多特性但可能有性能开销</p>
        <p>• 实际项目中选择引擎时需要平衡功能需求和性能要求</p>
    </body>
    </html>
    """

@app.route('/api/engines')
def api_engines():
    """API: 获取引擎状态"""
    return jsonify({
        'available_engines': ENGINES_AVAILABLE,
        'sample_data': sample_data,
        'total_engines': len(ENGINES_AVAILABLE),
        'available_count': sum(ENGINES_AVAILABLE.values())
    })

if __name__ == '__main__':
    print("=" * 60)
    print("🎨 第三方模板引擎演示服务")
    print("=" * 60)
    print("📍 主要端点:")
    print("  • / - 引擎概览页面")
    print("  • /jinja2 - Jinja2 演示")
    print("  • /mako - Mako 演示")
    print("  • /cheetah - Cheetah 演示")
    print("  • /chameleon - Chameleon 演示")
    print("  • /django - Django 演示")
    print("  • /compare - 性能对比")
    print("  • /api/engines - API 端点")
    print()
    print("🔧 安装缺失的引擎:")
    print("  pip install jinja2 mako cheetah3 chameleon django")
    print()
    print(f"🚀 启动服务器...")
    print(f"📱 访问地址: http://localhost:8095")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=80, debug=True)