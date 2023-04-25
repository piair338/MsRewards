#!/usr/bin/python3.10
from modules.driver_tools import *
from modules.imports import *
import modules.globals as g
"""
Setup for option, like --override or --fulllog
"""

parser = argparse.ArgumentParser()

parser.add_argument(
    "-o", 
    "--override", 
    help="override", 
    dest="override", 
    action="store_true"
)

parser.add_argument(
    "-u", 
    "--unban", 
    help="unban an account", 
    dest="unban", 
    action="store_true"
)

parser.add_argument(
    "-l",
    "--log", 
    dest="log", 
    help="enable logging in terminal", 
    action="store_true"
)

parser.add_argument(
    "-fl",
    "--fulllog",
    dest="fulllog",
    help="enable full logging in discord",
    action="store_true",
)

parser.add_argument(
    "-c", 
    "--config", 
    help="Choose a specific config file", 
    default=""
)

parser.add_argument(
    "-a", 
    "--add-points", 
    help="Add points to the database from a file and exit",
    dest="points_file",
    default=""
)

parser.add_argument( 
    "-v", 
    "--vnc",
    help="enable VNC",
    dest="vnc",
    default="None"
)

parser.add_argument( 
    "--version",
    help="display a message on discord to tell that the bot have been updated",
    dest="update_version",
    default="None"
)

parser.add_argument(
    "--dev", 
    help="dev option", 
    dest="dev", 
    action="store_true"
)


args = parser.parse_args()

g.custom_start = args.override
g.unban = args.unban
g.log = args.log
g.full_log = args.fulllog
g.dev = args.dev

if g.custom_start :
    g.log = True

g.vnc_enabled = args.vnc != "None"
g.vnc_port = args.vnc
g.points_file = args.points_file
g.update_version = args.update_version
# global variables used later in the code
g.islinux = platform == "linux" # if the computer running this program is Linux, it allow more things 
g.start_time = time()

#reading configuration
config = configparser.ConfigParser()

if args.config :
    try :
        config_path  =f"{path.abspath(path.dirname(path.dirname( __file__ )))}/user_data/config{args.config}.cfg"
        config.read(config_path)
        g.mot_path = config["PATH"]["motpath"]
    except :
        config_path = path.abspath(args.config)
        config.read(config_path)
else : 
    config_path = f"{path.abspath(path.dirname(path.dirname( __file__ )))}/user_data/config.cfg"
    config.read(config_path)


# path configurations
g.mot_path = config["PATH"]["motpath"]
g.credential_path = config["PATH"]["logpath"]


# discord configuration
g.discord_success_link = config["DISCORD"]["successlink"]
g.discord_error_link = config["DISCORD"]["errorlink"]
g.discord_enabled_error = config["DISCORD"]["DiscordErrorEnabled"] == "True"
g.discord_enabled_success = config["DISCORD"]["DiscordSuccessEnabled"]== "True"
try :
    g.avatar_url = config["OTHER"]["avatar"] 
except :
    g.avatar_url = "https://cdn.discordapp.com/icons/793934298977009674/d8055bccef6eca4855c349e808d0d788.webp"
    
if g.discord_enabled_error:
    webhookFailure = Webhook.from_url(g.discord_error_link, adapter=RequestsWebhookAdapter())
if g.discord_enabled_success:
    webhookSuccess = Webhook.from_url(g.discord_success_link, adapter=RequestsWebhookAdapter())

# base settings
g.fidelity_link = config["SETTINGS"]["FidelityLink"]
g.discord_embed = config["SETTINGS"]["embeds"] == "True" #print new point value in an embed
g.headless = config["SETTINGS"]["headless"] == "True"

# proxy settings
g.proxy_enabled = config["PROXY"]["proxy_enabled"] == "True"
g.proxy_address = config["PROXY"]["url"]
g.proxy_port = config["PROXY"]["port"]

# MySQL settings
g.sql_enabled = config["SQL"]["sql_enabled"] == "True"
g.sql_usr = config["SQL"]["usr"]
g.sql_pwd = config["SQL"]["pwd"]
g.sql_host = config["SQL"]["host"]
g.sql_database = config["SQL"]["database"]


h = open(g.mot_path, "r", encoding="utf-8")
lines = h.readlines()
if len(lines) < 3 : 
    Liste_de_mot = list(lines[0].split(","))
else :
    Liste_de_mot = [x.replace('\n', "") for x in lines]
h.close()


with open(g.credential_path) as f:
    reader = reader(f)
    Credentials = list(reader)
shuffle(Credentials)
g._cred = Credentials

if g.proxy_enabled :
    setup_proxy(g.proxy_address,g.proxy_port)
