import cv2
import numpy as np


detection_threshold = 140
detection_area = 5000
roi_x = 0
roi_y = 0
roi_w = 0
roi_h = 0

camera = None
camera_active = False

current_match_info = {
    "detected_count": 0,
    "status": "Scanning"
}


def init_camera():
    global camera, camera_active
    try:
        # Open default system camera index (0)
        camera = cv2.VideoCapture(0)
        if camera.isOpened():
            camera_active = True
            print("--> Camera tracking engine initialized successfully!")
        else:
            print("--> Warning: Camera hardware could not be opened.")
            camera_active = False
    except Exception as e:
        print(f"--> Error starting camera: {e}")
        camera_active = False
        
def generate_frames():
    global camera, camera_active, current_match_info, detection_threshold, detection_area
    global roi_x, roi_y, roi_w, roi_h
    
    while camera_active:
        success, frame = camera.read()
        if not success:
            print("--> Error: Failed to grab image from camera frame.")
            break


        if roi_w > 0 and roi_h > 0:
            analysis_zone = frame[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w]
            # Draw an Orange bounding box overlay to visually show the active workspace boundary
            cv2.rectangle(frame, (roi_x, roi_y), (roi_x + roi_w, roi_y + roi_h), (0, 165, 255), 2)
        else:
            # Otherwise, analyze the entire video frame canvas
            analysis_zone = frame


        gray_image = cv2.cvtColor(analysis_zone, cv2.COLOR_BGR2GRAY)
        
        
        _, binary_map = cv2.threshold(gray_image, int(detection_threshold), 255, cv2.THRESH_BINARY_INV)
        
        
        found_contours, _ = cv2.findContours(binary_map, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detected_count = 0

        
        for contour in found_contours:
            # Drop any item structural size that falls below your area constraint limit
            if cv2.contourArea(contour) > detection_area:
                detected_count += 1
                x, y, w, h = cv2.boundingRect(contour)
                live_crop_img = analysis_zone[y:y+h, x:x+w]
                # Offset vector points back to parent matrix coordinate scale if analyzing within a crop box
                if roi_w > 0 and roi_h > 0:
                    contour[:, :, 0] += roi_x
                    contour[:, :, 1] += roi_y

                # Draw a clean, thick green outline around the verified items on screen
                cv2.drawContours(frame, [contour], -1, (0, 255, 0), 3)

        
        current_match_info["detected_count"] = detected_count

        
        success, jpeg_buffer = cv2.imencode('.jpg', frame)
        if not success:
            continue
        raw_bytes = jpeg_buffer.tobytes()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + raw_bytes + b'\r\n')



init_camera()