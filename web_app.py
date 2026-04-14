import streamlit as st
import json
import os
import datetime
import time

# 导入项目核心模块
from outline_generator import generate_outline
from retrieval import need_search, retrieve_context
from generator import generate_full_ppt
from validator import validate_slides
from ppt_generator import generate_ppt
from config import get_config, update_config
from template_manager import list_templates, set_current_template, get_current_template

# ================= 页面配置 =================
st.set_page_config(
    page_title="智创易演 轻量化PPT生成器",
    page_icon="✨",
    layout="wide"
)

# ================= 状态管理 =================
# 初始化 session_state 来保存跨页面的状态变量
if 'step' not in st.session_state:
    st.session_state.step = 'input'  # 当前所处阶段: input -> outline -> result
if 'topic' not in st.session_state:
    st.session_state.topic = ""
if 'num_slides' not in st.session_state:
    st.session_state.num_slides = 8
if 'outline' not in st.session_state:
    st.session_state.outline = None
if 'ppt_file' not in st.session_state:
    st.session_state.ppt_file = None

# ================= 侧边栏设置 =================
with st.sidebar:
    st.title("⚙️ 设置")
    
    # 1. 模板选择
    st.subheader("🎨 模板选择")
    templates = list_templates()
    template_options = {t['name']: t['id'] for t in templates}
    
    current_template = get_current_template()
    current_template_name = current_template.get('name', '默认简约')
    
    selected_template_name = st.selectbox(
        "请选择排版模板",
        options=list(template_options.keys()),
        index=list(template_options.keys()).index(current_template_name) if current_template_name in template_options else 0
    )
    # 自动更新所选模板
    if template_options[selected_template_name] != current_template.get('id'):
        set_current_template(template_options[selected_template_name])
        st.toast(f"已切换至 {selected_template_name} 模板", icon="✅")

    # 2. 系统参数设置 (获取当前配置)
    st.subheader("🛠️ 系统参数")
    config = get_config()
    
    outline_model = st.text_input("大纲生成模型", value=config['models'].get('outline', 'glm-5.1'))
    content_model = st.text_input("内容生成模型", value=config['models'].get('content', 'glm-5.1'))
    
    enable_api = st.checkbox("启用远程 API", value=config['api'].get('enable', True))
    enable_search = st.checkbox("启用百度检索", value=config['baidu_search'].get('enable', True))
    
    # 点击保存配置
    if st.button("保存系统配置"):
        update_config("models.outline", outline_model)
        update_config("models.content", content_model)
        update_config("api.enable", enable_api)
        update_config("baidu_search.enable", enable_search)
        st.success("配置已保存！")

# ================= 主界面区域 =================
st.title("✨ 智创易演 - 轻量化PPT自动生成")
# st.markdown("基于大语言模型，自动完成 **大纲规划** -> **联网检索** -> **内容生成** -> **排版渲染** 全流程。")

# ----------------- 阶段 1：输入主题 -----------------
if st.session_state.step == 'input':
    with st.container():
        st.header("1. 告诉我您想做什么主题？")
        topic_input = st.text_input("PPT 主题", placeholder="例如：人工智能的发展历程与未来趋势...", value=st.session_state.topic)
        num_slides_input = st.slider("目标页数（不含标题页）", min_value=3, max_value=20, value=st.session_state.num_slides)
        
        if st.button("🚀 第一步：生成 PPT 大纲", type="primary"):
            if not topic_input.strip():
                st.error("请输入有效的 PPT 主题！")
            else:
                st.session_state.topic = topic_input
                st.session_state.num_slides = num_slides_input
                
                with st.spinner("🤖 AI 正在飞速构思大纲，请稍候..."):
                    # 用于流式显示的框
                    stream_box = st.empty()
                    
                    outline_stream_state = {"content": ""}
                    def on_stream(text):
                        outline_stream_state["content"] += text
                        # 限制显示最后 20 行，保持代码框大小基本固定且实现自动向上滚动效果
                        lines = outline_stream_state["content"].split('\n')
                        if len(lines) > 20:
                            display_text = "...... (上方内容已自动折叠) ......\n" + '\n'.join(lines[-20:])
                        else:
                            display_text = outline_stream_state["content"]
                        stream_box.code(display_text, language="json")
                    
                    def on_fallback():
                        st.toast("⚠️ API连接失败或超时，自动降级为本地模型进行生成", icon="⚠️")
                        
                    # 调用大纲生成核心方法
                    outline_result = generate_outline(
                        topic_input, 
                        num_slides_input, 
                        stream_callback=on_stream,
                        on_fallback=on_fallback
                    )
                    stream_box.empty() # 生成结束后清空
                    
                    if outline_result and "slides" in outline_result:
                        st.session_state.outline = outline_result
                        st.session_state.step = 'outline'
                        st.rerun()
                    else:
                        st.error("大纲生成失败，请检查网络或 API 配置后重试。")

# ----------------- 阶段 2：大纲确认与编辑 -----------------
elif st.session_state.step == 'outline':
    if st.session_state.get('error_msg'):
        st.error(st.session_state.error_msg)
        st.session_state.error_msg = None  # 显示后立即清除，避免刷新一直存在

    st.header("2. 确认 PPT 大纲")
    st.info("💡 下方是大模型为您规划的结构。您可以直接在表格中进行修改（如：增删页面、修改标题、修改类型），完成后点击继续。")
    
    # 使用 data_editor 代替 text_area
    import pandas as pd
    
    outline_title = st.text_input("PPT 标题", value=st.session_state.outline.get("title", st.session_state.topic))
    
    # 提取 slides 数据用于表格展示
    slides_data = st.session_state.outline.get("slides", [])
    df = pd.DataFrame(slides_data)
    
    # 设置表格列配置
    column_config = {
        "title": st.column_config.TextColumn("页面标题", required=True),
        "type": st.column_config.SelectboxColumn("页面类型", options=["intro", "content", "summary"], required=True)
    }
    
    edited_df = st.data_editor(
        df,
        column_config=column_config,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ 确认，开始生成", type="primary", use_container_width=True):
            # 将编辑后的数据转回 JSON 格式
            updated_slides = edited_df.to_dict('records')
            st.session_state.outline = {
                "title": outline_title,
                "slides": updated_slides
            }
            st.session_state.step = 'generating'
            st.rerun()
                
    with col2:
        if st.button("🔄 不满意，返回重设", use_container_width=True):
            st.session_state.step = 'input'
            st.rerun()

# ----------------- 阶段 3：生成详情与排版 -----------------
elif st.session_state.step == 'generating':
    st.header("3. 正在生成与排版...")
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # ================= 执行核心流程 =================
    try:
        # 1. 检索信息
        status_text.text("🔍 [1/3] 正在判断是否需要联网检索背景资料...")
        time.sleep(0.5)
        context = ""
        if need_search(st.session_state.topic):
            status_text.text("🌐 [1/3] 正在使用百度搜索获取最新参考资料...")
            context = retrieve_context(st.session_state.topic)
        progress_bar.progress(33)
        
        # 2. 生成正文
        status_text.text("✍️ [2/3] AI 正在逐页撰写 PPT 详细内容，可能需要 1-2 分钟，请耐心等待...")
        
        # 用于流式显示的框
        content_stream_box = st.empty()
        
        # 使用可变对象存储 stream_content，避免回调函数内部作用域问题
        stream_state = {"content": ""}
        def on_content_stream(text):
            stream_state["content"] += text
            # 限制显示最后 20 行，保持代码框大小基本固定且实现自动向上滚动效果
            lines = stream_state["content"].split('\n')
            if len(lines) > 20:
                display_text = "...... (上方内容已自动折叠) ......\n" + '\n'.join(lines[-20:])
            else:
                display_text = stream_state["content"]
            content_stream_box.code(display_text, language="json")
            
        def on_content_fallback():
            st.toast("⚠️ API连接失败或超时，自动降级为本地模型进行生成", icon="⚠️")

        slides = generate_full_ppt(
            st.session_state.topic, 
            st.session_state.outline, 
            context,
            stream_callback=on_content_stream,
            on_fallback=on_content_fallback
        )
        content_stream_box.empty() # 生成结束后清空
        
        if not slides:
            st.session_state.error_msg = "❌ 内容生成失败！模型可能返回了异常的数据格式，自动还原至上一步，您的大纲修改已保留，可以直接尝试再次生成。"
            st.session_state.step = 'outline'
            st.rerun()
            
        validated_slides = validate_slides(slides)
        progress_bar.progress(66)
        
        # 3. 渲染排版
        status_text.text("🎨 [3/3] 正在调用 python-pptx 渲染排版，生成文件...")
        ppt_data = {
            "title": st.session_state.topic,
            "slides": validated_slides
        }
        
        current_time = datetime.datetime.now().strftime("%Y%m%d%H%M")
        safe_topic = st.session_state.topic.replace(" ", "_").replace("/", "_").replace("\\", "_")
        output_filename = f"{safe_topic}_{current_time}.pptx"
        
        template_config = get_current_template()
        success = generate_ppt(ppt_data, output_filename, template_config)
        progress_bar.progress(100)
        
        if success:
            st.session_state.ppt_file = output_filename
            st.session_state.step = 'done'
            st.rerun()
        else:
            st.session_state.error_msg = "❌ 渲染文件时发生错误，请查看控制台日志。您可以调整大纲后重试。"
            st.session_state.step = 'outline'
            st.rerun()
            
    except Exception as e:
        st.session_state.error_msg = f"❌ 发生未知错误: {e}。已为您保留当前大纲状态，您可以重试。"
        st.session_state.step = 'outline'
        st.rerun()

# ----------------- 阶段 4：生成完成 -----------------
elif st.session_state.step == 'done':
    st.success("🎉 生成完毕！")
    st.balloons()
    
    file_path = st.session_state.ppt_file
    if os.path.exists(file_path):
        with open(file_path, "rb") as file:
            btn = st.download_button(
                label="⬇️ 点击下载 PPT 文件",
                data=file,
                file_name=os.path.basename(file_path),
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                type="primary"
            )
    else:
        st.error("找不到生成的文件。")
    
    st.markdown("---")
    if st.button("✨ 再来一份！"):
        # 清除状态回到第一步
        st.session_state.step = 'input'
        st.session_state.outline = None
        st.session_state.ppt_file = None
        st.rerun()
