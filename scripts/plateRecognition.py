#coding=utf-8
import sys
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
import HyperLPRLite as pr
import cv2
import numpy as np
import time


fontC = ImageFont.truetype("../PlateRecognition/Font/platech.ttf", 14, 0)
#reload(sys)
#sys.setdefaultencoding("utf-8")


# 从本地读取图片并做识别，返回所有识别到车牌的【识别结果，置信度，位置】
# smallest_confidence：最小置信度
def recognize_plate(image, smallest_confidence = 0.7):
    start1 = time.time()
    model = pr.LPR("../PlateRecognition/model/cascade.xml","../PlateRecognition/model/model12.h5", \
                 "../PlateRecognition/model/ocr_plate_all_gru.h5")
    #print("模型加载所需时间:" + str(time.time() - start1))
    start2 = time.time()
    return_all_plate = []
    for pstr,confidence,rect in model.SimpleRecognizePlateByE2E(image):
        if confidence>smallest_confidence:
            return_all_plate.append([pstr,confidence,rect])
    #print("模型预测所需时间:" + str(time.time() - start2))
    return return_all_plate



# 测试识别该车牌所耗费时间
def SpeedTest(image_path):
    grr = cv2.imread(image_path)
    model = pr.LPR("../PlateRecognition/model/cascade.xml","../PlateRecognition/model/model12.h5", \
                    "../PlateRecognition/model/ocr_plate_all_gru.h5")
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
    model = pr.LPR("../PlateRecognition/model/cascade.xml","../PlateRecognition/model/model12.h5", \
        "../PlateRecognition/model/ocr_plate_all_gru.h5")
    for pstr,confidence,rect in model.SimpleRecognizePlateByE2E(grr):
        if confidence>0.7:
            #grr = drawRectBox(grr, rect, pstr+" "+str(round(confidence,3)))
            print ("车牌号:")
            print (pstr)
            print ("置信度")
            print (confidence)
            print(grr.shape)
            #print(rect[1], rect[3])
            #print(rect[0], rect[2])
            cv2.imshow("plate", grr[int(rect[1]) : int(rect[3] + rect[1]), \
                            int(rect[0]) : int(rect[2]+rect[0])])
    #cv2.imshow("image",grr)
    #cv2.waitKey(0)
    return grr



# SpeedTest("Images/test3.jpg")
#test_image = cv2.imread("Images/test4.jpg")
#print(recognize_plate(test_image))
#visual_draw_position(test_image)

    
