import torch
from redstone_lenet_class import RedstoneLeNet

# Load the trained model
model = RedstoneLeNet()
model.load_state_dict(torch.load("redstone_lenet.pth", map_location=torch.device('cpu')))
model.eval()

# Print the model structure
print(model)

# Print the first few weight values of the first layer
for name, param in model.named_parameters():
    print(f"Layer: {name} | Shape: {param.shape}")
    print(param[:5])  # Print first few values
    break  # Remove this to see all layers
