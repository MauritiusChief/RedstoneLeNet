
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

# Random sample
pred_limit = 1000
sample_indices = random.sample(range(len(mnist_dataset)), pred_limit)

images = []
labels = []
predictions = []

correct, total = 0, 0
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