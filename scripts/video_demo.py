from __future__ import division
import time
import torch 
import torch.nn as nn
from torch.autograd import Variable
import numpy as np
import cv2 
from util import *
from darknet import Darknet
from preprocess import prep_image, inp_to_image, letterbox_image
import pandas as pd
import random 
import pickle as pkl
import argparse
from detect import traffic_color_detect, detect_people_if_violation, \
                    detect_people_with_motor, get_motor_poisition


def get_test_input(input_dim, CUDA):
    img = cv2.imread("../dog-cycle-car.png")
    img = cv2.resize(img, (input_dim, input_dim)) 
    img_ =  img[:,:,::-1].transpose((2,0,1))
    img_ = img_[np.newaxis,:,:,:]/255.0
    img_ = torch.from_numpy(img_).float()
    img_ = Variable(img_)
    
    if CUDA:
        img_ = img_.cuda()
    
    return img_

def prep_image(img, inp_dim):
    """
    Prepare image for inputting to the neural network. 
    
    Returns a Variable 
    """

    orig_im = img
    dim = orig_im.shape[1], orig_im.shape[0]
    img = (letterbox_image(orig_im, (inp_dim, inp_dim)))    #重置图片size
    img_ = img[:,:,::-1].transpose((2,0,1)).copy()
    img_ = torch.from_numpy(img_).float().div(255.0).unsqueeze(0)
    return img_, orig_im, dim


def traffic_light_detect(x, img):
    for i in range(x.shape[0]):
        cls = int(x[i,-1])
        if cls == 9:
            img_copy = img.copy()
            traffic_light_roi = img_copy[int(x[i,2]):int(x[i, 4]), int(x[i, 1]):int(x[i, 3])]

            if traffic_color_detect(traffic_light_roi) == "green":
                return "green"
            else:
                return "red"
    
    return "unknown"

#　类别数目检测
def classNum_detect(x):
    people_num = 0
    cars_num = 0
    motors_num = 0
    for i in range(x.shape[0]):
        if int(x[i, -1]) == 0:
            people_num += 1
        elif int(x[i, -1]) == 2:
            cars_num += 1 
        elif int(x[i, -1]) == 9:
            motors_num += 1 
        else:
            pass
    return people_num, cars_num, motors_num



def write(output, img, motors_center):
    classes = load_classes('../yolov3/data/coco.names')
    colors = pkl.load(open("../yolov3/pallete", "rb"))
    pedestrians_num = 0             # 闯红灯人数
    global is_green_light
    for x in output:
        c1 = tuple(x[1:3].int())
        c2 = tuple(x[3:5].int())
        colors = [[225,0,0], [0,225,0], [0,0,225], [225,225,225], [205,90,106]]       # blue green red black
        cls = int(x[-1])
        label = "{},{:.3}".format(classes[cls], float(x[-3]))
        color = random.choice(colors)

        # 检测绿灯
        if cls == 9:
            img_copy = img.copy()
            traffic_light_roi = img_copy[int(x[2]):int(x[4]), int(x[1]):int(x[3])]
            #print(int(x[1]),int(x[2]), int(x[3]),int(x[4]))
            #print(traffic_light_roi.shape)
            #print(traffic_light_roi.size)
            #print(np.array(traffic_light_roi))
            '''try:
                cv2.namedWindow("traffic",0);
                cv2.resizeWindow("traffic", 400, 400)
                cv2.imshow("traffic", traffic_light_roi)
            except:
                pass'''
            if traffic_color_detect(traffic_light_roi) == "green":
                is_green_light = True
                #print("green")
            else:
                is_green_light = False
                #print("red")
        if cls == 0:
            try:
                if is_green_light:
                    if(detect_people_if_violation([int(x[3]), int(x[4])])):
                        people_center_x = int(c1[0]+(c2[0]-c1[0])/2)
                        if detect_people_with_motor(people_center_x, motors_center):
                            cv2.rectangle(img, c1, c2, colors[1], 1)
                        else:
                            cv2.rectangle(img, c1, c2, colors[2], 2)
                            pedestrians_num += 1
                    else:
                        cv2.rectangle(img, c1, c2, colors[1], 1)
                else:
                    cv2.rectangle(img, c1, c2, colors[1], 1)
            except:
                pass
        elif cls == 2:
            cv2.rectangle(img, c1, c2, colors[0], 1)
        elif cls == 9:
            cv2.rectangle(img, c1, c2, colors[3], 1)
        else:
            cv2.rectangle(img, c1, c2, colors[4], 1)

        t_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_PLAIN, 1 , 1)[0]
        #c2 = c1[0] + t_size[0] + 3, c1[1] + t_size[1] + 4
        #cv2.rectangle(img, c1, c2,color, -1)
        cv2.putText(img, label, (c1[0], c1[1] + t_size[1] + 4), cv2.FONT_HERSHEY_PLAIN, 1, [225,255,255], 1)
        cv2.rectangle(img, (100,450), (1870, 700), [0,0,0],2)
    return pedestrians_num


def arg_parse():
    """
    Parse arguements to the detect module
    
    """
    parser = argparse.ArgumentParser(description='YOLO v3 Video Detection Module')
   
    parser.add_argument("--video", dest = 'video', help = 
                        "Video to run detection upon",
                        default = "video.avi", type = str)
    parser.add_argument("--dataset", dest = "dataset", help = "Dataset on which the network has been trained", default = "pascal")
    parser.add_argument("--confidence", dest = "confidence", help = "Object Confidence to filter predictions", default = 0.5)
    parser.add_argument("--nms_thresh", dest = "nms_thresh", help = "NMS Threshhold", default = 0.4)
    parser.add_argument("--cfg", dest = 'cfgfile', help = 
                        "Config file",
                        default = "../yolov3/cfg/yolov3.cfg", type = str)
    parser.add_argument("--weights", dest = 'weightsfile', help = 
                        "weightsfile",
                        default = "../weights/yolov3.weights", type = str)
    parser.add_argument("--reso", dest = 'reso', help = 
                        "Input resolution of the network. Increase to increase accuracy. Decrease to increase speed",
                        default = "416", type = str)
    return parser.parse_args()

def onmouse(event, x, y, flags, param):
     if event==cv2.EVENT_LBUTTONDOWN:
        print(x,y)


def load_model():
    print("Loading network.....")

    model = Darknet("../yolov3/cfg/yolov3.cfg")
    model.load_weights("../yolov3/weights/yolov3.weights")

    print("Network successfully loaded")
    model.net_info["height"] = 416

    if CUDA:
        model.cuda()                        # 将模型迁移到GPU
        
    model(get_test_input(inp_dim, CUDA), CUDA)

    model.eval()

    return model

def target_detect(model, frame):
    confidence = 0.5
    nms_thesh = 0.4
    CUDA = torch.cuda.is_available() 
    num_classes = 80                        # 使用coco数据集,80个类

    inp_dim = 416

    
    bbox_attrs = 5 + num_classes

    img, orig_im, dim = prep_image(frame, inp_dim)
    
    im_dim = torch.FloatTensor(dim).repeat(1,2)                        
    
    
    if CUDA:
        im_dim = im_dim.cuda()
        img = img.cuda()
    
    with torch.no_grad():   
        output = model(Variable(img), CUDA)
    #print(output[:,:,4].shape)
    output = write_results(output, confidence, num_classes, nms = True, nms_conf = nms_thesh)

    #print(output)
    '''if type(output) == int:
        frames += 1
        print("FPS of the video is {:5.2f}".format( frames / (time.time() - start)))
        cv2.imshow("frame", orig_im)
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break
        continue'''

    im_dim = im_dim.repeat(output.size(0), 1)
    scaling_factor = torch.min(inp_dim/im_dim,1)[0].view(-1,1)
    
    output[:,[1,3]] -= (inp_dim - scaling_factor*im_dim[:,0].view(-1,1))/2
    output[:,[2,4]] -= (inp_dim - scaling_factor*im_dim[:,1].view(-1,1))/2
    
    output[:,1:5] /= scaling_factor

    for i in range(output.shape[0]):
        output[i, [1,3]] = torch.clamp(output[i, [1,3]], 0.0, im_dim[i,0])
        output[i, [2,4]] = torch.clamp(output[i, [2,4]], 0.0, im_dim[i,1])

    motors_center = get_motor_poisition(output) # 获得在人行道上行驶的摩托车的中心坐标,用于检测行人是否违规
    
    real_time_frame = orig_im.copy()
    #list(map(lambda x: write(x, real_time_frame, motors_center), output))      # 标注识别到的物体
    pedestrians_num = write(output, real_time_frame, motors_center)

    return output, orig_im, real_time_frame, pedestrians_num




'''if __name__ == '__main__':
    args = arg_parse()
    confidence = float(args.confidence)     # 置信度
    nms_thesh = float(args.nms_thresh)
    start = 0

    CUDA = torch.cuda.is_available()        # 判断是否有CUDA可用

    num_classes = 80                        # 使用coco数据集,80个类

    # CUDA = torch.cuda.is_available()
    
    bbox_attrs = 5 + num_classes
    
    print("Loading network.....")
    model = Darknet(args.cfgfile)           # 加载yolov3.cfg模型
    model.load_weights(args.weightsfile)    # 加载预训练模型权重
    print("Network successfully loaded")

    model.net_info["height"] = args.reso    # 输入网络图片的height, default=416
    inp_dim = int(model.net_info["height"])
    assert inp_dim % 32 == 0 
    assert inp_dim > 32

    if CUDA:
        model.cuda()                        # 将模型迁移到GPU
        
    model(get_test_input(inp_dim, CUDA), CUDA)

    model.eval()
    
    videofile = args.video
    
    cap = cv2.VideoCapture(videofile)
    
    assert cap.isOpened(), 'Cannot capture source'
    
    frames = 0
    start = time.time()    
    while cap.isOpened():
        
        ret, frame = cap.read()
        if ret:
            

            img, orig_im, dim = prep_image(frame, inp_dim)
            
            im_dim = torch.FloatTensor(dim).repeat(1,2)                        
            
            
            if CUDA:
                im_dim = im_dim.cuda()
                img = img.cuda()
            
            with torch.no_grad():   
                output = model(Variable(img), CUDA)
            #print(output[:,:,4].shape)
            output = write_results(output, confidence, num_classes, nms = True, nms_conf = nms_thesh)

            #print(output)
            # if type(output) == int:
            #     frames += 1
            #     print("FPS of the video is {:5.2f}".format( frames / (time.time() - start)))
            #     cv2.imshow("frame", orig_im)
            #     key = cv2.waitKey(1)
            #     if key & 0xFF == ord('q'):
            #         break
            #     continue'''

        #     im_dim = im_dim.repeat(output.size(0), 1)
        #     scaling_factor = torch.min(inp_dim/im_dim,1)[0].view(-1,1)
            
        #     output[:,[1,3]] -= (inp_dim - scaling_factor*im_dim[:,0].view(-1,1))/2
        #     output[:,[2,4]] -= (inp_dim - scaling_factor*im_dim[:,1].view(-1,1))/2
            
        #     output[:,1:5] /= scaling_factor
    
        #     for i in range(output.shape[0]):
        #         output[i, [1,3]] = torch.clamp(output[i, [1,3]], 0.0, im_dim[i,0])
        #         output[i, [2,4]] = torch.clamp(output[i, [2,4]], 0.0, im_dim[i,1])
            
        #     classes = load_classes('../yolov3/data/coco.names')
        #     colors = pkl.load(open("../yolov3/pallete", "rb"))

        #     motors_center = get_motor_poisition(output) # 获得在人行道上行驶的摩托车的中心坐标,用于检测行人是否违规
            
        #     list(map(lambda x: write(x, orig_im, motors_center), output))      # 标注识别到的物体
            
        #     out_win = "output_style_full_screen"
        #     cv2.namedWindow(out_win, cv2.WINDOW_NORMAL)
        #     cv2.setWindowProperty(out_win, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        #     cv2.setMouseCallback(out_win, onmouse, 0)
        #     cv2.imshow(out_win, orig_im)
        #     #cv2.imshow("frame", orig_im)
        #     key = cv2.waitKey(1)
        #     if key & 0xFF == ord('q'):
        #         break
        #     frames += 1
        #     print("FPS of the video is {:5.2f}".format( frames / (time.time() - start)))
        #     #print(output)

            
        # else:
        #     break
    

    
    

