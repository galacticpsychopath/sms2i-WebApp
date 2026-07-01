import cv2
import os


def check_product_existence(live_crop_img, all_db_products, similarity_threshold=0.70):
    
    if live_crop_img is None or not all_db_products:
        print("Error: live crop image is not found or database is empty !")
        return False, "the product does not exist"
    
    for product in all_db_products:
        prod_ref=product[0]
        prod_name=product[1]
        img_filename=product[2]
        image_path = os.path.join('uploads', img_filename)
        perfect_database_img = cv2.imread(image_path)
        if perfect_database_img is None:
            print(f"Error: perfect database image for {prod_name} not found at {image_path} !")
            continue
        #resize for comparison
        live_crop_img_resized = cv2.resize(live_crop_img, (perfect_database_img.shape[1],perfect_database_img.shape[0]))
        gray_live_img =cv2.cvtColor(live_crop_img_resized, cv2.COLOR_BGR2GRAY)
        gray_perfect_img =cv2.cvtColor(perfect_database_img, cv2.COLOR_BGR2GRAY)
        
        result = cv2.matchTemplate(gray_live_img, gray_perfect_img, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)
        
        if max_val >= similarity_threshold:
            print(f" Match found! Identified: {prod_name} ({prod_ref})")
            return True, "the product exists"
        
        print(f" No match found for: {prod_name} ({prod_ref})")

    print("Checked all products in database. No match found.")
    return False, "the product does not exist"
        