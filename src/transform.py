import re

import pandas as pd
import unidecode


def convert_to_number(value):
    value = str(value)
    if value.isdigit():
        return int(value)
    elif 'A' in value or 'D' in value:
        return int(value.split()[0])
    else:
        return pd.to_datetime(value).hour
    
def clean_text(texto):
    if isinstance(texto, str):
        texto = texto.lower()
        texto = unidecode.unidecode(texto)
        texto = re.sub(r'[^\w\s]', '', texto)
        texto = re.sub(r'\d+', '', texto)
        texto = re.sub(r'\s+', ' ', texto).strip()
    return texto


def normalize_city(city):
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

def normalize_insurer(insurer):
    if insurer in ['EPS SURA', 'PAC EPS SURA', 'FUND HOSPITAL SAN VICENTE -, SURA E.P.S']:
        return 'SURA'
    return insurer