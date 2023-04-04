#/usr/bin/python3.10

import configparser
import os 
import shutil
import requests



config = configparser.ConfigParser()

try : 
    config_path = f"{os.path.abspath( os.path.dirname( __file__ ) )}/user_data/config.cfg"
    if config.read(config_path)==[] :
        raise NameError("le fichier n'existe pas")
except :
    default_config = f"{os.path.abspath( os.path.dirname( __file__ ) )}/user_data/config.default"
    shutil.copyfile(default_config, config_path)
    config.read(config_path)


def confirm(texte, default = False):
    if default : 
        txt = '[Y/n]'
    else :
        txt = '[y/N]'
    
    yes = ['y', 'yes', 'o', 'oui']
    no = ['n', 'non', 'no']
    a = input(f"{texte} {txt}").lower()
    if a in yes :
        return True
    elif a in no :
        return False
    return default
    
lang = "fr"

text = {"fr" : {
    "compte" : "entrer l'adresse mail du compte ", 
    "mdp" : "entrez le mot de passe du compte ",
    "next" : "voulez vous ajouter un compte ? ",
    "finc" : "comptes en cours d'ajout ",
    "ajout" : "comptes ajouté ",
    "fidelity" : "avez vous un lien sur lequel le lien vers la page fidélité du mois est le seul contenu de la page ? ",
    "lien" : "entrez le lien ",
    "discorde" : "voulez vous envoyer les erreurs sur discord ? ",
    "w1" : "entrez le lien du WebHook pour envoyer les points ",
    "w2" : "entrez le lien du WebHook pour envoyer les erreurs ",
    "msqle" : "voulez vous utiliser une base de donnée ",
    "msqll" : "entrez le lien de la base de donnée ",
    "msqlu" : "entrez l'utilisateur de la base de donnée ",
    "msqlp" : "entrez le mot de passe de la base de donnée ",
    "msqlt" : "entrez le nom de la table de la base de donnée ",
    "proxye" : "voulez vous utiliser un proxy ",
    "proxyl" : "entrez le lien du proxy ",
    "proxyp" : "entrez le port du proxy "
    }
    }

t = text[lang]

def setup():
    setup_comptes()
    setup_settings()


def setup_comptes():
    lc = []
    compte = input(t["compte"])
    mdp = input(t["mdp"])
    lc.append(f"{compte},{mdp}")
    for i in range(5):
        if confirm(t["next"], default = True):
            compte = input(t["compte"])
            mdp = input(t["mdp"])
            lc.append(f"{compte},{mdp}")
        else:
            print(t["finc"])
            break
    f = open('./user_data/login.csv', "w")
    for i in lc :
        f.write(i)
        f.write("\n")
    f.close()
    print(t["ajout"])
    edit_config_txt("logpath",f'{os.getcwd()}/user_data/login.csv')


def edit_config_txt(ligne, contenu):
    f = open(config_path, "r")
    txt = f.readlines()
    f.close()
    if txt.count(txt) >1:
        raise NameError("il y a plus d'une occurence, echec de la modification")
    
    for i in range(len(txt)) :
        name = txt[i].split(" = ")[0]
        if name == ligne:
            txt[i] = name + " = " + str(contenu) + "\n"

    f = open(config_path, "w")
    for i in txt :
        f.write(i)
    f.close()


def setup_settings():
    general()
    discord()
    proxy()
    sql()


def general():
    if confirm(t["fidelity"]):
        lien = input(t["lien"])
        edit_config_txt('FidelityLink',lien)
    

def discord():
    enabled = confirm(t["discorde"], default = True)
    if enabled : 
        edit_config_txt("DiscordErrorEnabled", True)
        
        edit_config_txt('DiscordSuccessEnabled', confirm("send success ?", default = True))
        w1 = input(t["w1"])
        edit_config_txt("successlink",w1)
        w2 = input(t["w2"])
        edit_config_txt("errorlink",w2)
        
        
def sql() :
    enabled = confirm(t["msqle"], default = False)
    if enabled : 
        edit_config_txt("sql_enabled", True)
        lien = input(t["msqll"])
        edit_config_txt("host",lien)
        table = input(t["msqlt"])
        edit_config_txt("database",table)
        user = input(t["msqlu"])
        edit_config_txt("usr",user)
        pwd = input(t["msqlp"])
        edit_config_txt("pwd",pwd)


def proxy() :
    enabled = confirm(t["proxye"], default = False)
    if enabled : 
        edit_config_txt("proxy_enabled", True)
        lien = input(t["proxyl"])
        edit_config_txt("url",lien)
        port = input(t["proxyp"])
        edit_config_txt("port",port)


def check_update():
    try : 
        latest = requests.get("https://api.github.com/repos/piair338/MsRewards/releases").json()[0]["tag_name"]
    except Exception as e :
        print(e) 
        return ()
    f = open("./version", 'r')
    txt = f.readlines()[0].replace("\n","")
    f.close()
    if (txt == latest) :
        print("Already up to date.")
    else :
        print(f"updating to {latest}")
        os.system("git pull")
        print("updated")


LogPath = config["PATH"]["logpath"]
if LogPath == "/your/path/to/loginandpass.csv" :
    setup()
else :
    check_update()
    os.system("python3 V5.py")
