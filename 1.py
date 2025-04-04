# 1

from ultralytics import YOLO

# Cargar el modelo preentrenado
model = YOLO('yolov8n.pt')  # Usa un modelo ligero (n) para empezar. También puedes usar 'yolov8s.pt' o 'yolov8m.pt'

# Entrenar el modelo
model.train(
    data='/home/daniel/Escritorio/Programación de IA/Proyecto/dataset/data.yaml',  # Archivo de configuración de tus datos
    epochs=50,                         # Número de épocas
    imgsz=640,                         # Tamaño de las imágenes
    batch=8,                           # Tamaño del batch
    name='F1'                # Nombre del experimento
)

# Validar el modelo
metrics = model.val()
print(metrics)