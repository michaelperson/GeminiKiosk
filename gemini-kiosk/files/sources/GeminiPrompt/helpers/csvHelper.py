import csv
import threading
class CsvHelper:
    def __init__(self, file_path):
        """
        Initialise la classe avec le chemin du fichier CSV.
        """
        self.file_path = file_path+"/prompts.csv"
        self.data = [] 
        # Charger les données manuellement
        with open(self.file_path, mode='r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                self.data.append(row)
        self.lock= threading.Lock()

    def get_prompt(self, code, lang):
        """
        Retourne le PROMPT correspondant au CODE et à la langue demandée.
        Si aucun ne correspond à la langue et au CODE, retourne le PROMPT du CODE seul.
        Si rien ne correspond, retourne un message par défaut.

        :param code: Le CODE à rechercher.
        :param lang: La langue à rechercher.
        :return: Le texte du PROMPT.
        """
        # Recherche d'une correspondance exacte (CODE + LANG)
        with self.lock: 
            for row in self.data:
                if row['CODE'] == code and str(row['LANG']).strip().lower() == str(lang).strip().lower():
                     
                    return row['PROMPT']

            # Recherche d'une correspondance partielle (CODE uniquement)
            for row in self.data:
                if row['CODE'] == code:
                     
                    return row['PROMPT']

            # Aucun résultat trouvé
            return None
        