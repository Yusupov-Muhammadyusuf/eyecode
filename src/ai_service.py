import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def process_voice_to_code(audio_file_path: str, target_lang: str = "python", spoken_lang: str = "uz") -> tuple:
    with open(audio_file_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(audio_file_path, file.read()),
            model="whisper-large-v3",
            language=spoken_lang if spoken_lang in ["uz", "en", "ru", "es", "zh", "hi", "ar", "fr", "de", "ja", "ko", "tr", "pt"] else None,
            response_format="text"
        )
    
    user_prompt = transcription.strip()

    system_prompt = f"""
    You are an AI assistant helping developers, including visually impaired individuals, write code.
    The user will give instructions in natural language. You must understand it and return ONLY clean, working {target_lang} code.
    Do not include markdown code block syntaxing if not needed, or just standard clean code without extra explanations. Output only code.
    """

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.2
    )

    generated_code = chat_completion.choices[0].message.content
    return user_prompt, generated_code