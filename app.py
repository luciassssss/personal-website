import streamlit as st
import jinja2
import pdfkit
import os
from datetime import datetime
import base64
import tempfile

# 设置页面配置
st.set_page_config(
    page_title="简历排版工具",
    page_icon="📝",
    layout="wide"
)

# 创建必要的目录
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

# 创建HTML模板
resume_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{ name }}的简历</title>
    <style>
        body {
            font-family: 'Microsoft YaHei', sans-serif;
            line-height: 1.6;
            margin: 40px;
            color: #333;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .section {
            margin-bottom: 20px;
        }
        .section-title {
            border-bottom: 2px solid #2c3e50;
            padding-bottom: 5px;
            margin-bottom: 15px;
            color: #2c3e50;
        }
        .contact-info {
            text-align: center;
            margin-bottom: 20px;
        }
        .experience-item {
            margin-bottom: 15px;
        }
        .date {
            color: #666;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ name }}</h1>
        <div class="contact-info">
            <p>电话：{{ phone }} | 邮箱：{{ email }}</p>
        </div>
    </div>

    <div class="section">
        <h2 class="section-title">教育背景</h2>
        {{ education }}
    </div>

    <div class="section">
        <h2 class="section-title">工作经验</h2>
        {{ experience }}
    </div>

    <div class="section">
        <h2 class="section-title">技能</h2>
        {{ skills }}
    </div>
</body>
</html>
"""

# 保存模板
with open("templates/resume_template.html", "w", encoding="utf-8") as f:
    f.write(resume_template)

def create_pdf(html_content):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        # 配置pdfkit选项
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': 'UTF-8',
            'no-outline': None
        }
        pdfkit.from_string(html_content, tmp.name, options=options)
        return tmp.name

def get_download_link(file_path, file_name):
    with open(file_path, "rb") as f:
        bytes = f.read()
        b64 = base64.b64encode(bytes).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="{file_name}">点击下载PDF文件</a>'
        return href

# Streamlit界面
st.title("📝 简历排版工具")

# 基本信息输入
st.header("基本信息")
name = st.text_input("姓名")
phone = st.text_input("电话")
email = st.text_input("邮箱")

# 教育背景
st.header("教育背景")
education = st.text_area("教育经历（支持HTML格式）", height=150)

# 工作经验
st.header("工作经验")
experience = st.text_area("工作经历（支持HTML格式）", height=200)

# 技能
st.header("技能")
skills = st.text_area("技能列表（支持HTML格式）", height=150)

# 生成简历
if st.button("生成简历"):
    if name and phone and email:
        # 使用Jinja2渲染模板
        template = jinja2.Template(resume_template)
        html_content = template.render(
            name=name,
            phone=phone,
            email=email,
            education=education,
            experience=experience,
            skills=skills
        )

        # 显示HTML预览
        st.header("简历预览")
        st.components.v1.html(html_content, height=800, scrolling=True)

        try:
            # 生成PDF并提供下载
            pdf_path = create_pdf(html_content)
            st.markdown(get_download_link(pdf_path, f"{name}_简历.pdf"), unsafe_allow_html=True)
            
            # 清理临时文件
            os.unlink(pdf_path)
        except Exception as e:
            st.error(f"PDF生成失败：{str(e)}")
            st.info("请确保已安装wkhtmltopdf。在macOS上，可以使用以下命令安装：\nbrew install wkhtmltopdf")
    else:
        st.error("请填写所有必填字段！") 