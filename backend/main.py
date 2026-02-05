from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import torch
import cv2
import uvicorn
from contextlib import asynccontextmanager

from model import load_model
from camera import VideoCamera

# Global variables
model = None
device = None
camera = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global model, device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Load Model (assuming weights might be at 'model_weights.pth', or random init)
    model = load_model('emotion_model.pth', device)
    
    yield
    # Shutdown (if needed)
    pass

app = FastAPI(lifespan=lifespan)

# Allow CORS for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, verify specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_camera():
    global camera
    if camera is None:
        camera = VideoCamera(model, device)
    return camera

def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        if frame is None:
            break
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.get("/video_feed")
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return StreamingResponse(gen(get_camera()),
                    media_type='multipart/x-mixed-replace; boundary=frame')

@app.post("/toggle_confidence")
def toggle_confidence():
    cam = get_camera()
    cam.show_confidence = not cam.show_confidence
    return {"show_confidence": cam.show_confidence}

@app.get("/")
def read_root():
    return {"status": "Backend is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
