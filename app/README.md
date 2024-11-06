# Aplicativo modular

Este aplicativo busca poder generar de manera modular el reentrenamiento y la predicción de datos semana a semana a partir de un modelo predictivo para el ingreso semanal de un hospital.

## Arquitectura
Se tienen diferentes módulos enfocados a diferentes aspectos en el problema.

-Un módulo de configuración donde se almacenan variables importantes.
-Un módulo de procesamiento de datos donde se tienen aquellos funciones de pre-procesamiento, procesamiento, estandarización y demás importantes e influyentes en ambos caminos
-Un módulo de predicción en el cual se tiene el flujo necesario para poder llegar a una predicción.
-Un módulo de entrenamiento en el cual se tiene el flujo necesario para poder llevar a cabo un reentrenamiento del modelo ya almacenado.
-Un módulo principal o main en el cual se almacena el inicio del flujo
-Una carpeta llamada model en la que se guarda el modelo usado actualmente y dentro de la misma carpeta un modelo denominado last_model en el cual se almacena una copia del modelo antes de realizar un re-entrenamiento.
-Una carpeta de database donde se almacena la BD de facturación y una donde se almacena los datos ya procesados.

## Consideraciones.
Imaginando tener un ambiente productivo, se piensa como si se tuviera una base de datos donde se van almacenando los datos de manera ordenada y en bruto para poder realizar su respectivo tratamiento. Y por otro lado, una BD que actua como data_lake en el que se van almacenando los datos ya procesados con las variables relevantes en el modelo.

IMPORTANTE: Es importante señalar que estas dos bases de datos no se suben al repositorio por su tamaño y que este aplicativo modular no tiene los respectivos pipelines o ETLs que permiten ir almacenando nuevos registros en la BD que hace de datalake.

## Instalación

La instalación se realiza de manera similar, instalando las librerías almacenadas en requirements.txt que son las que en mayor parte se usan para poder usar el modelo, reentrenarlo y demás funciones que en principio tiene el aplicativo.


## Uso
Para poder predecir el modelo es necesario incluir dentro de la BD considerada como datalake los nuevos valores que se requieren usar en la predicción. Dado que no tenemos esos valores de la semana actual que queremos predecir, entonces es necesario realizar un ventaneo con la media de 3 registros atrás para poder completarlo.

Por otro lado, es necesario incluir en la BD de facturación los nuevos registros para poder realizar un re-entrenamiento del modelo, puesto que este realiza el proceso necesario de estandarización y limpieza de datos de los nuevos datos agregados para cada semana.


Para poder ejecutar se debe usar el comando python main.py así:

python main.py --entrenar 
o 
python main.py --predecir

segpun sea el caso, se puede usar una opción o la otra y se debe especificar la raíz donde se encuentra el archivo main.py. 

La configuración estima cambios en donde se almacena las carpetas pero es necesario tener las BDs correspondientes. 

EL uso de las BDs es una muestra de como podría implementarse un modelo y mantenimiento haciendo uso de erramientas que podrían ejecutarse junto a un data factory o base de datos como el entorno que ofrece Azure, AWS o incluso GCP. 
