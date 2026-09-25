import tkinter as tk
from tkinter import filedialog, messagebox
import win32com.client
from pathlib import Path
import traceback

def obtener_asunto_desde_archivo(archivo):
    return Path(archivo).name

def leer_html(archivo):
    errores = []
    for encoding in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            with open(archivo, "r", encoding=encoding) as f:
                return f.read(), encoding
        except UnicodeDecodeError as error:
            errores.append(f"{encoding}: {error}")

    detalle = "\n".join(errores) or "No se obtuvo detalle del error."
    raise RuntimeError(
        "No se pudo leer con utf-8, utf-8-sig, cp1252 ni latin-1.\n" + detalle
    )

def mostrar_error_outlook(error):
    detalle = traceback.format_exc()
    texto_error = str(error).lower()

    if "cuadro de di" in texto_error or "dialog" in texto_error:
        messagebox.showerror(
            "Outlook esta ocupado",
            "Outlook tiene un cuadro de dialogo abierto y no permite crear o mostrar el correo.\n\n"
            "Cierra cualquier ventana, alerta o cuadro de dialogo abierto en Outlook y vuelve a intentarlo.\n\n"
            "Detalle tecnico:\n" + detalle
        )
        return

    messagebox.showerror(
        "Error al abrir Outlook",
        "No se pudo crear o mostrar el correo en Outlook.\n\n" + detalle
    )

def seleccionar_archivo():
    archivo = filedialog.askopenfilename(
        title="Seleccionar plantilla HTML",
        initialdir=r"D:\Mis Documentos\Proyectos\ProcesoEditorial\SCALA\Archivos\Produccion\Archivos\Html",
        filetypes=[("Archivos HTML", "*.html *.htm")]
    )
    if archivo:
        entrada_archivo.delete(0, tk.END)
        entrada_archivo.insert(0, archivo)
        entrada_asunto.delete(0, tk.END)
        entrada_asunto.insert(0, obtener_asunto_desde_archivo(archivo))

def abrir_en_outlook():
    archivo = entrada_archivo.get().strip()
    correo_destino = entrada_correo.get().strip()

    if not archivo:
        messagebox.showwarning("Validacion", "Selecciona una plantilla HTML.")
        return

    if not Path(archivo).exists():
        messagebox.showerror("Error", "El archivo HTML no existe.")
        return

    try:
        html, encoding_usado = leer_html(archivo)
    except Exception:
        messagebox.showerror(
            "Error al leer la plantilla",
            "No se pudo leer el archivo HTML.\n\n" + traceback.format_exc()
        )
        return

    asunto = obtener_asunto_desde_archivo(archivo)
    entrada_asunto.delete(0, tk.END)
    entrada_asunto.insert(0, asunto)
    ventana.title(f"Probar plantilla HTML en Outlook - {encoding_usado}")

    try:
        outlook = win32com.client.Dispatch("Outlook.Application")
        mail = outlook.CreateItem(0)

        mail.To = correo_destino
        mail.Subject = asunto
        mail.HTMLBody = html

        mail.Display()
    except Exception as error:
        mostrar_error_outlook(error)

ventana = tk.Tk()
ventana.title("Probar plantilla HTML en Outlook")
ventana.geometry("650x220")

tk.Label(ventana, text="Plantilla HTML:").pack(anchor="w", padx=10, pady=(10, 0))

frame_archivo = tk.Frame(ventana)
frame_archivo.pack(fill="x", padx=10)

entrada_archivo = tk.Entry(frame_archivo)
entrada_archivo.pack(side="left", fill="x", expand=True)

tk.Button(frame_archivo, text="Buscar", command=seleccionar_archivo).pack(side="left", padx=5)

tk.Label(ventana, text="Correo destino:").pack(anchor="w", padx=10, pady=(10, 0))
entrada_correo = tk.Entry(ventana)
entrada_correo.pack(fill="x", padx=10)
entrada_correo.insert(0, "victor.garcia@legis.com.co")

tk.Label(ventana, text="Asunto:").pack(anchor="w", padx=10, pady=(10, 0))
entrada_asunto = tk.Entry(ventana)
entrada_asunto.pack(fill="x", padx=10)
entrada_asunto.insert(0, "Selecciona una plantilla HTML")

tk.Button(
    ventana,
    text="Abrir en Outlook",
    command=abrir_en_outlook,
    height=2
).pack(pady=15)

ventana.mainloop()
