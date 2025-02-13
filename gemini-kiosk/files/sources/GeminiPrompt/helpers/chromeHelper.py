
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class ChromeHelper:
    def get_chrome_language(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Lancement en mode sans interface graphique
        chrome_options.add_argument("--remote-debugging-port=9222")  # Debugging pour interagir avec Chrome
        
        # Instancier le driver
        driver = webdriver.Chrome(options=chrome_options)
        try:
            # Naviguer vers une page pour initialiser le driver
            driver.get("chrome://settings/")        
            # Récupérer la langue via JavaScript
            language = driver.execute_script("return navigator.language || navigator.userLanguage;")
            return language
        finally:
            driver.quit()