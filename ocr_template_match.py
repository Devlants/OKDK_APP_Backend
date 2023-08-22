import cv2
import pytesseract
from PIL import Image
import re

pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
def extract_card_info(image_path):
    # 이미지 로드
    image = Image.open(image_path)
    # 이미지 내의 텍스트 추출
    extracted_text = pytesseract.image_to_string(image)
    card_number = re.findall(r'\d{4} \d{4} \d{4} \d{4}', extracted_text)[0]
    expiration_date = re.findall(r'\d{2}/\d{2}', extracted_text)[0]
    cvc_number = re.findall(r'\d{3}', extracted_text)[0]

    return {
        'card_number': card_number,
        'expiration_date': expiration_date,
        'cvc_number': cvc_number
    }

card_image_path = 'C:\\Users\\jomul\\Desktop\\OKDK_APP_Backend\\media\\card_create\\스크린샷 2023-08-14 033411.png'

# 카드 정보 추출
card_info = extract_card_info(card_image_path)
print(card_info)

