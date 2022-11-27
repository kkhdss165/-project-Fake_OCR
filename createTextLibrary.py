# 라이브러리 생성
import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image

# 글꼴지정
font = ImageFont.truetype("font/malgun.ttf", 40)
# 이미지 크기 지정
img = np.full((60, 60, 3), (255, 255, 255), dtype=np.uint8)

# 한글 생성
for i in range(11172):
    img[:60, :60] = (255, 255, 255)
    # cv2 이미지를 PIL 이미지로 변환
    imgPIL = Image.fromarray(img)
    draw = ImageDraw.Draw(imgPIL)
    text = chr(0xAC00 + i)

    num = str(i).zfill(5)
    file_name = "./img/library/" + num + ".png"
    # print(file_name)
    draw.text((5, 5), text, font=font, fill=(0, 0, 0))

    # PIL 이미지를 cv2 이미지로 변환
    img = np.array(imgPIL)
    # cv2.waitKey()
    # cv2.imshow('img', img)
    cv2.imwrite(file_name, img)

# 한글 이외의 문자 2만번대로 생성 (문장부호, 영어 대소문자)
for i in range(94):
    img[:60, :60] = (255, 255, 255)
    imgPIL = Image.fromarray(img)
    draw = ImageDraw.Draw(imgPIL)
    text = chr(0x021 + i)

    num = str(20000 + i).zfill(5)
    file_name = "./img/library/" + num + ".png"
    # print(file_name)
    draw.text((10, 5), text, font=font, fill=(0, 0, 0))

    img = np.array(imgPIL)
    # cv2.waitKey()
    # cv2.imshow('img', img)
    cv2.imwrite(file_name, img)

cv2.waitKey()
cv2.destroyAllWindows()