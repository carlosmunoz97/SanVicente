from pathlib import Path

DATABASE_ROOT_PATH = str(Path(__file__).parent / "database")
MODEL_ROOT_PATH = str(Path(__file__).parent / "model")
CSV_NAME = 'Facturacion.xlsx'
DATA_WEEK = 'data_week.xlsx' 

ASEGURADORA = ['alianza medellin antioquia','allianz seguros de vida','axa colpatria seguros','colmedica prepagada','colsanitas med prepagada','compania mundial de segurossa','coomeva medicina prepagada','coosalud entidad promotora de','empresas publicas','fund hosp san vicente de paul','nueva empresa promotora de salu','particulares','salud total','seguros de vida suramericana','seguros de vida suramericana polizas global o cla','seguros del estado soat','seguros generales suramericana soat','sura']

POBLACION = ['bello','carmen de viboral','ceja','envigado','guarne','itagui','marinilla','medellin','penol','retiro','rionegro','san vicente','santuario']

GENERO = ['Genero_F', 'Genero_M']

CENTRO_RESPONSABILIDAD = ['centro_530101', 'centro_530201','centro_530301', 'centro_530401', 'centro_530718', 'centro_530801','centro_530809', 'centro_530812', 'centro_530815']

CLASE_EPISODIO = ['Episodio_ambulatorio', 'Episodio_hospitalizado']