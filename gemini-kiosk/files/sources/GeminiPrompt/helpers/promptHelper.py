import os  
import time
import threading
from helpers.chromeHelper import ChromeHelper
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class PromptHelper:
    def ___envoyer_prompt_gemini(self, prompt, driver):
        cHelper = ChromeHelper()
        lang  = cHelper.get_chrome_language()
        if(lang == "" or lang == None): lang =os.environ.get('Lang')
        print(len(driver.window_handles))
        if len(driver.window_handles)>1:
           print("Trop de tab") 
           self.FermerOngletSupp(driver)

        # Ouvrir la page de gemini
        driver.get(f"https://gemini.google.com/app?hl={lang}")
        #temporisation de la page de gemini
        time.sleep(1)
        print("Stqrting...")
        # Localisation du champ d'entrée du prompt
        actions = ActionChains(driver)
        input_field = driver.find_element(By.CLASS_NAME, "ql-editor")
        print (input_field)
        print (prompt)
        actions.move_to_element(input_field).click().send_keys(prompt).perform()

        # Envoyer le prompt
        actions.send_keys(Keys.ENTER).perform()

        # Attendre les résultats
        print("Prompt sended. waiting result...") 
        #lire le résultat du prompt
        print(f"Read : {os.environ.get('MustRead')}")
        if(os.environ.get('MustRead')=='true'):
            try:
                son_icon = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.mat-mdc-tooltip-trigger.tts-button")))
                son_icon.click()
            except:
                print("L'icône de son n'a pas été trouvée.")
        

    

    def run_in_thread(self, prompt, driver):
        thread = threading.Thread(target=self.___envoyer_prompt_gemini, args=(prompt,driver))
        thread.start()
        return thread


    def FermerOngletSupp(self, driver):
        # Obtenir les handles des fenêtres ouvertes
        window_handles = driver.window_handles 
        # Index de l'onglet gemini
        current_index = 0
        cpt=1
        # Fermer les onglets à droite (index supérieur à l'onglet actif)
        for handle in window_handles[current_index + 1:]:
            print(f"onglet n° {cpt}")
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
            print("end of closing process")
