import subprocess as sp
import threading
import sys
import time



sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')
import cv2



def tt1():
    cap = cv2.VideoCapture("rtmp://kevinnan.org.cn/live/livestream")
    rtmpUrl = "rtmp://kevinnan.org.cn/live/stream"

    # Get video information
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # ffmpeg command
    command = ['ffmpeg',
            '-y',
            '-f', 'rawvideo',
            '-vcodec','rawvideo',
            '-pix_fmt', 'bgr24',
            '-s', "{}x{}".format(width, height),
            '-r', str(fps),
            '-i', '-',        
            '-pix_fmt', 'yuv420p',
            '-f', 'flv', 
            rtmpUrl]

    # 管道配置
    p = sp.Popen(command, stdin=sp.PIPE)
            
    # read webcamera
    while(cap.isOpened()):
        ret, frame = cap.read()
        if not ret:
            print("Opening camera is failed")
            break
                
        # process frame
        # your code
        # process frame
       
        # write to pipe
        p.stdin.write(frame.tostring())

def tt2():
    time.sleep(3)
    print(122)

if __name__ == '__main__':
    thread_1 = threading.Thread(target=tt1, daemon=True)
    thread_1.start()
    while True:
        time.sleep(3)
        print(1)
