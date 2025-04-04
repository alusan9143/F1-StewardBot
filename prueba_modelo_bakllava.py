import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import base64
import ollama


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

# Cargar el modelo entrenado de clasificación
modelo_path = "F1MarshAIl.pth"  # Asegúrate de que este archivo existe
modelo = models.resnet152()
num_ftrs = modelo.fc.in_features
modelo.fc = nn.Linear(num_ftrs, 2)
modelo.load_state_dict(torch.load(modelo_path, map_location=device))
modelo.to(device)
modelo.eval()

# Definir las clases y mensajes personalizados
clases = ["con_sancion", "sin_sancion"]
mensajes = {
    "con_sancion": "🔴 La siguiente acción es sancionable.",
    "sin_sancion": "✅ La siguiente acción no es sancionable, es un lance de carrera."
}

def clasificar_imagen(image_path):
    """
    Clasifica la imagen y devuelve un mensaje basado en la categoría.
    """
    image = Image.open(image_path).convert('RGB')
    image = clasificacion_transform(image).unsqueeze(0).to(device)
    with torch.no_grad():
        output = modelo(image)
        _, pred = torch.max(output, 1)
    categoria = clases[pred.item()]
    return mensajes[categoria], categoria

# -----------------------
# PARTE 2: Integración de Clasificación y Descripción con Bakllava
# -----------------------

def analizar_imagen(image_path):
    """
    Clasifica la imagen y, además, utiliza Bakllava para obtener una descripción detallada.
    """
    # mensaje, categoria = clasificar_imagen(image_path)
    # print("\n🔍 Análisis de la imagen:")
    # print(f"➡️ Clasificación: {mensaje}")
    
    # Obtener descripción detallada usando Bakllava
    # Se asume que 'describe_image' es el método que genera la descripción de la imagen
    # descripcion_detallada = bakllava_embeddings.describe_image(image_path)
    # print("➡️ Descripción detallada:", descripcion_detallada)

    """ Generar una descripción detallada del accidente usando BakLLaVA"""
    with open(image_path, "rb") as img_file:
        encoded_image = base64.b64encode(img_file.read()).decode("utf-8")
    
    prompt = """
        Analiza la imagen y describe objetivamente la acción ocurrida. **No determines si es sancionable o no.**  
        Responde en este formato exacto:  

        1. **Número de coches involucrados**: [número]  
        2. **Colores de los coches**: [color1] y [color2]  
        3. **Zona de la colisión**: [parte del coche golpeada, ej. "lateral derecho", "frontal contra trasero"]  
        4. **Posición relativa**: [¿Estaban en paralelo? ¿Uno por delante del otro?]  
        5. **Contexto de la acción**: [¿Qué estaba pasando antes del contacto? Ej: "Uno intentaba adelantar", "Frenada brusca"]  
        6. **Posible culpable**: [¿Quien podría ser el posible culpable?]

        Descripción adicional: [Breve resumen]  
        """

    response = ollama.generate(
        model="llava",  # Alternativa más estable
        prompt=prompt,
        images=[encoded_image]
    )

    return response.get("response", "Error al generar la descripción")

# Prueba con una imagen
ruta_imagen = "./pruebas/frame_83.jpg"  # Cambia por la ruta de tu imagen
resultado = analizar_imagen(ruta_imagen)
print(resultado)
