#!/usr/bin/env python
# coding: utf-8

# In[2]:


# 快速构建Web应用的python框架
import json
import time
import streamlit as st
from openai import OpenAI

# #region agent log
def _dbg_log(location, message, data, hypothesis_id):
    try:
        with open("debug-d4b701.log", "a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "sessionId": "d4b701",
                        "location": location,
                        "message": message,
                        "data": data,
                        "hypothesisId": hypothesis_id,
                        "timestamp": int(time.time() * 1000),
                        "runId": "pre-fix",
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
    except Exception:
        pass
# #endregion

# 网页顶部显示一级标题
st.title("🤖 多模型AI对比助手")
# 生成一个较小的灰色辅助字
st.caption("同时对比多个AI模型的回答效果")

# 将以下的组件都放到侧边栏
with st.sidebar:
    
    # 侧边栏的标题
    st.header("模型选择")
    # 创建多选框下拉框，选择模型
    select_models = st.multiselect(
        "选择要对比的AI模型：\n(默认选择通义千问和deepseek)",
        options=["通义千问","deepseek","智谱GLM-5.1"],
        default=["通义千问","deepseek"]
    )
    # 添加一条分割线
    st.divider()
    st.caption("提示：选择多个模型可以一起对比")


# In[3]:


# 创建文本输入框
user_input = st.text_input("输入你的问题：")

def get_model(model_name):
    
    """定义不同模型的配置，返回配置字典"""
    # 定义不同模型的配置
    configs  = {
        "通义千问": {
            # 如果不存在key则返回空字符串防止报错
            # 去.streamlit/secrets.toml文件中查找名为DASHSCOPE_KEY的值
            "api_key": st.secrets.get("DASHSCOPE_KEY",""),
            # 服务器地址
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            # 模型（plus版）
            "model": "qwen-plus"
        },
        "deepseek": {
            "api_key": st.secrets.get("DEEPSEEK_KEY", ""),
            "base_url": "https://api.deepseek.com/v1",
            "model": "deepseek-chat",
        },
        "智谱GLM-5.1": {
            "api_key": st.secrets.get("ZHIPU_KEY", ""),
            "base_url": "https://open.bigmodel.cn/api/paas/v4",
            "model": "glm-4"
        }
    }
    config = configs.get(model_name)
    # #region agent log
    _dbg_log(
        "test.py:get_model",
        "model config lookup",
        {
            "model_name": model_name,
            "config_keys": list(configs.keys()),
            "config_found": config is not None,
            "api_key_len": len(config["api_key"]) if config else 0,
            "has_DEEPSEEKAPI_KEY": "DEEPSEEKAPI_KEY" in st.secrets,
            "has_DEEPSEEK_KEY": "DEEPSEEK_KEY" in st.secrets,
            "has_DASHSCOPE_KEY": "DASHSCOPE_KEY" in st.secrets,
        },
        "A-B-D",
    )
    # #endregion
    return config


def call_model(model_name,user_question):
    
    """得到不同模型的回答"""
    # 得到模型参数配置
    config = get_model(model_name)

    # #region agent log
    _dbg_log(
        "test.py:call_model:entry",
        "call_model started",
        {
            "model_name": model_name,
            "has_config": config is not None,
            "will_skip_api": (not config) or (not config.get("api_key") if config else True),
        },
        "A-B",
    )
    # #endregion

    # 判断是否有配置返回和是否设置了api
    if not config or not config["api_key"]:

        # #region agent log
        _dbg_log(
            "test.py:call_model:skip",
            "skipped API call",
            {"model_name": model_name, "reason": "no_config" if not config else "empty_api_key"},
            "A-B",
        )
        # #endregion
        return f"{model_name}的API key没有配置，请在secrets.toml文件中添加"
    
    try:
        # 调用大模型
        client = OpenAI(
            api_key=config["api_key"], 
            # 服务器地址
            base_url=config["base_url"]
        )
        
        response = client.chat.completions.create(
            model=config["model"],
            # 输入用户提问
            messages=[{"role": "user", "content": user_question}],
            temperature = 0.7,  # 控制创造性
            timeout = 30   # 超过30秒表示超时
        )
        
        # 返回对话结果
        content = response.choices[0].message.content
        # #region agent log
        _dbg_log(
            "test.py:call_model:success",
            "API call succeeded",
            {"model_name": model_name, "response_len": len(content) if content else 0},
            "C-E",
        )
        # #endregion
        return content

        # 捕捉异常
    except Exception as e:
        # #region agent log
        _dbg_log(
            "test.py:call_model:error",
            "API call failed",
            {"model_name": model_name, "error_type": type(e).__name__, "error": str(e)[:500]},
            "C-E",
        )
        # #endregion
        return f"{model_name}调用失败：{str(e)}"


# In[4]:


# 如果点击了按钮（“开始对话”）设置为主要按钮
if st.button("开始对话",type="primary"):
    
    if not user_input:
        st.warning("请输入问题后再点击按钮")
        
    elif not select_models:
        st.warning("请至少选择一个模型")
    
    else:
        # 显示用户的问题（生成信息提示框）
        st.info(f"你的问题是：{user_input}")
        
        # 创建进度提示
        with st.spinner(f"正在调用{len(select_models)}个AI模型，请稍等"):
            # 创建字典接受结果
            results = {}
            # 依次调用每个模型
            for model in select_models:
                results[model] = call_model(model,user_input)
                
        # 显示对比结果
        st.divider()     # 分割线
        st.subheader("模型回答对比")
        
        # 按列的方式排列结果
        cols = st.columns(len(select_models))  # 创建选择模型数量等宽的列
        # 提取序号和模型
        for i, model in enumerate(select_models):
            
            # 遍历第i个cols(列对象)
            with cols[i]:
                # 模型标题
                st.markdown(f"###{model}")
                st.divider()
                # 显示回答内容
                st.write(results[model])    # results字典中key为model的值
                st.caption(f"{model}回答完毕")
                


# In[ ]:




