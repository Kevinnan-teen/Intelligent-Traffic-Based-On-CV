# 基于计算机视觉的交通路口智能监控系统

> 交通路口智能监控系统2.0版本更新．2.0版本在之前版本的基础上做了一定改进，尤其是对项目的架构做了大幅度的调整．之后此项目默认分支为version2.0，如果要查看之前的版本可以在`Switch branches`菜单中选择master分支．

> To Do : clone 分支代码; 或 clone整个项目,然后在本地切换分支

## 1、项目介绍

**项目背景**:智能交通监控系统采用识别技术进行分析，有异常状况发生(比如，当有行人闯红灯时、路口车辆和行人流量过大，导致堵塞交通时)就会自动通知交通管理人员．

基于以上背景，我简要介绍一下本项目的设计架构．

<div align=center><img width="350" height="300" src="./resources/design-framework.png"/></div>

项目主要由三个模块组成，分别是：SRS流媒体服务器，云端GPU服务器，本地客户端．

首先，网络摄像机将交通路口的监控视频实时上传到**SRS流媒体服务器**。

然后，当SRS流媒体服务器有视频流输入时，**云端GPU服务器**拉取原始视频流，然后通过YOLO等目标检测算法对视频进行分析和处理，然后将处理后的视频推流到SRS服务器。

对于**本地客户端**，一方面可以直接从流媒体服务器拉流，查看远端网络摄像机的实时监控画面。另一方面，本地客户端也可以选择和远端的服务器通过`Socket`进行通信，获取服务器对监控视频的分析结果，比如路口的车流量、人流量等。同时，当选择与GPU服务器连接时，本地客户端也将更换`rtmp`流地址，拉取处理后的视频流．

> 这里没有采用将分析结果发送到客户端，然后在客户端对目标进行标注的原因主要是考虑到分析结果和视频流刷新的同步问题。直接把处理后的视频推流是一个简单粗暴但行之有效的方法。

## 2、环境依赖

- SRS流媒体服务器

使用开源的[SRS实时视频服务器](https://github.com/ossrs/srs)，在之前购买的阿里云服务器上搭建了一个流媒体服务器，详细的过程可以参考我的博客－－[基于SRS搭建RTMP直播推流服务器](http://kevinnan.org.cn/index.php/archives/537/)．

当然，如果你没有云服务器，也可以在本地的Linux机器上搭建SRS流媒体服务器，搭建方法可以查看该项目文档，也可参考之前提到的我的博客．

- GPU服务器

我直接在本地运行服务端脚本来替代GPU服务器．如果是要部署的话，只需要修改服务器脚本`server_selector.py`中的`IP`和`Port`即可．

- 本地客户端

## 3、部署步骤

### 3.1 向SRS流媒体服务器推流

为了方便演示，我使用`ffmpeg`把本地的交通路口监控视频推流到我在阿里云服务器搭建的的流媒体服务器．**这个步骤用来代替之前提到的网络摄像机的推流过程**．

```shell
ffmpeg -re -stream_loop -1 -i traffic.flv -c copy -f flv rtmp://101.132.236.124/live/livestream
```

上面的命令是对视频`traffic.flv`进行循环推流，推流到你的SRS流媒体服务器上．该rtmp流地址可根据你的情况修改．

### 3.2 安装环境依赖

>  Note: 我的测试环境: ubuntu16.04STL + Python3.5

1. 进入目录内
```shell
cd Intelligent-Traffic-Based-On-CV
```

2. 创建python虚拟环境
```shell
python3 -m venv .
```

3. 激活虚拟环境
```shell
source bin/activate
```

3. 安装python依赖包
```shell
pip install -r requirements.txt
```

> Note：如果遇到某个包不能下载，可以先搜索该库对应版本的whl文件，下载到本地，然后安装whl．

4. 下载YOLOv3权重
	- [官方下载地址](https://pjreddie.com/media/files/yolov3.weights) 
	- [百度网盘下载链接](https://pan.baidu.com/s/1CVgvP4hQQvDNbKmXhmkxqw) 　
下载完成后将weights文件放在 **yolov3/weights** 目录下

### 3.3 运行服务器程序（本地）

运行服务器脚本, 2.0版本的代码在`scripts_2`目录下．

```shell
cd scripts_2
```

```shell
python server_selector.py
```

### 3.4 运行客户端程序

```shell
python client_selector.py
```

## 4、项目演示

演示视频地址 : [https://lucasnan.gitee.io/info/video.html](https://lucasnan.gitee.io/info/video.html)

![](resources/demo.png)

## 5、代码结构说明

1. **scripts_2** : python脚本
   - server_selector.py : 服务端脚本
   - client_selector.py main_window.py sub_window.py : 客户端PyQt5界面
   - bbox.py  darknet.py video_demo.py util.py : YOLO相关代码
   - detect.py  : 颜色检测
   - plateRecognition.py  preprocess.py HyperLPRLite.py : 车牌检测相关代码
2. demo : 测试脚本

   - selectors_echo_client.py : selectors客户端
   - selectors_echo_server.py : selectors服务端
3. **ui** : 使用`Qt Designer`设计的界面ui文件
   - core_v1.ui : 1.0版本界面
   - core_u2.ui : 2.0版本界面
   - core.py : 使用命令`pyuic5 -o core.py Core.ui`将Core.ui文件转为python脚本
4. **yolov3** : YOLO模型配置文件
   - cfg : YOLO网络模型
   - data : YOLO识别类型
   - weights : YOLO模型权重
5. **PlateRecognition** : 中文车牌识别HyperLPR项目配置文件
6. **videos** : 提供的道路测试视频
7. **log** : 程序运行过程中保存的日志 

## 6、各模块功能详细说明

### 6.1 流媒体服务器模块

搭建基于SRS的流媒体服务器．用于接收网络摄像头交通路口实时监控画面，同时将接收到的rtmp流推送到需要的地方．比如推流到GPU服务器用于视频内容分析，推流到客户端供交通管理员监控路口交通状况．

### 6.2 GPU服务端模块

#### 6.2.1 目标识别模块

（1）功能介绍：本模块通过使用YOLOv3多尺度目标识别技术对视频流的图像帧进行识别，并将事先在训练类别中的目标在视频画面中实时标注出来，并将识别的信息提供给其他模块使用，比如红绿灯检测模块，车流量检测模块等。

（2）详细实现：本模块我们使用YOLO(You Only Look Once)模型对图像中的物体进行识别。首先在模型构建方面，我们读取darknet框架使用的yolov3.cfg 卷积神经网络模型文件，对网络的结构进行分析然后转换为相应的pytorch模型，使用已经加载的yolov3.weight权重模型，至此我们的CNN识别模块已经搭建完成。然后将opencv读取的图像帧丢入已经定义的卷积神经网络模型对结果进行预测，得到输出信息（包括置信度、位置坐标），使用opencv作图模块将这些输出信息实时标注在对应的图像帧上。最后将处理过的图像帧显示在界面上即可。

#### 6.2.2 红绿灯检测模块

（1）功能介绍：本模块使用目标识别模块的输出信息得到交通灯的位置坐标，使用颜色识别算法对交通灯状态进行分析。

（2）详细实现：首先对pytorch预测输出的信息进行分析，得到交通灯对应的位置信息。接着，调用opencv模块将交通灯对应的ROI区域截取出来，由于HSV空间能够非常直观的表达色彩的明暗，色调，以及鲜艳程度，方便进行颜色之间的对比，因此将截取出区域的RGB图像先转换为HSV图像。最后将每种颜色对应的HSV阈值与截取区域中的HSV颜色进行比对，重合率最高的即为识别到的颜色种类。

#### 6.2.3 车流量检测模块

（1）功能介绍：本模块对图像帧中出现的车辆数目进行统计，实时分析交通路口的车流量，提供参考数据给使用人员。

（2）详细实现：首先对pytorch预测输出的信息进行分析，得到图像帧中所有识别到的车辆信息，对车辆信息进行统计，然后实时在界面上显示。

#### 6.2.4 人流量检测模块

（1）功能介绍：本模块对图像帧中出现的行人数目进行统计，实时分析交通路口的人流量，提供参考数据给使用人员。

（2）详细实现：首先对pytorch预测输出的信息进行分析，得到图像帧中所有识别到的行人信息，对行人信息进行统计，然后实时在界面上显示。

#### 6.2.5 车牌识别模块

（1）功能介绍：本模块对图像帧中出现的车辆车牌号进行识别，并将识别到车牌的图像区域和OCR识别结果实时显示在界面上。

（2）详细实现：使用HyperLPR 车牌识别开源项目，首先利用利用cascade进行车牌定位，其次利用左右边界回归模型，预测出车牌的左右边框，进一步裁剪，进行精定位，最后利用CRNN进行车牌字符识别。

#### 6.3 客户端模块

#### 6.3.1 界面显示模块

（1）功能介绍：模块实现了本地客户端的人机交互界面部分．用于交通管理员对交通路口的视频进行监控，以及查看服务器端对视频进行分析的结果．

（2）详细实现：首先，使用qt designer设计界面．然后将ui界面转为python pyqt5的源代码，以便实现更加复杂的逻辑（比如信号与槽，按钮事件的处理）．

#### 6.3.2 数据可视化模块

（1）功能介绍：本模块将从服务器获取的数据（如人流量、车流量）等信息进行可视化，方便系统管理人员查看交通路口实时流量变化．

（2）详细实现：使用matplotlib提供的FigureCanvasQTAgg模块，将pyqt5设计的界面和matplotlib的画图耦合．

#### 6.3.3 Socket通信模块

（1）功能介绍：本模块用于本地客户端和云端GPU服务器之间的通信，本地客户端接收服务端发送的实时分析数据．

（2）详细实现：使用基于tcp的Socket套接字．将分析的数据如人流量、车流量、交通灯状态等信息封装为json格式的数据发送到客户端．客户端收到数据后验证是否正确，然后将结果反馈给服务端．

#### 6.3.4 系统日志模块

（1）功能介绍：本模块对视频分析中得到的信息进行汇总，并实时在在画面上进行刷新，使用者可以方便地查看当前以及之前的分析结果；

​	（2）详细实现：首先定义一个日志消息队列，在视频分析开始运行之后将得到的信息使用put函数加载到队列当中，然后在日志显示模块使用get函数得到最新的消息并实时显示在画面上。

## 7、参考资料

[1][A PyTorch implementation of the YOLO v3 object detection algorithm](https://github.com/ayooshkathuria/pytorch-yolo-v3.git) 

[2][基于深度学习高性能中文车牌识别HyperLPR](https://github.com/zeusees/HyperLPR.git) 