import re

import pandas as pd
import unidecode

import config


class TrainError(Exception):
    def __init__(self, message="Error in training"):
        self.message = message
        super().__init__(self.message)


def charge_data(is_dataset:bool = False)->pd.DataFrame:
    """
    Carga un archivo Excel desde una ruta especificada en la configuración.
    Dependiendo del valor de 'is_dataset', se selecciona un archivo diferente para cargar.
    
    Parámetros:
    -----------
    is_dataset : bool, opcional
        Si se establece en True, se cargará el archivo especificado en 'config.DATA_WEEK'.
        Si es False (valor predeterminado), se cargará el archivo especificado en 'config.CSV_NAME'.

    Retorna:
    --------
    pandas.DataFrame
        Un DataFrame de pandas que contiene los datos cargados desde el archivo Excel correspondiente.
    """
    root = config.DATABASE_ROOT_PATH
    name = config.CSV_NAME
    if is_dataset:
        name = config.DATA_WEEK
    return pd.read_excel(f'{root}/{name}')


def charge_last_data()->pd.DataFrame:
    """
    Carga los datos de la última semana, ordenados por la columna 'Creado el', 
    y elimina la columna 'Valor neto' del primer registro.

    La función utiliza `charge_data` para obtener los datos de la semana (con el parámetro `is_dataset=True`),
    luego establece la columna 'Creado el' como índice, ordena los registros de forma descendente 
    y retorna el primer registro después de eliminar la columna 'Valor neto'.

    Retorna:
    --------
    pandas.DataFrame
        Un DataFrame que contiene el primer registro de los datos de la última semana, 
        sin la columna 'Valor neto'.
    """
    data = charge_data(True)
    data = data.set_index("Creado el")
    data = data.sort_index(ascending=False)
    first_register = data.iloc[[0]]
    first_register = first_register.drop(columns=['Valor neto'])
    return first_register


def verify_last_data(data_week: pd.DataFrame, data_billing: pd.DataFrame)->pd.DataFrame:
    """
    Verifica si hay nuevos registros en `data_billing` para las fechas de la última semana,
    y devuelve los registros de los últimos 4 semanas si los hay.

    La función compara las fechas entre los datos semanales (`data_week`) y los registros de facturación (`data_billing`).
    Si se detectan nuevas fechas, se filtran los registros de `data_billing` para las últimas 4 semanas desde la fecha más temprana de esas nuevas fechas.

    Parámetros:
    -----------
    data_week : pandas.DataFrame
        DataFrame que contiene las fechas de las semanas anteriores. Se utiliza para comparar las fechas con `data_billing`.
    
    data_billing : pandas.DataFrame
        DataFrame que contiene los registros de facturación, con la columna 'Creado el' representando las fechas de los registros.

    Retorna:
    --------
    bool or pandas.DataFrame
        - Si no hay nuevas fechas en `data_billing` en comparación con `data_week`, devuelve `False`.
        - Si hay nuevas fechas, devuelve un DataFrame con los registros de los últimos 4 semanas desde la fecha más temprana de esas nuevas fechas.
    """
    data = data_billing.copy()
    data = data.set_index("Creado el")
    df_week = data.resample("W").count()
    new_dates = df_week.index.difference(data_week.index)
    if new_dates.empty:
        return False
    earliest_date = new_dates.min()
    date_4_weeks_ago = earliest_date - pd.DateOffset(weeks=4)
    filtered_records = data[data.index > date_4_weeks_ago]
    return filtered_records



def extract_data_4_train_model_process()-> pd.DataFrame:
    """
    Extrae los datos necesarios para entrenar el modelo, verifica si hay nuevos registros de facturación,
    y lanza un error si el modelo ya está actualizado con la última información.

    La función carga los datos semanales y de facturación, los ordena por fecha y verifica si existen nuevos datos
    de facturación para entrenar el modelo. Si no hay nuevos datos, lanza una excepción `TrainError` con un mensaje
    indicando que el modelo está actualizado.

    Retorna:
    --------
    pandas.DataFrame
        Si hay nuevos datos, devuelve los registros de facturación más recientes que serán utilizados
        para el entrenamiento del modelo.
    """
    data_week = charge_data(True)
    data_week = data_week.set_index("Creado el")
    data_week = data_week.sort_index(ascending=True)
    data_billing = charge_data()
    data_billing = data_billing.sort_values(by="Creado el", ascending=True)
    new_data_exist = verify_last_data(data_week, data_billing)
    if not new_data_exist:
        message = 'El modelo está actualizado con la última información'
        raise TrainError(message)
    return new_data_exist
    
    
def convert_to_number(value)->int:
    """
    Convierte un valor de entrada en un número entero basado en el formato del valor.
    
    Esta función intenta convertir diferentes tipos de valores en números. Si el valor es un número en formato de texto, 
    se convierte directamente a entero. Si contiene las letras 'A' o 'D', se extrae el número antes de esas letras.
    Si el valor es una fecha, se extrae la hora de la fecha y se devuelve como un número entero.

    Parámetros:
    -----------
    value : cualquier tipo
        El valor a convertir. Puede ser un número en formato de cadena, una fecha en formato de texto o una cadena con letras
        que contienen un número seguido de 'A' o 'D'.
    
    Retorna:
    --------
    int
        Un número entero derivado del valor de entrada:
        - Si el valor es un número en texto, se convierte a entero.
        - Si el valor contiene 'A' o 'D', se toma el número antes de esas letras.
        - Si el valor es una fecha, se devuelve la hora de esa fecha como entero.
    """
    value = str(value)
    if value.isdigit():
        return int(value)
    elif 'A' in value or 'D' in value:
        return int(value.split()[0])
    else:
        return pd.to_datetime(value).hour


def clean_text(texto:str)->str:
    """
    Limpia un texto para normalizarlo, eliminando caracteres no deseados como tildes, puntuación, números
    y espacios en exceso, y lo convierte a minúsculas.

    Esta función realiza una serie de transformaciones al texto de entrada:
    1. Convierte todo el texto a minúsculas.
    2. Elimina los acentos o tildes de los caracteres utilizando `unidecode`.
    3. Elimina cualquier signo de puntuación.
    4. Elimina todos los números.
    5. Elimina los espacios en blanco extra, dejando solo un espacio entre las palabras y recortando los espacios al inicio y final.

    Parámetros:
    -----------
    texto : str
        El texto a limpiar. Si el valor no es una cadena, se retornará el valor tal como está.
    
    Retorna:
    --------
    str
        El texto limpio y normalizado, después de realizar las transformaciones mencionadas.
    """
    if isinstance(texto, str):
        texto = texto.lower()
        texto = unidecode.unidecode(texto)
        texto = re.sub(r'[^\w\s]', '', texto)
        texto = re.sub(r'\d+', '', texto)
        texto = re.sub(r'\s+', ' ', texto).strip()
    return texto


def normalize_insurer(insurer: str)->str:
    """
    Normaliza los nombres de las aseguradoras a una forma estándar.

    Esta función toma el nombre de una aseguradora y, si el nombre coincide con una lista de valores predefinidos, 
    lo normaliza a un nombre estándar. Si el nombre no está en la lista, se retorna tal cual.

    Parámetros:
    -----------
    insurer : str
        El nombre de la aseguradora que se desea normalizar.
    
    Retorna:
    --------
    str
        El nombre de la aseguradora normalizado. Si el nombre está en la lista predefinida, se reemplaza por 'SURA'.
        De lo contrario, se retorna el nombre tal como está.
    """
    if insurer in ['EPS SURA', 'PAC EPS SURA', 'FUND HOSPITAL SAN VICENTE -, SURA E.P.S']:
        return 'SURA'
    return insurer


def normalize_city(city: str)->str:
    """
    Normaliza los nombres de las ciudades a una forma estándar.

    Esta función toma el nombre de una ciudad y, si el nombre coincide con alguna de las variantes predefinidas,
    lo normaliza a un nombre estándar. Si el nombre no está en la lista, se retorna tal cual.

    Parámetros:
    -----------
    city : str
        El nombre de la ciudad que se desea normalizar.
    
    Retorna:
    --------
    str
        El nombre de la ciudad normalizado. Si el nombre está en la lista predefinida, se reemplaza por el valor estándar.
        De lo contrario, se retorna el nombre tal como está.
    """
    if city in ['medellin', 'medelllin', 'medellin barri san javi', 'merdellin']:
        return 'medellin'
    if city in ['rionegro', 'rionegr', 'rionegri', 'rioengro', 'rionegro palinitagm', 'rio negro', 'rinegro', 'riionegro', 'ronegro']:
        return 'rionegro'
    if city in ['san antonio rionegro', 'rionegro san antonio']:
        return 'rionegro san antonio'
    if city in ['retiro linamorozcogma', 'retiro studiojuanmadrig', 'retiro']:
        return 'retiro'
    if city in ['carmen de viboral', 'carmen de vivoral']:
        return 'carmen de viboral'
    return city


def clean_insurance(data: pd.DataFrame)->pd.DataFrame:
    """
    Limpia y normaliza los nombres de las aseguradoras en un DataFrame.

    Esta función toma un DataFrame que contiene una columna llamada 'Aseguradora' y realiza una serie de transformaciones
    para limpiar y normalizar los nombres de las aseguradoras. Primero se normaliza cada nombre de aseguradora con 
    `normalize_insurer`, luego se aplica una limpieza de texto mediante `clean_text`, y finalmente se eliminan ciertas
    palabras clave (como 'sa', 'sas', 'eps', 'epss') que podrían estar presentes en los nombres de las aseguradoras.

    Parámetros:
    -----------
    data : pd.DataFrame
        El DataFrame que contiene la columna 'Aseguradora' con los nombres de las aseguradoras a limpiar y normalizar.
    
    Retorna:
    --------
    pd.DataFrame
        El DataFrame original con la columna 'Aseguradora' limpiada y normalizada.
    """
    data['Aseguradora'] = data['Aseguradora'].apply(normalize_insurer)
    data['Aseguradora'] = data['Aseguradora'].apply(clean_text)
    data['Aseguradora'] = data['Aseguradora'].replace(r'\b(sa|sas)\b', '', regex=True)
    data['Aseguradora'] = data['Aseguradora'].replace(r'\b(s|a)\b', '', regex=True)
    data['Aseguradora'] = data['Aseguradora'].replace(r'\b(eps|epss)\b', '', regex=True)
    data['Aseguradora'] = data['Aseguradora'].apply(clean_text)
    return data


def clean_pobl(data:pd.DataFrame)->pd.DataFrame:
    """
    Limpia y normaliza los nombres de las poblaciones en un DataFrame.

    Esta función toma un DataFrame que contiene una columna llamada 'Población' y realiza una serie de transformaciones
    para limpiar y normalizar los nombres de las poblaciones. Primero se aplica una limpieza de texto mediante la función 
    `clean_text`, luego se eliminan palabras clave específicas como 'dc', 'd', 'c', 'el' y 'la'. Finalmente, se normalizan 
    los nombres de las poblaciones utilizando la función `normalize_city`.

    Parámetros:
    -----------
    data : pd.DataFrame
        El DataFrame que contiene la columna 'Población' con los nombres de las poblaciones a limpiar y normalizar.
    
    Retorna:
    --------
    pd.DataFrame
        El DataFrame original con la columna 'Población' limpiada y normalizada.
    """
    data['Población'] = data['Población'].apply(clean_text)
    data['Población'] = data['Población'].replace(r'\b(dc)\b', '', regex=True)
    data['Población'] = data['Población'].replace(r'\b(d|c)\b', '', regex=True)
    data['Población'] = data['Población'].replace(r'\b(el|la)\b', '', regex=True)
    data['Población'] = data['Población'].apply(clean_text)
    data['Población'] = data['Población'].apply(normalize_city)
    return data


def convert_trm(data: pd.DataFrame)->pd.DataFrame:
    """
    Convierte el valor neto de los registros en USD a la moneda local utilizando el TRM.

    Esta función toma un DataFrame que contiene una columna llamada 'Mon.' que indica la moneda de los registros y una columna 
    llamada 'Valor neto'. Si la moneda es USD, se convierte el valor neto multiplicándolo por el TRM (Tasa de Representación del 
    Mercado). El valor por defecto de la TRM es 4000.

    Parámetros:
    -----------
    data : pd.DataFrame
        El DataFrame que contiene las columnas 'Mon.' (moneda) y 'Valor neto' (valor en la moneda indicada).
    
    Retorna:
    --------
    pd.DataFrame
        El DataFrame actualizado con los valores de 'Valor neto' convertidos a la moneda local si la moneda original es USD.
    """
    TRM = 4000
    data.loc[data['Mon.'] == 'USD', 'Valor neto'] *= TRM
    return data


def pre_process_new_data(new_data: pd.DataFrame)->pd.DataFrame:
    """
    Preprocesa un DataFrame de datos nuevos, realizando varias transformaciones y limpieza de columnas.

    Esta función aplica una serie de pasos de preprocesamiento a los datos contenidos en el DataFrame `new_data`:
    1. Convierte la columna 'Edad' a valores numéricos.
    2. Limpia la columna 'Aseguradora' aplicando normalización y eliminación de texto innecesario.
    3. Limpia la columna 'Clase episodio' eliminando texto adicional.
    4. Normaliza y limpia los nombres de las ciudades en la columna 'Población'.
    5. Convierte los valores de 'Valor neto' en la moneda USD a la moneda local utilizando el TRM (4000).
    6. Elimina las columnas 'Mon.', 'Causa Externa', y 'Pais de Nacimiento'.

    Parámetros:
    -----------
    new_data : pd.DataFrame
        El DataFrame que contiene los datos que se desean preprocesar. Debe contener al menos las columnas:
        - 'Edad': Información sobre la edad que será convertida a formato numérico.
        - 'Aseguradora': Información sobre la aseguradora que será normalizada.
        - 'Clase episodio': Información que será limpiada de texto innecesario.
        - 'Población': Nombres de ciudades que serán limpiados y normalizados.
        - 'Mon.': Columna que indica la moneda de los valores en 'Valor neto'.
        - 'Valor neto': Valores monetarios que serán convertidos si es necesario.
    
    Retorna:
    --------
    pd.DataFrame
        El DataFrame preprocesado con las transformaciones y limpiezas aplicadas.
    """
    new_data['Edad'] = new_data['Edad'].apply(convert_to_number)
    new_data = clean_insurance(new_data)
    new_data['Clase episodio'] = new_data['Clase episodio'].apply(clean_text)
    new_data = clean_pobl(new_data)
    new_data = convert_trm(new_data)
    columns_t_delete = ['Mon.', 'Causa Externa', 'Pais de Nacimiento']
    new_data = new_data.drop(columns=columns_t_delete)
    return new_data


def reduce_dimentionality(data: pd.DataFrame)-> pd.DataFrame:
    """
    Reduce la dimensionalidad de las columnas 'Población' y 'Aseguradora' al asignar un valor común para los valores
    que no pertenecen a una lista predefinida de valores.

    Esta función modifica las columnas 'Población' y 'Aseguradora' en el DataFrame `data`:
    - Si un valor en la columna 'Población' está presente en `config.POBLACION`, se mantiene tal como está. 
      De lo contrario, se asigna el valor 'Otro'.
    - Si un valor en la columna 'Aseguradora' está presente en `config.ASEGURADORA`, se mantiene tal como está.
      De lo contrario, se asigna el valor 'Otro'.

    Esto ayuda a reducir la variabilidad en los datos y a mejorar el rendimiento de modelos posteriores, especialmente
    en los casos donde hay una gran cantidad de categorías poco frecuentes en las variables de texto.

    Parámetros:
    -----------
    data : pd.DataFrame
        El DataFrame que contiene las columnas 'Población' y 'Aseguradora' que serán transformadas.
    
    Retorna:
    --------
    pd.DataFrame
        El DataFrame con las columnas 'Población' y 'Aseguradora' transformadas, donde los valores no presentes
        en las listas predefinidas son reemplazados por 'Otro'.
    """
    data['Población'] = data['Población'].apply(lambda x: x if x in config.POBLACION else 'Otro')
    data['Aseguradora'] = data['Aseguradora'].apply(lambda x: x if x in config.ASEGURADORA else 'Otro')
    return data


def generate_one_hot_encoding(data: pd.DataFrame)->pd.DataFrame:
    """
    Aplica codificación one-hot a columnas específicas del DataFrame, agregando nuevas columnas con prefijos indicativos
    y eliminando las columnas originales.

    Esta función toma un DataFrame `data` y transforma varias columnas categóricas mediante la codificación one-hot, 
    de modo que cada valor único de una columna se convierte en una columna nueva con valores binarios. 
    El nombre de cada nueva columna comienza con un prefijo que identifica la columna original.

    Parámetros:
    -----------
    data : pd.DataFrame
        El DataFrame que contiene las columnas categóricas que serán transformadas mediante one-hot encoding.

    Retorna:
    --------
    pd.DataFrame
        El DataFrame con las nuevas columnas generadas por la codificación one-hot y sin las columnas originales 
        que fueron codificadas.
    """
    columns = {'Población':'Poblacion', 'Aseguradora':'Aseguradora', 'Género':'Genero', 'Centro de Responsabilidad':'centro', 'Clase episodio':'Episodio'}
    for column, prefix in columns.items():
        data = pd.concat([data, pd.get_dummies(data[column], prefix=prefix)], axis=1)
    data = data.drop(columns=columns.keys())
    return data


def group_by_week(data:pd.DataFrame)->pd.DataFrame:
    """
    Agrupa los datos por semana, aplicando funciones de agregación específicas para cada columna.

    Esta función toma un DataFrame con un índice temporal (por ejemplo, fechas) y agrupa los datos en intervalos
    semanales. Calcula la media para las columnas de edad y la suma para el resto de columnas, permitiendo
    un análisis consolidado por semana.

    Parámetros:
    -----------
    data : pd.DataFrame
        DataFrame que contiene los datos a agrupar, con un índice temporal adecuado para la resampleación semanal.
    
    Retorna:
    --------
    pd.DataFrame
        Un nuevo DataFrame con los datos agregados por semana, donde se ha calculado la media para la columna 'Edad'
        (convertida a enteros) y la suma para el resto de las columnas.
    """
    mean_columns = ['Edad']
    agg_dict = {col: 'mean' if col in mean_columns else 'sum' for col in data.columns}
    data_week = data.resample('W').agg(agg_dict)
    data_week['Edad'] = data_week['Edad'].astype(int)
    return data_week


def delete_old_columns(data_week:pd.DataFrame)->pd.DataFrame:
    """
    Elimina columnas no deseadas de un DataFrame semanal, manteniendo solo las necesarias.

    Esta función identifica y elimina todas las columnas del DataFrame `data_week` que no sean de interés.
    Mantiene únicamente las columnas especificadas, como 'Valor neto' y 'Edad', así como aquellas columnas
    cuyo nombre comienza con el prefijo 'Freq_'.

    Parámetros:
    -----------
    data_week : pd.DataFrame
        DataFrame que contiene los datos semanales procesados, con diversas columnas.
    
    Retorna:
    --------
    pd.DataFrame
        DataFrame modificado sin las columnas no deseadas.
    """
    columns = data_week.columns
    columns_2_delete = []
    for column in columns:
        if column in ['Valor neto', 'Edad'] or column.startswith('Freq_'):
            continue
        columns_2_delete.append(column)
    data_week = data_week.drop(columns=columns_2_delete)
    return data_week


def windowing(data_week: pd.DataFrame)->pd.DataFrame:
    """
    Aplica una media móvil de ventana sobre las columnas especificadas de un DataFrame semanal.

    La función aplica una media móvil de 4 semanas sobre cada columna en `data_week`, excluyendo
    las columnas 'Valor neto' y 'Edad'. Para cada columna relevante, crea una nueva columna
    llamada `Freq_<nombre_columna>` que contiene la media móvil de 4 semanas.
    
    Parámetros:
    -----------
    data_week : pd.DataFrame
        DataFrame que contiene datos agregados por semana, con varias columnas.

    Retorna:
    --------
    pd.DataFrame
        DataFrame actualizado con columnas adicionales que contienen la media móvil
        de 4 semanas para cada columna (excepto 'Valor neto' y 'Edad').
    """
    columns = data_week.columns
    for column in columns:
        if column in ['Valor neto', 'Edad']:
            continue
        data_week[f'Freq_{column}'] = data_week[column].rolling(window=4, min_periods=1).mean()
    return data_week
    
    
def complete_all_columns(data_week: pd.DataFrame)->pd.DataFrame:
    """
    Completa las columnas faltantes en un DataFrame semanal con valores cero.

    La función asegura que el DataFrame `data_week` contenga todas las columnas esperadas,
    basadas en configuraciones predefinidas de poblaciones, aseguradoras, géneros, centros
    de responsabilidad y clases de episodio. Si alguna columna esperada no está presente
    en `data_week`, se agrega con un valor de 0 en todas las filas.

    Parámetros:
    -----------
    data_week : pd.DataFrame
        DataFrame que contiene datos agrupados semanalmente y puede no incluir todas las
        columnas esperadas en el modelo final.

    Retorna:
    --------
    pd.DataFrame
        DataFrame actualizado con todas las columnas esperadas. Las columnas que estaban
        ausentes se añaden con valores cero.
    """
    POBLACION = ['Freq_Poblacion' + nombre for nombre in config.POBLACION]
    ASEGURADORA = ['Freq_Aseguradora' + nombre for nombre in config.ASEGURADORA]
    GENERO = ['Freq' + nombre for nombre in config.GENERO]
    CENTRO_RESPONSABILIDAD = ['Freq' + nombre for nombre in config.CENTRO_RESPONSABILIDAD]
    CLASE_EPISODIO = ['Freq' + nombre for nombre in config.CLASE_EPISODIO]
    TOTAL = POBLACION + ASEGURADORA + GENERO + CENTRO_RESPONSABILIDAD + CLASE_EPISODIO
    columns = set(data_week.columns)
    for column in TOTAL:
        if column not in columns:
            data_week[column] = 0
    return data_week    


def save_last_registers(data: pd.DataFrame)->pd.DataFrame:
    """
    Guarda los registros más recientes en un archivo de Excel, evitando duplicados.

    La función `save_last_registers` carga datos semanales de una fuente externa y los combina
    con los datos más recientes proporcionados en `data`. Solo se agregan los registros
    que tengan una fecha posterior a la última fecha en los datos existentes, asegurando así
    que los datos se mantengan actualizados y sin duplicados.

    Parámetros:
    -----------
    data : pd.DataFrame
        DataFrame con los registros más recientes, los cuales podrían incluir nuevas
        observaciones o registros actualizados.

    Retorna:
    --------
    pd.DataFrame
        DataFrame con los registros que se añadieron a `data_week` debido a su fecha posterior
        a la última fecha de `data_week`.
    """
    data_week = charge_data(True)
    data_week = data_week.set_index("Creado el")
    data_week = data_week.sort_index(ascending=True)
    max_date = data_week.index.max()
    rest_registers = data[data.index > max_date]
    data_week = pd.concat([data_week, rest_registers])
    data_week= data_week[~data_week.index.duplicated(keep='first')]
    data_week.to_excel(f'{config.DATABASE_ROOT_PATH}/{config.DATA_WEEK}')
    return rest_registers
    

def process_new_data(data: pd.DataFrame)->pd.DataFrame:
    """
    Procesa los nuevos datos semanales para un modelo predictivo, incluyendo reducción de dimensionalidad,
    codificación one-hot, agrupación semanal, cálculo de ventanas móviles y completado de columnas faltantes.
    Los registros procesados se guardan, evitando duplicados.

    Parámetros:
    -----------
    data : pd.DataFrame
        DataFrame con los nuevos datos a procesar, donde cada fila representa un registro de datos
        y cada columna corresponde a una característica relevante para el modelo.

    Retorna:
    --------
    pd.DataFrame
        Un DataFrame con los registros nuevos procesados y guardados, correspondiente a aquellos
        con fechas posteriores a los registros actuales en `data_week`.
    """
    data = reduce_dimentionality(data)
    data = generate_one_hot_encoding(data)
    new_data_week = group_by_week(data)
    new_data_week = windowing(new_data_week)
    new_data_week = delete_old_columns(new_data_week)
    new_data_week = complete_all_columns(new_data_week)
    new_data_week['Semana'] = new_data_week.index.isocalendar().week
    new_data_week['Mes'] = new_data_week.index.month
    new_data_week = pd.get_dummies(new_data_week, columns=['Mes'])
    rest_registers = save_last_registers(new_data_week)
    return rest_registers
    
    
def load_data(train_model = False):
    if train_model:
        try:
            print('Se comienza a extraer la información')
            new_data = extract_data_4_train_model_process()
            print('Se comienza a pre-procesar la información')
            new_data = pre_process_new_data(new_data)
            print('Se comienza a procesar la información')
            new_data = process_new_data(new_data)
            print('La nueva data ha sido guardada ')
            return new_data
        except TrainError:
            raise
    else:
        data = charge_last_data()
        return data