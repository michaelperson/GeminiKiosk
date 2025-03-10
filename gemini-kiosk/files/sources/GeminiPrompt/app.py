import time
import sys
import os
import threading
import subprocess
import logging

from helpers.rfidPcscdReader import RFIDPCSCReader
from helpers.csvHelper import CsvHelper
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from helpers.promptHelper import PromptHelper
from helpers.watchHelper import WatchHelper
from helpers.systemHelper import SystemHelper
from smartcard.util import toHexString
from time import sleep
load_dotenv()
driver=None

recent_tags={}




# récupération tag
def on_rfid_tag(tag):
    if(tag==""):
        return
    global recent_tags
    current_time = time.time()

    # Vérifier si le tag a déjà été reçu dans les 5 dernières secondes
    if tag in recent_tags and current_time - recent_tags[tag] < 5:
        print(f"Tag {tag} ignoré (déjà reçu récemment)")
        return

    # Mettre à jour le timestamp du tag
    recent_tags[tag] = current_time
    pHelper= PromptHelper() 
    prompt=tag #f"{toHexString(tag)}"

    #récupération du prompt via le csv
  
    csvHelper = CsvHelper(os.environ.get('CSVPath'))
    prompt= csvHelper.get_prompt(prompt,os.environ.get('Lang'))
    if(prompt!=None):
        thread = pHelper.run_in_thread(prompt, driver)
        thread.join()  # Attendre que le thread se termine avant de continuer
        # surveillance_thread = threading.Thread(target=wHelper.surveiller_inactivite, args=(driver,))
        # surveillance_thread.start()        
        # surveillance_thread = threading.Thread(target=wHelper.surveillance_onglet, args=(driver,))
        # surveillance_thread.start()
        wHelper.demarrer_surveillance(driver) 
    # Nettoyer le dictionnaire pour éviter qu'il ne grossisse indéfiniment
    recent_tags = {t: ts for t, ts in recent_tags.items() if current_time - ts < 5}

if __name__ == "__main__":
    print("Configuration :")
    print(f"CSVPath: {os.environ.get('CSVPath')}")
    print(f"Profil: {os.environ.get('HOME')+'/.config/google-chrome/default'}")    
    print(f"InactivityTimeSecondes: {os.environ.get('InactivityTimeMinutes')}")
    print(f"Default URL: {os.environ.get('DefaultUrl')}")    
    print(f"MustRead: {os.environ.get('MustRead')}")   
    print(f"Language: {os.environ.get('Lang')}")
   
    sHelper = SystemHelper()
    wHelper= WatchHelper()

    # Désactiver les logs de Selenium
    logging.getLogger('selenium').setLevel(logging.CRITICAL) 
   # Configuration du navigateur
    profil=os.environ.get('HOME')+'/.config/google-chrome/default'
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-new-window")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--log-level=3")  
    options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
    options.add_experimental_option("useAutomationExtension", False) 
    options.add_argument(fr'--user-data-dir={profil}')
    # Set profile directory
    options.add_argument('--profile-directory=Profile 1')
    options.add_argument("--kiosk") 
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options) 
    driver.get(os.environ.get('DefaultUrl'))
    
    # Ouvrir la page de gemini 
    #reader = RFIDPCSCReader()
    #reader.set_callback(on_rfid_tag)
   # reader.start()
    # surveillance_thread = threading.Thread(target=wHelper.surveiller_inactivite, args=(driver,))
    # surveillance_thread.start()        
    # surveillance_thread = threading.Thread(target=wHelper.surveillance_onglet, args=(driver,))
    # surveillance_thread.start() 
    wHelper.demarrer_surveillance(driver) 
    
    try:
        while True:
            sleep(1)
            if not driver.window_handles:  
                print("Le navigateur est fermé.")
                driver.quit()
    except KeyboardInterrupt:
        # try:
        #    # reader.stop()
        # except:
            
            print("Reader Disconnected")
    except:
        # try:
        #    # reader.stop()
        # except:
            
            print("Reader Disconnected")
       
    finally:

        wHelper.arreter_surveillance() 
        driver.quit()
    print("Apllication closed")
