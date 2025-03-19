import time 
import os 
import logging
import threading
from typing import List, Optional

class WatchHelper:
    def __init__(self):
        self.initial_handles: Optional[List[str]] = None
        
        self.inject_button_script = """
           document.body.addEventListener('click', function(event) 
           {
                let target = event.target;
                console.log('interception');
            
                console.log(target.tagName);
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
        
        # Variables centralisées pour suivre l'inactivité
        self.temps_inactif = 0
        self.dernier_contenu_page = None
        self.dernier_onglet_actif = None
        self.lock = threading.Lock()  # Pour protéger l'accès aux variables partagées
        
        # Intervalle et temps d'attente
        self.intervalle_check = 2  # Vérification toutes les 2 secondes
    
    def reset_inactivity(self):
        """Réinitialise le compteur d'inactivité de manière thread-safe"""
        with self.lock:
            self.temps_inactif = 0
            print("Compteur d'inactivité réinitialisé")
            
    def increment_inactivity(self):
        """Incrémente le compteur d'inactivité de manière thread-safe"""
        with self.lock:
            self.temps_inactif += self.intervalle_check
            return self.temps_inactif

    def get_inactivity(self):
        """Récupère la valeur actuelle du compteur d'inactivité"""
        with self.lock:
            return self.temps_inactif

    def surveillance_onglet(self, driver):
        """Surveille l'ouverture et le changement d'onglets"""
        try:
            self.initial_handles = driver.window_handles
            self.dernier_onglet_actif = driver.current_window_handle
            
            while self.running:
                time.sleep(self.intervalle_check)
                
                try:
                    # Vérifier si de nouveaux onglets ont été ouverts
                    current_handles = driver.window_handles
                    current_handle = driver.current_window_handle
                    
                    # Si un nouvel onglet est ouvert
                    if len(current_handles) > 1:
                        self.inject_button(driver)
                    
                    # Si l'onglet actif a changé
                    if current_handle != self.dernier_onglet_actif:
                        print(f"Changement d'onglet détecté: {self.dernier_onglet_actif} -> {current_handle}")
                        self.dernier_onglet_actif = current_handle
                        # Réinitialiser le temps d'inactivité car changement d'onglet
                        self.reset_inactivity()
                        
                except Exception as e:
                    print(f"Erreur lors de la surveillance d'onglet: {e}")
                    try:
                        # Essayer de revenir à l'onglet principal
                        driver.switch_to.window(driver.window_handles[0])
                        self.dernier_onglet_actif = driver.current_window_handle
                    except:
                        pass
                        
        except Exception as e:
            print(f"Fin surveillance Onglet: {e}")

    def surveiller_activite(self, driver):
        """Thread principal de surveillance qui vérifie le contenu et incrémente le temps d'inactivité"""
        try:
            # Initialiser le temps d'attente max
            wait_time = int(os.environ.get('InactivityTimeMinutes', '5')) 
            
            # Initialiser le contenu de la page
            try:
                self.dernier_contenu_page = hash(driver.page_source[:1000])
            except:
                driver.switch_to.window(driver.window_handles[0])
                self.dernier_contenu_page = hash(driver.page_source[:1000])
            
            while self.running:
                time.sleep(self.intervalle_check)
                
                try:
                    # Libérer les ressources inutilisées périodiquement
                    if hasattr(driver, "execute_cdp_cmd"):
                        driver.execute_cdp_cmd("Network.clearBrowserCache", {})
                    
                    # Vérifier le contenu de la page actuelle
                    nouveau_contenu = hash(driver.page_source[:1000])
                    
                    # Si le contenu a changé, réinitialiser le compteur d'inactivité
                    if nouveau_contenu != self.dernier_contenu_page:
                        print("Changement de contenu détecté")
                        self.dernier_contenu_page = nouveau_contenu
                        # Réinitialiser le temps d'inactivité car changement de contenu
                        self.reset_inactivity()
                    else:
                        # Incrémenter le temps d'inactivité si pas de changement
                        temps_actuel = self.increment_inactivity()
                        print(f"Temps d'inactivité: {temps_actuel} secondes")
                        
                        # Vérifier si le temps d'inactivité a atteint le seuil
                        if temps_actuel >= wait_time:
                            print(f"Temps d'inactivité maximum atteint: {temps_actuel} secondes")
                            self.FermerOngletSupp(driver)
                            driver.switch_to.window(driver.window_handles[0])
                            driver.get(os.environ.get('DefaultUrl'))
                            self.reset_inactivity()  # Réinitialiser après le reset
                
                except Exception as e:
                    print(f"Erreur lors de la vérification de contenu: {e}")
                    try:
                        driver.switch_to.window(driver.window_handles[0])
                        self.dernier_contenu_page = hash(driver.page_source[:1000])
                    except:
                        pass
                    
        except Exception as e:
            print(f"Fin de la surveillance d'activité: {e}")

    def FermerOngletSupp(self, driver):
        """Ferme tous les onglets supplémentaires"""
        try:
            # Obtenir les handles des fenêtres ouvertes
            window_handles = driver.window_handles
            
            # Fermer les onglets à droite (index supérieur à l'onglet actif)
            for handle in window_handles[1:]:
                driver.switch_to.window(handle)
                try:
                    driver.close()
                except Exception as e:
                    print(f"Erreur fermeture onglet: {e}")
            
            # Revenir à l'onglet actif
            driver.switch_to.window(driver.window_handles[0])
        except Exception as e:
            print(f"Erreur lors de la fermeture des onglets: {e}")

    def inject_button(self, driver):
        """Injecte le bouton 'Back to Gemini' dans un nouvel onglet"""
        try:
            # Passer au dernier onglet ouvert
            current = driver.window_handles[-1]
            driver.switch_to.window(current)
            
            # Vérifier si le bouton existe déjà
            button_exists = driver.execute_script("""return document.getElementById('close-all-btn-gemini') !== null;""")
            
            if not button_exists:
                print("Ajout du bouton")
                driver.execute_script(self.inject_button_script)
                print("Bouton créé avec succès")
            
            # Si on a plus de 2 onglets, fermer le second (garder le premier et le dernier)
            if len(driver.window_handles) > 2:
                print("Trop d'onglets ouverts, fermeture du second")
                driver.switch_to.window(driver.window_handles[1])
                driver.close()
                driver.switch_to.window(current)
                
        except Exception as e:
            print(f"Erreur lors de l'injection du bouton: {e}")

    def demarrer_surveillance(self, driver):
        """Démarre tous les threads de surveillance en parallèle."""
        print("Démarrage de la surveillance complète")
        self.running = True
        self.reset_inactivity()  # Réinitialiser le compteur au démarrage
        
        # Thread pour surveiller l'ouverture de nouveaux onglets
        onglet_thread = threading.Thread(target=self.surveillance_onglet, args=(driver,))
        onglet_thread.daemon = True
        
        # Thread pour surveiller l'inactivité (contenu et URL combinés)
        activite_thread = threading.Thread(target=self.surveiller_activite, args=(driver,))
        activite_thread.daemon = True
        
        # Démarrer les threads
        onglet_thread.start()
        activite_thread.start()
        
        # Garder une référence aux threads actifs
        self.active_threads = [onglet_thread, activite_thread]
        
        print("Tous les threads de surveillance sont démarrés")
        
        return onglet_thread, activite_thread
    
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