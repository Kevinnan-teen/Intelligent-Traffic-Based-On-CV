#A组－－基于计算机视觉的交通场景智能应用

####环境依赖
- ununtu16.04LTS
- python3.5

#### 部署步骤
1. 进入目录内
> cd Intelligent-Traffic-Analysis
2. 创建python虚拟环境
> python3 -m venv .
3. 安装python依赖包
> pip install -r requirements.txt
4. 下载YOLOv3权重
	- [官方下载地址](https://pjreddie.com/media/files/yolov3.weights) 
	- [百度网盘下载链接](https://pan.baidu.com/s/1CVgvP4hQQvDNbKmXhmkxqw) 　
下载完成后将weights文件放在 **yolov3/weights** 目录下

#### 目录结构描述
. 
├── Readme.md 
├── requirements.txt
├── log
│   └── log_info.txt
├── PlateRecognition
│   ├── Font
│   │   └── platech.ttf
│   └── model
│       ├── cascade_lbp.xml
│       ├── cascade.xml
│       ├── char_chi_sim.h5
│       ├── char_judgement1.h5
│       ├── char_judgement.h5
│       ├── char_rec.h5
│       ├── model12.h5
│       ├── ocr_plate_all_gru.h5
│       ├── ocr_plate_all_w_rnn_2.h5
│       └── plate_type.h5
├── scripts
│   ├── bbox.py
│   ├── core.py
│   ├── darknet.py
│   ├── detect.py
│   ├── HyperLPRLite.py
│   ├── main.py
│   ├── plateRecognition.py
│   ├── preprocess.py
│   ├── util.py
│   └── video_demo.py
├── ui
│   ├── core.py
│   └── Core.ui
├── videos
│   ├── video2.avi
│   ├── video3.avi
│   ├── video4.mp4
│   └── video.mp4
└── yolov3
    ├── cfg
    │   ├── tiny-yolo-voc.cfg
    │   ├── yolo.cfg
    │   ├── yolov3.cfg
    │   └── yolo-voc.cfg
    ├── data
    │   ├── coco.names
    │   └── voc.names
    ├── pallete
    └── weights
        └── yolov3.weights
#### 参考资料
[1][A PyTorch implementation of the YOLO v3 object detection algorithm](https://github.com/ayooshkathuria/pytorch-yolo-v3.git) 
[2][基于深度学习高性能中文车牌识别HyperLPR](https://github.com/zeusees/HyperLPR.git) 