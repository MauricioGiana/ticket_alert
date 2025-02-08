from dotenv import load_dotenv
import os

load_dotenv()

CONSULT_URL = f"{os.getenv('HOST')}/web/buscarServicios"

CONSULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9,es-AR;q=0.8,es;q=0.7",
    "Cache-Control": "max-age=0",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://reservapasajes.cnrt.gob.ar",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
}

CONSULT_DATA = {
    "token": None,
    "beneficiarioCnrtId": os.getenv('USER_ID'),
    "origen": "",
    "destino": "",
    "fechaSalida": "",
    "cantidadPasajes": "",
}

LOGIN_URL = f"{os.getenv('HOST')}/web/ingresar"

LOGIN_DATA = {
    "documentoOpciones": "1",
    "nroDocumento": os.getenv('DNI'),
    "tipoCredencial": "CUD",
    "nroCredencial": os.getenv('CUD'), 
    "sexo": "1",  # Gender (1 for male, 2 for female)
}