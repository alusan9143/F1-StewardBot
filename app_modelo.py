import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import base64
import ollama
import json
from typing import List, Dict

# ---------------------------------------------------
# PARTE 1: Clasificación y descripción con Llava
# ---------------------------------------------------

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Configuración del modelo de clasificación
clasificacion_transform = transforms.Compose([
    transforms.Resize(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

modelo_path = "StewardBot.pth"
modelo = models.resnet152()
num_ftrs = modelo.fc.in_features
modelo.fc = nn.Linear(num_ftrs, 2)
modelo.load_state_dict(torch.load(modelo_path, map_location=device))
modelo.to(device)
modelo.eval()

clases = ["con_sancion", "sin_sancion"]
mensajes = {
    "con_sancion": "🔴 La siguiente acción es sancionable.",
    "sin_sancion": "✅ La siguiente acción no es sancionable, es un lance de carrera."
}

def clasificar_imagen(image_path: str) -> tuple:
    """Clasifica la imagen como sancionable o no"""
    image = Image.open(image_path).convert('RGB')
    image = clasificacion_transform(image).unsqueeze(0).to(device)
    with torch.no_grad():
        output = modelo(image)
        _, pred = torch.max(output, 1)
    categoria = clases[pred.item()]
    return mensajes[categoria], categoria

def analizar_imagen(image_path: str) -> str:
    """Genera descripción técnica de la acción"""
    with open(image_path, "rb") as img_file:
        encoded_image = base64.b64encode(img_file.read()).decode("utf-8")
    
    prompt = """
    Analiza la imagen de carrera con foco en posibles infracciones reglamentarias. Responde EXCLUSIVAMENTE en este formato:
    
    1. **Acción observada**: [adelantamiento/defensa/frenada/salida de pista]
    2. **Tipo de contacto**: [lateral/frontal/trasero/sin contacto] 
    3. **Cambios de trayectoria**: [describe qué coche movió y dirección]
    4. **Posición en pista**: [curva/recta/zona de frenado]
    5. **Bandera visible**: [sí/no + tipo si es visible]
    6. **Posible infracción**: [Bloqueo/Cambio múltiple de línea/Salida peligrosa/Defensa agresiva]
    """
    
    response = ollama.generate(
        model="llava",
        prompt=prompt,
        images=[encoded_image]
    )
    
    return response.get("response", "Error al generar la descripción")

# ---------------------------------------------------
# PARTE 2: Búsqueda de sanciones en JSON
# ---------------------------------------------------

def cargar_sanciones(json_path: str = "sanciones.json") -> List[Dict]:
    """Carga las sanciones desde el archivo JSON"""
    with open(json_path) as f:
        return json.load(f)

def buscar_sanciones(descripcion: str, sanciones: List[Dict]) -> List[Dict]:
    """Busca sanciones relevantes en base a la descripción"""
    resultados = []
    descripcion_lower = descripcion.lower()
    
    for sancion in sanciones:
        # Verificar coincidencia en palabras clave
        palabras_clave = sancion["metadata"]["palabras_clave"]
        coincidencias = sum(1 for kw in palabras_clave if kw.lower() in descripcion_lower)
        
        # Puntaje basado en coincidencias y gravedad
        if coincidencias > 0:
            sancion["puntaje"] = coincidencias + (
                0.5 if "agresiv" in descripcion_lower else 0
            )
            resultados.append(sancion)
    
    # Ordenar por puntaje (mayor primero)
    return sorted(resultados, key=lambda x: x["puntaje"], reverse=True)

def mostrar_resultados(resultados: List[Dict]):
    """Muestra los resultados de forma legible"""
    if not resultados:
        print("\n✅ No se encontraron infracciones aplicables")
        return
    
    mejor = resultados[0]
    md = mejor["metadata"]
    
    print(f"\n⚖️ SANCIÓN RECOMENDADA: {md['penalizacion']}")
    print(f"📜 Artículo: {md['articulo']} - {md['tipo']} ({md['gravedad']})")
    print(f"📌 Palabras clave: {', '.join(md['palabras_clave'][:3])}...")
    print("\n📝 Texto relevante:")
    print(mejor["text"][:200] + "...")
    
    if "ejemplos" in md:
        print("\n🔍 Ejemplos aplicables:")
        for ej in md["ejemplos"][:2]:
            print(f"- {ej}")

# ---------------------------------------------------
# FLUJO PRINCIPAL
# ---------------------------------------------------
if __name__ == "__main__":
    ruta_imagen = "./pruebas/frame_83.jpg"
    
    # 1. Clasificación inicial
    mensaje_clasificacion, categoria = clasificar_imagen(ruta_imagen)
    print(f"\nClasificación: {mensaje_clasificacion}")
    
    # 2. Solo continuar si es "con_sancion"
    if categoria == "con_sancion":
        descripcion_generada = analizar_imagen(ruta_imagen)
        print("\nDescripción técnica:")
        print(descripcion_generada)
        
        # 3. Búsqueda de sanciones
        sanciones = cargar_sanciones()
        resultados = buscar_sanciones(descripcion_generada, sanciones)
        mostrar_resultados(resultados)
