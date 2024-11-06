import pandas as pd
import xgboost as xgb

import config


def load_model(predict = False) -> xgb.XGBRegressor:
    """
    Carga un modelo previamente entrenado de XGBoost y, opcionalmente, guarda una copia del modelo cargado.

    Parámetros:
    -----------
    predict : bool, opcional
        Indica si solo se debe cargar el modelo para realizar predicciones. Si es `False` (por defecto), 
        también se guarda el modelo cargado en una carpeta específica.
    
    Retorna:
    --------
    xgb.XGBRegressor
        El modelo cargado de XGBoost que se puede utilizar para realizar predicciones o continuar con el entrenamiento.
    """
    model_name = 'predictor_xgboost.json'
    model = xgb.XGBRegressor()  # Crear un nuevo objeto XGBRegressor
    model.load_model(f'{config.MODEL_ROOT_PATH}/predictor_xgboost.json')
    if not predict:
        model.save_model(f'{config.MODEL_ROOT_PATH}/last_model/{model_name}')
    return model


def re_train_model(model: xgb.XGBRegressor, data:pd.DataFrame)->xgb.XGBRegressor:
    """
    Vuelve a entrenar un modelo de XGBoost utilizando nuevos datos. La función ajusta el modelo con los 
    datos proporcionados y conserva el entrenamiento previo (si existe) usando el parámetro `xgb_model`.

    Parámetros:
    -----------
    model : xgb.XGBRegressor
        El modelo de XGBoost previamente cargado que se desea reentrenar.

    data : pd.DataFrame
        El conjunto de datos con los cuales se reentrenará el modelo. Este DataFrame debe contener una columna 
        llamada 'Valor neto', que se utilizará como la variable objetivo (Y). El resto de las columnas se utilizarán 
        como las variables independientes (X).

    Retorna:
    --------
    xgb.XGBRegressor
        El modelo de XGBoost reentrenado con los nuevos datos.
    """
    Y=data['Valor neto']
    X=data.drop(columns=['Valor neto'])
    model.fit(X, Y, xgb_model=model.get_booster()) 
    return model


def save_new_model(model: xgb.XGBRegressor):
    """
    Guarda un modelo de XGBoost en un archivo JSON en la ruta especificada en la configuración.

    Parámetros:
    -----------
    model : xgb.XGBRegressor
        El modelo de XGBoost que se desea guardar. Este modelo debe haber sido entrenado previamente.
    """
    model_name = 'predictor_xgboost.json'
    model.save_model(f'{config.MODEL_ROOT_PATH}/{model_name}')


def train_model(data: pd.DataFrame):
    """
    Entrena un modelo XGBoost utilizando los datos proporcionados, y guarda el modelo entrenado en un archivo JSON.

    Este proceso implica cargar el modelo previamente entrenado (si existe), reentrenarlo con los nuevos datos
    proporcionados, y luego guardar el modelo actualizado en el disco.

    Parámetros:
    -----------
    data : pd.DataFrame
        El DataFrame con los datos que se utilizarán para reentrenar el modelo. 
        Este DataFrame debe contener la variable objetivo 'Valor neto' y las características necesarias para el entrenamiento.
    """
    model = load_model()
    model = re_train_model(model, data)
    save_new_model(model)
    
    