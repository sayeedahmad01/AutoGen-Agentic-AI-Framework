import asyncio
import os
from io import BytesIO
import requests
import streamlit as st
from dotenv import load_dotenv
from PIL import Image

# AutoGen Imports - Note: Import UserMessage directly from autogen_core.models
from autogen_core import Image as AGImage
from autogen_core.models import ModelInfo, UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

# 1. Page Configuration
st.set_page_config(
    page_title="Multimodal AutoGen Analyzer by PRAKASH SENAPATI",
    page_icon="🖼️",
    layout="centered"
)

# Load environment variables from .env
load_dotenv()

st.title("🖼️ Gemini Vision Analyzer (AutoGen 0.4+)")
st.caption("Powered by Streamlit, Google Gemini 1.5 Flash, and Microsoft AutoGen")

# 2. Sidebar API Key check
gemini_key = os.getenv("GEMINI_API_KEY") or st.sidebar.text_input("Gemini API Key", type="password")

if not gemini_key:
    st.warning("Please provide a GEMINI_API_KEY in your `.env` file or sidebar to proceed.")
    st.stop()

# 3. Image Selection Input
st.subheader("1. Choose an Image")
input_option = st.radio("Image Source", ["Upload Image", "Use Sample Random Image"], horizontal=True)

pil_image = None

if input_option == "Upload Image":
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png", "webp"])
    if uploaded_file is not None:
        pil_image = Image.open(uploaded_file)
else:
    if st.button("Fetch New Sample Image"):
        st.session_state["sample_img"] = requests.get("https://picsum.photos/600/400").content
    
    if "sample_img" not in st.session_state:
        st.session_state["sample_img"] = requests.get("https://picsum.photos/600/400").content
        
    pil_image = Image.open(BytesIO(st.session_state["sample_img"]))

# Display preview if an image is loaded
if pil_image:
    st.image(pil_image, caption="Preview Image", use_container_width=True)

# 4. User Prompt Input
st.subheader("2. Enter Prompt")
user_prompt = st.text_area(
    "What would you like to ask about this image?", 
    value="Can you describe the content of this image in detail and list its key elements?"
)

# 5. Async Function for AutoGen Execution
async def run_autogen_vision_analysis(image: Image.Image, prompt: str, api_key: str):
    # Configure model capabilities for Gemini
    gemini_model_info = ModelInfo(
        vision=True,
        function_calling=True,
        json_output=True,
        family="unknown"
    )

    # Initialize OpenAIChatCompletionClient pointing to Gemini
    model_client = OpenAIChatCompletionClient(
        model="gemini-3-flash-preview",
        api_key=api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        model_info=gemini_model_info
    )

    # Convert PIL Image into AutoGen's AGImage wrapper
    ag_img = AGImage(image)

    # Construct a UserMessage with a list containing text and AGImage
    # (Replaces MultiModalMessage which was causing the type error)
    user_msg = UserMessage(
        content=[prompt, ag_img],
        source="user"
    )

    # Request response from the model
    response = await model_client.create([user_msg])
    
    # Close client connection
    await model_client.close()
    
    return response.content

# 6. Trigger Analysis
if st.button("🚀 Analyze Image", type="primary", disabled=(pil_image is None)):
    with st.spinner("🤖 Gemini is analyzing your image..."):
        try:
            analysis_result = asyncio.run(run_autogen_vision_analysis(pil_image, user_prompt, gemini_key))
            
            st.success("Analysis Complete!")
            st.markdown("### 📋 Response:")
            st.markdown(analysis_result)
            
        except Exception as e:
            st.error(f"An error occurred during execution: {e}")