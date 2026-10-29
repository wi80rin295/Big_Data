#Importamos librerías necesarias
import os
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.window import Window

# Configuración del Entorno de Ejecución
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-17-openjdk-amd64"
os.environ["SPARK_LOCAL_IP"] = "192.168.1.26"

# Inicialización de la Sesión de PySpark
spark = SparkSession.builder.appName('Tarea5').getOrCreate()

# Ruta de tu archivo CSV local
file_path_local = 'Listado_IPS.csv'

try:
    print("Descargando y procesando los datos...")
    
    # 1. Leer el archivo de forma nativa con Spark
    df = spark.read.csv(file_path_local, header=True, inferSchema=True)
    
    # -------------------------------------------------------------------------
    # REQUERIMIENTO 1: Los 20 primeros hospitales (Máximo 1 por municipio)
    # -------------------------------------------------------------------------
    print("\n=======================================================")
    print("1. TOP 20 PRIMEROS HOSPITALES DEL PAÍS CON TELÉFONO")
    print("=======================================================")
    
    # En PySpark eliminamos duplicados por municipio de forma nativa usando dropDuplicates
    df_unicos_por_muni = df.dropDuplicates(subset=['depa_nombre', 'muni_nombre'])
    
    # Seleccionamos columnas y limitamos a 20 registros
    top_20_unicos = df_unicos_por_muni.select('depa_nombre', 'muni_nombre', 'nombre_prestador', 'telefono').limit(20)
    
    # Mostramos el resultado de forma limpia (no truncate para leer nombres largos)
    top_20_unicos.show(20, truncate=False)
    
    # -------------------------------------------------------------------------
    # REQUERIMIENTO 2: Detalle de sedes para IPS Multisede
    # -------------------------------------------------------------------------
    print("\n====================================================================")
    print(" 2. DETALLE DE SEDES: IPS CON MÁS DE UNA SEDE EN EL PAÍS")
    print("====================================================================")
    
    # Contamos cuántas sedes tiene cada NIT y filtramos las que tengan más de 1
    conteo_sedes = df.groupBy("nits_nit").count().filter("count > 1")
    
    # Filtramos el DataFrame original cruzándolo con el listado de NITs multisede (Left Semi Join)
    df_resultado = df.join(conteo_sedes, on="nits_nit", how="left_semi")
    
    # Seleccionamos columnas y ordenamos para agrupar visualmente las sedes
    df_resultado_vista = df_resultado.select('nombre_prestador', 'depa_nombre', 'muni_nombre', 'nits_nit') \
                                     .orderBy('nits_nit', 'depa_nombre', 'muni_nombre')
    
    # Mostramos las primeras 30 sedes
    df_resultado_vista.show(30, truncate=False)
    
    # -------------------------------------------------------------------------
    # REQUERIMIENTO 3: Tabla de cantidad de IPS Públicas vs Privadas
    # -------------------------------------------------------------------------
    print("\n=======================================================")
    print("3. CANTIDAD DE IPS PÚBLICAS VS PRIVADAS")
    print("=======================================================")
    
    if 'naju_nombre' in df.columns:
        # Agrupamos y contamos de forma nativa en Spark
        df.groupBy('naju_nombre').count().withColumnRenamed('count', 'Cantidad IPS').show(truncate=False)
    else:
        print("Columna 'naju_nombre' no disponible para el conteo directo.")

except Exception as e:
    print(f"Ocurrió un error inesperado en la infraestructura Spark: {e}")
