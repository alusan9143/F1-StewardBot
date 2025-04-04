import cv2
import random
import os

def extraer_frames_video(video_path, video_index, num_frames=10, output_dir="frames"):
    """
    Extrae num_frames aleatorios de un video y los guarda en output_dir.
    El nombre de cada imagen será: videox_framey.jpg, donde x es el índice del video y y el número del frame.
    """
    # Crear carpeta de salida si no existe
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: No se pudo abrir el video {video_path}")
        return
    
    # Obtener el número total de frames del video
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames == 0:
        print(f"Error: El video {video_path} no contiene frames.")
        return

    # Si el video tiene menos frames de los que queremos extraer, se ajusta el número
    if total_frames < num_frames:
        print(f"El video {video_path} solo tiene {total_frames} frames. Se extraerán todos.")
        num_frames = total_frames

    # Seleccionar índices aleatorios y ordenarlos
    indices_aleatorios = sorted(random.sample(range(total_frames), num_frames))
    
    frame_counter = 1
    for idx in indices_aleatorios:
        # Posicionar el video en el frame deseado
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret:
            print(f"No se pudo leer el frame en el índice {idx} del video {video_path}.")
            continue

        # Nombre de la imagen: videox_framey.jpg
        filename = f"video{video_index}_frame{frame_counter}.jpg"
        output_path = os.path.join(output_dir, filename)
        cv2.imwrite(output_path, frame)
        print(f"Guardado {output_path}")
        frame_counter += 1
    
    cap.release()

def extraer_frames_de_carpeta(folder_path, num_frames=20, output_dir="frames"):
    """
    Recorre la carpeta especificada, busca archivos .mp4 y extrae num_frames de cada uno.
    """
    # Listar archivos que terminen con .mp4 (sin distinguir mayúsculas y minúsculas)
    archivos = [f for f in os.listdir(folder_path) if f.lower().endswith(".mp4")]
    if not archivos:
        print("No se encontraron archivos .mp4 en la carpeta.")
        return

    video_index = 1
    for archivo in archivos:
        video_path = os.path.join(folder_path, archivo)
        print(f"\nProcesando {video_path}...")
        extraer_frames_video(video_path, video_index, num_frames, output_dir)
        video_index += 1

if __name__ == "__main__":
    folder_path = input("Ingresa la ruta de la carpeta: ")
    extraer_frames_de_carpeta(folder_path)
