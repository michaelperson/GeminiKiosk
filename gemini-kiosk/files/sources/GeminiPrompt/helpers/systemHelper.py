import subprocess
class SystemHelper:
    #Fonction pour exécuter un autre script Python
    def run_external_script(self, path):
        subprocess.run(["python", path])