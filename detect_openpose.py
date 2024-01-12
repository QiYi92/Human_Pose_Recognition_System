# func:通过openpose实现多人实时姿态估计
#注：修改openpose姿态估计相关配置文件主要在此.py中进行
# anthor:yohn
# time:20220814

import argparse

import cv2
import numpy as np
import torch
import time

from models.with_mobilenet import PoseEstimationWithMobileNet
from modules.keypoints import extract_keypoints, group_keypoints
from modules.load_state import load_state
from modules.pose import Pose, track_poses
from val import normalize, pad_width

#初始化：
#加载网络
net = PoseEstimationWithMobileNet()
#'--cpu', action='store_true', help='run network inference on cpu'
cpu=False
#'--track', type=int, default=1, help='track pose id in video'
#是否设置跟踪id （目标跟踪）
track=int(1)
smooth=int(1)

#设置权重路径
#path_weight=
checkpoint = torch.load("./train_model/checkpoint_iter_370000.pth", map_location='cpu')
#加载状态？
load_state(net, checkpoint)
#设置高度
height_size=int(256)

net = net.eval()
if not cpu:
    net = net.cuda()
    print(torch.__version__)

def infer_fast(net, img, net_input_height_size, stride, upsample_ratio, cpu,
               pad_value=(0, 0, 0), img_mean=np.array([128, 128, 128], np.float32), img_scale=np.float32(1/256)):
    height, width, _ = img.shape
    scale = net_input_height_size / height

    scaled_img = cv2.resize(img, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
    scaled_img = normalize(scaled_img, img_mean, img_scale)
    min_dims = [net_input_height_size, max(scaled_img.shape[1], net_input_height_size)]
    padded_img, pad = pad_width(scaled_img, stride, pad_value, min_dims)

    tensor_img = torch.from_numpy(padded_img).permute(2, 0, 1).unsqueeze(0).float()
    if not cpu:
        tensor_img = tensor_img.cuda()

    stages_output = net(tensor_img)

    stage2_heatmaps = stages_output[-2]
    heatmaps = np.transpose(stage2_heatmaps.squeeze().cpu().data.numpy(), (1, 2, 0))
    heatmaps = cv2.resize(heatmaps, (0, 0), fx=upsample_ratio, fy=upsample_ratio, interpolation=cv2.INTER_CUBIC)

    stage2_pafs = stages_output[-1]
    pafs = np.transpose(stage2_pafs.squeeze().cpu().data.numpy(), (1, 2, 0))
    pafs = cv2.resize(pafs, (0, 0), fx=upsample_ratio, fy=upsample_ratio, interpolation=cv2.INTER_CUBIC)

    return heatmaps, pafs, scale, pad


def detect(img):
    start = cv2.getTickCount()

    # 返回当前时间戳
    start_time = time.time()
    counter = 0

    stride = 8
    upsample_ratio = 4
    num_keypoints = Pose.num_kpts
    previous_poses = []
    delay = 1
    orig_img = img.copy()
    heatmaps, pafs, scale, pad = infer_fast(net, img, height_size, stride, upsample_ratio, cpu)

    total_keypoints_num = 0
    all_keypoints_by_type = []

    for kpt_idx in range(num_keypoints):  # 19th for bg
        total_keypoints_num += extract_keypoints(heatmaps[:, :, kpt_idx], all_keypoints_by_type, total_keypoints_num)

    pose_entries, all_keypoints = group_keypoints(all_keypoints_by_type, pafs)
    for kpt_id in range(all_keypoints.shape[0]):
        all_keypoints[kpt_id, 0] = (all_keypoints[kpt_id, 0] * stride / upsample_ratio - pad[1]) / scale
        all_keypoints[kpt_id, 1] = (all_keypoints[kpt_id, 1] * stride / upsample_ratio - pad[0]) / scale
    current_poses = []
    for n in range(len(pose_entries)):
        if len(pose_entries[n]) == 0:
            continue
        pose_keypoints = np.ones((num_keypoints, 2), dtype=np.int32) * -1
        for kpt_id in range(num_keypoints):
            if pose_entries[n][kpt_id] != -1.0:  # keypoint was found
                pose_keypoints[kpt_id, 0] = int(all_keypoints[int(pose_entries[n][kpt_id]), 0])
                pose_keypoints[kpt_id, 1] = int(all_keypoints[int(pose_entries[n][kpt_id]), 1])
        pose = Pose(pose_keypoints, pose_entries[n][18])
        current_poses.append(pose)

    # 如果需要跟踪，则进行跟踪
    if track:
        track_poses(previous_poses, current_poses, smooth=smooth)
        previous_poses = current_poses

    # 绘制姿势
    for pose in current_poses:
        pose.draw(img)
    #img = cv2.addWeighted(orig_img, 0.6, img, 0.4, 0)
    # 每个当前姿势绘制其边界框
    for pose in current_poses:
        cv2.rectangle(img, (pose.bbox[0], pose.bbox[1]), (pose.bbox[0] + pose.bbox[2], pose.bbox[1] + pose.bbox[3]), (0, 255, 0))
        if track:
            cv2.putText(img, 'id: {}'.format(pose.id), (pose.bbox[0], pose.bbox[1] - 16), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255))
    #cv2.imshow('Lightweight Human Pose Estimation Python Demo', img)
    # cv2.waitKey(100)

    for pose in current_poses:
        x, y, w, h = pose.bbox
        # 获取肩部关键点
        sho_r = pose.keypoints[2]
        sho_l = pose.keypoints[5]
        sho_y = round((sho_l[1] + sho_r[1]) / 2)

        # 获取脚部关键点
        ank_r = pose.keypoints[10]
        ank_l = pose.keypoints[13]
        ank_y = round((ank_l[1] + ank_r[1]) / 2)
        str = ""
        # 判断跌倒或站立
        if (w < h):
            if (abs(ank_y - sho_y) > 0.5 * max(w, h) and w < h):  # 判断跌倒
                str = "stand!"
            elif (h / w < 1.5):
                str = "squat!"  # 蹲坐
            # 在图像上绘制文本
            # 位置参数说明：图片，添加的文字，文字添加到图片上的位置，字体的类型，字体大小，字体颜色，字体粗细
            cv2.putText(img, str, (x, y + h), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
        elif (w > h):
            if (abs(ank_y - sho_y) > 0.5 * max(w, h) and w > h):  # 判断站立
                str = "fall!"
            elif (w > 1.5 * h):
                str = "fall!"
            # 在图像上绘制文本
            # 位置参数说明：图片，添加的文字，文字添加到图片上的位置，字体的类型，字体大小，字体颜色，字体粗细
            cv2.putText(img, str, (x, y + h), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)

    counter += 1  # 计算帧数
    # 实时显示帧数
    if (time.time() - start_time) != 0:
        cv2.putText(img, "FPS {0}".format(float('%.1f' % (counter / (time.time() - start_time)))), (30, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (20, 144, 255), 2)

    end = cv2.getTickCount()    # 运行耗时
    use_time = (end - start) / cv2.getTickFrequency()
    print('use-time: %.4fs' % use_time)

    return current_poses