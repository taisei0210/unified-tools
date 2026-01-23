from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, Response, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import tempfile
from pathlib import Path
from moviepy.editor import VideoFileClip

app = FastAPI()

# Mount static files
# Mount static files moved to the end to avoid conflicts


# CORS (Enable all for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)

@app.post("/api/video-to-audio")
async def video_to_audio(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected")
    
    try:
        # Save uploaded video
        temp_video_path = TEMP_DIR / file.filename
        with open(temp_video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Process with MoviePy
        video = VideoFileClip(str(temp_video_path))
        audio_filename = Path(file.filename).stem + ".mp3"
        output_path = TEMP_DIR / audio_filename
        
        # Write audio
        video.audio.write_audiofile(str(output_path), bitrate="192k", verbose=False, logger=None)
        video.close()
        
        # Calculate stats
        original_size = os.path.getsize(temp_video_path)
        new_size = os.path.getsize(output_path)
        reduction = original_size - new_size
        reduction_percent = (reduction / original_size) * 100
        
        # Cleanup video
        os.remove(temp_video_path)
        
        return JSONResponse({
            "status": "success",
            "download_url": f"/api/download/{audio_filename}",
            "stats": {
                "original_size": original_size,
                "new_size": new_size,
                "reduction_percent": round(reduction_percent, 1)
            }
        })
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    file_path = TEMP_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        file_path, 
        media_type="audio/mpeg", 
        filename=filename,
        background=None # Allow browser to handle download
    )

@app.get("/api/downloads/screenshot-shortcut")
async def download_screenshot_tool():
    # Return the zip file of the screenshot tool (we'll implement the zipping later)
    # For now, just a placeholder or point to the directory? 
    # Better: create a zip on the fly or pre-zip. 
    # Let's assume we pre-zip it to static/downloads
    zip_path = Path("static/downloads/screenshot_shortcut.zip")
    if zip_path.exists():
         return FileResponse(zip_path, filename="screenshot_shortcut.zip")
    return JSONResponse(status_code=404, content={"message": "Download not available yet"})

# Mount static files at the root (Last to avoid overriding API routes)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
