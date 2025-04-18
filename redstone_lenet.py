import numpy as np
import torchvision.transforms as transforms
from skimage.morphology import skeletonize

def shift_image(img, dx, dy):
    """Shift image by dx (columns) and dy (rows), fill new area with 0."""
    shifted = np.zeros_like(img)
    if dy >= 0:
        rows_src = slice(0, img.shape[0] - dy)
        rows_dst = slice(dy, img.shape[0])
    else:
        rows_src = slice(-dy, img.shape[0])
        rows_dst = slice(0, img.shape[0] + dy)

    if dx >= 0:
        cols_src = slice(0, img.shape[1] - dx)
        cols_dst = slice(dx, img.shape[1])
    else:
        cols_src = slice(-dx, img.shape[1])
        cols_dst = slice(0, img.shape[1] + dx)

    shifted[rows_dst, cols_dst] = img[rows_src, cols_src]
    return shifted

def custom_skeletonize(binary):
    # Step 1: Skeletonize the binary image
    skeleton = skeletonize(binary).astype(np.uint8)

    # Step 2: Generate 3 slightly thickened variants by copying pixels
    variant1 = skeleton | shift_image(skeleton, -1, 0)  # left
    variant2 = skeleton | shift_image(skeleton, 0, 1)   # down
    variant3 = skeleton | shift_image(skeleton, -1, 0) \
                         | shift_image(skeleton, 0, 1) \
                         | shift_image(skeleton, -1, 1)  # left, down, left-down
    
    variants = [variant1, variant2, variant1, variant2, variant3] # 减小变种3出现的概率

    # Step 3: Random cut and merge
    h, w = skeleton.shape
    mid_x = np.random.randint(w // 3, 2 * w // 3)
    mid_y = np.random.randint(h // 3, 2 * h // 3)

    new_img = np.zeros_like(skeleton)

    # Define 4 blocks and fill from randomly selected variant
    new_img[:mid_y, :mid_x] = variants[np.random.randint(5)][:mid_y, :mid_x]       # Top-left
    new_img[:mid_y, mid_x:] = variants[np.random.randint(5)][:mid_y, mid_x:]       # Top-right
    new_img[mid_y:, :mid_x] = variants[np.random.randint(5)][mid_y:, :mid_x]       # Bottom-left
    new_img[mid_y:, mid_x:] = variants[np.random.randint(5)][mid_y:, mid_x:]

    return new_img

class SkeletonizeTransform:
    def __call__(self, img):
        # 确保图像是灰度
        img = img.convert('L')

        # # Resize 到 15x15（可以改成你想要的大小）
        # img = img.resize((15, 15))

        # 转为 numpy 数组
        arr = np.array(img)

        # 若最大值不为0，则进行缩放
        max_val = arr.max()
        if max_val > 0:
            arr = arr * (255.0 / max_val)

        # 二值化
        binary = arr > 128  # True/False array

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

