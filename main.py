from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import whisper
import shutil
import uuid
import os

app = FastAPI()
model = whisper.load_model("base")
max_upload_size = 10*1024*1024

app.add_middleware(
    CORSMiddleware,
    #allow_origins=["http://localhost:3000"],
    allow_origins=["https://salmon-pebble-025c32210.2.azurestaticapps.net"],
    allow_methods=["*"],
    allow_headers=["*"]
)

ALLOWED_AUDIO_TYPES = {
    "audio/mpeg", "audio/wav", "audio/x-wav", "audio/x-m4a", "audio/webm",
    "audio/ogg", "audio/flac", "audio/mp4", "audio/x-ms-wma"
}

@app.post("/transcribe")
async def transcribe_audio(request: Request, file: UploadFile = File(...)):
    file_size = request.headers.get("content-length")

    if file_size and int(file_size) > max_upload_size:
        raise HTTPException(status_code=413, detail="File larger than 10 MB")

    if file.content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(status_code=415, detail="Not audio file - Unacceptable file")

    unique_id = uuid.uuid4()
    temp_path = f"temp_{unique_id}"

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = model.transcribe(temp_path)
    os.remove(temp_path)

    return {"Transcript": result["text"]}