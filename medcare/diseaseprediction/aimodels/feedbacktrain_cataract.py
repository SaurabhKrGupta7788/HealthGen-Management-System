import torch
import torch.nn as nn
import torchvision.transforms as tt
from PIL import Image
from torch.utils.data import DataLoader, Dataset, ConcatDataset
from torchvision.datasets import ImageFolder
import os

# Define Convolutional Block
class ConvBlock(nn.Module):
    def _init_(self, in_channel, out_channel, stride):
        super()._init_()  # Fixed typo
        self.conv = nn.Sequential(
            nn.Conv2d(in_channel, out_channel, kernel_size=4, stride=stride, padding=1, bias=True),
            nn.BatchNorm2d(out_channel),
            nn.LeakyReLU(0.2, inplace=True)
        )

    def forward(self, x):
        return self.conv(x)

# Define Model
class NeuralNet(nn.Module):
    def _init_(self, in_channels=3, out_channels=[64, 128, 256, 512, 512]):
        super()._init_()  # Fixed typo
        layers = []
        for i in range(len(out_channels)):
            layers.append(ConvBlock(in_channels, out_channels[i], stride=2 if out_channels[i] != 512 else 1))
            in_channels = out_channels[i]

        self.layers = nn.Sequential(*layers)
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(512 * 30 * 30, 1024),
            nn.ReLU(),
            nn.Linear(1024, 1)  # Binary classification output
        )

    def forward(self, x):
        out = self.classifier(self.layers(x))
        return out

# Set Device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# Load Model
model = NeuralNet().to(device)
model.load_state_dict(torch.load("./cataract_model_epoch_40.pth", map_location=device))  # Load trained weights

# Define Transformations
transform = tt.Compose([
    tt.Resize((256, 256)),
    tt.CenterCrop((256, 256)),
    tt.ToTensor()
])

# Define dataset paths (Ensure these are set correctly)
test_data_dir = "./test"
feedback_data_dir = "./feedback"

train_dataset = ImageFolder(test_data_dir, transform=transform)
feedback_dataset = ImageFolder(feedback_data_dir, transform=transform)

# Combine Datasets
combined_dataset = ConcatDataset([train_dataset, feedback_dataset])
combined_dataloader = DataLoader(combined_dataset, batch_size=32, shuffle=True, pin_memory=True)

# Define Optimizer & Loss
optimizer = torch.optim.Adam(model.parameters(), lr=0.001, betas=(0.9, 0.999))
criterion = nn.BCEWithLogitsLoss()

# Train Model
num_epochs = 10
for epoch in range(num_epochs):
    model.train()
    for image, label in combined_dataloader:
        image, label = image.to(device), label.to(device)

        pred = model(image)
        loss = criterion(pred.flatten(), label.to(dtype=torch.float32))

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

# Save the Model
model.eval()
scripted_model = torch.jit.script(model)
torch.jit.save(scripted_model, "cataract3.pt")
print("✅ Model with trained weights saved successfully!")

# Prediction Function
def predict_image(image_path):
    model_path = "cataract3.pt"
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    Model = torch.jit.load(model_path, map_location=device)
    Model.eval()

    transform = tt.Compose([
        tt.Resize((256, 256)),
        tt.CenterCrop(256),
        tt.ToTensor()
    ])

    img = Image.open(image_path).convert('RGB')  # Open Image
    img = transform(img).unsqueeze(0).to(device)  # Apply transformation
    with torch.no_grad():
        pred = Model(img)
        prob = torch.sigmoid(pred).item()  # Convert to probability
        label = "Cataract" if prob > 0.5 else "Normal"
        print(f"Prediction: {label} (Probability: {prob:.4f})")

# Example Prediction
image_path = r"C:\Users\GANAPATHI\Desktop\training\cataract\cataract_data\test\1\cat_0_5.jpg"
predict_image(image_path)