import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import font as tkfont
from PIL import ImageTk, Image
import os
from app_modelo import clasificar_imagen, analizar_imagen, cargar_sanciones, buscar_sanciones

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
        self.widget.bind("<Enter>", self.showtip)
        self.widget.bind("<Leave>", self.hidetip)

    def showtip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                        background="#ffffe0", relief=tk.SOLID, 
                        borderwidth=1, font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador de Incidentes FIA")
        self.root.geometry("850x950")
        self.root.minsize(750, 850)
        
        # Variables de estado
        self.ruta_imagen = None
        self.dark_mode = False
        
        # Configurar fuente general
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(size=10)
        
        # Configurar estilos
        self.configure_styles()
        
        # Frame principal
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame para la imagen
        img_frame = ttk.LabelFrame(main_frame, text="Vista Previa", padding=(10, 5))
        img_frame.pack(fill=tk.X, pady=5)
        
        self.image_label = ttk.Label(img_frame, text="Imagen no cargada", 
                                  background='#f0f0f0', relief='sunken', 
                                  anchor='center', padding=10,
                                  font=('TkDefaultFont', 9, 'italic'))
        self.image_label.pack(fill=tk.BOTH, expand=True)
        
        # Frame para botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Botones
        self.load_button = ttk.Button(button_frame, text="📂 Seleccionar Imagen", 
                                    command=self.cargar_imagen, style='Accent.TButton')
        self.load_button.pack(side="left", padx=5, fill=tk.X, expand=True)
        
        self.analyze_button = ttk.Button(button_frame, text="🔎 Analizar Imagen", 
                                       command=self.analizar_imagen, state="disabled")
        self.analyze_button.pack(side="left", padx=5, fill=tk.X, expand=True)
        
        self.reset_button = ttk.Button(button_frame, text="🔄 Reiniciar", 
                                     command=self.reiniciar_app)
        self.reset_button.pack(side="left", padx=5, fill=tk.X, expand=True)
        
        # Botón tema oscuro
        self.theme_button = ttk.Button(button_frame, text="🌙 Tema Oscuro", 
                                     command=self.toggle_dark_mode)
        self.theme_button.pack(side="left", padx=5, fill=tk.X, expand=True)
        
        # Tooltips para botones
        ToolTip(self.load_button, "Selecciona una imagen de un incidente en pista")
        ToolTip(self.analyze_button, "Analiza la imagen para detectar posibles infracciones")
        ToolTip(self.reset_button, "Reinicia la aplicación al estado inicial")
        ToolTip(self.theme_button, "Cambiar entre tema claro y oscuro")
        
        # Resultados de clasificación
        self.resultado_clasificacion = ttk.Label(main_frame, text="", 
                                               font=('TkDefaultFont', 10, 'bold'),
                                               foreground='#2c3e50',
                                               wraplength=600, justify="left")
        self.resultado_clasificacion.pack(fill=tk.X, pady=5)
        
        # Frame para descripción técnica
        desc_frame = ttk.LabelFrame(main_frame, text="📝 Descripción Técnica", padding=(10, 5))
        desc_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.descripcion_text = tk.Text(desc_frame, height=10, wrap="word", 
                                      font=('TkDefaultFont', 9),
                                      padx=5, pady=5)
        self.descripcion_text.pack(fill=tk.BOTH, expand=True)
        
        scroll_desc = ttk.Scrollbar(desc_frame, command=self.descripcion_text.yview)
        scroll_desc.pack(side=tk.RIGHT, fill=tk.Y)
        self.descripcion_text.config(yscrollcommand=scroll_desc.set)
        
        # Frame para sanción
        sancion_frame = ttk.LabelFrame(main_frame, text="⚖️ Resultado de Sanción", 
                                      padding=(10, 5))
        sancion_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.sancion_text = tk.Text(sancion_frame, height=14, wrap="word", 
                                  font=('TkDefaultFont', 9),
                                  padx=5, pady=5)
        self.sancion_text.pack(fill=tk.BOTH, expand=True)
        
        scroll_sancion = ttk.Scrollbar(sancion_frame, command=self.sancion_text.yview)
        scroll_sancion.pack(side=tk.RIGHT, fill=tk.Y)
        self.sancion_text.config(yscrollcommand=scroll_sancion.set)
        
        # Configurar tags para texto con estilo
        for text_widget in [self.descripcion_text, self.sancion_text]:
            text_widget.tag_configure('title', font=('TkDefaultFont', 10, 'bold'))
            text_widget.tag_configure('highlight', foreground='#e74c3c')
            text_widget.tag_configure('success', foreground='#27ae60')
            text_widget.tag_configure('warning', foreground='#f39c12')
        
        # Barra de estado
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(root, textvariable=self.status_var, 
                                  relief='sunken', anchor='w',
                                  style='Status.TLabel')
        self.status_bar.pack(fill=tk.X)
        
        # Barra de progreso (inicialmente oculta)
        self.progress = ttk.Progressbar(root, mode='indeterminate')
    
    def configure_styles(self):
        """Configura estilos personalizados para los widgets"""
        style = ttk.Style()
        
        # Estilo para botón principal
        style.configure('Accent.TButton', 
                      foreground='white', 
                      background='#3498db',
                      font=('TkDefaultFont', 10, 'bold'),
                      padding=5)
        style.map('Accent.TButton',
                background=[('active', '#2980b9'), ('disabled', '#bdc3c7')])
        
        # Estilo para los LabelFrame
        style.configure('TLabelframe', 
                      background=self.root.cget('background'),
                      bordercolor='#bdc3c7')
        style.configure('TLabelframe.Label', 
                      foreground='#2c3e50',
                      font=('TkDefaultFont', 10, 'bold'))
        
        # Estilo para la barra de estado
        style.configure('Status.TLabel', 
                      background='#ecf0f1',
                      foreground='#7f8c8d',
                      font=('TkDefaultFont', 8))
        
        # Estilo para tema oscuro
        style.configure('Dark.TFrame', background='#2c3e50')
        style.configure('Dark.TLabelframe', background='#34495e', bordercolor='#7f8c8d')
        style.configure('Dark.TLabelframe.Label', foreground='#ecf0f1')
        style.configure('Dark.TLabel', background='#2c3e50', foreground='#ecf0f1')
        style.configure('DarkStatus.TLabel', background='#34495e', foreground='#bdc3c7')
    
    def cargar_imagen(self):
        ruta = filedialog.askopenfilename(
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.bmp"),
                      ("Todos los archivos", "*.*")],
            title="Seleccionar imagen de incidente"
        )
        if not ruta:
            return

        self.reiniciar_app()
        self.ruta_imagen = ruta
        self.status_var.set(f"Cargando imagen: {os.path.basename(ruta)}")
        self.root.update()
        
        try:
            img = Image.open(ruta)
            
            # Redimensionar manteniendo aspecto
            max_size = (400, 400)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Crear imagen con borde
            bordered_img = Image.new('RGB', 
                                   (img.width + 20, img.height + 20), 
                                   '#ecf0f1' if not self.dark_mode else '#34495e')
            bordered_img.paste(img, (10, 10))
            
            self.img_tk = ImageTk.PhotoImage(bordered_img)
            self.image_label.config(
                image=self.img_tk, 
                text="",
                background='#f0f0f0' if not self.dark_mode else '#34495e'
            )
            self.image_label.image = self.img_tk

            self.analyze_button.config(state="normal")
            self.status_var.set(f"Imagen cargada: {os.path.basename(ruta)} - Lista para analizar")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen:\n{str(e)}")
            self.status_var.set("Error al cargar la imagen")
    
    def analizar_imagen(self):
        if not self.ruta_imagen:
            messagebox.showwarning("Advertencia", "Primero selecciona una imagen.")
            return

        try:
            # Mostrar progreso
            self.progress.pack(fill=tk.X)
            self.progress.start(10)
            self.analyze_button.config(state="disabled")
            self.status_var.set("Analizando imagen...")
            self.root.update()
            
            mensaje_clasificacion, categoria = clasificar_imagen(self.ruta_imagen)
            self.resultado_clasificacion.config(
                text=f"📊 Clasificación: {mensaje_clasificacion}",
                foreground='#e74c3c' if categoria == "con_sancion" else '#27ae60'
            )
            
            # Limpiar textos anteriores
            self.descripcion_text.delete("1.0", tk.END)
            self.sancion_text.delete("1.0", tk.END)
            
            if categoria == "sin_sancion":
                self.descripcion_text.insert(tk.END, "✅ No se requiere análisis adicional.", 'success')
                self.sancion_text.insert(tk.END, "✅ Ninguna sanción aplicable.", 'success')
                self.status_var.set("Análisis completado - No se detectaron infracciones")
                return
            
            # Mostrar ventana de carga
            self.show_loading()
            
            descripcion = analizar_imagen(self.ruta_imagen)
            self.descripcion_text.insert(tk.END, descripcion)
            
            sanciones = cargar_sanciones()
            resultados = buscar_sanciones(descripcion, sanciones)
            
            if resultados:
                mejor = resultados[0]
                md = mejor["metadata"]

                texto = f"""⚖️ Sanción Recomendada: {md['penalizacion']}\n
📜 Artículo: {md['articulo']} ({md['gravedad']}) – {md['tipo']} / {md['subtipo']}\n
📌 Aplicación: {md['aplicacion']}\n\n
📝 Descripción:\n{mejor['text']}\n\n
🔍 Palabras clave detectadas:\n• {'\n• '.join(md['palabras_clave'][:3])}\n\n
📚 Ejemplos aplicables:\n- {'\n- '.join(md['ejemplos'][:2])}
"""
                self.sancion_text.insert(tk.END, texto)
                self.sancion_text.tag_add('title', '1.0', '1.end')
                self.sancion_text.tag_add('highlight', '2.0', '2.end')
                self.status_var.set(f"Análisis completado - Sanción recomendada: {md['penalizacion']}")
            else:
                self.sancion_text.insert(tk.END, "✅ No se encontraron infracciones aplicables.", 'success')
                self.status_var.set("Análisis completado - No se encontraron infracciones aplicables")

        except Exception as e:
            messagebox.showerror("Error", f"Error durante el análisis:\n{str(e)}")
            self.status_var.set(f"Error durante el análisis: {str(e)}")
        finally:
            self.progress.stop()
            self.progress.pack_forget()
            if hasattr(self, 'loading'):
                self.loading.destroy()
    
    def show_loading(self):
        """Muestra ventana de carga durante operaciones largas"""
        self.loading = tk.Toplevel(self.root)
        self.loading.title("Procesando")
        self.loading.geometry("300x100")
        self.loading.resizable(False, False)
        
        # Centrar la ventana
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 150
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 50
        self.loading.geometry(f"+{x}+{y}")
        
        ttk.Label(self.loading, text="Analizando imagen...").pack(pady=10)
        ttk.Progressbar(self.loading, mode='indeterminate').pack(fill=tk.X, padx=20)
        
        self.loading.transient(self.root)
        self.loading.grab_set()
        self.root.update()
    
    def toggle_dark_mode(self):
        """Cambia entre tema claro y oscuro"""
        self.dark_mode = not self.dark_mode
        
        if self.dark_mode:
            bg = '#2c3e50'
            fg = '#ecf0f1'
            widget_bg = '#34495e'
            self.theme_button.config(text="☀️ Tema Claro")
            style = 'Dark.TFrame'
            label_style = 'Dark.TLabel'
            status_style = 'DarkStatus.TLabel'
        else:
            bg = '#ecf0f1'
            fg = '#2c3e50'
            widget_bg = '#f0f0f0'
            self.theme_button.config(text="🌙 Tema Oscuro")
            style = 'TFrame'
            label_style = 'TLabel'
            status_style = 'Status.TLabel'
        
        # Configurar colores de fondo
        self.root.configure(background=bg)
        
        # Actualizar widgets
        widgets = [
            self.image_label, self.resultado_clasificacion,
            self.descripcion_text, self.sancion_text
        ]
        
        for widget in widgets:
            if isinstance(widget, tk.Text):
                widget.configure(
                    background=widget_bg, 
                    foreground=fg,
                    insertbackground=fg
                )
            else:
                widget.configure(background=widget_bg, foreground=fg)
        
        # Actualizar estilo de los frames
        for frame in self.root.winfo_children():
            if isinstance(frame, ttk.Frame) or isinstance(frame, ttk.LabelFrame):
                frame.configure(style=style)
        
        # Actualizar barra de estado
        self.status_bar.configure(style=status_style)
        
        # Si hay una imagen cargada, actualizar su fondo
        if hasattr(self, 'img_tk'):
            self.image_label.configure(background=widget_bg)
    
    def reiniciar_app(self):
        """Reinicia la aplicación al estado inicial"""
        self.image_label.config(
            image="", 
            text="Imagen no cargada",
            background='#f0f0f0' if not self.dark_mode else '#34495e'
        )
        self.image_label.image = None
        self.resultado_clasificacion.config(text="")
        self.descripcion_text.delete("1.0", tk.END)
        self.sancion_text.delete("1.0", tk.END)
        self.analyze_button.config(state="disabled")
        self.ruta_imagen = None
        self.status_var.set("Listo")
        
        if hasattr(self, 'progress'):
            self.progress.stop()
            self.progress.pack_forget()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()