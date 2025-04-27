import csv
import pandas as pd
import torch
import torch.nn.functional as F
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from torchvision import transforms

from redstone_lenet_class import RedstoneLeNet
from redstone_lenet_forward import load_weights, predict

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
image_array = pd.read_csv("pre_draw/dig6.csv", header=None).values
# image_array = draw_digit()
# image_array[0,0] = 0

# print(image_array)
# with open('pre_draw/temp.csv', 'w', newline='') as csvfile:
#     spamwriter = csv.writer(csvfile, quotechar='|', quoting=csv.QUOTE_MINIMAL)
#     for row in image_array:
#         spamwriter.writerow([int(i) for i in row])

weights = load_weights("redstone_lenet.pth")
# print(weights.keys())
prediction = predict(image_array, weights)

print(f"Predicted Number: {prediction}")

# Show the drawn image again
plt.imshow(image_array, cmap="gray")
plt.title(f"Predicted: {prediction}")
plt.axis("off")
plt.show()
