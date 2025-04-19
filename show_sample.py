import math
import torchvision
import matplotlib.pyplot as plt

# Load MNIST dataset
from redstone_lenet import transform

# from torchvision.transforms import transforms
# transform = transforms.Compose([
#     transforms.ToTensor(),
# ])

mnist_dataset = torchvision.datasets.MNIST(root="./data", train=True, transform=transform, download=True)

# Function to find and display images of a specific digit
def show_mnist_samples(target_label, skip_num = 0, num_samples=5, cols=7):
    images = []
    labels = []

    # Loop through dataset to find images with the target label
    skipped = 0
    for img, label in mnist_dataset:
        if label == target_label:
            if skipped < skip_num:
                skipped += 1
                continue
            images.append(img)
            labels.append(label)
        if len(images) >= num_samples:
            break  # Stop when we collect enough samples

    # Calculate number of rows needed
    rows = math.ceil(num_samples / cols)

    # Plot images
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 2, rows * 2))
    axes = axes.flatten()
    for i in range(num_samples):
        axes[i].imshow(images[i].squeeze(), cmap="gray")
        axes[i].axis("off")
        axes[i].set_title(f"Label: {labels[i]}")

    # Hide any unused subplots
    for j in range(num_samples, len(axes)):
        axes[j].axis("off")
    
    plt.tight_layout()
    # plt.savefig(f"pics/dig{target_label}_org_pg{skip_num//28}.png")
    # plt.savefig(f"pics/preprocess1/dig{target_label}_skl_pg{skip_num//28}.png")
    plt.show()
    return images

samples = show_mnist_samples(target_label=9, skip_num=28*0, num_samples=28)
# for d in range(10):
#     for p in range(1):
#         show_mnist_samples(target_label=d, skip_num=28*p, num_samples=28)
