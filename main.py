from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
import shutil
import os
from app.analysis import analyze

app = FastAPI(
    title="Dance Pose Analysis API",
    description="Analyze dance videos and generate pose detections (video + JSON) without freezing Swagger UI.",
    version="1.0.0"
)

# Directories
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Background task to process video
def process_video(input_path: str, output_video: str, output_json: str):
    try:
        analyze(input_path, output_video, output_json)
    except Exception as e:
        
        print(f"Error processing {input_path}: {e}")

# Endpoint to upload video and start analysis
@app.post("/analyze")
async def analyze_video(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    
    input_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    
    output_video = os.path.join(OUTPUT_DIR, "annotated_" + file.filename.replace(".mp4", ".avi"))
    output_json = os.path.join(OUTPUT_DIR, file.filename.replace(".mp4", ".json"))


    background_tasks.add_task(process_video, input_path, output_video, output_json)

    
    return JSONResponse(
        content={
            "status": "Processing started",
            "uploaded_file": file.filename,
            "output_video": output_video,
            "output_json": output_json
        }
    )


@app.get("/status/{filename}")
async def check_status(filename: str):
    output_video = os.path.join(OUTPUT_DIR, "annotated_" + filename.replace(".mp4", ".avi"))
    output_json = os.path.join(OUTPUT_DIR, filename.replace(".mp4", ".json"))

    if os.path.exists(output_video) and os.path.exists(output_json):
        return JSONResponse(
            content={
                "status": "completed",
                "output_video": output_video,
                "output_json": output_json
            }
        )
    else:
        return JSONResponse(
            content={
                "status": "processing"
            }
        )

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Dance Pose Analysis API is running!"}
