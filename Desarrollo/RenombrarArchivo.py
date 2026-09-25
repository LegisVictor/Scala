import os

# Ruta de la carpeta donde están los archivos a renombrar
ruta = r'D:\Mis Documentos\Proyectos\ProcesoEditorial\SCALA\Archivos\20250507\SQL\Sql'  # <- ajusta tu ruta aquí

# Recorre los archivos en la carpeta
for archivo in os.listdir(ruta):
    ruta_actual = os.path.join(ruta, archivo)

    if os.path.isfile(ruta_actual) and '-' in archivo:
        nuevo_nombre = archivo.replace('-', '_')
        ruta_nueva = os.path.join(ruta, nuevo_nombre)

        os.rename(ruta_actual, ruta_nueva)
        print(f'Renombrado: {archivo} -> {nuevo_nombre}')
