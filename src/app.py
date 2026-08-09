import os
import shutil
import requests
from src.ai_service import process_voice_to_code
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
    lang = payload.language.lower().strip()
    
    language_ids = {
        "python": 71,
        "javascript": 63,
        "js": 63,
        "typescript": 74,
        "ts": 74,
        "cpp": 54,
        "c++": 54,
        "c": 50,
        "csharp": 51,
        "c#": 51,
        "java": 62,
        "go": 60,
        "rust": 73,
        "php": 68,
        "ruby": 72,
        "swift": 83,
        "kotlin": 78,
        "sql": 82
    }
    
    lang_id = language_ids.get(lang, 71) # Standart holatda Python
    
    url = "https://ce.judge0.com/submissions?base64_encoded=false&wait=true"
    
    data = {
        "source_code": code_to_run,
        "language_id": lang_id
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        result = response.json()
        
        stdout = result.get("stdout")
        stderr = result.get("stderr")
        compile_output = result.get("compile_output")
        status = result.get("status", {}).get("description")
        
        if compile_output:
            return {"success": False, "output": "Compilation Error:\n" + compile_output}
        if stderr:
            return {"success": False, "output": stderr}
        if stdout is not None:
            return {"success": True, "output": stdout if stdout else "Code executed successfully (no output)."}
        
        return {"success": False, "output": f"Execution status: {status}"}
            
    except Exception as e:
        return {"success": False, "output": str(e)}