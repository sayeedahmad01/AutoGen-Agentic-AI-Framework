import asyncio
import os
import streamlit as st
from dotenv import load_dotenv

# AutoGen 0.4+ Imports
from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ModelInfo
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Page Config
st.set_page_config(page_title="Single Agent - AutoGen 0.4", page_icon="🌱", layout="centered")

load_dotenv()

st.title("🌱 Single Agent (Non-Tech Mentor)")
st.caption("Powered by AutoGen 0.4+ and Google Gemini 1.5 Flash")

# 1. API Key Check
gemini_key = os.getenv("GEMINI_API_KEY") or st.sidebar.text_input("Gemini API Key", type="password")

if not gemini_key:
    st.warning("⚠️ Please provide a GEMINI_API_KEY in your `.env` file or sidebar.")
    st.stop()

# 2. Input Prompt
user_prompt = st.text_area(
    "Ask a non-technical question:",
    value="Can you explain how a database index works using a library analogy?",
    height=100
)

# 3. Async Core Function
async def run_single_agent(prompt: str, api_key: str):
    # Configure Gemini capabilities
    model_info = ModelInfo(
        vision=True,
        function_calling=True,
        json_output=True,
        family="gemini"
    )

    model_client = OpenAIChatCompletionClient(
        model="gemini-3-flash-preview",
        api_key=api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        model_info=model_info
    )

    mentor = AssistantAgent(
        name="NonTech_Mentor",
        model_client=model_client,
        system_message=(
            "You are a friendly technical educator explaining concepts to a non-technical audience. "
            "Avoid code or heavy jargon. Use clear real-world analogies."
        ),
    )

    response = await mentor.run(task=prompt)
    await model_client.close()
    
    # Return the final agent message content
    return response.messages[-1].content

# 4. Trigger Analysis
if st.button("🚀 Ask Mentor", type="primary"):
    with st.spinner("Mentor is generating explanation..."):
        try:
            result = asyncio.run(run_single_agent(user_prompt, gemini_key))
            st.success("Response Generated!")
            st.markdown(result)
        except Exception as e:
            st.error(f"Error: {e}")