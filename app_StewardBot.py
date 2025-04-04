import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader

# 1. Definir las transformaciones para las imágenes
data_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# 2. Cargar el dataset desde la carpeta raíz que contiene las dos clases
data_dir = '/home/daniel/Escritorio/Programación de IA/Proyecto/accidentes'  # Esta carpeta contiene los directorios "con_sancion" y "sin_sancion"
dataset = datasets.ImageFolder(root=data_dir, transform=data_transform)

# Verificar las clases detectadas automáticamente
print("Clases:", dataset.classes)  # Ejemplo: ['con_sancion', 'sin_sancion']

# 3. Crear un DataLoader
batch_size = 50
dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=4)

# 4. Cargar un modelo preentrenado (por ejemplo, ResNet18)
model = models.resnet152(pretrained=True)

# Congelar los parámetros de todas las capas (opcional)
for param in model.parameters():
    param.requires_grad = False

# 5. Modificar la capa final para adaptarla a 2 clases
num_ftrs = model.fc.in_features
model.fc = nn.Linear(num_ftrs, 2)

# 6. Configurar dispositivo, función de pérdida y optimizador
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
model = model.to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(model.fc.parameters(), lr=0.001, momentum=0.9)

# 7. Bucle de entrenamiento
num_epochs = 30
total_loss = 0.0
total_corrects = 0

def calcular_accuracy(model, dataloader, device):
    model.eval()
    corrects = 0
    total = 0
    with torch.no_grad():
        for inputs, labels in dataloader:
            inputs = inputs.to(device)
            labels = labels.to(device)
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            corrects += torch.sum(preds == labels.data)
            total += labels.size(0)
    return corrects.double() / total

for epoch in range(num_epochs):
    model.train()  # Modo entrenamiento
    running_loss = 0.0
    running_corrects = 0
    
    for inputs, labels in dataloader:
        inputs = inputs.to(device)
        labels = labels.to(device)
        
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item() * inputs.size(0)
        _, preds = torch.max(outputs, 1)
        running_corrects += torch.sum(preds == labels.data)
    
    epoch_loss = running_loss / len(dataset)
    epoch_acc = running_corrects.double() / len(dataset)
    total_loss = epoch_loss
    total_corrects = epoch_acc
    print(f'Época {epoch+1}/{num_epochs} - Loss: {epoch_loss:.4f} - Accuracy: {epoch_acc:.4f}')

# Calcular métricas finales
final_accuracy = calcular_accuracy(model, dataloader, device)
print(f'Entrenamiento completado - Loss Final: {total_loss:.4f} - Accuracy Final: {final_accuracy:.4f}')

torch.save(model.state_dict(), "StewardBot.pth")
print("Modelo guardado como 'StewardBot.pth'")
