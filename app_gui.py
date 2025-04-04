import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import ImageTk, Image
import os

# Asegúrate de que estos import sean válidos según cómo tengas dividido tu código
from app_modelo import clasificar_imagen, analizar_imagen, cargar_sanciones, buscar_sanciones


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador de Incidentes FIA")

        self.ruta_imagen = None

        self.image_label = tk.Label(root, text="Imagen no cargada")
        self.image_label.pack()

        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        self.load_button = tk.Button(button_frame, text="📂 Seleccionar Imagen", command=self.cargar_imagen)
        self.load_button.pack(side="left", padx=5)

        self.analyze_button = tk.Button(button_frame, text="🔎 Analizar Imagen", command=self.analizar_imagen, state="disabled")
        self.analyze_button.pack(side="left", padx=5)

        self.reset_button = tk.Button(button_frame, text="🔄 Reiniciar", command=self.reiniciar_app)
        self.reset_button.pack(side="left", padx=5)

        self.resultado_clasificacion = tk.Label(root, text="", fg="blue", wraplength=600, justify="left")
        self.resultado_clasificacion.pack(pady=5)

        tk.Label(root, text="📝 Descripción Técnica:").pack()
        self.descripcion_text = tk.Text(root, height=10, width=80, wrap="word")
        self.descripcion_text.pack(pady=5)

        tk.Label(root, text="⚖️ Resultado de Sanción:").pack()
        self.sancion_text = tk.Text(root, height=14, width=80, wrap="word")
        self.sancion_text.pack(pady=5)

    def cargar_imagen(self):
        ruta = filedialog.askopenfilename(filetypes=[("Imágenes", "*.jpg *.png")])
        if not ruta:
            return

        self.reiniciar_app()
        self.ruta_imagen = ruta
        try:
            img = Image.open(ruta)
            img.thumbnail((300, 300))
            self.img_tk = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.img_tk, text="")
            self.image_label.image = self.img_tk

            self.analyze_button.config(state="normal")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen:\n{str(e)}")

    def analizar_imagen(self):
        if not self.ruta_imagen:
            messagebox.showwarning("Advertencia", "Primero selecciona una imagen.")
            return

        try:
            self.analyze_button.config(state="disabled")

            mensaje_clasificacion, categoria = clasificar_imagen(self.ruta_imagen)
            self.resultado_clasificacion.config(text=f"📊 Clasificación: {mensaje_clasificacion}")

            if categoria == "sin_sancion":
                self.descripcion_text.insert(tk.END, "✅ No se requiere análisis adicional.")
                self.sancion_text.insert(tk.END, "✅ Ninguna sanción aplicable.")
                return

            descripcion = analizar_imagen(self.ruta_imagen)
            self.descripcion_text.insert(tk.END, descripcion)

            sanciones = cargar_sanciones()
            resultados = buscar_sanciones(descripcion, sanciones)

            if resultados:
                mejor = resultados[0]
                md = mejor["metadata"]

                texto = f"""⚖️ Sanción Recomendada: {md['penalizacion']}
📜 Artículo: {md['articulo']} ({md['gravedad']}) – {md['tipo']} / {md['subtipo']}
📌 Aplicación: {md['aplicacion']}

📝 Descripción:
{mejor['text']}

🔍 Palabras clave detectadas:
• {chr(10) + '• '.join(md['palabras_clave'][:3])}

📚 Ejemplos aplicables:
- {chr(10) + '- '.join(md['ejemplos'][:2])}
"""
            else:
                texto = "✅ No se encontraron infracciones aplicables."

            self.sancion_text.insert(tk.END, texto)

        except Exception as e:
            messagebox.showerror("Error", f"Error durante el análisis:\n{str(e)}")

    def reiniciar_app(self):
        self.image_label.config(image="", text="Imagen no cargada")
        self.image_label.image = None
        self.resultado_clasificacion.config(text="")
        self.descripcion_text.delete("1.0", tk.END)
        self.sancion_text.delete("1.0", tk.END)
        self.analyze_button.config(state="disabled")
        self.ruta_imagen = None


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
