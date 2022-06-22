#/usr/bin/python3.10

import enquiries
import configparser
import os 

config_path = f"{os.path.abspath( os.path.dirname( __file__ ) )}/config"
config = configparser.ConfigParser()
config.read(config_path)



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
    compte = enquiries.freetext(t["compte"])
    mdp = enquiries.freetext(t["mdp"])
    lc.append(f"{compte},{mdp}")
    for i in range(5):
        if enquiries.confirm(t["next"], default = True, single_key = True):
            compte = enquiries.freetext(t["compte"])
            mdp = enquiries.freetext(t["mdp"])
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
    if enquiries.confirm(t["fidelity"], single_key = True):
        lien = enquiries.freetext(t["lien"])
        edit_config(7,lien)
    
def discord():
    enabled = enquiries.confirm(t["discorde"], single_key = True, default = True)
    if enabled : 
        edit_config(13, True)
        w1 = enquiries.freetext(t["w1"])
        edit_config(14,w1)
        w2 = enquiries.freetext(t["w2"])
        edit_config(15,w2)
        
def sql() :
    enabled = enquiries.confirm(t["msqle"], single_key = True, default = False)
    if enabled : 
        edit_config(25, True)
        lien = enquiries.freetext(t["msqll"])
        edit_config(26,lien)
        table = enquiries.freetext(t["msqlt"])
        edit_config(27,table)
        user = enquiries.freetext(t["msqlu"])
        edit_config(28,user)
        pwd = enquiries.freetext(t["msqlp"])
        edit_config(29,pwd)
     
def proxy() :
    enabled = enquiries.confirm(t["proxye"], single_key = True, default = False)
    if enabled : 
        edit_config(19, True)
        lien = enquiries.freetext(t["proxyl"])
        edit_config(20,lien)
        port = enquiries.freetext(t["proxyp"])
        edit_config(21,port)
     

LogPath = config["PATH"]["logpath"]
if LogPath == "/your/path/to/loginandpass.csv" :
    setup()
else :
    os.system("python3.10 V4.py")
