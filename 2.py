# 2

from ultralytics import YOLO

# Cargar el modelo entrenado
model = YOLO('/home/daniel/Escritorio/Programación de IA/Proyecto/runs/detect/F1/weights/best.pt')

# Realizar detecciones en un video
results = model.predict(
    source='/home/daniel/Escritorio/Programación de IA/Proyecto/videos/F1 2009 Onboard Crashes.mp4',  # Video en el que probar el modelo
    conf=0.5,                      # Umbral de confianza
    save=True                      # Guardar los resultados en una carpeta
)

print("Detección completa. Resultados guardados en:", results)
