# Vérifier si un argument a été fourni
if [ -z "$1" ]; then
  echo "Veuillez fournir la valeur de HOME en argument."
  exit 1
fi
ma_variable_home="$1"
# Installation des paquets requis
 apt-get update
 apt-get install -y python3 python3-pip python3.11-venv cmake libpcsclite-dev fonts-liberation
 apt install -y pcscd
 apt install -y pcsc-tools
 apt-get install -y desktop-file-utils
 
# Installation des paquets .deb
 dpkg -i packages/libacsccid1_1.1.10-1~bpo12+1_amd64.deb
 wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
 sudo dpkg -i google-chrome-stable_current_amd64.deb
 sudo apt-get install -f
 sudo rm google-chrome-stable_current_amd64.deb	
 
 sudo cp launch.sh "$ma_variable_home/"
 sudo chmod +x "$ma_variable_home/launch.sh"

# Définition du répertoire
DIR="/var/gemini/"
# Création du répertoire si nécessaire
if [ ! -d "$DIR" ]; then
    sudo mkdir -p "$DIR"
    echo "Directory $DIR created."
else
    echo "Directory $DIR already exists."
    sudo rm -rf "$DIR"
    sudo rm -f /etc/systemd/system/gemini_kiosk_settings.service
    systemctl daemon-reload
    sudo mkdir -p "$DIR"
    echo "Directory $DIR created."
fi
 
 
