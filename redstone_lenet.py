import numpy as np
import torchvision.transforms as transforms
from skimage.morphology import skeletonize

def custom_skeletonize(binary):
    # 复制输入，避免原地修改
    output = binary.copy()
    H, W = binary.shape

    for y in range(2, H - 2):
        for x in range(2, W - 2):
            if not binary[y, x]:
                continue

            up     = binary[y - 1, x] and binary[y - 2, x]
            down   = binary[y + 1, x] and binary[y + 2, x]
            left   = binary[y, x - 1] and binary[y, x - 2]
            right  = binary[y, x + 1] and binary[y, x + 2]

            # 规则 1: 四个方向全是 1，则中心设为 0
            if np.all([up, down, left, right]):
                output[y, x] = 0
                continue

            # 规则 2：检查四个主方向（上下左右）
            up_zero = not binary[y - 1, x]
            down_zero = not binary[y + 1, x]
            left_zero = not binary[y, x - 1]
            right_zero = not binary[y, x + 1]

            directions = {
                'up': up,
                'down': down,
                'left': left,
                'right': right,
            }

            zero_flags = {
                'up': up_zero,
                'down': down_zero,
                'left': left_zero,
                'right': right_zero,
            }

            ones = [k for k, v in directions.items() if v]
            zeros = [k for k, v in zero_flags.items() if v]

            # 斜角只看1格
            ur = binary[y - 1, x + 1]
            dr = binary[y + 1, x + 1]
            dl = binary[y + 1, x - 1]
            ul = binary[y - 1, x - 1]

            diagonal = {
                ('up', 'right'): ur,
                ('right', 'down'): dr,
                ('down', 'left'): dl,
                ('left', 'up'): ul
            }

            if len(ones) == 2 and len(zeros) == 2:
                for pair, corner in diagonal.items():
                    if all(d in ones for d in pair) and corner:
                        output[y, x] = 0
                        break

    return output

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
        binary = arr > 96  # True/False array

        # 执行骨架化（skeletonize expects boolean array）
        skeleton = custom_skeletonize(binary)
        # skeleton = binary

        # 转回 Tensor（0. or 1. float Tensor）
        skeleton_img = (skeleton.astype(np.float32))
        return transforms.ToTensor()(skeleton_img)  # shape: [1, H, W]

# 用于 DataLoader 的 transform
transform = transforms.Compose([
    SkeletonizeTransform()
])

