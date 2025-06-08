import streamlit as st
import jinja2
import os
import base64
import requests
from io import BytesIO
import json
from datetime import datetime
import shutil

# 设置页面配置
st.set_page_config(
    page_title="个人主页生成器",
    page_icon="🌟",
    layout="wide"
)

# 创建必要的目录
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)
os.makedirs("configs", exist_ok=True)
os.makedirs("styles", exist_ok=True)

# 预设样式
PRESET_STYLES = {
    "默认样式": "",
    "简约风格": """
        .section {
            padding: 2rem 0;
            border-bottom: 1px solid #eee;
        }
        .card {
            transition: transform 0.3s ease;
        }
        .card:hover {
            transform: translateY(-5px);
        }
    """,
    "现代风格": """
        .section {
            padding: 3rem 0;
            position: relative;
        }
        .section::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 50px;
            height: 3px;
            background: linear-gradient(to right, #3b82f6, #8b5cf6);
        }
        .card {
            border-radius: 15px;
            overflow: hidden;
        }
    """,
    "科技风格": """
        .section {
            background: linear-gradient(45deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 20px;
            margin: 2rem 0;
            padding: 2rem;
        }
        .card {
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(5px);
            border: 1px solid rgba(255,255,255,0.1);
        }
    """
}

# 定义主题
THEMES = {
    "默认主题": {
        "primary": "#93c5fd",      # 浅蓝色
        "secondary": "#f8fafc",    # 浅灰背景
        "accent": "#1e40af",       # 深蓝色
        "background": "#ffffff",   # 纯白背景
        "text": "#1e40af",         # 深蓝色文字
        "light_text": "#1e40af",   # 深蓝色文字
        "border": "#e5e7eb",       # 浅灰边框
        "hover": "#dbeafe",        # 浅蓝悬停
        "card_background": "#ffffff", # 白色卡片
        "gradient": "linear-gradient(135deg, #93c5fd 0%, #1e40af 100%)"
    },
    "暗色主题": {
        "primary": "#60a5fa",      # 浅蓝色
        "secondary": "#111827",    # 深灰背景
        "accent": "#1e40af",       # 深蓝色
        "background": "#0f172a",   # 深蓝背景
        "text": "#ffffff",         # 纯白文字
        "light_text": "#ffffff",   # 纯白文字
        "border": "#1f2937",       # 深灰边框
        "hover": "#1e293b",        # 深灰悬停
        "card_background": "#1f2937", # 深灰卡片
        "gradient": "linear-gradient(135deg, #60a5fa 0%, #1e40af 100%)"
    },
    "森林主题": {
        "primary": "#86efac",      # 浅绿色
        "secondary": "#f0fdf4",    # 浅灰背景
        "accent": "#065f46",       # 深绿色
        "background": "#ffffff",   # 纯白背景
        "text": "#065f46",         # 深绿色文字
        "light_text": "#065f46",   # 深绿色文字
        "border": "#e5e7eb",       # 浅灰边框
        "hover": "#dcfce7",        # 浅绿悬停
        "card_background": "#ffffff", # 白色卡片
        "gradient": "linear-gradient(135deg, #86efac 0%, #065f46 100%)"
    },
    "日落主题": {
        "primary": "#fdba74",      # 浅橙色
        "secondary": "#fffbeb",    # 浅灰背景
        "accent": "#b45309",       # 深橙色
        "background": "#ffffff",   # 纯白背景
        "text": "#b45309",         # 深橙色文字
        "light_text": "#b45309",   # 深橙色文字
        "border": "#e5e7eb",       # 浅灰边框
        "hover": "#fef3c7",        # 浅橙悬停
        "card_background": "#ffffff", # 白色卡片
        "gradient": "linear-gradient(135deg, #fdba74 0%, #b45309 100%)"
    },
    "极光主题": {
        "primary": "#c4b5fd",      # 浅紫色
        "secondary": "#f5f3ff",    # 浅灰背景
        "accent": "#5b21b6",       # 深紫色
        "background": "#ffffff",   # 纯白背景
        "text": "#5b21b6",         # 深紫色文字
        "light_text": "#5b21b6",   # 深紫色文字
        "border": "#e5e7eb",       # 浅灰边框
        "hover": "#ede9fe",        # 浅紫悬停
        "card_background": "#ffffff", # 白色卡片
        "gradient": "linear-gradient(135deg, #c4b5fd 0%, #5b21b6 100%)"
    },
    "海洋主题": {
        "primary": "#7dd3fc",      # 浅蓝色
        "secondary": "#f0f9ff",    # 浅灰背景
        "accent": "#075985",       # 深蓝色
        "background": "#ffffff",   # 纯白背景
        "text": "#075985",         # 深蓝色文字
        "light_text": "#075985",   # 深蓝色文字
        "border": "#e5e7eb",       # 浅灰边框
        "hover": "#e0f2fe",        # 浅蓝悬停
        "card_background": "#ffffff", # 白色卡片
        "gradient": "linear-gradient(135deg, #7dd3fc 0%, #075985 100%)"
    },
    "沙漠主题": {
        "primary": "#fcd34d",      # 浅黄色
        "secondary": "#fffbeb",    # 浅灰背景
        "accent": "#92400e",       # 深棕色
        "background": "#ffffff",   # 纯白背景
        "text": "#92400e",         # 深棕色文字
        "light_text": "#92400e",   # 深棕色文字
        "border": "#e5e7eb",       # 浅灰边框
        "hover": "#fef3c7",        # 浅棕悬停
        "card_background": "#ffffff", # 白色卡片
        "gradient": "linear-gradient(135deg, #fcd34d 0%, #92400e 100%)"
    },
    "星空主题": {
        "primary": "#a5b4fc",      # 浅靛蓝
        "secondary": "#eef2ff",    # 浅灰背景
        "accent": "#3730a3",       # 深靛蓝
        "background": "#ffffff",   # 纯白背景
        "text": "#3730a3",         # 深靛蓝文字
        "light_text": "#3730a3",   # 深靛蓝文字
        "border": "#e5e7eb",       # 浅灰边框
        "hover": "#e0e7ff",        # 浅靛蓝悬停
        "card_background": "#ffffff", # 白色卡片
        "gradient": "linear-gradient(135deg, #a5b4fc 0%, #3730a3 100%)"
    },
    "樱花主题": {
        "primary": "#f9a8d4",      # 浅粉色
        "secondary": "#fdf2f8",    # 浅灰背景
        "accent": "#9d174d",       # 深粉色
        "background": "#ffffff",   # 纯白背景
        "text": "#9d174d",         # 深粉色文字
        "light_text": "#9d174d",   # 深粉色文字
        "border": "#e5e7eb",       # 浅灰边框
        "hover": "#fce7f3",        # 浅粉悬停
        "card_background": "#ffffff", # 白色卡片
        "gradient": "linear-gradient(135deg, #f9a8d4 0%, #9d174d 100%)"
    }
}

# 技能图标配置
SKILL_ICONS = {
    "编程开发": {
        "Python": "fab fa-python",
        "JavaScript": "fab fa-js",
        "Java": "fab fa-java",
        "C++": "fas fa-code",
        "HTML5": "fab fa-html5",
        "CSS3": "fab fa-css3-alt",
        "React": "fab fa-react",
        "Node.js": "fab fa-node-js",
        "Git": "fab fa-git-alt",
        "Docker": "fab fa-docker"
    },
    "数据库": {
        "MySQL": "fas fa-database",
        "MongoDB": "fas fa-database",
        "PostgreSQL": "fas fa-database",
        "Redis": "fas fa-database"
    },
    "设计工具": {
        "Photoshop": "fab fa-adobe",
        "Illustrator": "fab fa-adobe",
        "Figma": "fab fa-figma",
        "Sketch": "fab fa-sketch"
    },
    "其他技能": {
        "项目管理": "fas fa-tasks",
        "数据分析": "fas fa-chart-bar",
        "机器学习": "fas fa-brain",
        "云计算": "fas fa-cloud",
        "网络安全": "fas fa-shield-alt",
        "移动开发": "fas fa-mobile-alt",
        "测试": "fas fa-vial",
        "文档": "fas fa-file-alt"
    }
}

# 创建HTML模板
personal_page_template = """
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ name }}的个人主页</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap');
        body {
            font-family: 'PingFang SC', '苹方', sans-serif;
        }
        {{ custom_css }}
    </style>
</head>
<body class="{{ theme.bg }}">
    <!-- 导航栏 -->
    <nav class="{{ theme.card }} shadow-lg fixed w-full z-10">
        <div class="max-w-6xl mx-auto px-4">
            <div class="flex justify-between items-center h-16">
                <div class="text-xl font-bold {{ theme.text }}">{{ name }}</div>
                <div class="flex space-x-4">
                    <a href="#about" class="{{ theme.text }} hover:text-gray-900">关于我</a>
                    <a href="#skills" class="{{ theme.text }} hover:text-gray-900">技能</a>
                    <a href="#projects" class="{{ theme.text }} hover:text-gray-900">项目</a>
                    <a href="#contact" class="{{ theme.text }} hover:text-gray-900">联系我</a>
                </div>
            </div>
        </div>
    </nav>

    <!-- 头部区域 -->
    <header class="pt-24 pb-12 bg-gradient-to-r {{ theme.primary }}">
        <div class="max-w-6xl mx-auto px-4 text-center">
            <div class="flex justify-center mb-8">
                <img src="{{ avatar_url }}" alt="{{ name }}" class="w-32 h-32 rounded-full border-4 border-white shadow-lg">
            </div>
            <h1 class="text-4xl font-bold text-white mb-4">{{ name }}</h1>
            <p class="text-xl text-white opacity-90">{{ title }}</p>
        </div>
    </header>

    <!-- 关于我 -->
    <section id="about" class="py-16 {{ theme.card }}">
        <div class="max-w-6xl mx-auto px-4">
            <h2 class="text-3xl font-bold {{ theme.text }} mb-8 text-center">关于我</h2>
            <div class="prose max-w-3xl mx-auto">
                {{ about }}
            </div>
        </div>
    </section>

    <!-- 技能 -->
    <section id="skills" class="py-16 {{ theme.bg }}">
        <div class="max-w-6xl mx-auto px-4">
            <h2 class="text-3xl font-bold {{ theme.text }} mb-8 text-center">技能专长</h2>
            <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                {% for skill in skills %}
                <div class="{{ theme.card }} p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
                    <div class="text-4xl text-blue-500 mb-4">
                        <i class="{{ skill.icon }}"></i>
                    </div>
                    <h3 class="text-lg font-semibold {{ theme.text }}">{{ skill.name }}</h3>
                    <p class="text-gray-600">{{ skill.description }}</p>
                </div>
                {% endfor %}
            </div>
        </div>
    </section>

    <!-- 项目 -->
    <section id="projects" class="py-16 {{ theme.card }}">
        <div class="max-w-6xl mx-auto px-4">
            <h2 class="text-3xl font-bold {{ theme.text }} mb-8 text-center">项目展示</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {% for project in projects %}
                <div class="{{ theme.card }} rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
                    <div class="relative">
                        <img src="{{ project.image }}" alt="{{ project.name }}" class="w-full h-48 object-cover">
                        <div class="absolute top-4 right-4 text-2xl text-white bg-black bg-opacity-50 p-2 rounded-full">
                            <i class="{{ project.icon }}"></i>
                        </div>
                    </div>
                    <div class="p-6">
                        <h3 class="text-xl font-semibold {{ theme.text }} mb-2">{{ project.name }}</h3>
                        <p class="text-gray-600 mb-4">{{ project.description }}</p>
                        <div class="flex space-x-4">
                            {% if project.github %}
                            <a href="{{ project.github }}" class="text-blue-500 hover:text-blue-700" target="_blank">
                                <i class="fab fa-github"></i> GitHub
                            </a>
                            {% endif %}
                            {% if project.demo %}
                            <a href="{{ project.demo }}" class="text-blue-500 hover:text-blue-700" target="_blank">
                                <i class="fas fa-external-link-alt"></i> 演示
                            </a>
                            {% endif %}
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </section>

    <!-- 联系方式 -->
    <section id="contact" class="py-16 {{ theme.bg }}">
        <div class="max-w-6xl mx-auto px-4">
            <h2 class="text-3xl font-bold {{ theme.text }} mb-8 text-center">联系我</h2>
            <div class="flex justify-center space-x-8">
                {{ contact_html }}
            </div>
        </div>
    </section>

    <!-- 页脚 -->
    <footer class="bg-gray-800 text-white py-8">
        <div class="max-w-6xl mx-auto px-4 text-center">
            <p>&copy; {{ year }} {{ name }}. All rights reserved.</p>
        </div>
    </footer>
</body>
</html>
"""

# 保存模板
with open("templates/personal_page_template.html", "w", encoding="utf-8") as f:
    f.write(personal_page_template)

def get_default_avatar():
    return "https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y"

def save_style(style_name, style_content):
    """保存自定义样式"""
    filename = f"styles/{style_name}.css"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(style_content)
    return filename

def load_style(style_name):
    """加载自定义样式"""
    filename = f"styles/{style_name}.css"
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def get_saved_styles():
    """获取所有保存的样式"""
    styles = {}
    for file in os.listdir("styles"):
        if file.endswith(".css"):
            style_name = file[:-4]
            styles[style_name] = load_style(style_name)
    return styles

def save_config(data):
    """保存配置到文件"""
    filename = f"configs/{data['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return filename

def load_config(filename):
    """从文件加载配置"""
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def delete_config(filename):
    """删除配置文件"""
    os.remove(os.path.join("configs", filename))

def copy_config(filename):
    """复制配置文件"""
    new_filename = f"{filename[:-5]}_copy.json"
    shutil.copy2(os.path.join("configs", filename), os.path.join("configs", new_filename))
    return new_filename

def generate_page(data):
    """生成个人主页HTML内容"""
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{data["name"]} - 个人主页</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            /* 基础样式 */
            body {{
                font-family: 'Microsoft YaHei', sans-serif;
                line-height: 1.6;
                color: {data["theme"]["text"]};
                background: {data["theme"]["background"]};
                margin: 0;
                padding: 0;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 2rem;
            }}
            
            /* 头部样式 */
            header {{
                background: {data["theme"]["gradient"]};
                padding: 3rem 0;
                margin-bottom: 2rem;
                border-radius: 1rem;
            }}
            
            .profile {{
                display: flex;
                align-items: center;
                gap: 2rem;
                padding: 0 2rem;
            }}
            
            .profile-image img {{
                width: 150px;
                height: 150px;
                border-radius: 50%;
                border: 4px solid {data["theme"]["primary"]};
                object-fit: cover;
            }}
            
            .profile-info h1 {{
                color: {data["theme"]["primary"]};
                margin: 0;
                font-size: 2.5rem;
            }}
            
            .profile-info .title {{
                color: {data["theme"]["accent"]};
                font-size: 1.2rem;
                margin: 0.5rem 0;
            }}
            
            .profile-info .about {{
                color: {data["theme"]["light_text"]};
                margin: 1rem 0;
            }}
            
            /* 技能部分 */
            .skills-section {{
                background: {data["theme"]["card_background"]};
                padding: 2rem;
                border-radius: 1rem;
                margin-bottom: 2rem;
            }}
            
            .skills-section h2 {{
                color: {data["theme"]["primary"]};
                margin-bottom: 1.5rem;
            }}
            
            .skills-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 1rem;
            }}
            
            .skill-card {{
                background: {data["theme"]["background"]};
                padding: 1rem;
                border-radius: 0.5rem;
                text-align: center;
                transition: transform 0.3s ease;
            }}
            
            .skill-card:hover {{
                transform: translateY(-5px);
            }}
            
            .skill-card i {{
                font-size: 2rem;
                color: {data["theme"]["primary"]};
                margin-bottom: 0.5rem;
            }}
            
            /* 项目部分 */
            .projects-section {{
                background: {data["theme"]["card_background"]};
                padding: 2rem;
                border-radius: 1rem;
                margin-bottom: 2rem;
            }}
            
            .projects-section h2 {{
                color: {data["theme"]["primary"]};
                margin-bottom: 1.5rem;
            }}
            
            .project-card {{
                background: {data["theme"]["background"]};
                padding: 1.5rem;
                border-radius: 0.5rem;
                margin-bottom: 1rem;
            }}
            
            .project-card h3 {{
                color: {data["theme"]["primary"]};
                margin: 0 0 0.5rem 0;
            }}
            
            .project-card .project-type {{
                color: {data["theme"]["accent"]};
                margin-bottom: 1rem;
            }}
            
            .project-card p {{
                color: {data["theme"]["text"]};
                margin: 0;
            }}
            
            /* 联系方式部分 */
            .contact-section {{
                background: {data["theme"]["card_background"]};
                padding: 2rem;
                border-radius: 1rem;
            }}
            
            .contact-section h2 {{
                color: {data["theme"]["primary"]};
                margin-bottom: 1.5rem;
            }}
            
            .contact-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 1rem;
            }}
            
            .contact-item {{
                display: flex;
                align-items: center;
                gap: 0.5rem;
                color: {data["theme"]["text"]};
            }}
            
            .contact-item i {{
                color: {data["theme"]["primary"]};
            }}
            
            /* 自定义样式 */
            {data.get("custom_css", "")}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <div class="profile">
                    <div class="profile-image">
                        <img src="{data.get('avatar_url', get_default_avatar())}" alt="{data["name"]}">
                    </div>
                    <div class="profile-info">
                        <h1>{data["name"]}</h1>
                        <p class="title">{data["title"]}</p>
                        <p class="about">{data.get("about", "这个人很懒，什么都没写...")}</p>
                    </div>
                </div>
            </header>
            
            <section class="skills-section">
                <h2>技能特长</h2>
                <div class="skills-grid">
                    {generate_skills_html(data["skills"])}
                </div>
            </section>
            
            <section class="projects-section">
                <h2>项目经历</h2>
                {generate_projects_html(data["projects"])}
            </section>
            
            <section class="contact-section">
                <h2>联系方式</h2>
                <div class="contact-grid">
                    {generate_contact_html(data["contacts"])}
                </div>
            </section>
        </div>
    </body>
    </html>
    """
    return html_content

def generate_skills_html(skills):
    """生成技能部分的HTML"""
    html = ""
    for skill in skills:
        html += f"""
        <div class="skill-card">
            <i class="{skill['icon']}"></i>
            <p>{skill['name']}</p>
            <p>{skill['description']}</p>
        </div>
        """
    return html

def generate_projects_html(projects):
    """生成项目部分的HTML"""
    html = ""
    for project in projects:
        icon_map = {
            "网站开发": "fas fa-globe",
            "移动应用": "fas fa-mobile-alt",
            "数据分析": "fas fa-chart-bar",
            "机器学习": "fas fa-brain",
            "其他": "fas fa-code"
        }
        icon = icon_map.get(project["type"], "fas fa-code")
        html += f"""
        <div class="project-card">
            <h3>{project['name']}</h3>
            <div class="project-type">
                <i class="{icon}"></i>
                {project['type']}
            </div>
            <p>{project['description']}</p>
        </div>
        """
    return html

def generate_contact_html(contacts):
    """生成联系方式部分的HTML"""
    html = ""
    for contact in contacts:
        icon_map = {
            "邮箱": "fas fa-envelope",
            "微信": "fab fa-weixin",
            "GitHub": "fab fa-github",
            "LinkedIn": "fab fa-linkedin",
            "个人网站": "fas fa-globe",
            "电话": "fas fa-phone",
            "微信公众号": "fab fa-weixin"
        }
        icon = icon_map.get(contact["type"], "fas fa-link")
        html += f"""
        <div class="contact-item">
            <i class="{icon}"></i>
            <span>{contact['value']}</span>
        </div>
        """
    return html

# 添加必填字段验证函数
def validate_required_fields(data):
    missing_fields = []
    
    # 基本信息验证
    if not data.get("name"):
        missing_fields.append("姓名")
    if not data.get("title"):
        missing_fields.append("职位")
    if not data.get("about"):
        missing_fields.append("个人简介")
    
    # 联系方式验证
    if not data.get("contacts"):
        missing_fields.append("至少一个联系方式")
    
    # 技能验证
    if not data.get("skills"):
        missing_fields.append("至少一个技能")
    
    # 项目验证
    if not data.get("projects"):
        missing_fields.append("至少一个项目")
    
    return missing_fields

# 添加必填字段标记的样式
required_field_style = """
<style>
.required-field::after {
    content: " *";
    color: red;
}
.error-message {
    color: red;
    font-size: 0.8em;
    margin-top: 5px;
}
</style>
"""
st.markdown(required_field_style, unsafe_allow_html=True)

# Streamlit界面
st.title("🌟 个人主页生成器")

# 侧边栏配置
with st.sidebar:
    st.header("主题设置")
    theme = st.selectbox("选择主题", list(THEMES.keys()), key="theme_selector")
    
    # 显示主题预览
    st.subheader("主题预览")
    preview_html = f"""
    <div style="padding: 20px; border-radius: 8px; background: {THEMES[theme]['gradient']}; color: white; margin-bottom: 20px;">
        <h3 style="margin: 0;">主题预览</h3>
    </div>
    <div style="display: flex; gap: 20px; margin-bottom: 20px;">
        <div style="flex: 1; padding: 15px; border: 1px solid {THEMES[theme]['border']}; border-radius: 8px; background: {THEMES[theme]['card_background']};">
            <h4 style="color: {THEMES[theme]['text']}; margin: 0 0 10px 0;">卡片样式</h4>
            <p style="color: {THEMES[theme]['light_text']}; margin: 0;">这是卡片内容的示例</p>
        </div>
        <div style="flex: 1; padding: 15px; border: 1px solid {THEMES[theme]['border']}; border-radius: 8px; background: {THEMES[theme]['card_background']};">
            <h4 style="color: {THEMES[theme]['text']}; margin: 0 0 10px 0;">文本样式</h4>
            <p style="color: {THEMES[theme]['light_text']}; margin: 0;">主要文本颜色</p>
            <p style="color: {THEMES[theme]['primary']}; margin: 5px 0 0 0;">强调色文本</p>
        </div>
    </div>
    """
    st.markdown(preview_html, unsafe_allow_html=True)
    
    # 自定义CSS
    st.subheader("自定义样式")
    st.markdown("""
    您可以添加自定义CSS来进一步调整页面样式。例如：
    ```css
    /* 修改字体 */
    body {
        font-family: 'Your Font', sans-serif;
    }

    /* 添加动画效果 */
    .skill-card {
        transition: transform 0.3s ease;
    }

    /* 自定义阴影 */
    .project-card {
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    ```
    """)
    custom_css = st.text_area("自定义CSS（可选）", height=200)

# 基本信息
st.header("基本信息")
st.markdown('<div class="required-field">姓名</div>', unsafe_allow_html=True)
name = st.text_input("", key="name")
st.markdown('<div class="required-field">职位</div>', unsafe_allow_html=True)
title = st.text_input("", key="title")
st.markdown('<div class="required-field">个人简介</div>', unsafe_allow_html=True)
about = st.text_area("", key="about")
st.markdown('<div class="required-field">头像URL</div>', unsafe_allow_html=True)
avatar_url = st.text_input("", key="avatar_url", value=get_default_avatar())

# 技能
st.header("技能")
st.markdown('<div class="required-field">至少添加一个技能</div>', unsafe_allow_html=True)
num_skills = st.number_input("技能数量", min_value=1, max_value=10, value=1, key="num_skills")
skills = []
for i in range(num_skills):
    with st.expander(f"技能 {i+1}"):
        skill_name = st.text_input("技能名称", key=f"skill_name_{i}")
        
        # 图标选择
        st.subheader("选择技能")
        icon_category = st.selectbox(
            "选择图标类别",
            list(SKILL_ICONS.keys()),
            key=f"icon_category_{i}"
        )
        
        # 创建图标选择按钮的样式
        icon_style = """
        <style>
        .icon-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
            margin-bottom: 20px;
        }
        .icon-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 10px;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            background: white;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .icon-item:hover {
            background: #f8fafc;
            transform: translateY(-2px);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .icon-item.selected {
            border-color: #3b82f6;
            background: #f0f9ff;
        }
        .icon-item i {
            font-size: 2em;
            color: #1f77b4;
            margin-bottom: 8px;
        }
        .icon-item p {
            margin: 0;
            font-size: 0.9em;
            color: #4b5563;
        }
        </style>
        """
        st.markdown(icon_style, unsafe_allow_html=True)

        # 使用Streamlit的radio组件来选择图标
        icon_options = {f"{icon_name}": icon_class for icon_name, icon_class in SKILL_ICONS[icon_category].items()}
        selected_icon_name = st.radio(
            "选择技能",
            options=list(icon_options.keys()),
            key=f"skill_icon_{i}",
            horizontal=True,
            label_visibility="collapsed"
        )
        
        # 显示选中的图标
        if selected_icon_name:
            selected_icon = icon_options[selected_icon_name]
            st.markdown(f"""
                <div style='text-align: center; padding: 15px; background: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0;'>
                    <i class='{selected_icon}' style='font-size: 2em; color: #1f77b4;'></i>
                    <p style='margin-top: 8px; color: #4b5563;'>已选择此技能</p>
                </div>
            """, unsafe_allow_html=True)
            st.session_state[f"selected_icon_{i}"] = selected_icon
        
        skill_description = st.text_area("技能描述", key=f"skill_desc_{i}")
        if skill_name and skill_description and selected_icon:
            skills.append({
                "name": skill_name,
                "icon": selected_icon,
                "description": skill_description
            })

# 项目
st.header("项目经历")
num_projects = st.number_input("项目数量", min_value=1, max_value=10, value=1, key="num_projects")
projects = []

for i in range(num_projects):
    st.markdown(f"### 项目 {i+1}")
    project_name = st.text_input("项目名称", key=f"project_name_{i}")
    project_type = st.selectbox(
        "项目类型",
        ["网站开发", "移动应用", "数据分析", "机器学习", "其他"],
        key=f"project_type_{i}"
    )
    project_icon = {
        "网站开发": "fas fa-globe",
        "移动应用": "fas fa-mobile-alt",
        "数据分析": "fas fa-chart-bar",
        "机器学习": "fas fa-brain",
        "其他": "fas fa-code"
    }.get(project_type, "fas fa-code")
    project_description = st.text_area("项目描述", key=f"project_desc_{i}")
    
    projects.append({
        "name": project_name,
        "type": project_type,
        "icon": project_icon,
        "description": project_description
    })

# 联系方式
st.header("联系方式")
st.markdown('<div class="required-field">至少添加一个联系方式</div>', unsafe_allow_html=True)
num_contacts = st.number_input("联系方式数量", min_value=1, max_value=10, value=1, key="num_contacts")
contacts = []

for i in range(num_contacts):
    st.markdown(f"### 联系方式 {i+1}")
    contact_type = st.selectbox(
        "类型",
        ["邮箱", "微信", "GitHub", "LinkedIn", "个人网站", "电话", "微信公众号"],
        key=f"contact_type_{i}"
    )
    contact_value = st.text_input("内容", key=f"contact_value_{i}")
    
    contacts.append({
        "type": contact_type,
        "value": contact_value
    })

# 生成按钮
if st.button("生成个人主页"):
    # 验证必填字段
    data = {
        "name": name,
        "title": title,
        "about": about,
        "avatar_url": avatar_url,
        "contacts": contacts,
        "skills": skills,
        "projects": projects,
        "theme": THEMES[theme],
        "custom_css": custom_css
    }
    
    missing_fields = validate_required_fields(data)
    
    if missing_fields:
        error_message = "请填写以下必填字段：\n" + "\n".join([f"❌ {field}" for field in missing_fields])
        st.error(error_message)
    else:
        # 生成HTML
        html_content = generate_page(data)
        
        # 显示预览
        st.header("预览")
        st.components.v1.html(html_content, height=800, scrolling=True)
        
        # 下载按钮
        st.download_button(
            label="下载HTML文件",
            data=html_content,
            file_name="personal_page.html",
            mime="text/html"
        ) 