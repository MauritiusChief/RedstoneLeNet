import numpy as np
import torchvision.transforms as transforms
from skimage.morphology import skeletonize

class SkeletonizeTransform:
    def __call__(self, img):
        # 确保图像是灰度
        img = img.convert('L')

        # Resize 到 15x15（可以改成你想要的大小）
        img = img.resize((15, 15))

        # 转为 numpy 数组
        arr = np.array(img)

        # 若最大值不为0，则进行缩放
        max_val = arr.max()
        if max_val > 0:
            arr = arr * (255.0 / max_val)

        # 二值化
        binary = arr > 128  # True/False array

        # 执行骨架化（skeletonize expects boolean array）
        skeleton = skeletonize(binary)
        # skeleton = binary

        # 转回 Tensor（0. or 1. float Tensor）
        skeleton_img = (skeleton.astype(np.float32))
        return transforms.ToTensor()(skeleton_img)  # shape: [1, H, W]

# 用于 DataLoader 的 transform
transform = transforms.Compose([
    SkeletonizeTransform()
])

