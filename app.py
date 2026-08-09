import os
import shutil
import sys
import io

from ai_service import process_voice_to_code
from dotenv import load_dotenv
from pydantic import BaseModel

from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

load_dotenv()

app = FastAPI(title="Voice Code Assistant")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class CodeExecutionRequest(BaseModel):
    code: str

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
    
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout
    
    try:
        exec(code_to_run, {})
        output = new_stdout.getvalue()
        success = True
    except Exception as e:
        output = str(e)
        success = False
    finally:
        sys.stdout = old_stdout
        
    return {
        "success": success,
        "output": output if output else "Code executed successfully (no print output)."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8080, reload=True)