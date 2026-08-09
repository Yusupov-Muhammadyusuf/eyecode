import os
import shutil
import requests
from ai_service import process_voice_to_code
from dotenv import load_dotenv

from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

load_dotenv()

app = FastAPI(title="Voice Code Assistant")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class CodeExecutionRequest(BaseModel):
    code: str
    language: str = "python"

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request, "main.html")

@app.post("/api/convert")
async def convert_voice(
    file: UploadFile = File(...),
    language: str = Form(default="python"),
    spoken_language: str = Form(default="uz")
):  
    temp_audio_path = f"temp_{file.filename}"
    with open(temp_audio_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        user_text, code = process_voice_to_code(temp_audio_path, language, spoken_language)
        return {
            "success": True,
            "transcription": user_text,
            "code": code
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

@app.post("/api/run-code")
async def run_code(payload: CodeExecutionRequest):
    code_to_run = payload.code
    lang = payload.language.lower()
    
    lang_config = {
        "python": {"language": "python", "version": "3.10.0"},
        "javascript": {"language": "javascript", "version": "18.15.0"},
        "js": {"language": "javascript", "version": "18.15.0"},
        "typescript": {"language": "typescript", "version": "5.0.3"},
        "ts": {"language": "typescript", "version": "5.0.3"},
        "cpp": {"language": "cpp", "version": "10.2.0"},
        "c++": {"language": "cpp", "version": "10.2.0"},
        "c": {"language": "c", "version": "10.2.0"},
        "csharp": {"language": "csharp", "version": "6.12.0"},
        "c#": {"language": "csharp", "version": "6.12.0"},
        "java": {"language": "java", "version": "15.0.2"},
        "go": {"language": "go", "version": "1.16.2"},
        "rust": {"language": "rust", "version": "1.68.2"},
        "php": {"language": "php", "version": "8.2.3"},
        "ruby": {"language": "ruby", "version": "3.0.1"},
        "swift": {"language": "swift", "version": "5.3.3"},
        "kotlin": {"language": "kotlin", "version": "1.8.20"},
        "sql": {"language": "sqlite3", "version": "3.36.0"}
    }
    
    config = lang_config.get(lang, {"language": "python", "version": "3.10.0"})
    
    url = "https://emkc.org/api/v2/piston/execute"
    data = {
        "language": config["language"],
        "version": config["version"],
        "files": [
            {
                "content": code_to_run
            }
        ]
    }
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        
        if "run" in result:
            output = result["run"].get("output", "")
            stderr = result["run"].get("stderr", "")
            
            if stderr:
                return {"success": False, "output": stderr}
            return {"success": True, "output": output if output else "Code executed successfully (no output)."}
        else:
            return {"success": False, "output": "Execution error from compiler service."}
            
    except Exception as e:
        return {"success": False, "output": str(e)}