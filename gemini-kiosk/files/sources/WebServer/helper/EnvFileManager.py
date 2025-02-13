class EnvFileManager:
    def __init__(self, file_path='.env'):
        """
        Initialise le gestionnaire de fichier .env.
        
        Args:
            file_path (str): Chemin vers le fichier .env
        """
        self.file_path = file_path
        self.env_dict = {}
        self.load_env()
    
    def load_env(self):
        """Charge le contenu du fichier .env dans un dictionnaire"""
        try:
            with open(self.file_path, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Gérer le cas où il y a plusieurs '=' dans la valeur
                        key, value = line.split('=', 1)
                        self.env_dict[key.strip()] = value.strip()
        except FileNotFoundError:
            print(f"Le fichier {self.file_path} n'existe pas.")
            
    def get_content(self):
        """Retourne le contenu complet sous forme de texte"""
        return '\n'.join(f"{key}={value}" for key, value in self.env_dict.items())
    
    def get_value(self, key):
        """Récupère la valeur d'une clé spécifique"""
        return self.env_dict.get(key)
    
    def set_value(self, key, value):
        """Modifie ou ajoute une valeur pour une clé donnée"""
        self.env_dict[key] = value
        
    def save(self):
        """Sauvegarde les modifications dans le fichier"""
        try:
            with open(self.file_path, 'w') as file:
                file.write(self.get_content())
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")