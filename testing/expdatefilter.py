import cv2 
import re 
import datetime

try:
    import pytesseract
except ModuleNotFoundError:
    pytesseract = None

def check_product_expiration(live_crop_img):
    if live_crop_img is None:
        return False, "live crop image is not found!"
    
    if pytesseract is None:
        return False, "pytesseract is not installed"

    gray = cv2.cvtColor(live_crop_img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    
    try:
        extracted_text = pytesseract.image_to_string(thresh).upper()
        print(f"DEBUG OCR TEXT: {extracted_text}") # Track what your engine sees

        # Regex mapping fallback to capture format like '25 JUL'
        text_match = re.search(r'(\d{2})\s*(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)', extracted_text)
        
        if text_match:
            day = int(text_match.group(1))
            month_str = text_match.group(2)
            
            # Map month word strings to integers
            months_map = {"JAN":1,"FEB":2,"MAR":3,"APR":4,"MAY":5,"JUN":6,"JUL":7,"AUG":8,"SEP":9,"OCT":10,"NOV":11,"DEC":12}
            month = months_map[month_str]
            
            # Default to the current year since the stamp omits it
            today = datetime.datetime.now()
            exp_date = datetime.datetime(year=today.year, month=month, day=day)
            
            if exp_date.date() < today.date():
                return False, "the product is expired"
            return True, "the product is valid"

        # Fallback to your original numeric format slashes check
        slash_match = re.search(r'\d{2}/\d{2}/\d{4}', extracted_text)
        if slash_match:
            date_str = slash_match.group(0)
            exp_date = datetime.datetime.strptime(date_str, "%d/%m/%Y")
            if exp_date < datetime.datetime.now():
                return False, "the product is expired"
            return True, "the product is valid"

        return False, "No clear expiration pattern identified"
            
    except Exception as e:
        print(f"Error in Expiration Parsing Logic: {e}")
        return False, "Parsing logic failure error"