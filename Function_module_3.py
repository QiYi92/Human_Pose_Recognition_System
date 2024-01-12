import os
import cv2
import detect_openpose


# 测试视频
path_video="./test6.mp4"
cap=cv2.VideoCapture(path_video)

#测试文件夹路径
path="E:\Code\openpose_lw\lightweight-human-pose-estimation.pytorch\data"
# 结果保存路径
save_path=path+"_result"
print(save_path)
# 如果结果保存路径不存在，则创建
if not os.path.exists(save_path):
    os.mkdir(save_path)

# 获取文件夹中的所有文件
files=[]
for root,dirs,files in os.walk(path,topdown=True):
    imgs=files

# 初始化计数器
num=0
# 遍历文件夹中的所有文件
for file in files:
    # 读取图像
    img=cv2.imread(path+"\\"+file)
    # 进行目标检测
    p_result = detect_openpose.detect(img)
    # 保存结果图像
    name=save_path+"\\res"+file
    cv2.imwrite(name,img)
    num+=1
    print(p_result)
    print("检测第 ",str(num)," 图像!")