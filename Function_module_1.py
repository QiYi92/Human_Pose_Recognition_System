import os
import cv2
import detect_openpose



# 打开摄像头
cap=cv2.VideoCapture(0)
if cap.isOpened():
    print('视频打开成功！')
else:
    print('视频打开失败！')

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
