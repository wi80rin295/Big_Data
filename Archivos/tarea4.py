#importamos lirerias necesarias
import pandas as pd
import requests

# URL del dataset en formato JSON proporcionado (Socrata API)
url = "https://www.datos.gov.co/resource/ugc5-acjp.json?$query=SELECT%0A%20%20%60depa_nombre%60%2C%0A%20%20%60muni_nombre%60%2C%0A%20%20%60codigo_habilitacion%60%2C%0A%20%20%60nombre_prestador%60%2C%0A%20%20%60tido_codigo%60%2C%0A%20%20%60nits_nit%60%2C%0A%20%20%60razon_social%60%2C%0A%20%20%60clpr_codigo%60%2C%0A%20%20%60clpr_nombre%60%2C%0A%20%20%60ese%60%2C%0A%20%20%60direccion%60%2C%0A%20%20%60telefono%60%2C%0A%20%20%60fax%60%2C%0A%20%20%60email%60%2C%0A%20%20%60gerente%60%2C%0A%20%20%60nivel%60%2C%0A%20%20%60caracter%60%2C%0A%20%20%60habilitado%60%2C%0A%20%20%60fecha_radicacion%60%2C%0A%20%20%60fecha_vencimiento%60%2C%0A%20%20%60fecha_cierre%60%2C%0A%20%20%60dv%60%2C%0A%20%20%60clase_persona%60%2C%0A%20%20%60naju_codigo%60%2C%0A%20%20%60naju_nombre%60%2C%0A%20%20%60numero_sede_principal%60%2C%0A%20%20%60fecha_corte_reps%60"

try:
    print("Descargando y procesando los datos...")
    # Realizar la consulta a la API
    response = requests.get(url)
    response.raise_for_status()
    
    # Cargar los datos directamente en un DataFrame de pandas
    data = response.json()
    df = pd.DataFrame(data)
    
    # -------------------------------------------------------------------------
    # REQUERIMIENTO 1: Los 20 primeros hospitales del país con su número telefónico
    # -------------------------------------------------------------------------
    print("\n=======================================================")
    print("1. TOP 20 PRIMEROS HOSPITALES DEL PAÍS CON TELÉFONO ")
    print("=======================================================")
	# 1. Eliminamos duplicados por municipio (nos quedamos con el primero que aparece)
    # Usamos depa_nombre junto a muni_nombre porque hay municipios con el mismo nombre en diferentes departamentos
    df_unicos_por_muni = df.drop_duplicates(subset=['depa_nombre', 'muni_nombre'], keep='first')
    
    # 2. Ahora tomamos los 20 primeros registros de este nuevo conjunto filtrado
    top_20_unicos = df_unicos_por_muni[['depa_nombre', 'muni_nombre', 'nombre_prestador', 'telefono']].head(20)
    
    # Imprimimos de forma limpia
    print(top_20_unicos.to_string(index=False))
    
       # -------------------------------------------------------------------------
    # REQUERIMIENTO: Detalle de sedes para IPS Multisede
    # -------------------------------------------------------------------------
    print("\n====================================================================")
    print(" DETALLE DE SEDES: IPS CON MÁS DE UNA SEDE EN EL PAÍS")
    print("====================================================================")
    
    # 1. Contamos cuántas sedes tiene cada NIT en el país
    conteo_sedes = df['nits_nit'].value_counts()
    
    # 2. Identificamos los NITs que se repiten más de una vez (> 1)
    nits_multisede = conteo_sedes[conteo_sedes > 1].index
    
    # 3. Filtramos el DataFrame original para conservar solo las filas de esos NITs
    df_resultado = df[df['nits_nit'].isin(nits_multisede)].copy()
    
    # 4. Seleccionamos las columnas solicitadas para la vista analítica
    # Agregamos 'nits_nit' para que puedas identificar visualmente cuáles sedes pertenecen a la misma IPS
    columnas_vista = ['nombre_prestador', 'depa_nombre', 'muni_nombre', 'nits_nit']
    df_resultado = df_resultado[columnas_vista]
    
    # 5. Ordenamos por NIT y por Departamento para agrupar visualmente las sedes de cada empresa
    df_resultado = df_resultado.sort_values(by=['nits_nit', 'depa_nombre', 'muni_nombre'])
    
    # Mostramos las primeras 30 sedes encontradas en la muestra de datos como ejemplo
    print(f"Se detectaron {len(df_resultado)} registros de sedes pertenecientes a IPS multisede.\n")
    print("Muestra de sedes indexadas (Primeras 30):")
    print(df_resultado.head(30).to_string(index=False))
    
    # -------------------------------------------------------------------------
    # Tabla de cantidad de IPS Públicas vs Privadas
    # -------------------------------------------------------------------------
    print("\n=======================================================")
    print("3. CANTIDAD DE IPS PÚBLICAS VS PRIVADAS")
    print("=======================================================")
    # Nota analítica: En el Registro Especial de Prestadores de Servicios de Salud (REPS),
    # el campo 'clase_persona' o la columna 'ese' (Empresa Social del Estado) 
    # y 'naju_nombre' definen la naturaleza jurídica (Pública, Privada o Mixta).
    # Usaremos 'naju_nombre' (Naturaleza Jurídica) que suele ser el estándar exacto.
    
    if 'naju_nombre' in df.columns:
        tabla_ips = df['naju_nombre'].value_counts().to_frame(name='Cantidad IPS')
        tabla_ips.index.name = 'Naturaleza Jurídica'
        print(tabla_ips)
    else:
        # Alternativa en caso de que utilices otra columna de agrupación de la API
        print("Columna 'naju_nombre' no disponible para el conteo directo.")

except requests.exceptions.RequestException as e:
    print(f"Error al conectarse a la API de datos.gov.co: {e}")
except KeyError as e:
    print(f"Error en la estructura de columnas esperada: {e}")
except Exception as e:
    print(f"Ocurrió un error inesperado: {e}")