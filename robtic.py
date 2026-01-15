import cv2
import os
import json
import time
from google import genai
from google.genai import types

# --- CONFIGURATION ---
# 1. PASTE YOUR API KEY INSIDE THE QUOTES BELOW
API_KEY = "AIzaSyD3rwVKFFsvNalp-1Q5i2miNmfvd5VdbRU" 

# If you exported it in terminal, we try to grab it from there first
if "GOOGLE_API_KEY" in os.environ:
    API_KEY = os.environ["GOOGLE_API_KEY"]

print(f"🔑 Using API Key: {API_KEY[:5]}... (hidden)")

client = genai.Client(api_key=API_KEY)

def analyze_image(image_bytes):
    print("\n🤖 Gemini is thinking...")
    prompt = """
    Locate up to 5 distinct objects in this image.
    Return a raw JSON list. Format: [{"point": [y, x], "label": "name"}].
    Normalize points to 0-1000. Do not use Markdown formatting.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-robotics-er-1.5-preview",
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg'),
                prompt
            ],
            config=types.GenerateContentConfig(
                temperature=0.5,
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            )
        )
        # Clean up response to ensure valid JSON
        text = response.text.replace("```json", "").replace("```", "").strip()
        print(f"📝 Raw Response: {text}") # Debug print
        return json.loads(text)
    except Exception as e:
        print(f"❌ Error calling API: {e}")
        return []

def main():
    # Use Camera Index 0 since your test confirmed it works
    cap = cv2.VideoCapture(0)
    
    # Warm up the camera
    time.sleep(1) 

    if not cap.isOpened():
        print("❌ Error: Could not open video device.")
        return

    # Set resolution to 640x480 for faster processing
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print("\n--- ROBOT EYE ACTIVE ---")
    print("👉 Point camera at an object")
    print("👉 Press 'SPACE' to detect objects")
    print("👉 Press 'q' to quit")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to grab frame. Exiting...")
            break

        # Show the live feed
        cv2.imshow('Robot Eye - Gemini 1.5', frame)

        key = cv2.waitKey(1) & 0xFF

        # If SPACE is pressed, take a snapshot and analyze
        if key == ord(' '):
            print("📸 Snap! Sending to Google...")
            
            # 1. Encode image to bytes for API
            success, encoded_image = cv2.imencode('.jpg', frame)
            if success:
                # 2. Send to Gemini
                detections = analyze_image(encoded_image.tobytes())
                
                # 3. Draw results on the captured frame
                height, width, _ = frame.shape
                
                if not detections:
                    print("⚠️ No objects detected or JSON error.")
                
                for item in detections:
                    try:
                        y_norm, x_norm = item['point']
                        label = item['label']
                        
                        # Convert 0-1000 scale to actual pixel coordinates
                        x = int((x_norm / 1000) * width)
                        y = int((y_norm / 1000) * height)
                        
                        # Draw a green circle
                        cv2.circle(frame, (x, y), 8, (0, 255, 0), -1) 
                        # Draw a text label with a black background for readability
                        cv2.putText(frame, label, (x + 15, y), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 4) # Thick black outline
                        cv2.putText(frame, label, (x + 15, y), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2) # Green text
                    except Exception as e:
                        print(f"Error drawing item: {e}")

                # Show the analyzed image (stops the video)
                cv2.imshow('Robot Eye - Gemini 1.5', frame)
                print("✅ Analysis complete. Press ANY KEY to continue video.")
                cv2.waitKey(0)

        # If 'q' is pressed, quit
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()