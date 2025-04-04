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
    canvas = np.zeros((15, 15))  # Create a blank canvas
    drawing = False  # Flag to track when to draw

    def on_press(event):
        """Activate drawing when the mouse button is pressed."""
        nonlocal drawing
        drawing = True

    def on_release(event):
        """Stop drawing when the mouse button is released."""
        nonlocal drawing
        drawing = False

    def on_draw(event):
        """Draw only when the mouse button is held down."""
        if drawing and event.xdata is not None and event.ydata is not None:
            x, y = int(event.xdata), int(event.ydata)
            if 0 <= x < 15 and 0 <= y < 15:  # Ensure within bounds
                canvas[y, x] = 1  # Simulate brush effect
                ax.imshow(canvas, cmap="gray")
                plt.draw()

    fig.canvas.mpl_connect("button_press_event", on_press)
    fig.canvas.mpl_connect("button_release_event", on_release)
    fig.canvas.mpl_connect("motion_notify_event", on_draw)
    plt.show()

    return canvas

# Draw number
image_array = draw_digit()
image_array[0,0] = 0
# image_array = pd.read_csv("digit4.csv", header=None).values
# print(image_array)

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
