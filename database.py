import mysql.connector
import configparser
from os import path
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "-f", 
    "--file", 
    help="Choose a file", 
    type=argparse.FileType('r')
)

args = parser.parse_args()


config_path = "./user_data/config.cfg"
config = configparser.ConfigParser()
config.read(config_path)

sql_usr = config["SQL"]["usr"]
sql_pwd = config["SQL"]["pwd"]
sql_host = config["SQL"]["host"]
sql_database = config["SQL"]["database"]


mydb = mysql.connector.connect(
    host=sql_host,
    user=sql_usr,
    password=sql_pwd,
    database = sql_database
)
mycursor = mydb.cursor()

def add_account(name: str, endroit: str, proprio: str):
    command = f'INSERT INTO comptes (compte, proprio, endroit, last_pts) VALUES ("{name}", "{proprio}", "{endroit}",0);'
    mycursor.execute(command)


def ban_account(name: str, pts = 0):

    command1 = f"INSERT INTO banned (nom, total) VALUES ('{name}', {pts});"
    command2 = f'DELETE FROM comptes WHERE compte = "{name}";'
    mycursor.execute(command1)
    mycursor.execute(command2)

def update_pts(name: str, pts = 0):
    pass


print("ajouter un compte : 1\nban un compte : 2")
i = input()
if i == "1":
    if args.file :
        l =[x.split(",")[0] for x in args.file.readlines()] 
        endroit = input("ou est le bot ? ")
        proprio = input("qui est le proprio ? ")
        for name in l :
            add_account(name, endroit, proprio)
    else : 
        name = input("quel est le nom ? ").split("@")[0]
        endroit = input("ou est le bot ? ")
        proprio = input("qui est le proprio ? ")
        add_account(name, endroit, proprio)
elif i == '2':
    name = input("quel est le compte qui a été ban ? ")
    pts = input("il avait combien de points ? ")
    ban_account(name, pts)

mydb.commit()
mycursor.close()
mydb.close()
