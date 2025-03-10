import time 
import os 
import logging
import threading 

class WatchHelper:
    initialHandles=None
    def __init__(self):
              
        self.initial_handles: Optional[List[str]] = None
        
        self.inject_button_script=""" 
        
           document.body.addEventListener('click', function(event) 
           {
                let target = event.target;
                console.log('interception');
            
                console.log(target.tagName );
                // Vérifie si l'élément cliqué est un lien (<a>)
                while (target && target.tagName !== 'A') 
                {
                    target = target.parentElement;
                }

                if (target && target.tagName === 'A' && target.getAttribute('target') === '_blank') 
                {
                    event.preventDefault();  // Empêche l'ouverture d'un nouvel onglet
                    window.location.href = target.href;  // Redirige vers le même onglet
                }
            });
        
           const button = document.createElement('a');
  

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
        # Flag pour contrôler les threads
        self.running = True
        # Threads actifs
        self.active_threads = [] 
    

    def surveillance_onglet(self,driver):
        try:
         intervalle_check = 2  # Vérification toutes les 30 secondes
         self.initialHandles =driver.window_handles
         waitTime = int(os.environ.get('InactivityTimeMinutes'))   # exemple 300 secondes = 5 minutes 
         while True:
             time.sleep(intervalle_check)       
             current_handles = driver.window_handles
             if len(current_handles) > 1 : 
                self.inject_button(driver)  # Injecter le bouton dans le nouvel onglet
        except:
            print("Fin surveillance Onglet")

    def surveiller_inactivite(self,driver):
        try:
            temps_inactif = 0
            dernier_contenu = hash(driver.page_source[:1000]) # Contenu initial de la page        
            intervalle_check = 2  # Vérification toutes les 30 secondes       
            waitTime = int(os.environ.get('InactivityTimeMinutes'))   # exemple 300 secondes = 5 minutes
            #print(waitTime)
            while True:                
                time.sleep(intervalle_check)
                
                try:
                    # Libérer les ressources inutilisées périodiquement
                    if hasattr(driver, "execute_cdp_cmd"):
                        driver.execute_cdp_cmd("Network.clearBrowserCache", {})
                    nouveau_contenu = hash(driver.page_source[:1000])
                except:
                    driver.switch_to.window(driver.window_handles[0]) 
                    nouveau_contenu = hash(driver.page_source[:1000])
                print("avant")
                print(temps_inactif)
                if nouveau_contenu == dernier_contenu:
                    temps_inactif += intervalle_check
                else:
                    temps_inactif = 0  # Réinitialiser le compteur d'inactivité
                    dernier_contenu = nouveau_contenu 
                print("apres")
                print(temps_inactif)
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
            driver.switch_to.window(driver.window_handles[0])
        except:
            print("End of closing process")

     
    # Fonction pour injecter le bouton dans un onglet donné
    def inject_button(self,driver):
        try:
            # Vérifier si le bouton existe déjà
            current =driver.window_handles[len(driver.window_handles)-1]
            driver.switch_to.window(current) 
            button_exists = driver.execute_script("""return document.getElementById('close-all-btn-gemini') !== null;""")
        
            if not button_exists:
                print("bouton ajout")     
                
                driver.execute_script(self.inject_button_script)    
                surveillance_thread = threading.Thread(target=self.surveiller_Url, args=(driver,))
                surveillance_thread.daemon=True
                surveillance_thread.start()  
                self.active_threads.append(surveillance_thread)  
                print("bouton cree")
                self.active_threads = [t for t in self.active_threads if t.is_alive()]
            
            # si on a plusieurs onglets
            if  len(driver.window_handles)>2:
                
                print("trop de tab")
                driver.switch_to.window(driver.window_handles[1]) 
                driver.close()  
                driver.switch_to.window(current) 
                    
        except Exception as e:
            print(e)

    def demarrer_surveillance(self, driver):
        """Démarre tous les threads de surveillance en parallèle."""
        print("Démarrage de la surveillance complète")
        self.running = True
        
        # Thread pour surveiller l'ouverture de nouveaux onglets
        onglet_thread = threading.Thread(target=self.surveillance_onglet, args=(driver,))
        onglet_thread.daemon = True
        
        # Thread pour surveiller l'inactivité
        inactivite_thread = threading.Thread(target=self.surveiller_inactivite, args=(driver,))
        inactivite_thread.daemon = True
        
        # Démarrer les threads
        onglet_thread.start()
        inactivite_thread.start()
        
        # Garder une référence aux threads actifs
        self.active_threads = [onglet_thread, inactivite_thread]
        
        print("Tous les threads de surveillance sont démarrés")
        
        return onglet_thread, inactivite_thread
    
    def arreter_surveillance(self):
        """Arrête tous les threads de surveillance."""
        print("Arrêt de la surveillance")
        self.running = False
        
        # Attendre que tous les threads se terminent (avec timeout)
        for thread in self.active_threads:
            if thread.is_alive():
                thread.join(timeout=5)
        
        self.active_threads = []
        print("Tous les threads de surveillance sont arrêtés")