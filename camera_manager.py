import cv2
import numpy as np
import os
import sqlite3

# Global variables
camera = None
camera_active = False
current_match_info = {
    "name": "No object detected",
    "reference": "None",
    "image_url": "",
    "count": 0
}
cached_templates = []

def init_camera():
    """Starts up the camera hardware and loads database templates on startup."""
    global camera, camera_active, cached_templates
    
    # 1. Try to open the webcam
    try:
        camera = cv2.VideoCapture(0)
        if camera.isOpened():
            camera_active = True
            print("--> Camera found and started successfully!")
        else:
            print("--> Warning: Camera hardware could not be opened.")
            camera_active = False
    except Exception as e:
        print(f"--> Error starting camera: {e}")
        camera_active = False

    # 2. Pre-load your database pictures 
    cached_templates = load_product_templates()


def load_product_templates():
    """Reads saved product images from the database and grabs their shapes."""
    templates_list = []
    
    # Safety check: if the uploads folder doesn't exist yet, stop here
    if not os.path.exists("uploads"):
        return templates_list
        
    try:
        # Connect to  SQLite product database 
        conn = sqlite3.connect("product.db")
        cursor = conn.cursor()
        cursor.execute("SELECT prod_ref, prod_name, prod_img1 FROM products")
        all_rows = cursor.fetchall()
        conn.close()
        
        for row in all_rows:
            ref = row[0]
            name = row[1]
            img_name = row[2] 
            
            # Find the path to the file on your computer
            img_path = os.path.join("uploads", img_name)
            
            if os.path.exists(img_path):
                # Process the saved image into a shape contour
                saved_img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                _, thresh = cv2.threshold(saved_img, 130, 255, cv2.THRESH_BINARY_INV)
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                if contours:
                    # Grab the largest detected shape contour from the image
                    largest_contour = max(contours, key=cv2.contourArea)
                    
                    # Store it in a simple dictionary list
                    templates_list.append({
                        "reference": ref,
                        "name": name,
                        "img_url": f"/uploads/{img_name}",
                        "contour": largest_contour
                    })
        print(f"--> Database Sync: Loaded {len(templates_list)} items for matching.")
    except Exception as e:
        print(f"--> Error loading database shapes: {e}")
        
    return templates_list


def generate_frames():
    """Continuously captures frames from the camera, tracks objects, and streams them."""
    global camera, camera_active, current_match_info, cached_templates
    
    while camera_active:
        success, frame = camera.read()
        if not success:
            print("--> Error: Failed to grab image from camera frame.")
            break

        # --- STEP 1: Turn image to black and white for shape detection ---
        gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 
        _, binary_map = cv2.threshold(gray_image, 130, 255, cv2.THRESH_BINARY_INV)
        
        # --- STEP 2: Find all shape outlines (contours) ---
        found_contours, _ = cv2.findContours(binary_map, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detected_count = 0
        best_match_found = None
        lowest_score = 0.28  # Sensitivity cutoff (lower means a closer shape match)

        # --- STEP 3: Loop through each detected object ---
        for contour in found_contours:
            # Only count the item if it's large enough (filters out tiny visual noise)
            if cv2.contourArea(contour) > 4000: 
                detected_count += 1 
                
                # Draw a bright green outline around the object on screen
                cv2.drawContours(frame, [contour], -1, (0, 255, 0), 3)

                # Compare this live shape with your saved product blueprints
                for template in cached_templates:
                    # OpenCV checks how closely the curves match
                    score = cv2.matchShapes(contour, template["contour"], 1, 0.0)
                    
                    # If it looks closer than anything else we've seen, remember it
                    if score < lowest_score:
                        lowest_score = score
                        best_match_found = template

        # --- STEP 4: Update our global live data tracking info ---
        if best_match_found and detected_count > 0:
            current_match_info = {
                "name": best_match_found["name"],
                "reference": best_match_found["reference"],
                "image_url": best_match_found["img_url"],
                "count": detected_count
            }
        elif detected_count == 0:
            current_match_info = {
                "name": "No object detected",
                "reference": "None",
                "image_url": "",
                "count": 0
            }

        
        
        # --- STEP 5: Package the frame up as a clean image stream for Flask ---
        success, jpeg_buffer = cv2.imencode('.jpg', frame)
        if not success:
            continue
            
        raw_bytes = jpeg_buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + raw_bytes + b'\r\n')



init_camera()