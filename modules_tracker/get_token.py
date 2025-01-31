import os
from dotenv import load_dotenv

load_dotenv()

import requests
from IPython.display import display
from credentials import *
from credentials import client_id, client_secret, client_id_pro, client_secret_pro

print(f"DEBUG - client_id: {client_id}")
print(f"DEBUG - client_secret: {client_secret[:5]}******")  # Masquer la clé
print(f"DEBUG - client_id_pro: {client_id_pro}")
print(f"DEBUG - client_secret_pro: {client_secret_pro[:5]}******")# Masquer la clé


def get_token():
    token_url = 'https://sandbox-oauth.piste.gouv.fr/api/oauth/token'
    #inject cred 
    token_data = {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret,
    'scope': 'openid'}
    response = requests.post(token_url, data=token_data)
    print(f"DEBUG - Status Code: {response.status_code}")
    print(f"DEBUG - Response Text: {response.text}")  # Affiche le message d'erreur
    response.raise_for_status()  # vérif  erreurs
    # récup  jeton
    token_info = response.json()
    access_token = token_info['access_token']
    return access_token

def get_token_prod():
    token_url = 'https://oauth.piste.gouv.fr/api/oauth/token'  # URL de production
    token_data = {
        'grant_type': 'client_credentials',
        'client_id': client_id_pro,
        'client_secret': client_secret_pro,
        'scope': 'openid'
    }
    response = requests.post(token_url, data=token_data)
    print(f"DEBUG - Status Code: {response.status_code}")
    print(f"DEBUG - Response Text: {response.text}")
    response.raise_for_status()  # Vérifie les erreurs
    token_info = response.json()
    access_token = token_info['access_token']
    return access_token