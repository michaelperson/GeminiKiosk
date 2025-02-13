import time 
import os 

import threading
class WatchHelper:
    initialHandles=None
    def __init__(self):
        #  Script pour ajouter un bouton sur la page
        
        
        self.inject_button_script=""" const button = document.createElement('a');
  

            button.id = 'close-all-btn-gemini';
            // Styles pour le positionnement
            button.style.position = 'fixed'; // Fixe le bouton à l'écran
            button.style.left = '0'; // Bords gauche
            button.style.bottom = '50%'; // bas de page
            button.style.transform = 'translateY(-50%)'; // Ajuste le positionnement vertical
            button.style.zIndex = '9999'; // Au-dessus de tout

            // Styles pour le bouton (comme précédemment)
            button.style.display = 'inline-flex';
            button.style.alignItems = 'center';
            button.style.padding = '8px 16px';
            button.style.backgroundColor = '#4285F4';
            button.style.color = 'white';
            button.style.textDecoration = 'none';
            button.style.borderRadius = '4px';
            button.style.cursor = 'pointer';
            button.style.fontFamily = 'sans-serif';
            button.style.height = '50px';

            const logo = document.createElement('img');
            logo.src = 'https://lh3.googleusercontent.com/c-z7BK6NYcQIruZJd9A4KI1m8YrBauXH0VRglPudmj9Fgr5yzgJCsnaZ5W_nxZnB2hazA9hsg05uX1djFYPbMS-DsbYXp6UtVKFfdicBfF8klhVshJ8'; // Chemin vers l'image
            logo.alt = "Logo";
            logo.style.width = '20px';
            logo.style.height = '20px';
            logo.style.marginRight = '8px';
            logo.style.verticalAlign = 'middle';

            button.appendChild(logo);
            button.appendChild(document.createTextNode('Back to Gemini'));
            
                            button.onclick = () => {
                                window.close();
                            };
            document.body.appendChild(button);"""

  
    def surveillance_onglet(self,driver):
        try:
         intervalle_check = 2  # Vérification toutes les 30 secondes
         self.initialHandles =driver.window_handles
         waitTime = int(os.environ.get('InactivityTimeMinutes'))   # exemple 300 secondes = 5 minutes 
         while True:
             time.sleep(2)
             intervalle_check = 2  # Vérification toutes les 30 secondes         
             current_handles = driver.window_handles
             if len(current_handles) > 1 : 
                self.inject_button(driver)  # Injecter le bouton dans le nouvel onglet
        except:
            print("Fin surveillance Onglet")

    def surveiller_inactivite(self,driver):
        try:
            temps_inactif = 0
            dernier_contenu = driver.page_source  # Contenu initial de la page        
            intervalle_check = 2  # Vérification toutes les 30 secondes       
            waitTime = int(os.environ.get('InactivityTimeMinutes'))   # exemple 300 secondes = 5 minutes
            while True:                
                time.sleep(intervalle_check)
                try:
                    nouveau_contenu = driver.page_source
                except:
                    driver.switch_to.window(driver.window_handles[0]) 
                    nouveau_contenu = driver.page_source

                #print(temps_inactif)
                if nouveau_contenu == dernier_contenu:
                    temps_inactif += intervalle_check
                else:
                    temps_inactif = 0  # Réinitialiser le compteur d'inactivité
                    dernier_contenu = nouveau_contenu 

                if temps_inactif >= waitTime:
                    self.FermerOngletSupp(driver) 
                    driver.switch_to.window(driver.window_handles[0])
                    driver.get(os.environ.get('DefaultUrl'))
                    break
        except:
            print("Fin de la surveillance inactivite")

                 
    def surveiller_Url(self,driver):
        try:   
            temps_inactif = 0
            dernier_contenu = driver.page_source  # Contenu initial de la page        
            intervalle_check = 2  # Vérification toutes les 30 secondes       
            waitTime = int(os.environ.get('InactivityTimeMinutes'))   # exemple 300 secondes = 5 minutes
            while True:                
                time.sleep(intervalle_check)
                try:
                    nouveau_contenu = driver.current_url
                except:
                    driver.switch_to.window(driver.window_handles[0]) 
                    nouveau_contenu = driver.current_url
                
                if nouveau_contenu == dernier_contenu:
                    temps_inactif += intervalle_check
                else:
                    temps_inactif = 0  # Réinitialiser le compteur d'inactivité
                    dernier_contenu = nouveau_contenu 

                if temps_inactif >= waitTime:
                    self.FermerOngletSupp(driver) 
                    driver.switch_to.window(driver.window_handles[0])
                    driver.get(os.environ.get('DefaultUrl'))
                    break
        except:
            print("FIn de la surveillance Url")   


    def surveillanceLog(self,driver):
        logs = driver.get_log("browser")  # Récupérer les logs de la console
        for log in logs:
            if "close_all_except_first" in log["message"]:
                self.FermerOngletSupp(driver)
                print("Tous les onglets sauf le premier ont été fermés.")
                self.initialHandles=driver.window_handles
                return True
        return False

    def FermerOngletSupp(self, driver):
        # Obtenir les handles des fenêtres ouvertes
        window_handles = driver.window_handles 
        # Index de l'onglet gemini
        current_index = 0
        cpt=1
        # Fermer les onglets à droite (index supérieur à l'onglet actif)
        for handle in window_handles[current_index + 1:]:
             
            driver.switch_to.window(handle)
            try:
                driver.close()
            except:
                print("tab already closed")   
            cpt=cpt+1 

        # Revenir à l'onglet actif
        try:
            driver.switch_to.window(driver.window_handle[0])
        except:
            print("End of closing process")

     
    # Fonction pour injecter le bouton dans un onglet donné
    def inject_button(self,driver):
         # Vérifier si le bouton existe déjà
        button_exists = driver.execute_script("""return document.getElementById('close-all-btn-gemini') !== null;""")
    
        if not button_exists:
            print("bouton ajout")
            
            surveillance_thread = threading.Thread(target=self.surveiller_Url, args=(driver,))
            surveillance_thread.start() 
            current_index = 0
            window_handles = driver.window_handles
            # Fermer les onglets à droite (index supérieur à l'onglet actif)
            for handle in window_handles[current_index + 1:]:                 
                    driver.switch_to.window(handle)
                    driver.execute_script(self.inject_button_script)
