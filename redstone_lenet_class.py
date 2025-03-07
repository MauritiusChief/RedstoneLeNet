import torch
import torch.nn as nn

# Define the LeNet-style neural network
class RedstoneLeNet(nn.Module):
    def __init__(self):
        super(RedstoneLeNet, self).__init__()
        self.conv1 = nn.Conv2d(in_channels=1, out_channels=1, kernel_size=3, stride=2)  # 3x3 kernel, stride 2
        self.fc1 = nn.Linear(7 * 7, 30)
        self.fc2 = nn.Linear(30, 30)
        self.fc3 = nn.Linear(30, 10)
        self.relu = nn.ReLU()
        self.tanh = nn.Tanh()

    def forward(self, x):
        x = self.conv1(x)
        x = self.relu(x)
        x = torch.clamp(x, max=1)  # Cut off values > 1
        x = x.view(x.size(0), -1)  # Flatten before FC layers
        x = self.tanh(self.fc1(x))
        x = self.tanh(self.fc2(x))
        x = self.fc3(x)
        return x
