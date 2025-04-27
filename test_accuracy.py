
import csv
import math
import random
import torch
import torchvision
import matplotlib.pyplot as plt

from redstone_lenet_forward import predict
from redstone_lenet import transform

mnist_dataset = torchvision.datasets.MNIST(root="./data", train=True, transform=transform, download=True)

def load_weights(filepath):
    return torch.load(filepath, map_location=torch.device('cpu'))

# Test accuracy
weights = load_weights("redstone_lenet.pth")
# print(weights.keys())

pred_limit = 100
# # 随机样本
# sample_indices = random.sample(range(len(mnist_dataset)), pred_limit)

# 特定标签的样本
target_label = 9
indices = [i for i, (_, label) in enumerate(mnist_dataset) if label == target_label]
sample_indices = random.sample(indices, pred_limit)

images = []
labels = []
predictions = []

correct, total = 0, 0
sample_written = False
for idx in sample_indices:
    img_tensor, label = mnist_dataset[idx]
    img = img_tensor.squeeze(0).tolist()
    # print(f"[DEBUG] type(img_tensor) = {type(img_tensor)}")
    # print(f"[DEBUG] type(img) = {type(img)}")

    pred = predict(img, weights)
    total += 1
    correct += (pred == label)
    if idx % 10 == 0:
        print(f"Current Accuracy: {100 * correct / total:.2f}%")
    # print(f"Label: {label} Pred: {pred}")
    # if (pred == label) and not sample_written and random.random() < 0.02:
    #     with open('pre_draw/temp.csv', 'w', newline='') as csvfile:
    #         spamwriter = csv.writer(csvfile, quotechar='|', quoting=csv.QUOTE_MINIMAL)
    #         for row in img:
    #             spamwriter.writerow([int(i) for i in row])
    #     sample_written = True
    images.append(img)
    labels.append(label)
    predictions.append(pred)

print(f"Test Accuracy on {pred_limit} samples: {100 * correct / total:.2f}%")

# Randomly select a few results to display
display_count = 28
selected_indices = random.sample(range(len(images)), display_count)

plt.figure(figsize=(10, 2))
for i, idx in enumerate(selected_indices):
    cols = 7
    rows = math.ceil(display_count / 7)
    plt.subplot(rows, cols, i + 1)
    plt.imshow(images[idx], cmap='gray')
    plt.title(f"True: {labels[idx]}\nPred: {predictions[idx]}")
    plt.axis('off')
    plt.subplots_adjust(hspace=0.6)

# plt.tight_layout()
plt.show()