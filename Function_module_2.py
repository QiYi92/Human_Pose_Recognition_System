import os
import cv2
import detect_openpose


# 测试视频
path_video="./video/test6.mp4"
cap=cv2.VideoCapture(path_video)


alarms=[]
while True:
    #判断摔倒标识位
    flag_trip = True

    #读取视频流
    ret,img = cap.read()
    if not ret:
        break

    #目标检测
    p_result=detect_openpose.detect(img)
    print(p_result)


    cv2.imshow("detect-result", img)

    #如果结果个数大于10，则清空以前结果
    if(len(alarms)>10):
        alarms=[]

    #按q键退出循环
    key = cv2.waitKey(1) & 0xFF
    if cv2.waitKey(1)==ord('q'):
        break

