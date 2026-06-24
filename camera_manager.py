import cv2 
import time
import numpy as np

class CameraManager:
    def __init__(self):
        # --- Camera Hardware Initialization ---
        self.live = cv2.VideoCapture(0)
        if not self.live.isOpened():
            self.live = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            
        if not self.live.isOpened():
            print("[Camera Hardware ERROR]: Operational camera device not found.")

        # --- Dashboard Core Properties ---
        self.battery_level = 100.0
        self.last_battery_check = time.time()
        self.robot_status = "Active"
        
        # --- Dynamic Object & Count Properties ---
        self.detected_object = None       # Maps to current product name detected
        self.detected_ref = None          # Reference SKU ID code
        self.total_detections = 0         # Cumulative total tracker counter
        self.already_counted = False      # State lock to prevent duplicate counting of a single object
        self.stats = {"Plastic": 0, "Metal": 0, "Organic": 0, "Paper": 0, "Glass": 0}
        self.product_registry = {}
        self.processing_threshold = 0.5
        self.roi = [0, 0, 640, 480]
        self.ioa = 0.0
        
        # --- Configurable Processing Thresholds ---
        self.min_contour_area = 1500
        self.binary_threshold = 100

    def update_registry(self, registry):
        """Updates the in-memory product registry used by the detection engine."""
        self.product_registry = registry or {}

    def update_config(self, threshold=None, ioa=None, roi=None):
        """Applies configuration values sent from the front-end engine controls."""
        if threshold is not None:
            self.processing_threshold = float(threshold)
            self.binary_threshold = int(max(0.0, min(1.0, self.processing_threshold)) * 255)
        if ioa is not None:
            self.ioa = float(ioa)
        if roi is not None and isinstance(roi, (list, tuple)) and len(roi) == 4:
            self.roi = [int(roi[0]), int(roi[1]), int(roi[2]), int(roi[3])]

    def _update_telemetry(self):
        """Simulates battery usage consumption to keep the UI panels dynamic."""
        current_time = time.time()
        if current_time - self.last_battery_check > 5.0:
            if self.robot_status == "Active":
                self.battery_level = max(0.0, round(self.battery_level - 0.1, 1))
            self.last_battery_check = current_time

    def get_frame(self):
        self._update_telemetry()

        # Fallback Canvas Generation logic if camera fails
        if not self.live.isOpened():
            return self._generate_error_frame("CAMERA HARDWARE ERROR")

        ret, frame = self.live.read()
        if not ret or frame is None:
            return self._generate_error_frame("FRAME READ ERROR")

        # Handle system standby state smoothly
        if self.robot_status == "Standby":
            standby_canvas = frame.copy()
            h, w = standby_canvas.shape[:2]
            cv2.rectangle(standby_canvas, (0, 0), (w, h), (0, 0, 0), -1)
            cv2.putText(standby_canvas, "SYSTEM STANDBY", (170, 240), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 165, 255), 2)
            ret, jpeg = cv2.imencode('.jpg', standby_canvas)
            return jpeg.tobytes() if ret else None

        objects_detected = 0
        x0, y0, x1, y1 = self.roi
        h, w = frame.shape[:2]
        x0 = max(0, min(x0, w - 1))
        x1 = max(0, min(x1, w))
        y0 = max(0, min(y0, h - 1))
        y1 = max(0, min(y1, h))

        processing_frame = frame[y0:y1, x0:x1] if (x1 > x0 and y1 > y0) else frame
        gray = cv2.cvtColor(processing_frame, cv2.COLOR_BGR2GRAY)
        _, binary_map = cv2.threshold(gray, self.binary_threshold, 255, cv2.THRESH_BINARY_INV)

        # Step 2: Computer Vision Shape Detection
        contours, _ = cv2.findContours(binary_map, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            if cv2.contourArea(contour) > self.min_contour_area:
                objects_detected += 1
                rx, ry, rw, rh = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x0 + rx, y0 + ry), (x0 + rx + rw, y0 + ry + rh), (255, 0, 0), 2)

        # --- STATE AND COUNT HANDLING PIPELINES ---
        if objects_detected > 0:
            if self.product_registry:
                detected_ref, product = next(iter(self.product_registry.items()))
                self.detected_object = product.get("name", "Product Asset")
                self.detected_ref = detected_ref
                if not self.already_counted:
                    self.total_detections += 1
                    product["count"] = product.get("count", 0) + 1
                    self.already_counted = True
            else:
                self.detected_object = "Product Asset"
                self.detected_ref = f"REF-{objects_detected:03d}"
                if not self.already_counted:
                    self.total_detections += 1
                    self.stats["Plastic"] += 1
                    self.already_counted = True
        else:
            self.detected_object = None
            self.detected_ref = None
            self.already_counted = False

        # Step 3: Text Render Overlays & State Maps on Matrix
        cv2.putText(frame, f"Objects Tracked: {objects_detected}", (20, 45), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        cv2.putText(frame, f"Total Detections: {self.total_detections}", (20, 80), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        if self.detected_ref:
            cv2.putText(frame, f"ID: {self.detected_ref}", (20, 110), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        # Compress output array array stream to bytes for rendering
        ret, jpeg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
        return jpeg.tobytes() if ret else None

    def _generate_error_frame(self, message):
        """Generates a stable message fallback display frame."""
        frame = np.zeros((480, 640, 3), np.uint8)
        cv2.putText(frame, message, (140, 240), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes() if ret else None

    def toggle_status(self):
        self.robot_status = "Active" if self.robot_status == "Standby" else "Standby"
        return self.robot_status

    def get_faults(self):
        """Generates runtime system alert logs dynamically."""
        faults = []
        if not self.live.isOpened():
            faults.append({
                "component": "Vision Sensor",
                "issue": "I/O Hardware Bus Disconnected",
                "severity": "Critical",
                "timestamp": time.strftime("%H:%M:%S")
            })
        if self.battery_level < 20.0:
            faults.append({
                "component": "Power Supply",
                "issue": "Low System Voltage Warning",
                "severity": "Warning",
                "timestamp": time.strftime("%H:%M:%S")
            })
        return faults

# Singleton Export Engine Initialization Hook
camera_manager = CameraManager()