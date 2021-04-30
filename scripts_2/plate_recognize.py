import sys
sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')
#导入包
#导入OpenCV库
import cv2
#读入图片
from plateRecognition import recognize_plate, drawRectBox

# cap = cv2.VideoCapture("rtmp://kevinnan.org.cn/live/livestream")
# print("load complete")
# while(cap.isOpened()):
# 	ret, frame = cap.read()
# 	if ret:
# 		plate_info_list = recognize_plate(frame)
# 		# image,res  = pipline.SimpleRecognizePlate(frame)
# 		print(plate_info_list)
# 	print('next')
# image = cv2.imread("demo.jpg")
#识别结果

image = cv2.imread("HyperLPR_python-master/dataset/0.jpg")
image2 = cv2.imread("HyperLPR_python-master/dataset/1.jpg")
plate_info_list = recognize_plate(image)
print(plate_info_list)
plate_info_list = recognize_plate(image2)
print(plate_info_list)

