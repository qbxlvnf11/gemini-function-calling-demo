import os
import google.generativeai as genai
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.api.chat_router import router as chat_router
from backend.core.config import GCP_PROJECT_ID

# Configure Gemini
# If you have an API key, use genai.configure(api_key=...)
# If GOOGLE_APPLICATION_CREDENTIALS is set, it might use Application Default Credentials.
# Note: For GCP Service Accounts, you typically use the 'vertexai' package, but we match the user's snippet here.
# If needed, you can switch to `vertexai.init(project=GCP_PROJECT_ID, location="asia-northeast3")`
try:
    genai.configure()
except Exception as e:
    print(f"Warning: Failed to configure genai: {e}")

app = FastAPI(title="Native Function Calling Demo")

# Include WebSocket router
app.include_router(chat_router)

# Mount frontend files
app.mount("/css", StaticFiles(directory="frontend/css"), name="css")
app.mount("/js", StaticFiles(directory="frontend/js"), name="js")

@app.get("/")
async def get_index():
    return FileResponse("frontend/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8001, reload=True)
