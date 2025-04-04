import cv2
import os

def main(video_path, output_folder):
    # Crear la carpeta de salida si no existe
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    cap = cv2.VideoCapture(video_path)
    frame_number = 0
    saved_count = 0
    auto_play = False
    speed = 1  # Factor de velocidad (1x por defecto)
    
    while cap.isOpened():
        
        ret, frame = cap.read()
        if not ret:
            print("Fin del video o error al leer.")
            break
        
        cv2.imshow("Frame", frame)

        if auto_play:
            key = cv2.waitKey(30 // speed)  # Ajustar velocidad de reproducción
            frame_number += 1  # Avanzar automáticamente en modo auto-play
        else:
            key = cv2.waitKey(0)  # Esperar una tecla
        
        if key == ord('s'):  # Guardar el frame si se presiona 's'
            frame_filename = os.path.join(output_folder, f"frame_silverstone_{frame_number}.jpg")
            cv2.imwrite(frame_filename, frame)
            print(f"Captura guardada: {frame_filename}")
            saved_count += 1
        elif key == ord('q'):  # Salir si se presiona 'q'
            print("Saliendo...")
            break
        elif key == ord('a'):  # Activar/desactivar auto-play
            auto_play = not auto_play
            print("Auto-play activado" if auto_play else "Auto-play desactivado")
        elif key == ord('x'):  # Duplicar la velocidad
            speed = 6 if speed == 1 else 1
            print("Velocidad x2 activada" if speed == 6 else "Velocidad normal activada")
        elif key == ord('b'):  # Retroceder un frame
            frame_number = max(0, frame_number - 1)  # Retrocede un frame
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)  # Fijar el frame antes de la siguiente lectura
            print(f"Retrocediendo al frame {frame_number}")
        elif key == ord('d'):  # Avanzar un frame manualmente
            frame_number += 1
            print(f"Avanzando al frame {frame_number}")
        elif key == ord('m'):  # Ir a un minuto específico
            try:
                minuto = int(input("Ingrese el minuto al que desea avanzar: "))
                segundo = int(input("Ingrese el segundo al que desea avanzar: "))
                tiempo_ms = (minuto * 60 + segundo) * 1000  # Convertir a milisegundos
                cap.set(cv2.CAP_PROP_POS_MSEC, tiempo_ms)
                print(f"Saltando a {minuto}:{segundo}")
            except ValueError:
                print("Entrada inválida. Introduzca valores numéricos.")

    cap.release()
    cv2.destroyAllWindows()
    print(f"Total de capturas guardadas: {saved_count}")

if __name__ == "__main__":
    video_path = "/home/daniel/Escritorio/Programación de IA/Proyecto/videos/Verstappen & Hamilton Collide At Silverstone _ 2021 British Grand Prix.mp4" 
    #video_path = "/home/daniel/Escritorio/Programación de IA/Proyecto/videos/F1 Mercedes Onboard Crashes.mp4"  # Ruta del video
    output_folder = "accidentes"  # Carpeta donde se guardarán las capturas
    main(video_path, output_folder)