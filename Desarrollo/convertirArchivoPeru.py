import os

# Ruta de entrada (donde están los .html) carpeta origen
ruta_entrada = r'D:\Mis Documentos\Proyectos\ProcesoEditorial\SCALA\Archivos\Produccion\Archivos\Html Peru'   

# Ruta de salida (donde se guardarán los .sql) carpeta destino
ruta_salida = r'D:\Mis Documentos\Proyectos\ProcesoEditorial\SCALA\Archivos\Produccion\SQL\Sql Peru'    

# Crear la carpeta de salida si no existe
os.makedirs(ruta_salida, exist_ok=True)

# Recorrer los archivos HTML
for archivo in os.listdir(ruta_entrada):
    if archivo.endswith(".html"):
        ruta_html = os.path.join(ruta_entrada, archivo)
        
        try:
            with open(ruta_html, 'r', encoding='utf-8') as f:
                contenido_html = f.read()
        except UnicodeDecodeError:
            with open(ruta_html, 'r', encoding='latin-1') as f:
               contenido_html = f.read()
            print(f" error : {ruta_html}")

        # Extraer nombre base y plantilla
        nombre_base = os.path.splitext(archivo)[0]
        partes = nombre_base.split("_")

        if partes[0].isdigit():
            # Caso con Id_TareaEnvioCorreo
            id_tarea = partes[0]
            base = partes[1].lower()
            campo = 'MensajeRenovacion' if 'renovacion' in base else 'Mensaje'

            query = f"""UPDATE TareaEnvioCorreo
            SET {campo} = '{contenido_html}'
            WHERE codfilial = 91 AND Id_TareaEnvioCorreo = {id_tarea};"""

        else:
            base = partes[1].lower()
            plantilla = partes[0].upper()

            # Elegir campo correcto
            campo = 'MensajeRenovacion' if 'renovacion' in base else 'Mensaje'

            # Generar el query
            query = f"""UPDATE TareaEnvioCorreo
                        SET {campo} = '{contenido_html}'
                        WHERE codfilial = 91 AND PlantillaMail = '{plantilla}';"""

        # Ruta del archivo de salida
        ruta_sql = os.path.join(ruta_salida, f"{nombre_base}.sql")
        with open(ruta_sql, 'w', encoding='utf-8') as f_sql:
            f_sql.write(query)

        print(f"SQL generado: {ruta_sql}")
