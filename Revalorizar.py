import json

def cargar_y_crear_matriz(ruta_archivo_json):
    """
    Carga el archivo JSON y crea una matriz de nombre y valoración.
    La matriz será una lista de diccionarios, donde cada diccionario
    contiene 'nombre', 'valoracion_original' y un índice.
    Ahora, busca la valoración y el ranking directamente en el nivel superior del alojamiento,
    o en 'detallesAdicionales' si no están en el nivel superior.
    """
    try:
        with open(ruta_archivo_json, 'r', encoding='utf-8') as f:
            datos_json = json.load(f)
    except FileNotFoundError:
        print(f"Error: El archivo '{ruta_archivo_json}' no fue encontrado.")
        return None, None
    except json.JSONDecodeError:
        print(f"Error: El archivo '{ruta_archivo_json}' no es un JSON válido.")
        return None, None

    matriz_valoraciones = []
    if "alojamientos" in datos_json:
        for i, alojamiento in enumerate(datos_json["alojamientos"]):
            nombre = alojamiento.get("nombre", "Nombre Desconocido")
            
            # Intenta obtener la valoración directamente del nivel del alojamiento
            valoracion = alojamiento.get("valoracion") 
            ranking_existente = alojamiento.get("ranking")

            # Si no está en el nivel superior, busca en 'detallesAdicionales'
            if valoracion is None and "detallesAdicionales" in alojamiento:
                valoracion_da = alojamiento["detallesAdicionales"].get("valoracion")
                if valoracion_da is not None:
                    valoracion = valoracion_da
            
            if ranking_existente is None and "detallesAdicionales" in alojamiento:
                ranking_da = alojamiento["detallesAdicionales"].get("ranking")
                if ranking_da is not None:
                    ranking_existente = ranking_da

            # Asegura que valoracion sea numérica, por defecto 0.0
            try:
                valoracion = float(valoracion) if valoracion is not None else 0.0
            except ValueError:
                valoracion = 0.0

            # Asegura que ranking_existente sea un número entero, por defecto None o 0
            try:
                ranking_existente = int(ranking_existente) if ranking_existente is not None else None
            except ValueError:
                ranking_existente = None


            matriz_valoraciones.append({
                "indice_json": i, # Guardamos el índice para facilitar la actualización
                "nombre": nombre,
                "valoracion_original": valoracion, # Guardamos la original para referencia
                "valoracion_actualizada": valoracion, # Esta es la que editarás
                "ranking_actualizado": ranking_existente # Se usará para el nuevo ranking
            })
    return matriz_valoraciones, datos_json

def mostrar_y_editar_matriz(matriz):
    """
    Muestra la matriz y permite al usuario editar las valoraciones.
    La matriz se ordena por valoración_actualizada (descendente) antes de mostrarse.
    """
    if not matriz:
        print("La matriz está vacía. No hay datos para editar.")
        return

    # Ordenar la matriz por 'valoracion_actualizada' en orden descendente para la visualización inicial
    matriz.sort(key=lambda x: float(x.get('valoracion_actualizada', 0)), reverse=False)


    print("\n--- Matriz de Alojamientos y Valoraciones (Ordenado por Valoración) ---")
    for i, item in enumerate(matriz):
        print(f"{i}. Nombre: {item['nombre']} | Valoración Actual: {item['valoracion_actualizada']}")

    print("\nPara editar, ingresa el número del alojamiento *como se muestra en esta lista* y el nuevo valor (ej: '0 4.5').")
    print("Para terminar la edición, escribe 'fin'.")
    print("Nota: La edición se aplica a la lista mostrada, no al orden original del JSON.")

    while True:
        entrada = input("Tu edición (ej: '0 4.5') o 'fin': ").strip()
        if entrada.lower() == 'fin':
            break

        partes = entrada.split()
        if len(partes) == 2:
            try:
                indice_mostrado = int(partes[0]) 
                nueva_valoracion = float(partes[1])

                if 0 <= indice_mostrado < len(matriz):
                    matriz[indice_mostrado]["valoracion_actualizada"] = nueva_valoracion
                    print(f"'{matriz[indice_mostrado]['nombre']}' actualizado a {nueva_valoracion}.")
                else:
                    print("Índice fuera de rango. Intenta de nuevo.")
            except ValueError:
                print("Entrada inválida. Asegúrate de usar el formato 'NUMERO VALOR' (ej: '0 4.5').")
        else:
            print("Formato incorrecto. Usa 'NUMERO VALOR' o 'fin'.")

def volcar_modificaciones(ruta_archivo_json, matriz_modificada, datos_json_original):
    """
    Vuelca las valoraciones modificadas de vuelta al archivo JSON original.
    Ahora, la valoración y el ranking se guardan directamente en el nivel superior del alojamiento.
    El ranking se reasigna después de ordenar la matriz por valoración de menor a mayor.
    """
    if not matriz_modificada:
        print("No hay modificaciones para volcar.")
        return

    # 1. Ordenar la matriz_modificada por 'valoracion_actualizada' de MENOR a MAYOR
    matriz_modificada.sort(key=lambda x: float(x.get('valoracion_actualizada', 0)), reverse=True)

    # 2. Reasignar el ranking entero empezando por 1
    for i, item in enumerate(matriz_modificada):
        item["ranking_actualizado"] = i + 1

    # 3. Volcar las modificaciones al JSON original usando el 'indice_json'
    for item in matriz_modificada:
        original_index = item["indice_json"]
        nueva_valoracion = item["valoracion_actualizada"]
        nuevo_ranking = item["ranking_actualizado"]
        
        if "alojamientos" in datos_json_original and original_index < len(datos_json_original["alojamientos"]):
            alojamiento = datos_json_original["alojamientos"][original_index]
            
            # Establecer la valoración y el ranking directamente en el nivel superior del alojamiento
            alojamiento["valoracion"] = nuevo_ranking *10
            
            # Opcional: Si la valoración o el ranking existían en detallesAdicionales, elimínalos de allí
            if "detallesAdicionales" in alojamiento:
                if "valoracion" in alojamiento["detallesAdicionales"]:
                    del alojamiento["detallesAdicionales"]["valoracion"]
                if "ranking" in alojamiento["detallesAdicionales"]:
                    del alojamiento["detallesAdicionales"]["ranking"]
                
                # Si detallesAdicionales queda vacío después de esto, puedes eliminarlo
                if not alojamiento["detallesAdicionales"]:
                   del alojamiento["detallesAdicionales"]
    
    try:
        with open(ruta_archivo_json, 'w', encoding='utf-8') as f:
            json.dump(datos_json_original, f, indent=2, ensure_ascii=False)
        print(f"\n¡Archivo '{ruta_archivo_json}' actualizado con éxito!")
    except IOError as e:
        print(f"Error al escribir en el archivo '{ruta_archivo_json}': {e}")

# --- Cómo usar el script ---
if __name__ == "__main__":
    nombre_archivo = "alojamientos.json" # Asegúrate de que tu JSON se llame así o cambia el nombre aquí

    # 1. Cargar el JSON y crear la matriz
    matriz_alojamientos, datos_originales_json = cargar_y_crear_matriz(nombre_archivo)

    if matriz_alojamientos is not None:
        # 2. Mostrar y editar la matriz
        mostrar_y_editar_matriz(matriz_alojamientos)

        # 3. Volcar las modificaciones al JSON (esto también asigna el nuevo ranking)
        volcar_modificaciones(nombre_archivo, matriz_alojamientos, datos_originales_json)
        