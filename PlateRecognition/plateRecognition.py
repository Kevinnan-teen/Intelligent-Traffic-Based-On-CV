#coding=utf-8
import sys
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
import HyperLPRLite as pr
import cv2
import numpy as np
import time

fontC = ImageFont.truetype("Font/platech.ttf", 14, 0)
#reload(sys)
#sys.setdefaultencoding("utf-8")


# 从本地读取图片并做识别，返回所有识别到车牌的【识别结果，置信度，位置】
# smallest_confidence：最小置信度
def recognize_plate(image, smallest_confidence = 0.7):
    # # grr = cv2.imread(image_path)

    model = pr.LPR("model/cascade.xml", "model/model12.h5", "model/ocr_plate_all_gru.h5")
    model.SimpleRecognizePlateByE2E(image)
    return_all_plate = []
    for pstr,confidence,rect in model.SimpleRecognizePlateByE2E(image):
        if confidence>smallest_confidence:
            return_all_plate.append([pstr,confidence,rect])
    return return_all_plate



# 测试识别该车牌所耗费时间
def SpeedTest(image_path):
    grr = cv2.imread(image_path)
    model = pr.LPR("model/cascade.xml", "model/model12.h5", "model/ocr_plate_all_gru.h5")
    model.SimpleRecognizePlateByE2E(grr)
    t0 = time.time()
    for x in range(20):
        model.SimpleRecognizePlateByE2E(grr)
    t = (time.time() - t0)/20.0
    print ("图片size:" + str(grr.shape[1])+"x"+str(grr.shape[0]) +  " 需要 " + str(round(t*1000,2))+"ms")



# 在image上画上车牌所在框和车牌号
def drawRectBox(image,rect,addText):
    cv2.rectangle(image, (int(rect[0]), int(rect[1])), (int(rect[0] + rect[2]), int(rect[1] + rect[3])), (0,0, 255), 2,cv2.LINE_AA)
    cv2.rectangle(image, (int(rect[0]-1), int(rect[1])-16), (int(rect[0] + 115), int(rect[1])), (0, 0, 255), -1,
                  cv2.LINE_AA)
    img = Image.fromarray(image)
    draw = ImageDraw.Draw(img)
    draw.text((int(rect[0]+1), int(rect[1]-16)), addText, (255, 255, 255), font=fontC)
    imagex = np.array(img)
    return imagex


# 测试结果 并可视化
def visual_draw_position(grr):
    model = pr.LPR("model/cascade.xml","model/model12.h5","model/ocr_plate_all_gru.h5")
    for pstr,confidence,rect in model.SimpleRecognizePlateByE2E(grr):
        if confidence>0.7:
            grr = drawRectBox(grr, rect, pstr+" "+str(round(confidence,3)))
            print ("车牌号:")
            print (pstr)
            print ("置信度")
            print (confidence)
    #cv2.imshow("image",grr)
    #cv2.waitKey(0)
    return grr



# SpeedTest("Images/test3.jpg")
#test_image = cv2.imread("Images/test4.jpg")
#print(recognize_plate(test_image))
#visual_draw_position(test_image)

videofile = "./video.mp4"
cap = cv2.VideoCapture(videofile)
assert cap.isOpened(), 'Cannot capture source'
frames = 0
start = time.time()    
num_frame = 0
while cap.isOpened(): 
    ret, frame = cap.read()
    if(num_frame == 5):
        num_frame = 0
        if ret:
            grr = visual_draw_position(frame)
            cv2.imshow("image", grr)
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q'):
                break
    else:
        num_frame = num_frame + 1

    
