#/usr/bin/python3.10

import configparser
import os 
print
config_path = f"{os.path.abspath( os.path.dirname( __file__ ) )}/config"
config = configparser.ConfigParser()
config.read(config_path)

def confirm(texte, default = False):
    if default : 
        txt = '[y/N]'
    else :
        txt = '[Y/n]'
    
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
    "next" : "voulez vous ajouter un compte ?",
    "finc" : "comptes en cours d'ajout",
    "ajout" : "comptes ajouté",
    "fidelity" : "avez vous un lien sur lequel le lien vers la page fidelité du mois est le seul contenu de la page ?",
    "lien" : "entrez le lien",
    "discorde" : "voulez vous envoyer les points sur discord ?",
    "w1" : "entrez le lien du WebHook pour envoyer les points (https://support.discord.com/hc/fr/articles/228383668-Utiliser-les-Webhooks)",
    "w2" : "entrez le lien du WebHook pour envoyer les erreurs",
    "msqle" : "voulez vous untiliser une base de donnée",
    "msqll" : "entrez le lien de la base de donnée",
    "msqlu" : "entrez l'utilisateur de la base de donnée",
    "msqlp" : "entrez le mot de passe de la base de donnée",
    "msqlt" : "entrez le nom de la table de la base de donnée",
    "proxye" : "voulez vous utiliser un proxy",
    "proxyl" : "entrez le lien du proxy",
    "proxyp" : "entrez le port du proxy"

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
            lc.append(f"{compte},{mdp}\n")
        else:
            print(t["finc"])
            break
    f = open('./login.csv', "w")
    for i in lc :
        f.write(i)
    f.close()
    print(t["ajout"])

    #modifie le fichier de configuration
    edit_config(3,f'{os.getcwd()}/login.csv')


def edit_config(ligne, contenu):
    f = open(config_path, "r")
    txt = f.readlines()
    txt[ligne] = f'{txt[ligne].split("=")[0]}= {contenu}\n'
    f.close()

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
        edit_config(7,lien)
    
def discord():
    enabled = confirm(t["discorde"], default = True)
    if enabled : 
        edit_config(13, True)
        w1 = input(t["w1"])
        edit_config(14,w1)
        w2 = input(t["w2"])
        edit_config(15,w2)
        
def sql() :
    enabled = confirm(t["msqle"], default = False)
    if enabled : 
        edit_config(25, True)
        lien = input(t["msqll"])
        edit_config(26,lien)
        table = input(t["msqlt"])
        edit_config(27,table)
        user = input(t["msqlu"])
        edit_config(28,user)
        pwd = input(t["msqlp"])
        edit_config(29,pwd)
     
def proxy() :
    enabled = confirm(t["proxye"], default = False)
    if enabled : 
        edit_config(19, True)
        lien = input(t["proxyl"])
        edit_config(20,lien)
        port = input(t["proxyp"])
        edit_config(21,port)
     

LogPath = config["PATH"]["logpath"]
if LogPath == "/your/path/to/loginandpass.csv" :
    setup()
else :
    os.system("python3.10 V4.py")
