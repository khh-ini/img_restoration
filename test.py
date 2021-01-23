import cv2
import numpy as np

def img_mask(img, threshold1, threshold2, kernel):
    # Load GrayScale Image
    marked_demages = cv2.imread(img, 0)

    # Merubah menjadi citra binary
    ret, thresh1 = cv2.threshold(marked_demages, threshold1, threshold2, cv2.THRESH_BINARY)
    # Memperbesar ukuran citra binary
    kernel = np.ones(kernel, np.uint8)
    # mask = cv2.dilate(thresh1, kernel, iterations=1)
    mask = cv2.morphologyEx(thresh1, cv2.MORPH_DILATE, kernel)
    cv2.imwrite("static/masking.jpg", mask)

img_mask()