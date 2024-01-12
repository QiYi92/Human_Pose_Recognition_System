# Human_Pose_Recognition_System
 基于OpenPose卷积神经网络的人体姿态识别及预警系统
## 概述
 本文引入了轻量级的OpenPose优化方法，并将OpenPose的检测模块朝着轻量化方向进行改进。通过改进后的卷积结构，实现了人体姿态的实时识别和预警，同时保证了识别精度。具体来说，将OpenPose的检测模块进行了优化，以保证在保持高识别精度的同时提高识别速度。该项目的实验结果表明，该方法在面对大量人群和物体遮挡等复杂情况时，能够有效地提高识别的准确性和效率。

## 环境需求
 python v3.8
 
 CUDA v11.3
 
 cudnn v8.2.1
 
 **注意**
本项目使用的运算显卡为RTX3070，复现项目者请根据你电脑显卡型号下载对应的CUDA和cudnn版本，不然运行时会有项目崩溃的可能。

## 第三方库&依赖项
请安装Anacoda再导入环境文件openpose_lw1.yml

目录如下：


`根目录\env\openpose_lw1.yml`

## 数据库
两个表分别是data和regist，管理mysql数据库推荐使用navicat

`根目录\database\data.csv`

`根目录\database\management.csv`

## 运行
运行根目录文件下的
**main.py**
即可

运行效果：
<div align="center">
  <img src="https://github.com/QiYi92/ImageHost/blob/main/img/hprs1.png">
  <img src="https://github.com/QiYi92/ImageHost/blob/main/img/hprs2.png">
</div>
