import pandas as pd
import torch
import torch.nn.functional as F
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from torchvision import transforms

from redstone_lenet_class import RedstoneLeNet

# Load trained model
model = RedstoneLeNet()
model.load_state_dict(torch.load("redstone_lenet.pth", map_location=torch.device('cpu')))
model.eval()

# Define transformation
transform = transforms.Compose([
    transforms.Resize((15, 15)),  # Resize to match model input
    transforms.Grayscale(num_output_channels=1),  # Convert to grayscale
    transforms.ToTensor()  # Convert to tensor
])

# Function to draw an image
def draw_digit():
    fig, ax = plt.subplots(figsize=(3, 3))
    ax.set_xticks([])  # Hide axes
    ax.set_yticks([])
    canvas = np.ones((15, 15))  # Create a blank canvas
    drawing = []

    def on_draw(event):
        if event.xdata is not None and event.ydata is not None:
            x, y = int(event.xdata), int(event.ydata)
            canvas[y - 1:y + 1, x - 1:x + 1] = 0  # Simulate brush effect
            drawing.append((x, y))
            ax.imshow(canvas, cmap="gray")
            plt.draw()

    fig.canvas.mpl_connect("motion_notify_event", on_draw)
    plt.show()

    return canvas

# Draw number
# image_array = draw_digit()
image_array = pd.read_csv("digit.csv", header=None).values
print(image_array)

# Convert drawn image to PIL Image
image_pil = Image.fromarray((image_array * 255).astype(np.uint8))  # Convert back to 0-255 range
image_pil = image_pil.resize((15, 15))  # Resize to 15x15

# Convert to tensor
image_tensor = transform(image_pil).unsqueeze(0)  # Add batch dimension

# Classify with model
with torch.no_grad():
    output = model(image_tensor)
    prediction = torch.argmax(F.softmax(output, dim=1)).item()

print(f"Predicted Number: {prediction}")

# Show the drawn image again
plt.imshow(image_pil, cmap="gray")
plt.title(f"Predicted: {prediction}")
plt.axis("off")
plt.show()
