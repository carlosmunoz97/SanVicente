import pandas as pd
from train import load_model


def predict(data:pd.DataFrame):
    """
    Realiza predicciones sobre un conjunto de datos de entrada utilizando un modelo previamente guardado.

    Parámetros:
    -----------
    data : pd.DataFrame
        DataFrame con los datos de entrada en el formato esperado por el modelo, donde cada fila representa
        un conjunto de características a ser evaluadas.

    Retorna:
    --------
    np.ndarray
        Un array con las predicciones generadas por el modelo para cada fila del DataFrame de entrada.
    """
    model = load_model(True)
    pred = model.predict(data)
    return pred