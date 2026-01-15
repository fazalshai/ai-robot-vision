import cv2

def test_camera():
    print("Attempting to open camera...")
    
    # Try index 0 first, then index 1
    for index in [0, 1]:
        print(f"Testing Camera Index {index}...")
        cap = cv2.VideoCapture(index)
        
        if not cap.isOpened():
            print(f"❌ Could not open camera {index}")
            continue
        
        ret, frame = cap.read()
        if not ret:
            print(f"❌ Camera {index} opened but returned no image (Check Permissions!)")
            cap.release()
            continue
            
        print(f"✅ SUCCESS! Camera {index} is working.")
        print("Press 'q' to quit the video window.")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            cv2.imshow(f"Camera {index} Test", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        return # Exit after finding a working camera

    print("\n--- TROUBLESHOOTING ---")
    print("If no camera opened:")
    print("1. Go to System Settings -> Privacy & Security -> Camera")
    print("2. Ensure 'Terminal' is allowed.")
    print("3. Restart Terminal completely.")

if __name__ == "__main__":
    test_camera()