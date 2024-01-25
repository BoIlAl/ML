import cv2
import pytesseract
import numpy as np
import matplotlib.pyplot as plt
import re

def is_float(value):
  if value is None:
      return False
  try:
      float(value)
      return True
  except:
      return False


class TextRecognizer:
    def __init__(self) -> None:
        pytesseract.pytesseract.tesseract_cmd = 'E:/Tesseract-OCR/tesseract.exe'
    
    @staticmethod
    def _apply_filters(img):
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, th_img = cv2.threshold(gray_img, 200, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        res_img = cv2.dilate(th_img,np.zeros((5,5),np.uint8),iterations = 1)
        plt.imshow(res_img)
        return res_img

    def extract_product_info(self, img_path: str):
        img = cv2.imread(img_path)
        img = TextRecognizer._apply_filters(img)
        text = pytesseract.image_to_string(img, lang='rus')

        #print(text)

        return self._contain_key_word(text)


    def _contain_key_word(self, text: str):
        new_str = ' ' + text.replace('\n', ' ') + ' '
        key_words = []

        product_info = {
            'products_protein' : 0.0,
            'products_fat' : 0.0,
            'products_carbs' : 0.0
        }

        def get_from_math(_match):
            s = _match[0].replace('—',' ')
            s = s.replace('-', ' ')
            found = s.split(' ')

            fff = [fs for fs in found if len(fs) > 0]
            if (len(fff) < 2):
                return None
            fff[1] = fff[1].replace(',', '.')

            if is_float(fff[1]):
                return float(fff[1])


        if re.search(r'\bжир[ыао]в?\b', new_str, re.IGNORECASE):
            key_words.append('жиры')

            match = re.search(r'жир[ыао]в?\s?[—-]?\s?[0123456789]+[,.\s]?[0123456789]+\s?[г]?', new_str, re.IGNORECASE)
            if match:
                product_info['products_fat'] = get_from_math(match)


        if re.search(r'\bуглевод[ыо]в?\b', new_str, re.IGNORECASE):
            key_words.append('углеводы')

            match = re.search(r'углевод[ыо]в?\s?[—-]?\s?[0123456789]+[,.\s]?[0123456789]+\s?[г]?', new_str, re.IGNORECASE)
            if match:
                product_info['products_carbs'] = get_from_math(match)
            
        
        if re.search(r'\bбелк[аио]в?\b', new_str, re.IGNORECASE):
            key_words.append('белки')

            match = re.search(r'белк[аио]в?\s?[—-]?\s?[0123456789]+[,.\s]?[0123456789]+\s?[г]?', new_str, re.IGNORECASE)
            if match:
                product_info['products_protein'] = get_from_math(match)
        
        return product_info
