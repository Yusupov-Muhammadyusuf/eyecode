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
    
    lang_mapping = {
        "python": "python",
        "cpp": "cpp",
        "c++": "cpp",
        "javascript": "javascript",
        "js": "javascript",
        "java": "java",
        "csharp": "csharp",
        "c#": "csharp"
    }
    
    piston_lang = lang_mapping.get(lang, "python")
    
    url = "https://emkc.org/api/v2/piston/execute"
    data = {
        "language": piston_lang,
        "version": "*",
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8080, reload=True)