#!/usr/bin/env python
# coding: utf-8

import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="多模型 AI 对比",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

MODEL_META = {
    "通义千问": {"emoji": "🌐", "color": "#6366f1", "tag": "阿里云 · Qwen"},
    "deepseek": {"emoji": "🧠", "color": "#0ea5e9", "tag": "DeepSeek Chat"},
    "智谱GLM-5.1": {"emoji": "✨", "color": "#10b981", "tag": "智谱 · GLM"},
}

EXAMPLE_PROMPTS = [
    "用三句话解释什么是机器学习",
    "写一首关于春天的五言绝句",
    "对比 Python 和 JavaScript 的优缺点",
]

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans SC', sans-serif; }
    .block-container {
        padding-top: 4.5rem;
        padding-bottom: 2rem;
        max-width: 1280px;
    }
    [data-testid="stHeader"] {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(6px);
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(165deg, #0f172a 0%, #1e293b 55%, #334155 100%);
    }
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stCaption { color: #cbd5e1 !important; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 { color: #f8fafc !important; }

    .hero-wrap {
        background: linear-gradient(135deg, #eef2ff 0%, #e0f2fe 50%, #ecfdf5 100%);
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.75rem 2rem;
        margin-bottom: 1.25rem;
    }
    .hero-title {
        font-size: 1.85rem;
        font-weight: 700;
        margin: 0 0 0.35rem 0;
        background: linear-gradient(90deg, #4f46e5, #0284c7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-sub { color: #475569; font-size: 0.95rem; margin: 0; line-height: 1.6; }

    .sidebar-chip {
        display: inline-block;
        padding: 0.25rem 0.7rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 500;
        margin: 0.2rem 0.35rem 0.2rem 0;
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.2);
        color: #f1f5f9 !important;
    }
    .card-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 0.75rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid #f1f5f9;
    }
    .card-dot {
        width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0;
    }
    .card-title { font-size: 1.1rem; font-weight: 600; color: #0f172a; margin: 0; }
    .card-tag {
        font-size: 0.72rem; padding: 2px 10px; border-radius: 999px;
        font-weight: 500;
    }
    .answer-body {
        color: #334155;
        line-height: 1.75;
        font-size: 0.95rem;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 14px !important;
        border-color: #e2e8f0 !important;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06);
        background: #ffffff;
    }
    div[data-testid="stMetric"] {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 0.5rem 0.75rem;
        margin-top: 0.25rem;
    }
    .footer-note {
        text-align: center; color: #94a3b8; font-size: 0.8rem;
        margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #e2e8f0;
    }
    .sidebar-guide {
        background: linear-gradient(135deg, rgba(59,130,246,0.22) 0%, rgba(99,102,241,0.18) 100%);
        border: 1.5px solid rgba(147, 197, 253, 0.55);
        border-radius: 14px;
        padding: 1rem 1.1rem;
        margin-top: 0.25rem;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.25);
    }
    .sidebar-guide-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #bfdbfe !important;
        margin: 0 0 0.85rem 0;
        letter-spacing: 0.02em;
    }
    .sidebar-guide-section {
        font-size: 0.88rem;
        font-weight: 600;
        color: #e2e8f0 !important;
        margin: 0.75rem 0 0.4rem 0;
    }
    .sidebar-guide p, .sidebar-guide li {
        color: #cbd5e1 !important;
        font-size: 0.86rem;
        line-height: 1.65;
        margin: 0.2rem 0;
    }
    .sidebar-guide code {
        background: rgba(15, 23, 42, 0.45);
        color: #fde68a !important;
        padding: 0.1rem 0.35rem;
        border-radius: 4px;
        font-size: 0.8rem;
    }
    .guide-panel {
        background: linear-gradient(135deg, #eff6ff 0%, #eef2ff 50%, #f0fdf4 100%);
        border: 2px solid #93c5fd;
        border-radius: 16px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.12);
    }
    .guide-panel-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1d4ed8;
        margin: 0 0 1rem 0;
    }
    .guide-steps {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.85rem;
    }
    .guide-step {
        background: #ffffff;
        border: 1px solid #bfdbfe;
        border-radius: 12px;
        padding: 0.85rem 1rem;
        text-align: center;
    }
    .guide-step-num {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 1.75rem;
        height: 1.75rem;
        border-radius: 50%;
        background: linear-gradient(135deg, #3b82f6, #6366f1);
        color: #fff;
        font-size: 0.85rem;
        font-weight: 700;
        margin-bottom: 0.45rem;
    }
    .guide-step-text {
        color: #334155;
        font-size: 0.9rem;
        font-weight: 500;
        line-height: 1.5;
        margin: 0;
    }
    .guide-config {
        margin-top: 0.9rem;
        padding-top: 0.85rem;
        border-top: 1px dashed #93c5fd;
        color: #475569;
        font-size: 0.88rem;
        line-height: 1.7;
    }
    .guide-config code {
        background: #dbeafe;
        color: #1e40af;
        padding: 0.1rem 0.4rem;
        border-radius: 4px;
        font-size: 0.82rem;
    }
    @media (max-width: 768px) {
        .guide-steps { grid-template-columns: 1fr; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_model(model_name):
    """定义不同模型的配置，返回配置字典"""
    configs = {
        "通义千问": {
            "api_key": st.secrets.get("DASHSCOPE_KEY", ""),
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "model": "qwen-plus",
        },
        "deepseek": {
            "api_key": st.secrets.get("DEEPSEEK_KEY", ""),
            "base_url": "https://api.deepseek.com/v1",
            "model": "deepseek-chat",
        },
        "智谱GLM-5.1": {
            "api_key": st.secrets.get("ZHIPU_KEY", ""),
            "base_url": "https://open.bigmodel.cn/api/paas/v4",
            "model": "glm-4",
        },
    }
    return configs.get(model_name)


def call_model(model_name, user_question, temperature=0.7):
    """得到不同模型的回答"""
    config = get_model(model_name)
    if not config or not config["api_key"]:
        return f"{model_name} 的 API key 没有配置，请在 `.streamlit/secrets.toml` 中添加"

    try:
        client = OpenAI(api_key=config["api_key"], base_url=config["base_url"])
        response = client.chat.completions.create(
            model=config["model"],
            messages=[{"role": "user", "content": user_question}],
            temperature=temperature,
            timeout=30,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"{model_name} 调用失败：{str(e)}"


def render_result_card(model_name, text):
    """在卡片中展示单个模型回答"""
    meta = MODEL_META.get(model_name, {"emoji": "🤖", "color": "#64748b", "tag": "AI"})
    is_error = "失败" in text or "没有配置" in text

    with st.container(border=True):
        st.markdown(
            f"""
            <div class="card-header">
                <span class="card-dot" style="background:{meta['color']}"></span>
                <p class="card-title">{meta['emoji']} {model_name}</p>
                <span class="card-tag" style="color:{meta['color']};
                    background:{meta['color']}1a;">{meta['tag']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if is_error:
            st.error(text)
        else:
            st.markdown(text)


# —— 侧边栏 ——
with st.sidebar:
    st.markdown("## 🎛️ 控制台")
    st.caption("勾选模型 · 输入问题 · 一键对比")

    select_models = st.multiselect(
        "对比模型",
        options=list(MODEL_META.keys()),
        default=["通义千问", "deepseek"],
        help="至少选择一个模型",
    )

    temperature = st.slider("创造性 (temperature)", 0.0, 1.0, 0.7, 0.1)

    st.divider()
    st.markdown("**当前已选**")
    if select_models:
        chips = "".join(
            f'<span class="sidebar-chip">{MODEL_META[m]["emoji"]} {m}</span>'
            for m in select_models
        )
        st.markdown(chips, unsafe_allow_html=True)
    else:
        st.caption("请在上方选择至少一个模型")

    st.divider()
    st.markdown(
        """
        <div class="sidebar-guide">
            <p class="sidebar-guide-title">📖 使用说明</p>
            <p class="sidebar-guide-section">使用步骤</p>
            <p>1. 勾选要对比的模型</p>
            <p>2. 输入问题并点击「开始对话」</p>
            <p>3. 查看并排展示的对比结果</p>
            <p class="sidebar-guide-section">配置密钥</p>
            <p>在 <code>.streamlit/secrets.toml</code> 中填写：</p>
            <p>• <code>DASHSCOPE_KEY</code> — 通义千问</p>
            <p>• <code>DEEPSEEK_KEY</code> — DeepSeek</p>
            <p>• <code>ZHIPU_KEY</code> — 智谱（可选）</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# —— 主标题区 ——
st.markdown(
    """
    <div class="hero-wrap">
        <p class="hero-title">🤖 多模型 AI 对比助手</p>
        <p class="hero-sub">
            一次提问，并排查看多个大模型的回答 —— 快速对比回答质量、风格与细节差异。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# —— 顶栏指标 ——
m1, m2, m3 = st.columns(3)
m1.metric("可选模型", len(MODEL_META))
m2.metric("已选模型", len(select_models))
m3.metric("创造性", f"{temperature:.1f}")

st.markdown(
    """
    <div class="guide-panel">
        <p class="guide-panel-title">📖 快速上手</p>
        <div class="guide-steps">
            <div class="guide-step">
                <div class="guide-step-num">1</div>
                <p class="guide-step-text">在左侧勾选<br>要对比的模型</p>
            </div>
            <div class="guide-step">
                <div class="guide-step-num">2</div>
                <p class="guide-step-text">输入问题<br>点击「开始对话」</p>
            </div>
            <div class="guide-step">
                <div class="guide-step-num">3</div>
                <p class="guide-step-text">查看多个模型的<br>并排对比结果</p>
            </div>
        </div>
        <p class="guide-config">
            <strong>首次使用？</strong> 请在项目
            <code>.streamlit/secrets.toml</code> 中配置 API 密钥：
            <code>DASHSCOPE_KEY</code>（通义千问）、
            <code>DEEPSEEK_KEY</code>（DeepSeek）、
            <code>ZHIPU_KEY</code>（智谱，可选）
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


def _set_example_prompt(prompt):
    st.session_state.question_input = prompt


# —— 输入区 ——
with st.container(border=True):
    st.markdown("##### ✏️ 输入你的问题")
    user_input = st.text_area(
        "问题内容",
        placeholder="在这里输入你想问 AI 的问题…",
        height=130,
        label_visibility="collapsed",
        key="question_input",
    )

    st.caption("💡 试试示例问题（点击填入）：")
    ex_cols = st.columns(len(EXAMPLE_PROMPTS))
    for col, prompt in zip(ex_cols, EXAMPLE_PROMPTS):
        with col:
            st.button(
                prompt,
                key=f"ex_{prompt}",
                use_container_width=True,
                on_click=_set_example_prompt,
                args=(prompt,),
            )

    btn_col, hint_col = st.columns([1, 2])
    with btn_col:
        start = st.button("🚀 开始对话", type="primary", use_container_width=True)
    with hint_col:
        st.caption("将依次调用所选模型，结果以卡片并排展示")

# —— 对话结果 ——
if start:
    question = st.session_state.get("question_input", "").strip()
    if not question:
        st.warning("⚠️ 请输入问题后再开始对话")
    elif not select_models:
        st.warning("⚠️ 请至少在侧边栏选择一个模型")
    else:
        st.markdown("##### 💬 你的提问")
        st.info(question)

        progress = st.progress(0, text="准备调用模型…")
        results = {}
        for idx, model in enumerate(select_models):
            progress.progress(
                (idx) / len(select_models),
                text=f"正在请求 {MODEL_META[model]['emoji']} {model}…",
            )
            results[model] = call_model(model, question, temperature)
        progress.progress(1.0, text="全部完成")
        progress.empty()

        st.markdown("##### 📊 模型回答对比")
        cols = st.columns(len(select_models))
        for col, model in zip(cols, select_models):
            with col:
                render_result_card(model, results[model])

        st.success(f"已完成 {len(select_models)} 个模型的回答对比")

else:
    st.markdown("##### 🧭 支持的模型")
    preview_cols = st.columns(len(MODEL_META))
    for col, (name, meta) in zip(preview_cols, MODEL_META.items()):
        with col:
            with st.container(border=True):
                st.markdown(
                    f"""
                    <div style="text-align:center;padding:0.5rem 0;">
                        <span style="font-size:2rem;">{meta['emoji']}</span>
                        <p style="font-weight:600;margin:0.5rem 0 0.25rem;color:#0f172a;">{name}</p>
                        <p style="font-size:0.8rem;color:{meta['color']};margin:0;">{meta['tag']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                selected = name in select_models
                st.caption("✅ 已勾选" if selected else "在左侧勾选以参与对比")

st.markdown(
    '<p class="footer-note">多模型 AI 对比助手 · Streamlit</p>',
    unsafe_allow_html=True,
)
