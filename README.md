# 智创易演 (AI PPT Generator)

[English](#english) | [中文](#chinese)

---

<a name="english"></a>
## English

AI PPT Generator is a powerful tool designed to automate the creation of professional PowerPoint presentations. By leveraging Large Language Models (LLMs) and Search-Augmented Generation (RAG), it transforms a simple topic into a structured, content-rich, and visually appealing PPT.

### 🌟 Key Features
- **Intelligent Content Generation**: Supports Zhipu AI (GLM-4/5) and local Ollama models.
- **RAG (Search-Enhanced)**: Automatically fetches latest information via Baidu Search API for time-sensitive or professional topics.
- **Smart Charting**: Automatically generates bar, line, and pie charts based on data analysis.
- **Visual Templates**: Multiple built-in styles (Minimalist, Academic, Business, etc.) with customizable color schemes.
- **Human-in-the-loop**: Interactive outline confirmation and table-based editing before full content generation.
- **Multi-platform Support**: Provides both Command Line Interface (CLI) and Streamlit Web UI.

### 🚀 Quick Start
1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/aippt_v2.git
   cd aippt_v2
   ```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure API Keys**:
   Edit `config.py` and replace the placeholders with your API keys for Zhipu AI and Baidu Search.If you are using other providers, please modify the `api_base` field accordingly.
4. **Run the application**:
   - **Command line version**:
     ```bash
     python main.py
     ```
   - **Web version (Streamlit)**:
     ```bash
     streamlit run web_app.py
     ```

---

## 🛠 Technical Documentation

### 1. System Architecture
The project follows a modular design, separating concerns between content generation, information retrieval, and PPT rendering.

#### Module Structure
- `main.py`: Entry point for CLI mode.
- `web_app.py`: Entry point for Streamlit Web UI.
- `controller.py`: Orchestrates the generation pipeline.
- `outline_generator.py`: Generates PPT structure using LLM.
- `generator.py`: Generates detailed slide content using LLM and context.
- `llm.py`: Unified interface for LLM calls (Ollama/API).
- `retrieval.py`: RAG implementation using Baidu Search API.
- `ppt_generator.py`: Renders `.pptx` files using `python-pptx`.
- `chart_generator.py`: Generates data visualizations for slides.
- `template_manager.py`: Manages visual styles and themes.
- `config.py`: Configuration management.

### 2. Core Workflow
1. **User Input**: Subject and target slide count.
2. **Outline Generation**: AI creates a JSON-formatted structure.
3. **Human Confirmation**: Users can review and edit the outline (via CLI or Web Table).
4. **Information Retrieval (RAG)**: System checks if external search is needed based on the topic.
5. **Content Generation**: AI fills each slide with bullets, detailed content, and key messages.
6. **Validation**: Ensures content integrity and format.
7. **PPT Rendering**: Converts JSON data into a styled PowerPoint file with optional charts.

### 3. Configuration
The system uses `config.json` (auto-generated from `config.py`) to manage:
- `models`: Default models for outline and content generation.
- `api`: Zhipu AI API settings.
- `baidu_search`: Baidu Search API settings.
- `template`: Currently active visual theme.

---

<a name="chinese"></a>
## 中文

“智创易演”是一款基于人工智能的自动化 PPT 生成工具。它结合了大语言模型 (LLM) 与检索增强生成 (RAG) 技术，能够将简单的选题转化为结构完整、内容详实、且具备专业图表的演示文稿。

### 🌟 核心功能
- **智能内容生成**：支持智谱 AI (GLM-4/5) 及 Ollama 本地模型。
- **RAG 检索增强**：针对时效性或专业性主题，自动调用百度搜索 API 获取最新资料。
- **自动图表渲染**：根据内容逻辑自动生成柱状图、折线图及饼图。
- **模板化设计**：内置简约、学术、商务等多种设计风格，支持配色自定义。
- **人机协同**：支持大纲确认及表格化编辑，确保内容方向准确。
- **多端支持**：提供命令行交互与 Streamlit Web 界面。

### 🚀 快速开始
1. **克隆仓库**：
   ```bash
   git clone https://github.com/your-username/aippt_v2.git
   cd aippt_v2
   ```
2. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```
3. **配置 API Key**：
   编辑 `config.py` 文件，填写您的智谱 AI 及百度搜索 API 密钥。若使用其他服务提供商，可以适当修改 `api_base` 一栏以适配。
4. **运行程序**：
   - **命令行版本**：
     ```bash
     python main.py
     ```
   - **Web 可视化版本**：
     ```bash
     streamlit run web_app.py
     ```

---

## 🛠 技术说明

### 1. 系统架构
项目采用模块化设计，将内容规划、信息检索与文档渲染高度解耦。

#### 模块职责
- `main.py`: 命令行模式入口。
- `web_app.py`: Streamlit Web 界面入口。
- `controller.py`: 核心流程调度器。
- `outline_generator.py`: 负责利用 LLM 规划 PPT 结构。
- `generator.py`: 结合上下文生成幻灯片正文。
- `llm.py`: 统一的 LLM 调用接口，支持 Ollama 与远程 API。
- `retrieval.py`: 基于百度搜索 API 的 RAG（检索增强生成）实现。
- `ppt_generator.py`: 使用 `python-pptx` 进行文档渲染。
- `chart_generator.py`: 自动生成幻灯片关联图表。
- `template_manager.py`: 视觉样式与配色方案管理。
- `config.py`: 系统配置逻辑。

### 2. 核心流水线
1. **用户输入**：确定主题与目标页数。
2. **大纲规划**：AI 生成 JSON 格式的目录结构。
3. **人工交互**：用户在线预览并可直接在表格中微调大纲。
4. **联网检索 (RAG)**：系统自动判断主题时效性，按需抓取外部参考资料。
5. **内容填充**：AI 细化每一页的要点、正文及关键信息。
6. **内容校验**：确保生成数据格式完整且符合逻辑。
7. **渲染输出**：将结构化数据转换为美观的 PPTX 文件，包含自动渲染的图表。

### 3. 配置说明
系统通过 `config.json`（由 `config.py` 初始化）管理：
- `models`: 指定大纲与内容生成的模型。
- `api`: 智谱 AI 接口配置。
- `baidu_search`: 百度搜索接口配置。
- `template`: 当前生效的视觉模板。