#https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/index.html
#pip install -U "autogen-agentchat" "autogen-ext[openai,azure]" 
import asyncio
import os
from dotenv import load_dotenv
# Import ModelInfo along with UserMessage
from autogen_core.models import UserMessage, ModelInfo
from autogen_ext.models.openai import OpenAIChatCompletionClient
# 1. Load environment variables from .env
load_dotenv()
async def main():
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("GEMINI_API_KEY is missing! Make sure it is set in your .env file.")
    # 2. Explicitly define model capabilities for AutoGen 0.4+
    gemini_model_info = ModelInfo(
        vision=True,
        function_calling=True,
        json_output=True,
        family="gemini",)
    # 3. Pass model_info AND Google's OpenAI-compatible base_url
    model_client = OpenAIChatCompletionClient(
        model="gemini-3-flash-preview",
        api_key=gemini_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        model_info=gemini_model_info  # <--- Fixes the ValueError
    )
    # 4. Create request
    response = await model_client.create([
        UserMessage(content="What is the autogen framework in Agentic AI?", source="user")
    ])    
    print("Response:\n", response.content)
    # 5. Close client connection
    await model_client.close()
if __name__ == "__main__":
    asyncio.run(main())