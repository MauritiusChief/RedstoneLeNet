import torch

def relu_cut(x):
    return torch.clamp(x, 0.0, 1.0)

def tanh(x):
    return x.tanh()

def conv2d_manual(input_tensor, weight, bias, stride=2):
    C_out, C_in, K, _ = weight.shape
    H_out = (input_tensor.shape[1] - K) // stride + 1
    W_out = (input_tensor.shape[2] - K) // stride + 1
    output = torch.zeros((C_out, H_out, W_out))

    for co in range(C_out):
        for i in range(H_out):
            for j in range(W_out):
                region = input_tensor[0,
                         i*stride:i*stride+K,
                         j*stride:j*stride+K]
                val = 0.0
                for ki in range(K):
                    for kj in range(K):
                        val += region[ki][kj] * weight[co, 0, ki, kj]
                val += bias[co]
                output[co, i, j] = val
    return output

def flatten(tensor):
    return tensor.view(-1)

def linear_manual(input_vec, weight_matrix, bias_vec):
    """
    input_vec: [N]
    weight_matrix: [M, N]
    bias_vec: [M]
    Return: [M]
    """
    M, N = weight_matrix.shape
    output = torch.zeros(M)
    for i in range(M):
        acc = 0.0
        for j in range(N):
            acc += input_vec[j] * weight_matrix[i][j]
        acc += bias_vec[i]
        output[i] = acc
    return output

def load_weights(filepath):
    return torch.load(filepath, map_location=torch.device('cpu'))

def predict(binary_image, weight_dict):
    """
    binary_image: 28x28 list of 0/1
    weight_dict: torch.load from redstone_lenet.pth
    """
    # 转换为 Tensor 格式
    x = torch.tensor(binary_image, dtype=torch.float32).unsqueeze(0)  # shape [1, 28, 28]

    # ===== Conv Layer =====
    w_conv = weight_dict['conv1.weight']  # shape [1,1,3,3]
    b_conv = weight_dict['conv1.bias']    # shape [1]
    x = conv2d_manual(x, w_conv, b_conv, stride=2)  # → [1, 13, 13]
    x = relu_cut(x)

    # ===== Flatten =====
    x = flatten(x)  # shape [169]

    # ===== FC1 =====
    w1 = weight_dict['fc1.weight']  # [30, 169]
    b1 = weight_dict['fc1.bias']    # [30]
    x = linear_manual(x, w1, b1)
    x = tanh(x)

    # ===== FC2 =====
    w2 = weight_dict['fc2.weight']  # [30, 30]
    b2 = weight_dict['fc2.bias']
    x = linear_manual(x, w2, b2)
    x = tanh(x)

    # ===== FC3 =====
    w3 = weight_dict['fc3.weight']  # [10, 30]
    b3 = weight_dict['fc3.bias']
    x = linear_manual(x, w3, b3)

    # ===== Argmax 输出结果 =====
    return torch.argmax(x).item()
