from helper.csvHelper import CsvHelper
from helper.EnvFileManager import EnvFileManager
from flask import Flask, request, render_template,redirect
import csv
import os 

app = Flask(__name__)
# Configuration du dossier de destination
UPLOAD_FOLDER = r"/var/gemini"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def welcome():
    env_manager = EnvFileManager('/var/gemini/sources/GeminiPrompt/.env')
    
    # Afficher le contenu actuel
    print("Contenu initial:")
    print(env_manager.get_content())
    InactivityTimeMinutes=env_manager.get_value('InactivityTimeMinutes')
    screensaver=env_manager.get_value('ScreenSaver')
    ScreenSaverText = "Disabled" if screensaver == "0" else "Enabled"
    csvpath=env_manager.get_value('CSVPath')
    csvHelper = CsvHelper(csvpath)
    nbprompts=csvHelper.get_nb_prompts() 
    prompts=csvHelper.get_prompts()
    return render_template('index.html', inactivity=InactivityTimeMinutes,screensaverstate=ScreenSaverText, nbPrompts=nbprompts, data=prompts)

@app.route('/screensaver')
def screensaver():
    return render_template("screenSaver.html")
@app.route('/screensaverconfig', methods=["GET", "POST"])
def screensaverconfig():
    geminiurl="https://gemini.google.com/app"
    env_manager = EnvFileManager('/var/gemini/sources/GeminiPrompt/.env') 
    screensaver=env_manager.get_value('ScreenSaver')
    if request.method == "POST": 
        if("chkenabled" in request.form):
            file = request.files.get("file") 
            if file and file.filename.endswith(".html"):
                filepath = os.path.join("./templates", "screenSaver.html")
                file.save(filepath)
                print(f"Fichier sauvegardé : {filepath}")
                env_manager.set_value('DefaultUrl','http://127.0.0.1:5000/screensaver')
                env_manager.set_value('ScreenSaver',1)
                env_manager.save()
                screensaver=1 
                return redirect("/", code=302)   
            else:
                return render_template("Erreur.html") 
        else:
                print("Desactivation")
                env_manager.set_value('DefaultUrl',geminiurl)
                env_manager.set_value('ScreenSaver',0)
                env_manager.save()
                return redirect("/", code=302)   
    
    return render_template("screenSaverconfig.html",screensaver=screensaver )


@app.route('/redirection', methods=["GET", "POST"])
def redirection():
    try:
        env_manager = EnvFileManager('/var/gemini/sources/GeminiPrompt/.env')
        screensaver=env_manager.get_value('ScreenSaver')
        if request.method == "POST":
            inactivity = request.form['txtIdle']
            if(inactivity.isdigit() and float (inactivity) > 0):
                env_manager.set_value('InactivityTimeMinutes',inactivity)         
            url = request.form['txtRedirect']
            env_manager.set_value('DefaultUrl', url)
            InactivityTimeMinutes=env_manager.get_value('InactivityTimeMinutes')
            DefaultUrl=env_manager.get_value('DefaultUrl')
            env_manager.save()
            return render_template("redirection.html", inactivity=InactivityTimeMinutes, url=DefaultUrl,screesaver=screensaver)
        InactivityTimeMinutes=env_manager.get_value('InactivityTimeMinutes')
        DefaultUrl=env_manager.get_value('DefaultUrl')
        return render_template("redirection.html", inactivity=InactivityTimeMinutes, url=DefaultUrl,screesaver=screensaver)
    except Exception as e:
        return render_template("Erreur.html")

@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    rows = []
    headers = []
    if request.method == "POST":
        file = request.files.get("file") 
        if file and file.filename.endswith(".csv"):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], "prompts.csv")
            file.save(filepath)
            print(f"Fichier sauvegardé : {filepath}")

            # Lecture du fichier CSV
            with open(filepath, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                headers = next(reader, [])
                rows = list(reader)
        return render_template('confirm.html') 
    else:
        return render_template('upload.html') #render_template_string(html_form, headers=headers, rows=rows)

if __name__ == '__main__':
    app.run(debug=True)
