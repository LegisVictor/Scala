import os
import time

# Carpeta donde están los archivos HTML
ruta_entrada = (
    r"D:\Mis Documentos\Proyectos\ProcesoEditorial"
    r"\SCALA\Archivos\Produccion\Archivos\Html"
)

# Carpeta donde se guardarán los archivos SQL
ruta_salida = (
    r"D:\Mis Documentos\Proyectos\ProcesoEditorial"
    r"\SCALA\Archivos\Produccion\SQL\Sql"
)

# Tamaño máximo permitido por archivo: 100 MB
# Puedes aumentar este valor si tus HTML contienen imágenes en base64.
TAMANO_MAXIMO = 100 * 1024 * 1024

os.makedirs(ruta_salida, exist_ok=True)


def leer_archivo_por_bloques(
    ruta_archivo: str,
    encoding: str,
    tamano_bloque: int = 1024 * 1024
) -> str:
    """
    Lee un archivo de texto por bloques de 1 MB.
    """

    bloques = []

    with open(
        ruta_archivo,
        "r",
        encoding=encoding,
        errors="strict"
    ) as archivo:
        while True:
            bloque = archivo.read(tamano_bloque)

            if not bloque:
                break

            bloques.append(bloque)

    return "".join(bloques)


def leer_html(ruta_html: str) -> tuple[str, str]:
    """
    Intenta leer primero como UTF-8.
    Si falla, intenta con Windows-1252 y luego Latin-1.
    """

    codificaciones = ["utf-8", "cp1252", "latin-1"]

    ultimo_error = None

    for codificacion in codificaciones:
        try:
            contenido = leer_archivo_por_bloques(
                ruta_html,
                codificacion
            )

            return contenido, codificacion

        except UnicodeDecodeError as error:
            ultimo_error = error

    raise UnicodeDecodeError(
        ultimo_error.encoding,
        ultimo_error.object,
        ultimo_error.start,
        ultimo_error.end,
        f"No se pudo leer el archivo: {ruta_html}"
    )


archivos_html = sorted(
    archivo
    for archivo in os.listdir(ruta_entrada)
    if archivo.lower().endswith(".html")
)

print(f"Archivos HTML encontrados: {len(archivos_html)}")

generados = 0
errores = 0

for numero, archivo in enumerate(archivos_html, start=1):

    ruta_html = os.path.join(ruta_entrada, archivo)

    try:
        if not os.path.isfile(ruta_html):
            print(f"\n[{numero}/{len(archivos_html)}] Se omite: no es archivo")
            continue

        tamano_bytes = os.path.getsize(ruta_html)
        tamano_mb = tamano_bytes / (1024 * 1024)

        print(
            f"\n[{numero}/{len(archivos_html)}] "
            f"Procesando: {archivo}"
        )
        print(f"Tamaño: {tamano_mb:.2f} MB")

        if tamano_bytes > TAMANO_MAXIMO:
            print(
                f"OMITIDO: supera el límite de "
                f"{TAMANO_MAXIMO / (1024 * 1024):.0f} MB"
            )
            errores += 1
            continue

        inicio_lectura = time.perf_counter()

        contenido_html, codificacion = leer_html(ruta_html)

        tiempo_lectura = time.perf_counter() - inicio_lectura

        print(
            f"Lectura completada en {tiempo_lectura:.2f} segundos "
            f"usando {codificacion}"
        )

        # Escapar comillas simples para SQL
        contenido_html = contenido_html.replace("'", "''")

        nombre_base = os.path.splitext(archivo)[0]
        partes = nombre_base.split("_")

        if len(partes) < 2:
            raise ValueError(
                "El nombre del archivo debe contener al menos un guion bajo. "
                "Ejemplos: P2_bienvenida.html o 123_bienvenida.html"
            )

        if partes[0].isdigit():
            # Ejemplo: 123_bienvenida.html
            id_tarea = partes[0]
            base = "_".join(partes[1:]).lower()

            campo = (
                "MensajeRenovacion"
                if "renovacion" in base
                else "Mensaje"
            )

            query = f"""UPDATE TareaEnvioCorreo
SET {campo} = '{contenido_html}'
WHERE codfilial = 6
  AND Id_TareaEnvioCorreo = {id_tarea};
"""

        else:
            # Ejemplo: P2_bienvenida.html
            plantilla = partes[0].upper()
            base = "_".join(partes[1:]).lower()

            campo = (
                "MensajeRenovacion"
                if "renovacion" in base
                else "Mensaje"
            )

            query = f"""UPDATE TareaEnvioCorreo
SET {campo} = '{contenido_html}'
WHERE codfilial = 6
  AND PlantillaMail = '{plantilla}';
"""

        ruta_sql = os.path.join(
            ruta_salida,
            f"{nombre_base}.sql"
        )

        with open(
            ruta_sql,
            "w",
            encoding="utf-8",
            newline="\n"
        ) as archivo_sql:
            archivo_sql.write(query)

        generados += 1
        print(f"SQL generado: {ruta_sql}")

    except KeyboardInterrupt:
        print(f"\nProceso interrumpido mientras se procesaba: {archivo}")
        print(f"Ruta: {ruta_html}")
        raise

    except Exception as error:
        errores += 1
        print(f"ERROR procesando {archivo}: {error}")
        continue


print("\nProceso terminado")
print(f"SQL generados correctamente: {generados}")
print(f"Archivos con error u omitidos: {errores}")