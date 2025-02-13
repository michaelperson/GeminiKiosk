#!/bin/bash

# Chemins
SERVICE_NAME="gemini_kiosk_settings"
SERVICE_PATH="/etc/systemd/system/${SERVICE_NAME}.service"
APP_PATH="/var/gemini/sources/WebServer"
VENV_PATH="/var/gemini/.venv"

# Vérification des permissions root
if [ "$EUID" -ne 0 ]; then 
    echo "Ce script doit être exécuté en tant que root"
    exit 1
fi

# Vérification de l'existence du dossier applicatif
if [ ! -d "$APP_PATH" ]; then
    echo "Erreur: Le dossier $APP_PATH n'existe pas"
    exit 1
fi

# activation de l'environnement virtuel
source "$VENV_PATH/bin/activate"
   
# Configuration des permissions
chown -R www-data:www-data "$APP_PATH"
chmod -R 755 "$APP_PATH"

# Copie du fichier service
cp gemini.service "$SERVICE_PATH"
chmod 644 "$SERVICE_PATH"

# Rechargement de systemd et activation du service
systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl start $SERVICE_NAME

echo "Le service Gemini a été installé et démarré"
echo "Utilisez 'systemctl status $SERVICE_NAME' pour vérifier l'état du service"
