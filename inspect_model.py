import torch
from redstone_lenet_class import RedstoneLeNet

# Load the trained model
model = RedstoneLeNet()
model.load_state_dict(torch.load("redstone_lenet.pth", map_location=torch.device('cpu')))
model.eval()

# Print the model structure
print(model)

torch.set_printoptions(threshold=torch.inf)
f = open("model_weights.txt", "w")
for name, param in model.named_parameters():
    # print(f"层: {name} | 形状: {param.shape}")
    # print(param.data)
    f.write(f"\n[LAYER]: {name} | [SHAPE]: {param.shape}\n")
    f.write(str(param.data))

f.close()