import argparse
import cv2
import os

import torch
from torch.nn import DataParallel
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import transforms

from datasets.coco import CocoTrainDataset
from datasets.transformations import ConvertKeypoints, Scale, Rotate, CropPad, Flip
from modules.get_parameters import get_parameters_conv, get_parameters_bn, get_parameters_conv_depthwise
from models.with_mobilenet import PoseEstimationWithMobileNet
from modules.loss import l2_loss
from modules.load_state import load_state, load_from_mobilenet
from val import evaluate

cv2.setNumThreads(0)  # 设置OpenCV线程数为0
cv2.ocl.setUseOpenCL(False)  # 禁用OpenCL以防止DataLoader冻结


def train(prepared_train_labels, train_images_folder, num_refinement_stages, base_lr, batch_size, batches_per_iter,
          num_workers, checkpoint_path, weights_only, from_mobilenet, checkpoints_folder, log_after,
          val_labels, val_images_folder, val_output_name, checkpoint_after, val_after):
    net = PoseEstimationWithMobileNet(num_refinement_stages)  # 初始化PoseEstimationWithMobileNet模型

    stride = 8  # 步长为8
    sigma = 7  # sigma为7
    path_thickness = 1  # path_thickness为1
    dataset = CocoTrainDataset(prepared_train_labels, train_images_folder,
                               stride, sigma, path_thickness,
                               transform=transforms.Compose([
                                   ConvertKeypoints(),  # 转换关键点
                                   Scale(),  # 缩放
                                   Rotate(pad=(128, 128, 128)),  # 旋转
                                   CropPad(pad=(128, 128, 128)),  # 裁剪
                                   Flip()]))  # 翻转
    train_loader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers)  # 初始化DataLoader

    optimizer = optim.Adam([  # 初始化Adam优化器
        {'params': get_parameters_conv(net.model, 'weight')},
        {'params': get_parameters_conv_depthwise(net.model, 'weight'), 'weight_decay': 0},
        {'params': get_parameters_bn(net.model, 'weight'), 'weight_decay': 0},
        {'params': get_parameters_bn(net.model, 'bias'), 'lr': base_lr * 2, 'weight_decay': 0},
        {'params': get_parameters_conv(net.cpm, 'weight'), 'lr': base_lr},
        {'params': get_parameters_conv(net.cpm, 'bias'), 'lr': base_lr * 2, 'weight_decay': 0},
        {'params': get_parameters_conv_depthwise(net.cpm, 'weight'), 'weight_decay': 0},
        {'params': get_parameters_conv(net.initial_stage, 'weight'), 'lr': base_lr},
        {'params': get_parameters_conv(net.initial_stage, 'bias'), 'lr': base_lr * 2, 'weight_decay': 0},
        {'params': get_parameters_conv(net.refinement_stages, 'weight'), 'lr': base_lr * 4},
        {'params': get_parameters_conv(net.refinement_stages, 'bias'), 'lr': base_lr * 8, 'weight_decay': 0},
        {'params': get_parameters_bn(net.refinement_stages, 'weight'), 'weight_decay': 0},
        {'params': get_parameters_bn(net.refinement_stages, 'bias'), 'lr': base_lr * 2, 'weight_decay': 0},
    ], lr=base_lr, weight_decay=5e-4)

    num_iter = 0  # 迭代次数初始化为0
    current_epoch = 0  # 当前epoch初始化为0
    drop_after_epoch = [100, 200, 260]  # 在第100、200、260个epoch后降低学习率
    scheduler = optim.lr_scheduler.MultiStepLR(optimizer, milestones=drop_after_epoch, gamma=0.333)  # 初始化学习率调度器
    if checkpoint_path:  # 如果有checkpoint路径
        checkpoint = torch.load(checkpoint_path)  # 加载checkpoint

        if from_mobilenet:  # 如果是从mobilenet加载
            load_from_mobilenet(net, checkpoint)  # 从mobilenet加载
        else:
            load_state(net, checkpoint)  # 加载状态
            if not weights_only:  # 如果不仅加载权重
                optimizer.load_state_dict(checkpoint['optimizer'])  # 加载优化器状态
                scheduler.load_state_dict(checkpoint['scheduler'])  # 加载学习率调度器状态
                num_iter = checkpoint['iter']  # 加载迭代次数
                current_epoch = checkpoint['current_epoch']  # 加载当前epoch


    net = DataParallel(net).cuda()  # 将模型放到GPU上并行计算
    net.train()  # 设置模型为训练模式
    for epochId in range(current_epoch, 280):  # 遍历每个epoch
        scheduler.step()  # 更新学习率
        total_losses = [0, 0] * (num_refinement_stages + 1)  # heatmaps loss, paf loss per stage
        batch_per_iter_idx = 0
        for batch_data in train_loader:  # 遍历每个batch
            if batch_per_iter_idx == 0:
                optimizer.zero_grad()  # 梯度清零

            images = batch_data['image'].cuda()  # 将数据放到GPU上
            keypoint_masks = batch_data['keypoint_mask'].cuda()
            paf_masks = batch_data['paf_mask'].cuda()
            keypoint_maps = batch_data['keypoint_maps'].cuda()
            paf_maps = batch_data['paf_maps'].cuda()

            stages_output = net(images)  # 前向传播

            losses = []
            for loss_idx in range(len(total_losses) // 2):  # 计算loss
                losses.append(l2_loss(stages_output[loss_idx * 2], keypoint_maps, keypoint_masks, images.shape[0]))
                losses.append(l2_loss(stages_output[loss_idx * 2 + 1], paf_maps, paf_masks, images.shape[0]))
                total_losses[loss_idx * 2] += losses[-2].item() / batches_per_iter
                total_losses[loss_idx * 2 + 1] += losses[-1].item() / batches_per_iter

            loss = losses[0]
            for loss_idx in range(1, len(losses)):
                loss += losses[loss_idx]
            loss /= batches_per_iter
            loss.backward()  # 反向传播
            batch_per_iter_idx += 1
            if batch_per_iter_idx == batches_per_iter:
                optimizer.step()  # 更新参数
                batch_per_iter_idx = 0
                num_iter += 1
            else:
                continue

            if num_iter % log_after == 0:  # 打印loss
                print('Iter: {}'.format(num_iter))
                for loss_idx in range(len(total_losses) // 2):
                    print('\n'.join(['stage{}_pafs_loss:     {}', 'stage{}_heatmaps_loss: {}']).format(
                        loss_idx + 1, total_losses[loss_idx * 2 + 1] / log_after,
                        loss_idx + 1, total_losses[loss_idx * 2] / log_after))
                for loss_idx in range(len(total_losses)):
                    total_losses[loss_idx] = 0
            if num_iter % checkpoint_after == 0:  # 保存模型
                snapshot_name = '{}/checkpoint_iter_{}.pth'.format(checkpoints_folder, num_iter)
                torch.save({'state_dict': net.module.state_dict(),
                            'optimizer': optimizer.state_dict(),
                            'scheduler': scheduler.state_dict(),
                            'iter': num_iter,
                            'current_epoch': epochId},
                           snapshot_name)
            if num_iter % val_after == 0:  # 验证模型
                print('Validation...')
                evaluate(val_labels, val_output_name, val_images_folder, net)


                net.train()


# /e:/Code/openpose_lw/object1/object/train.py
if __name__ == '__main__':
    # 解析命令行参数
    parser = argparse.ArgumentParser()
    parser.add_argument('--prepared-train-labels', type=str, required=True,
                        help='path to the file with prepared annotations')
    parser.add_argument('--train-images-folder', type=str, required=True, help='path to COCO train images folder')
    parser.add_argument('--num-refinement-stages', type=int, default=1, help='number of refinement stages')
    parser.add_argument('--base-lr', type=float, default=4e-5, help='initial learning rate')
    parser.add_argument('--batch-size', type=int, default=80, help='batch size')
    parser.add_argument('--batches-per-iter', type=int, default=1, help='number of batches to accumulate gradient from')
    parser.add_argument('--num-workers', type=int, default=8, help='number of workers')
    parser.add_argument('--checkpoint-path', type=str, required=True, help='path to the checkpoint to continue training from')
    parser.add_argument('--from-mobilenet', action='store_true',
                        help='load weights from mobilenet feature extractor')
    parser.add_argument('--weights-only', action='store_true',
                        help='just initialize layers with pre-trained weights and start training from the beginning')
    parser.add_argument('--experiment-name', type=str, default='default',
                        help='experiment name to create folder for checkpoints')
    parser.add_argument('--log-after', type=int, default=100, help='number of iterations to print train loss')

    parser.add_argument('--val-labels', type=str, required=True, help='path to json with keypoints val labels')
    parser.add_argument('--val-images-folder', type=str, required=True, help='path to COCO val images folder')
    parser.add_argument('--val-output-name', type=str, default='detections.json',
                        help='name of output json file with detected keypoints')
    parser.add_argument('--checkpoint-after', type=int, default=5000,
                        help='number of iterations to save checkpoint')
    parser.add_argument('--val-after', type=int, default=5000,
                        help='number of iterations to run validation')
    args = parser.parse_args()

    # 创建保存模型的文件夹
    checkpoints_folder = '{}_checkpoints'.format(args.experiment_name)
    if not os.path.exists(checkpoints_folder):
        os.makedirs(checkpoints_folder)

    # 开始训练
    train(args.prepared_train_labels, args.train_images_folder, args.num_refinement_stages, args.base_lr, args.batch_size,
          args.batches_per_iter, args.num_workers, args.checkpoint_path, args.weights_only, args.from_mobilenet,
          checkpoints_folder, args.log_after, args.val_labels, args.val_images_folder, args.val_output_name,
          args.checkpoint_after, args.val_after)


