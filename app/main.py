import argparse

from app.data_processing import load_data
from app.predict import predict
from app.train import train_model


def main():
    parser = argparse.ArgumentParser(description="Aplicativo para predicción semanal de ingresos")
    parser.add_argument('--entrenar', action='store_true', help="Reentrenar el modelo")
    parser.add_argument('--predecir', action='store_true', help="Predecir")
    args = parser.parse_args()

    if args.entrenar:
        print('Se va a reentrenar el modelo...')
        data = load_data(True)
        train_model(data)
        print('Entrenamiento finalizado!')
    elif args.predecir:
        print('Se va a realizar una predicción con la última información añadida')
        data = load_data()
        predict_val_neto = predict(data)
        print(f"Predicción realizada: {predict_val_neto}")
    else:
        print("Por favor, especifica una acción: --entrenar o --predecir.")
        
        

if __name__ == '__main__':
    main()
