import os
import json
import time
from flask import Flask, render_template, Response, jsonify, request, url_for , send_from_directory
import camera_manager
from testing import formfilter
from testing import expdatefilter
from testing import exsistingproddetection
import sqlite3


app = Flask(__name__, template_folder='templates', static_folder='static')


# routes for web pages
@app.route('/')
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/livefeed')
def live_feed_page():
    
    return render_template('livefeed.html')

@app.route('/register')
def registerproduct():
    return render_template('registerproduct.html')

# product saving path 
upload_folder = 'uploads'
os.makedirs(upload_folder, exist_ok=True) 

# data base setup 
BD_path = "product.db"

def init_db():
    conn = sqlite3.connect(BD_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            prod_ref TEXT UNIQUE NOT NULL,
            prod_name TEXT NOT NULL,
            prod_img1 TEXT NOT NULL,
            prod_img2 TEXT NOT NULL,
            prod_img3 TEXT NOT NULL
        )
    ''')
    conn.commit() 
    conn.close()     
 
init_db() 


def dbinsert_product(ref, name, img1, img2, img3):
    conn = sqlite3.connect(BD_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO products (prod_ref, prod_name, prod_img1, prod_img2, prod_img3) 
        VALUES (?, ?, ?, ?, ?)
    ''', (ref, name, img1, img2, img3))
    conn.commit()
    conn.close()

 
def dbproduct_exists(prod_ref):
    conn = sqlite3.connect(BD_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM products WHERE prod_ref=?", (prod_ref,))
    result = cur.fetchone()
    conn.close()
    return result


def dbget_all_products():
    conn = sqlite3.connect(BD_path)
    cur = conn.cursor()
    # FIX: Select the correct columns matching your table schema layout
    cur.execute("SELECT prod_ref, prod_name, prod_img1, prod_img2, prod_img3 FROM products")
    result = cur.fetchall()
    conn.close()
    return result


def dbdelete_product(prod_ref):
    conn = sqlite3.connect(BD_path)
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE prod_ref=?", (prod_ref,)) 
    conn.commit()
    conn.close()

# ==========================================
# API ROUTES FOR DATA HANDLING
# ==========================================

@app.route('/api/register_product', methods=['POST'])
def register_product():
    data = request.form
    prod_ref = data.get('prod_ref')
    prod_name = data.get('prod_name')
    files = request.files.getlist('images')

    print("Form Keys received:", request.form.keys())
    print("File Keys received:", request.files.keys())
    print("Files list length:", len(files))
    
    len_files = 0
    for file in files:
        if file and file.filename:
            len_files += 1

    if not prod_ref or not prod_name or len_files != 3:
        return jsonify({'error': 'Provide a reference, name, and exactly 3 images.'}), 400

    if dbproduct_exists(prod_ref):
        return jsonify({'error': 'Product already exists'}), 400

    saved_filenames = []
    
    # FIX: Loop through each file using enumerate to save all three items uniquely
    for index, file in enumerate(files):
        filename = f"{prod_ref}_angle_{index}.png"
        # Using hardcoded static pathway so images load on the UI pages seamlessly
        file.save(os.path.join('uploads', filename))
        saved_filenames.append(filename)

    # FIX: Pass all three generated filenames to your insertion function
    dbinsert_product(prod_ref, prod_name, saved_filenames[0], saved_filenames[1], saved_filenames[2])
    
    return jsonify({'message': 'Product registered successfully'}), 201 

#display all products
@app.route('/uploads/<filename>')
def serve_upload_file(filename):
    uploads_dir = os.path.join(app.root_path, 'uploads')
    return send_from_directory(uploads_dir, filename)

@app.route('/api/get_products', methods=['GET'])
def get_products():
    # 1. Pull the raw database array list
    raw_rows = dbget_all_products() 
    
    # 2. Build a brand new list to hold mapped dictionaries
    formatted_products = []
    
    for row in raw_rows:
        # Convert the raw array [0, 1, 2, 3, 4] into the key-value names your JS is screaming for
        formatted_products.append({
            "reference": row[0],
            "name": row[1],
            "image_url": f"/uploads/{row[2]}" if row[2] else "",
            "image_url2": f"/uploads/{row[3]}" if row[3] else "",
            "image_url3": f"/uploads/{row[4]}" if row[4] else ""
        })
          
    # 3. Return the clean JSON objects to your JavaScript frontend fetch call
    return jsonify(formatted_products)
@app.route('/api/delete_product', methods=['POST'])
def delete_product():
    data = request.get_json()
    print("!!! DELETE API HIT !!!",data)
    prod_ref = data.get('reference')
    print("Product reference received for deletion:", prod_ref)
    if not prod_ref:
        return jsonify({'error': 'Product reference is required'}), 400
    if not dbproduct_exists(prod_ref):
        return jsonify({'error': 'Product does not exist'}), 404
    else:
        dbdelete_product(prod_ref)
        return jsonify({'message': 'Product deleted successfully'}), 200



@app.route('/video_feed')
def video_feed():
    """Streams live video directly to the livefeed html <img> element."""
    if not camera_manager.camera_active:
        return "Camera hardware is not running.", 503
    return Response(camera_manager.generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/current_detection')
def current_detection():
    
    return jsonify(camera_manager.current_match_info)


@app.route('/api/update_config', methods=['POST'])
def update_config():
    data = request.get_json()
    print("Config update request received:", data)
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    threashold = data.get('threashold')
    objectarea = data.get('objectarea')
    roivalues = data.get('roi')
    if roivalues and len(roivalues)==4 :
        camera_manager.roi_x = int(roivalues[0])
        camera_manager.roi_y = int(roivalues[1])
        camera_manager.roi_w = int(roivalues[2])
        camera_manager.roi_h = int(roivalues[3])
        
    if threashold is not None:
        camera_manager.detection_threshold = float(threashold)
    if objectarea is not None:
        camera_manager.detection_area = float(objectarea)

    return jsonify({'message': 'Configuration updated successfully'}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)