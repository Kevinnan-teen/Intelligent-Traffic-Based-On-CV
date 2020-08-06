import cv2
import numpy as np


def traffic_color_detect(img):
	color_classes = 2
	# set blue thresh
	lower_blue=np.array([100,43,46])
	upper_blue=np.array([124,255,255])

	# set red thresh
	lower_red = np.array([0, 43, 46])
	upper_red = np.array([10, 255, 255])

	# set green thresh
	lower_green = np.array([35, 43, 46])
	upper_green = np.array([99, 255, 255])

	#threshold_range = [[lower_red, upper_red], [lower_green, upper_green], [lower_blue, upper_blue]]
	#color = ["red", "green", "blue"]
	threshold_range = [[lower_red, upper_red], [lower_green, upper_green]]
	color = ["red", "green"]

	# change to hsv model
	hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	
	# get mask
	mask = []
	for i in range(color_classes):
			Mask = cv2.inRange(hsv, threshold_range[i][0], threshold_range[i][1])
			mask.append(Mask)

	uniques = []
	for MASK in mask:
		res = cv2.bitwise_and(img, img, mask=MASK)
		Uniques = np.unique(res)
		uniques.append(Uniques.shape[0])
	#print(uniques[0],uniques[1])
	#print(uniques.index(max(uniques))) 
	return color[uniques.index(max(uniques))]
	
	'''if detect_color == "green":
		mask = cv2.inRange(hsv, lower_green, upper_green)
	elif detect_color == "red":
		mask = cv2.inRange(hsv, lower_red, upper_red)
	else:
		pass
	
	# detect color
	res = cv2.bitwise_and(img, img, mask=mask)
	uniques = np.unique(res)
	#print(uniques)
	if uniques.shape[0] > 2:
		print(detect_color)
	else:
		print("not %s" % detect_color)'''

def detect_people_if_violation(position):
	crosswalk_x1 = 100		# 给出人行道的ROI
	crosswalk_y1 = 450
	crosswalk_x2 = 1870
	crosswalk_y2 = 700
	#print(position[0], position[1])
	if crosswalk_x1 < position[0] and crosswalk_x2 > position[0] and \
						 crosswalk_y1 < position[1] and crosswalk_y2 > position[1]:
		return True 
	else:
		False

def detect_motor_if_in_ROI(position):
	crosswalk_x1 = 100		# 给出人行道的ROI
	crosswalk_y1 = 450
	crosswalk_x2 = 1870
	crosswalk_y2 = 700
	#print(position[0], position[1])
	if crosswalk_x1 < position[0] and crosswalk_x2 > position[0] and \
						 crosswalk_y1 < position[1] and crosswalk_y2 > position[1]:
		return True 
	else:
		False


def get_motor_poisition(outputs):
	motors_center = []
	for output in outputs:
		if int(output[-1]) == 3:
			if detect_motor_if_in_ROI([ int(output[3]), int(output[4]) ]):
				#center_x = int(output[3] - output[1])
				#print(int(output[1]))
				center_x = int( output[1] + (output[3]-output[1])/2 )

				#center_y = int(output[4] - output[2])
				center_y = int( output[2] + (output[4]-output[2])/2 )

				motors_center.append(tuple((center_x, center_y)))
	return motors_center


def detect_people_with_motor(people_center_x, motors_center):
	for motor in motors_center:
		if abs(motor[0] - people_center_x) < 11:
			return True
		#print(abs(motor[0] - people_center_x))
	return False 





# 检测汽车颜色
def detect_car_color(output, plate_frame, plate_center):
	for x in output:
		c1 = tuple(x[1:3].int())
		c2 = tuple(x[3:5].int())
		cls = int(x[-1])
		if cls == 2:
			#print(int(c1[1]), plate_center[1], int(c2[1]))
			if int(c1[0]) < plate_center[0] and int(c2[0]) > plate_center[0]:
				car_roi_img = plate_frame[int(x[2]) : int(x[4]), int(x[1]) : int(x[3])]
				return detect_color(car_roi_img)
	return "white"


def detect_color(img):
	color_classes = 3
	# set block thresh
	lower_block=np.array([0,0,0])
	upper_block=np.array([180,255,80])

	# set gray thresh
	lower_gray = np.array([0, 0, 81])
	upper_gray = np.array([180, 43, 180])

	# set white thresh
	lower_white = np.array([0,0,181])
	upper_white = np.array([180,30,255])

	#threshold_range = [[lower_red, upper_red], [lower_green, upper_green], [lower_blue, upper_blue]]
	#color = ["red", "green", "blue"]
	threshold_range = [[lower_block, upper_block], [lower_gray, upper_gray], [lower_white, upper_white]]
	color = ["黑色", "灰色", "白色"]

	# change to hsv model
	hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	
	# get mask
	mask = []
	for i in range(color_classes):
			Mask = cv2.inRange(hsv, threshold_range[i][0], threshold_range[i][1])
			mask.append(Mask)

	uniques = []
	for MASK in mask:
		res = cv2.bitwise_and(img, img, mask=MASK)
		Uniques = np.unique(res)
		uniques.append(Uniques.shape[0])
	#print(uniques[0],uniques[1])
	#print(uniques.index(max(uniques))) 
	return color[uniques.index(max(uniques))]