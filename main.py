from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import shutil
import os
from app.analysis import analyze

app = FastAPI()

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.post("/analyze")
async def analyze_video(file: UploadFile = File(...)):
    # Save uploaded video
    input_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    
    output_video = os.path.join(OUTPUT_DIR, "annotated_" + file.filename.replace(".mp4", ".avi"))
    output_json = os.path.join(OUTPUT_DIR, file.filename.replace(".mp4", ".json"))

    # Run analysis
    analyze(input_path, output_video, output_json)

    # Return summary JSON as response
    import json
    with open(output_json, "r") as f:
        data = json.load(f)

    return JSONResponse(content=data)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Dance Pose Analysis API is running!"}
