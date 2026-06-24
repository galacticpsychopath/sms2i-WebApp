import os
import json
import time
from flask import Flask, render_template, Response, jsonify, request
from camera_manager import camera_manager

app = Flask(__name__)

# --- ACTIVE ENGINES ---
engine_config = {
    "threshold": 0.50,
    "roi": [0, 0, 640, 480],
    "ioa": 0.0
}

# --- GLOBAL INDUSTRIAL PRODUCT DATABASES ---
# Stores product details and historical tracking counts
product_registry = {}

session_stats = {
    "session_total": 0,
    "detected_object": None  # Will hold: {"name": x, "reference": y, "image_url": z}
}

UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/')
def object_counting():
    return render_template('objectcounting.html')


def gen(camera_instance):
    while True:
        frame = camera_instance.get_frame()
        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.01)

@app.route('/objectcounting')
def video_feed():
    return Response(gen(camera_manager),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/stats', methods=['GET'])
def get_stats():
    # Append the exact total count of this specific item dynamically if detected
    response_data = dict(session_stats)
    if session_stats["detected_object"]:
        ref = session_stats["detected_object"]["reference"]
        if ref in product_registry:
            response_data["session_total"] = product_registry[ref]["count"]
    return jsonify(response_data)


@app.route('/api/configure', methods=['POST'])
def configure_engine():
    try:
        data = request.json
        if not data: return jsonify({"status": "error"}), 400
        if 'threshold' in data: engine_config['threshold'] = float(data['threshold'])
        if 'ioa' in data: engine_config['ioa'] = float(data['ioa'])
        return jsonify({"status": "success", "config": engine_config}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/add_product', methods=['POST'])
def add_product():
    """Saves details and binds dynamic paths directly to identification buffers."""
    try:
        product_name = request.form.get('product_name')
        reference_code = request.form.get('reference_code')
        files = request.files.getlist('product_images')

        if not product_name or not reference_code or len(files) != 3:
            return jsonify({"status": "error", "message": "Invalid form payload."}), 400

        saved_paths = []
        for index, file in enumerate(files):
            if file.filename != '':
                filename = f"{reference_code}_angle_{index}.png"
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                saved_paths.append(file_path)

        # Register inside memory map arrays
        product_registry[reference_code] = {
            "name": product_name,
            "images": saved_paths,
            "count": 0
        }

        # Sync registry tracking data straight over to the camera manager module
        camera_manager.update_registry(product_registry)

        print(f"[Registry Sync]: {product_name} ({reference_code}) loaded into active identification memory maps.")
        return jsonify({"status": "success"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)