import os
import uuid
import shutil
import json
import sys
import webbrowser
import signal
from threading import Timer
import uvicorn
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydub import AudioSegment
import torch
from transformers import pipeline
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# Graceful shutdown handler
def shutdown_server():
    print("Shutting down the server gracefully...")
    # This sends SIGTERM to the current process, which uvicorn catches to shutdown
    os.kill(os.getpid(), signal.SIGTERM)

# Inicializace Gemini Clienta
try:
    client = genai.Client()
except Exception as e:
    print(f"WARNING: Could not initialize Gemini Client. Check your GEMINI_API_KEY. Error: {e}")

# Inicializace FastAPI
app = FastAPI(title="UsirevAI Backend")

os.makedirs("temp_audio", exist_ok=True)

# Načtení Whisper modelu
print("Loading mikr/whisper-small-cs-cv11 model... This might take a moment.")
device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
model_kwargs = {"attn_implementation": "sdpa"} if torch.cuda.is_available() else {}

try:
    transcriber = pipeline(
        "automatic-speech-recognition",
        model="mikr/whisper-small-cs-cv11",
        device=device,
        torch_dtype=torch_dtype,
        model_kwargs=model_kwargs,
        chunk_length_s=30,
        batch_size=24,
    )
    print(f"Model loaded successfully on {device}.")
except Exception as e:
    print(f"Error loading Transformers model: {e}")
    transcriber = None


# --- NOVÁ STRUKTURA: Rozdělili jsme anamnézu na jednotlivá pole ---
class StrukturovanaAnamneza(BaseModel):
    no: str = Field(description="Nynější onemocnění: proč pacient přichází, aktuální obtíže")
    oa: str = Field(description="Osobní anamnéza: předchozí nemoci, operace")
    fa: str = Field(description="Farmakologická anamnéza: léky")
    abusus: str = Field(description="Kouření, alkohol, drogy")
    aa: str = Field(description="Alergická anamnéza")
    ra: str = Field(description="Rodinná anamnéza: rodiče, sourozenci")
    obj: str = Field(description="Objektivní nález")
    vysetreni: str = Field(description="Případná vyšetření a doporučení")

class MedicalResponse(BaseModel):
    rozdeleny_dialog: str = Field(description="Dialog logicky rozdělený na 'Lékař: ...' a 'Pacient: ...'")
    anamneza: StrukturovanaAnamneza


SYSTEM_PROMPT = """
Jsi zkušený lékař a analytik textu. Obdržíš surový, nepřerušený přepis rozhovoru mezi lékařem a pacientem.

Tvým úkolem jsou DVA kroky:

1. KROK: Rozdělení dialogu
Přečti si surový text a logicky ho rozděl na to, co říká lékař a co pacient.
Výsledek zapiš přesně takto:
Lékař: [text]
Pacient: [text]

2. KROK: Tvorba anamnézy
Z rozhovoru extrahuj informace do připravených polí anamnézy.
Pokud informace v textu chybí, napiš do daného pole pouze "Neuvedeno".
U alergií (AA), pokud nejsou, napiš "Neguje". Nevymýšlej si.

Zde je surový přepis rozhovoru k analýze:
"""

@app.post("/api/process-audio")
def process_audio(
    audio: UploadFile = File(...),
    gemini_model: str = Form("gemini-1.5-flash")
):
    if transcriber is None:
        raise HTTPException(status_code=500, detail="AI Model pro přepis nebyl správně načten.")

    file_id = uuid.uuid4().hex
    temp_webm_path = os.path.join("temp_audio", f"{file_id}.webm")
    temp_wav_path = os.path.join("temp_audio", f"{file_id}.wav")

    # 1. Uložení audia
    with open(temp_webm_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)

    if os.path.getsize(temp_webm_path) == 0:
        os.remove(temp_webm_path)
        raise HTTPException(status_code=400, detail="Nahraný zvukový soubor je prázdný.")

    try:
        # 2. Konverze WebM -> WAV
        print(f"Converting audio to WAV...")
        try:
            audio_segment = AudioSegment.from_file(temp_webm_path)
            audio_segment.export(temp_wav_path, format="wav")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Chyba při konverzi audia: {str(e)}")

        # 3. Přepis přes lokální Whisper
        print(f"Transcribing {temp_wav_path}...")
        with torch.no_grad():
            result = transcriber(temp_wav_path)

        transcribed_text = result["text"]
        print("Transcription complete.")

        if not transcribed_text.strip():
            raise HTTPException(status_code=400, detail="Nepodařilo se rozpoznat žádný text z audia.")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chyba při přepisu audia: {str(e)}")
    finally:
        for path in [temp_webm_path, temp_wav_path]:
            if os.path.exists(path):
                os.remove(path)

    try:
        # 4. Magie s Gemini
        print(f"Sending to Gemini to format dialogue and extract anamnesis...")
        prompt = SYSTEM_PROMPT + transcribed_text

        response = client.models.generate_content(
            model=gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=MedicalResponse,
                temperature=0.1
            )
        )

        result_data = json.loads(response.text)
        anamneza_data = result_data["anamneza"]

        # --- ZDE SKLÁDÁME VÝSLEDNÝ TEXT S PEVNÝM ODŘÁDKOVÁNÍM ---
        formatted_anamnesis = (
            "Anamnéza\n\n"
            f"NO - {anamneza_data['no']}\n\n"
            f"OA - {anamneza_data['oa']}\n\n"
            f"FA - {anamneza_data['fa']}\n\n"
            f"Abusus - {anamneza_data['abusus']}\n\n"
            f"AA - {anamneza_data['aa']}\n\n"
            f"RA - {anamneza_data['ra']}\n\n"
            f"Obj. - {anamneza_data['obj']}\n\n"
            f"Vyšetření - {anamneza_data['vysetreni']}"
        ) # TATO ZÁVORKA JE KRITICKÁ

        return {
            "anamnesis": formatted_anamnesis,
            "transcription": result_data["rozdeleny_dialog"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chyba při komunikaci s Gemini: {str(e)}")

@app.post("/api/shutdown")
def shutdown():
    """Endpoint called by the browser when the tab is closed to prevent ghost processes."""
    Timer(1.0, shutdown_server).start()
    return {"message": "Shutting down..."}

def get_base_path():
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return base_path

static_dir = os.path.join(get_base_path(), "static")
os.makedirs(static_dir, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def get_index():
    index_path = os.path.join(static_dir, "index.html")
    # If the file doesn't exist, provide a basic fallback or it will raise an error.
    if not os.path.exists(index_path):
        return "<html><body><h1>UsirevAI Application is running. UI not found.</h1></body></html>"
    with open(index_path, "r", encoding="utf-8") as f:
        return f.read()

app.mount("/", StaticFiles(directory=static_dir), name="static")

def open_browser():
    webbrowser.open_new("http://127.0.0.1:7860/")

if __name__ == "__main__":
    Timer(1.5, open_browser).start()
    uvicorn.run(app, host="127.0.0.1", port=7860)