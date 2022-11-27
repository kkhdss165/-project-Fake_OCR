import cv2
import numpy as np
import glob
import tkinter
from tkinter import *
from tkinter import messagebox

# 공백의 크기를 판단하는 변수
space_size_y = 1
space_size_x = 1

file_list = glob.glob('./img/library/*')  # 라이브러리 위치
sample_list = glob.glob('./img/example/*')  # 비교할 샘플 위치
window_name = "Sample Image"  # 이미지 창 이름

image_library = []
# 샘플들 미리 읽기
for i in file_list:  # 라이브러리 한 모양씩 매칭하기
    print(i)
    target = cv2.imread(i)
    targetGray = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
    _, targetTh = cv2.threshold(targetGray, 140, 255, cv2.THRESH_BINARY_INV)
    cntrs_target, _ = cv2.findContours(targetTh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 컨투어의 x,y축의 최소 최대 좌표 구하기(관심 영역 지정이 필요)
    z1, z2, w1, w2 = -1, -1, -1, -1
    for cnt in cntrs_target:

        for l in cnt:
            # print(l)
            if z1 == -1:
                w1 = l[0][0]
                w2 = l[0][0]
                z1 = l[0][1]
                z2 = l[0][1]
            if l[0][1] < z1:
                z1 = l[0][1]
            if l[0][1] > z2:
                z2 = l[0][1]
            if l[0][0] < w1:
                w1 = l[0][0]
            if l[0][0] > w2:
                w2 = l[0][0]

    roi_file = targetGray[z1 - 2:z2 + 3, w1 - 2:w2 + 3]

    # cv2.imshow('roi_file', roi_file)
    # cv2.waitKey()
    # cv2.destryAllWindows()

    image_library.append((i , roi_file ))

texts = []  # img의 텍스트 리스트
result = ""  # 결과

is_sort = False  # 텍스트리스트 정렬 여부

img = None
img2 = None  # 원본을 살리기위해 img2를 사용
imgray = None
imthres = None
contour = None


# 결과 출력 함수
def print_result():
    print("result >> ")
    print(result)


# 문자 비교시 제일 근접한 문자의 파일명을 텍스트로 변경
def get_text_name(file_name):
    cord = file_name[-9:-4]  # 파일명 뒤에서 5~9번째 자리의 텍스트 앞에 폴더/ 와 .png자르기 위함

    # 한글 파일의 범위 00000 ~ 11171
    if int(cord) < 20000:
        return chr(0xAC00 + int(cord))  # 한글 유니코드의 범위는 0xAC00 ~ 0xD79F

    # 이외 파일
    else:
        return chr(0x021 + (int(cord) - 20000))  # 유니코드 0x021 ~ 0x07E의 범위의 문자는 문장 부호, 알파벳으로 구성


# 문자의 영역을 파란선으로 그려주는 함수
def draw_blueline():
    for n in texts:
        x1, x2, y1, y2 = n
        cv2.rectangle(img2, (y1 - 2, x1 - 2), (y2 + 2, x2 + 2), (255, 0, 0), 1)

    cv2.imshow(window_name, img2)
    cv2.waitKey(100)


# 문자를 비교하기 전에 이미지파일의 도형을 분리하고 분리된 텍스트를 한 묶음으로 묶어주는 함수
def combine_Texts():
    global texts
    texts = []
    for i in contour:
        x1, x2, y1, y2 = -1, -1, -1, -1

        # texts리스트에 중복 삽입을 방지하기 위한 변수
        is_append = False
        cv2.imshow(window_name, img2)

        # 컨투어를 이용해서 가로 세로 최고 최소 자표를 구한다.
        for j in i:
            # 초기값일때
            if x1 == -1:
                y1 = j[0][0]
                y2 = j[0][0]
                x1 = j[0][1]
                x2 = j[0][1]
            if j[0][1] < x1:
                x1 = j[0][1]
            if j[0][1] > x2:
                x2 = j[0][1]
            if j[0][0] < y1:
                y1 = j[0][0]
            if j[0][0] > y2:
                y2 = j[0][0]

        # 현재 도형과 기존에 있던 도형이 한 글자의 포함되는지 검사한다.
        for n in texts:

            if is_append == False:

                # 상하 붙이기
                if (y2 < n[2]) | (y1 > n[3]) == False:
                    if n[0] - x2 <= space_size_x:
                        # 조건의 만족으로 texts리스트의 값을 수정한다.(범위를 넓힌다)
                        tp_text = tuple(texts)

                        idx = tp_text.index(n)
                        texts = list(tp_text)
                        texts[idx] = (min(n[0], x1), max(n[1], x2), min(n[2], y1), max(n[3], y2))

                        # 이후 빠져나간다.
                        is_append = True
                        break

                        # 좌우 붙이기
                if (x2 < n[0]) | (x1 > n[1]) == False:
                    if y1 - n[3] <= space_size_y and n[2] - y2 <= space_size_y:
                        # 조건의 만족으로 texts리스트의 값을 수정한다.(범위를 넓힌다)
                        tp_text = tuple(texts)

                        idx = tp_text.index(n)
                        texts = list(tp_text)
                        texts[idx] = (min(n[0], x1), max(n[1], x2), min(n[2], y1), max(n[3], y2))

                        is_append = True
                        break

                        # 겹침 처리
                if ((x2 < n[0]) | (x1 > n[1]) | (y2 < n[2]) | (y1 > n[3])) == False:
                    # 조건의 만족으로 texts리스트의 값을 수정한다.(범위를 넓힌다)
                    tp_text = tuple(texts)

                    idx = tp_text.index(n)
                    texts = list(tp_text)
                    texts[idx] = (min(n[0], x1), max(n[1], x2), min(n[2], y1), max(n[3], y2))

                    is_append = True
                    break

                    # 텍스트 리스트에 아무것도 없을때 추가한다.
        if len(texts) == 0:
            # print("NULL")
            is_append = True
            texts.append((x1, x2, y1, y2))

        # 조건을 모두 통과하지 못한경우(겹치지도 않고, 붙여지지도 않은 독립된 문자)
        if is_append == False:
            texts.append((x1, x2, y1, y2))

        cv2.imshow(window_name, img2)

    # 시각화를 위해 파란선을 그린다.
    draw_blueline()


# 텍스트 리스트를 정렬하는 함수
def sort_Texts():
    global texts, is_sort

    # 이미 정렬된 경우 리턴
    if is_sort == True:
        return

    texts.reverse()  # 컨투어가 좌측하단부터 생성되기 때문에 리버스를 한다.
    c_texts = list(texts)  # texts를 복사해 이후에 순서를 맞게 정렬한 리스트들은 삭제한다.
    t_texts = list(texts)  # c_texts가 for반복문에서 원소가 삭제되면 원소의 순서가 바뀌기 때문에 선언
    texts.clear()  # texts를 모두 비운다
    # print(c_texts)

    while True:
        temp_list = []  # 한줄에 들어갈 글씨들의 임시 리스트를 선언한다
        min_x = -1  # 한 줄의 y축의 최소값
        max_x = -1  # 한 줄의 y축의 최대값
        for n in t_texts:
            if n in c_texts:

                # 초기값의 경우
                if min_x == -1:
                    min_x = n[0]
                    max_x = n[1]
                    # 한줄에 들어갈 리스트에 추가하고 c_texts에서는 제거
                    temp_list.append((n[0], n[1], n[2], n[3]))
                    c_texts.remove((n[0], n[1], n[2], n[3]))

                else:
                    # y축에서 좌표들이 겹치지 않을때의 부정조건을 이용해서 y축에 좌표들이 겹칠때의 조건
                    if (max_x < n[0]) | (min_x > n[1]) == False:
                        # 한줄의 y좌표 최대 최소 수정후에 한줄에 들어갈 리스트에 추가하고 c_texts에서는 제거
                        min_x = min(n[0], min_x)
                        max_x = max(n[1], max_x)
                        temp_list.append((n[0], n[1], n[2], n[3]))
                        c_texts.remove((n[0], n[1], n[2], n[3]))

        # (x1,x2,y1,y2)에서 y1, x축의 시작 좌표로 정렬
        temp_list.sort(key=lambda x: x[2])
        # print(temp_list)

        # texts뒤에 temp_list를 붙인다.
        texts.extend(temp_list)

        # 모두 삭제했을경우 반복문 탈출
        if len(c_texts) == 0:
            break

    is_sort = True


# 한 글자 텍스트 모양을 라이브러리에 있는 파일들과 비교하는 함수
def check_Texts():
    global texts, result

    # 결과 초기화
    result = ""
    # print(len(texts))

    for n in texts:
        min_point = -1  # 점수가 낮을수록 모양이 가장 유사하다.
        file_name = ""  # 가장 낮은점수의 파일명
        x1, x2, y1, y2 = n  # roi관심영역으로 지정하기 위함

        roi_text = imgray[x1 - 2:x2 + 3, y1 - 2:y2 + 3]

        for fname, fimage in image_library:  # 라이브러리 한 모양씩 매칭하기

            roi_file = fimage

            r_roi_text = cv2.resize(roi_text, (roi_file.shape[-1], roi_file.shape[0]))  # foi_file과 크기를 맞춘다.

            bit_xor = cv2.bitwise_xor(roi_file, r_roi_text)  # 비트와이즈 연산으로 겹치지 않는 겹치지 않는 부분은 흰색으로 표시.

            white_ratio = np.sum(bit_xor) / (roi_file.shape[-1] * roi_file.shape[0])  # 흰색 비율


            # print(aspect_ratio)
            # print(white_ratio)

            # cv2.destroyAllWindows()
            # cv2.imshow('roi_text', r_roi_text)
            # cv2.imshow('roi_file', roi_file)
            # cv2.imshow('res', bit_xor)
            # cv2.imshow(window_name, img2)
            # cv2.waitKey()

            # 점수는 흰색 비율
            point = white_ratio

            # 초기값인 경우
            if min_point == -1:
                min_point = point
                file_name = fname

            # 더 작은 포인트가 들어왔을때
            if point < min_point:
                min_point = point
                file_name = fname

                # cv2.destroyAllWindows()
                # cv2.imshow('roi_text', r_roi_text)
                # cv2.imshow('roi_file', roi_file)
                # cv2.imshow('res', bit_xor)
                # cv2.imshow(window_name, img2)
                # cv2.waitKey()

        # print(file_name)
        # 파일 인덱스가 첫번째가 아닌 두번쨰부터
        if texts.index(n) > 0:
            # print(texts[texts.index(n)-1])

            # 바로 전 리스트의 원소를 이용해서 띄어쓰기, 줄바꿈 구현하기
            _, _, _, b_y2 = texts[texts.index(n) - 1]

            # 전 문자의 x최대좌표가 현재 문자의 x최소좌표보다 큰 경우, 줄바꿈 했을때 (줄바꿈을 안했을때는 b_y2 < y1이 성립한다.)
            if b_y2 > y1:
                result = result + "\n"
            # 전 문자의 x최대좌표와 현재 문자의 x최소좌표사이의 거리가 x축 공백의 크기의 3배보다 작을때 띄어쓰기
            if y1 - b_y2 > 3 * space_size_y:
                result = result + " "

        # 결과문자열 수정
        result = result + get_text_name(file_name)

        cv2.rectangle(img2, (y1 - 2, x1 - 2), (y2 + 2, x2 + 2), (0, 0, 255), 1)
        cv2.imshow(window_name, img2)

        # ESC누르면 멈추기
        # 마음같아서는 for i in file_list반복문에서 키를 받으면 멈추게 하고싶은데 그렇게하면 탐색하는데 시간이 더 오래걸림
        key = cv2.waitKey(100) & 0xFF
        # print(key)
        if key == 27:
            messagebox.showinfo()
            print_result()
            return

    # 결과출력
    print_result()


# 파일을 선택하는 함수
def choose_file():
    global img, img2, imgray, imthres, contour, space_size_x, space_size_y, is_sort

    # spinbox의 값을 xy공백으 크기로 지정(사용자 지정 공백의 크기)
    space_size_y = int(spinbox1.get())
    space_size_x = int(spinbox2.get())

    # 선택한 샘플이 listbox의 어느 위치 원소인지 파익(파일명)
    src = sample_list[listbox.curselection()[0]]
    print(src + " 파일 선택완료")

    img = cv2.imread(src)
    img2 = img.copy()
    imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, imthres = cv2.threshold(imgray, 140, 255, cv2.THRESH_BINARY_INV)
    contour, _ = cv2.findContours(imthres, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    is_sort = False

    cv2.imshow(window_name, img2)


# 이미지 창 닫기
def destroy():
    cv2.destroyAllWindows()
    is_sort = False


# 사용자 지정 공백의 크기가 변경될때 / 영역 나누기를 할때
def spinbox_change():
    global img2, imgray, imthres, contour, space_size_x, space_size_y, is_sort

    space_size_y = int(spinbox1.get())
    space_size_x = int(spinbox2.get())

    img2 = img.copy()
    imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, imthres = cv2.threshold(imgray, 140, 255, cv2.THRESH_BINARY_INV)
    contour, _ = cv2.findContours(imthres, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.destroyAllWindows()

    is_sort = False

    # 글자 합치기 함수 호출
    combine_Texts()


# 해독함수
def decord():
    sort_Texts()  # 정렬하고
    draw_blueline()  # 파란선으로 따고
    check_Texts()  # 문자와 라이브러리 비교


##############################################################

# 윈도우 창 생성 및 창 이름 설정
window = tkinter.Tk()
window.title("Controller")

frame = tkinter.Frame(window)  # 최상위 프레임
frame1 = tkinter.Frame(frame)  # 파일명 스크롤바 프레임
frame2 = tkinter.Frame(frame)  # spinbox 프레임
frame3 = tkinter.Frame(frame)  # 버튼 모음 프레임
text_frame = tkinter.Frame(frame)  # 설명 라벨 프레임

# frame1
scrollbar = tkinter.Scrollbar(frame1)
scrollbar.pack(side="right", fill="y")

file_label = tkinter.Label(frame1, text="파일 이름")
file_label.pack(side="top")

listbox = tkinter.Listbox(frame1, height=1, width=35, yscrollcommand=scrollbar.set)
for i in sample_list:
    listbox.insert(sample_list.index(i), i)
listbox.pack(side="bottom")
scrollbar["command"] = listbox.yview

# frame2
button1 = tkinter.Button(frame2, text="파일선택", command=choose_file)
button1.pack(side="left")

x_label = tkinter.Label(frame2, text="가로 공백 크기")
x_label.pack(side="left")
spinbox1 = tkinter.Spinbox(frame2, from_=1, to=100, width=3)
spinbox1.pack(side="left")
y_label = tkinter.Label(frame2, text="세로 공백 크기")
y_label.pack(side="left")
spinbox2 = tkinter.Spinbox(frame2, from_=1, to=100, width=3)
spinbox2.pack(side="left")

# frame 3
button2 = tkinter.Button(frame3, text="영역나누기", command=spinbox_change)
button2.pack(side="left")
button3 = tkinter.Button(frame3, text="해독하기", command=decord)
button3.pack(side="left")
button4 = tkinter.Button(frame3, text="창닫기", command=destroy)
button4.pack(side="left")

# text_frame
text_label1 = tkinter.Label(text_frame, text="영역나누기는 한 글자의 범위을 지정합니다", fg='blue')
text_label1.pack(side="left")
text_label2 = tkinter.Label(text_frame, text=" 해독하기 중단을 원한다면 ESC키를 꾹 누르세요.", fg='red')
text_label2.pack(side="left")

text_frame.pack(side="bottom")
frame1.pack(side="left")
frame2.pack(side="left")
frame3.pack(side="right")

frame.pack(side="top")

window.mainloop()