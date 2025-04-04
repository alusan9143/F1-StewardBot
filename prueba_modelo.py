import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image

# Detectar si hay GPU disponible
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Usando dispositivo: {device}")

# -----------------------
# PARTE 1: Clasificación
# -----------------------

# Transformaciones para la clasificación
clasificacion_transform = transforms.Compose([
    transforms.Resize(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# Cargar el modelo entrenado
modelo_path = "StewardBot.pth"  # Asegúrate de que este archivo existe
modelo = models.resnet152()
num_ftrs = modelo.fc.in_features
modelo.fc = nn.Linear(num_ftrs, 2)
modelo.load_state_dict(torch.load(modelo_path, map_location=device))
modelo.to(device)  # Mover el modelo a GPU si está disponible
modelo.eval()

# Definir las clases y mensajes personalizados
clases = ["con_sancion", "sin_sancion"]
mensajes = {
    "con_sancion": "🔴 La siguiente acción es sancionable.",
    "sin_sancion": "✅ La siguiente acción no es sancionable, es un lance de carrera."
}

def clasificar_imagen(image_path):
    """
    Clasifica la imagen y devuelve un mensaje de la categoría.
    """
    image = Image.open(image_path).convert('RGB')
    image = clasificacion_transform(image).unsqueeze(0).to(device)  # Mover imagen a GPU
    with torch.no_grad():
        output = modelo(image)
        _, pred = torch.max(output, 1)
    categoria = clases[pred.item()]
    return mensajes[categoria], categoria

# -----------------------
# PARTE 2: Integración de Clasificación
# -----------------------

def analizar_imagen(image_path):
    """
    Clasifica la imagen y muestra el mensaje correspondiente.
    """
    mensaje, categoria = clasificar_imagen(image_path)
    
    print("\n🔍 Análisis de la imagen:")
    print(f"➡️ Clasificación: {mensaje}")

# Prueba con una imagen
ruta_imagen = "./pruebas/prueba.jpg"  # Cambia por la ruta de tu imagen
analizar_imagen(ruta_imagen)