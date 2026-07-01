import cv2

def check_product_form(live_crop_img, perfect_database_img, similarity_threshold=0.70):
    if live_crop_img is None or perfect_database_img is None:
        print("Error: one or both imgs are not found !")
        return False
    #resize for comparison
    live_crop_img_resized = cv2.resize(live_crop_img,( perfect_database_img.shape[1], perfect_database_img.shape[0]))
    # Convert both images to grayscale
    gray_live_img =cv2.cvtColor(live_crop_img_resized, cv2.COLOR_BGR2GRAY)
    gray_perfect_img=cv2.cvtColor(perfect_database_img, cv2.COLOR_BGR2GRAY)
    # Use template matching to compare the two images
    result = cv2.matchTemplate(gray_live_img, gray_perfect_img, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)
    if max_val >= similarity_threshold:
        return True, "the product is in good form"
    else:
        return False, "the product is in bad form"
    