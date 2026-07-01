import cv2 
import re 
import datetime

try:
    import pytesseract
except ModuleNotFoundError:
    pytesseract = None


def check_product_expiration(live_crop_img):
    
    if live_crop_img is None:
        print("Error : live crop image is not found !")
        return False , "live crop image is not found !"
    
    if pytesseract is None:
        print("Error: pytesseract is not installed.")
        return False, "pytesseract is not installed"

    gray = cv2.cvtColor(live_crop_img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    try:
        extracted_text = pytesseract.image_to_string(thresh)
        match = re.search(r'\d{2}/\d{2}/\d{4}', extracted_text)
        if not match:
            print("No expiration date found in the image.")
            return False, "No expiration date found in the image."
        date_str = match.group(0)
        print("extracted date string :", date_str)
        exp_date = datetime.datetime.strptime(date_str, "%d/%m/%Y")
        today = datetime.datetime.now()
        
        if exp_date < today:
            return False, "the product is expired"
        else:
            return True, "the product is valid"
            
    except Exception as e:
        print(f"Error: {e}")
        return False, "the product is expired"
        