import numpy as np
import pandas as pd
import torchvision
import torchvision.transforms as transforms
import matplotlib.pyplot as plt

# Load MNIST dataset
transform = transforms.Compose([
    transforms.Resize((15, 15)),  # Resize to 15x15
    transforms.ToTensor(),
    transforms.Lambda(lambda x: (x > 0.5).float())  # Binarize image
])
mnist_dataset = torchvision.datasets.MNIST(root="./data", train=True, transform=transform, download=True)

# Function to find and display images of a specific digit
def show_mnist_samples(target_label, num_samples=5):
    images = []
    labels = []

    # Loop through dataset to find images with the target label
    for img, label in mnist_dataset:
        if label == target_label:
            images.append(img)
            labels.append(label)
        if len(images) >= num_samples:
            break  # Stop when we collect enough samples

    # Plot images
    # fig, axes = plt.subplots(1, num_samples, figsize=(num_samples * 2, 2))
    # for i in range(num_samples):
    #     axes[i].imshow(images[i].squeeze(), cmap="gray")
    #     axes[i].axis("off")
    #     axes[i].set_title(f"Label: {labels[i]}")
    
    # plt.show()
    return images

samples = show_mnist_samples(target_label=0, num_samples=5)
sample = (samples[0].numpy().squeeze() * 1).astype(int)
print(sample)
pd.DataFrame(sample).to_csv("digit0.csv", index=False, header=False)
