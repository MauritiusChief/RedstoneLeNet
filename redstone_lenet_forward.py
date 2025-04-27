import math
import torch

def relu_cut(x):
    return max(0.0, min(x, 1.0))

def tanh(x):
    '''用Hard Tanh近似表示'''
    if x < -1:
        return -1
    elif x > 1:
        return 1
    else:
        return x

def rsr(x):
    """返回最近的2^-14整数倍，模拟舍弃精度锯齿化后的计算"""
    x = float(x)
    if not (-2 <= x <= 2):
        raise ValueError(f"输入值必须在 2^-14 到 2 之间，输入值为{x}")
    # 单位值：2^-14
    unit = 2 ** -14
    # 计算最接近的单位倍数
    nearest_multiple = round(x / unit)
    # 还原成实际值
    nearest_value = nearest_multiple * unit
    return nearest_value

def conv2d_manual(input_tensor, weight, bias, stride=2):
    """
    input_tensor: list of list of float, shape [28][28]
    weight: list of list of list of list [1][1][3][3]
    bias: list [1]
    return: list of list [13][13]
    """
    K = 3
    H_out = (len(input_tensor) - K) // stride + 1
    W_out = (len(input_tensor[0]) - K) // stride + 1
    output = [[0.0 for _ in range(W_out)] for _ in range(H_out)]

    for i in range(H_out):
        for j in range(W_out):
            val = 0.0
            for ki in range(K):
                for kj in range(K):
                    val += rsr(input_tensor[i*stride+ki][j*stride+kj]) * rsr(weight[0][0][ki][kj])
            val += rsr(bias[0])
            output[i][j] = relu_cut(val)
    return output

def flatten(matrix):
    flat = []
    for row in matrix:
        for val in row:
            flat.append(val)
    return flat

def linear_manual(input_vec, weight_matrix, bias_vec):
    """
    input_vec: [N]
    weight_matrix: [M, N]
    bias_vec: [M]
    Return: [M]
    """
    # print(f"[DEBUG] type(input_vec) = {type(input_vec)}")
    # print(f"[DEBUG] len(input_vec) = {len(input_vec)}")
    output = []
    for i in range(len(weight_matrix)):
        acc = 0.0
        for j in range(len(weight_matrix[i])):
            acc += rsr(input_vec[j]) * rsr(weight_matrix[i][j])
        acc += rsr(bias_vec[i])
        output.append(acc)
    return output

def load_weights(filepath):
    """
    加载后立即转换为普通list
    """
    raw_weights = torch.load(filepath, map_location=torch.device('cpu'))
    clean_weights = {}
    for key, value in raw_weights.items():
        clean_weights[key] = value.cpu().numpy().tolist()
    return clean_weights

def argmax(vec):
    """
    返回最大值的索引
    """
    max_idx = 0
    max_val = vec[0]
    for i in range(1, len(vec)):
        if vec[i] > max_val:
            max_val = vec[i]
            max_idx = i
    return max_idx

def predict(binary_image, weight_dict):
    """
    binary_image: 15x15 list of 0/1
    weight_dict: torch.load from redstone_lenet.pth, into list-based form
    """
    # print(f"[DEBUG] input:")
    # print(f"[DEBUG] type(binary_image) = {type(binary_image)}")
    # print(f"[DEBUG] len(binary_image) = {len(binary_image)}")

    # ===== Conv Layer =====
    w_conv = weight_dict['conv1.weight']  # shape [1,1,3,3]
    b_conv = weight_dict['conv1.bias']    # shape [1]
    x = conv2d_manual(binary_image, w_conv, b_conv, stride=2)  # → [1, 7, 7]
    # print(f"[DEBUG] after Conv Layer:")
    # print(f"[DEBUG] type(x) = {type(x)}")
    # print(f"[DEBUG] len(x) = {len(x)}")

    # ===== Flatten =====
    x = flatten(x)  # shape [49]
    # print(f"[DEBUG] after Flatten:")
    # print(f"[DEBUG] type(x) = {type(x)}")
    # print(f"[DEBUG] len(x) = {len(x)}")

    # ===== FC1 =====
    w1 = weight_dict['fc1.weight']  # [30, 49]
    b1 = weight_dict['fc1.bias']    # [30]
    x = linear_manual(x, w1, b1)
    x = [tanh(v) for v in x]

    # ===== FC2 =====
    w2 = weight_dict['fc2.weight']  # [30, 30]
    b2 = weight_dict['fc2.bias']
    x = linear_manual(x, w2, b2)
    x = [tanh(v) for v in x]

    # ===== FC3 =====
    w3 = weight_dict['fc3.weight']  # [10, 30]
    b3 = weight_dict['fc3.bias']
    x = linear_manual(x, w3, b3)

    # ===== Argmax 输出结果 =====
    return argmax(x)
