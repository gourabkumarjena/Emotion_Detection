import cv2
import numpy as np
import torch
import torchvision.transforms as transforms
from PIL import Image

import torch.nn.functional as F

class VideoCamera(object):
    def __init__(self, model, device):
        self.video = cv2.VideoCapture(0)
        self.model = model
        self.device = device
        self.show_confidence = True 
        
        # Load Face Cascade
        # Uses standard OpenCV Haar Cascade
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        self.emotions = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
        
        # Transformation pipeline matching the model training (usually 48x48 Grayscale)
        self.transform = transforms.Compose([
            transforms.Resize((48, 48)),
            transforms.ToTensor(),
            transforms.Normalize((0.5,), (0.5,))
        ])

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, image = self.video.read()
        if not success:
            return None
            
        # Convert to Grayscale for Face Detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect Faces (x, y, w, h)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        for (x, y, w, h) in faces:
            # Draw Region of Interest (ROI)
            cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            # Preprocess ROI for Model
            roi_gray = gray[y:y+h, x:x+w]
            roi_pil = Image.fromarray(roi_gray)
            
            roi_tensor = self.transform(roi_pil).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(roi_tensor)
                probs = F.softmax(outputs, dim=1)
                conf, predicted = torch.max(probs, 1)
                emotion_label = self.emotions[predicted.item()]
                confidence = conf.item() * 100
            
            # Overlay Emotion Label
            text = emotion_label
            if self.show_confidence:
                text += f" ({confidence:.1f}%)"
                
            cv2.putText(image, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)

        # Encode frame to JPEG
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()
