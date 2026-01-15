import cv2
import os
import json
import time
import threading
from google import genai
from google.genai import types

# --- CONFIGURATION ---
# Replace with your actual key
API_KEY = os.environ.get("GOOGLE_API_KEY", "AIzaSyD3rwVKFFsvNalp-1Q5i2miNmfvd5VdbRU")

client = genai.Client(api_key=API_KEY)

# --- GLOBAL SHARED VARIABLES ---
# These allow the two threads to talk to each other
current_frame = None
latest_detections = []
frame_lock = threading.Lock() # Prevents two threads from reading/writing at the exact same time
is_running = True

def api_worker():
    """
    This function runs in the background. It constantly checks for a new frame,
    sends it to Gemini, and updates the 'latest_detections' list.
    """
    global current_frame, latest_detections, is_running
    
    print("🚀 AI Worker Thread Started")
    
    while is_running:
        # 1. Grab the latest frame safely
        img_bytes = None
        with frame_lock:
            if current_frame is not None:
                # Encode immediately so we don't hold the lock while processing
                success, encoded = cv2.imencode('.jpg', current_frame)
                if success:
                    img_bytes = encoded.tobytes()
        
        # If we have an image, send it to Google
        if img_bytes:
            try:
                # Prompt optimized for speed
                prompt = """
                Locate objects. JSON format: [{"point": [y, x], "label": "name"}].
                Normalize 0-1000. Max 5 items.
                """
                
                response = client.models.generate_content(
                    model="gemini-robotics-er-1.5-preview",
                    contents=[
                        types.Part.from_bytes(data=img_bytes, mime_type='image/jpeg'),
                        prompt
                    ],
                    config=types.GenerateContentConfig(
                        temperature=0.5,
                        # Low thinking budget for speed
                        thinking_config=types.ThinkingConfig(thinking_budget=0) 
                    )
                )
                
                # Parse JSON
                text = response.text.replace("```json", "").replace("```", "").strip()
                new_data = json.loads(text)
                
                # Update the global detections list
                latest_detections = new_data
                
            except Exception as e:
                # If API fails (e.g. rate limit), just ignore and try again
                pass
        
        # Wait a tiny bit to not spam the API too hard (optional)
        time.sleep(0.1)

def main():
    global current_frame, is_running
    
    # Setup Camera
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # Start the background AI thread
    ai_thread = threading.Thread(target=api_worker, daemon=True)
    ai_thread.start()

    print("\n--- LIVE ROBOT EYE ACTIVE ---")
    print("The video is smooth, but detections update every ~1-2 seconds.")
    print("Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 1. Update the shared frame so the AI thread can see it
        with frame_lock:
            current_frame = frame.copy()

        # 2. Draw the LATEST KNOWN detections
        # (These might be from 1 second ago, but that's okay!)
        height, width, _ = frame.shape
        
        for item in latest_detections:
            try:
                y_norm, x_norm = item['point']
                label = item['label']
                
                x = int((x_norm / 1000) * width)
                y = int((y_norm / 1000) * height)
                
                # Visual styling
                cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
                cv2.putText(frame, label, (x + 10, y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 3)
                cv2.putText(frame, label, (x + 10, y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
            except:
                pass

        # 3. Show the video
        cv2.imshow('Live Robot Eye', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            is_running = False
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()