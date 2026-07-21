import torch
import torch.nn as nn
import torchvision.transforms as tt
from PIL import Image
def predict_image(image_path):
    model_path = "CS_Net.pt" 
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    Model = torch.jit.load(model_path, map_location=device)
    Model.eval()

    transform = tt.Compose(
    [
        tt.Resize((288,288)),
        tt.Grayscale(num_output_channels=1),
        tt.ToTensor()
    ]
)

    img = Image.open(image_path)  # Open Image
    img = transform(img).unsqueeze(0).to(device)  # Apply transformation
    with torch.no_grad():
        pred = Model(img)
        #pred = torch.sigmoid(pred).item()
        result = torch.argmax(pred, dim=1)
        print(f"Prediction: {result} ")

#
image_path = r"C:\Users\harry\Downloads\R.jpeg"
predict_image(image_path)