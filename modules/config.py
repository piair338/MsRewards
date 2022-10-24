#!/usr/bin/python3.10
import configparser
from csv import reader
from os import sys, system, path
from sys import platform
import argparse
from discord import (  # Importing discord.Webhook and discord.RequestsWebhookAdapter
    RequestsWebhookAdapter,
    Webhook,
)
from time import time


"""
Setup for option, like --override or --fulllog
"""

parser = argparse.ArgumentParser()

parser.add_argument(
    "-o", "--override", help="override", dest="override", action="store_true"
)
parser.add_argument(
    "-l", "--log", dest="log", help="enable logging in terminal", action="store_true"
)
parser.add_argument(
    "-fl",
    "--fulllog",
    dest="fulllog",
    help="enable full logging in discord",
    action="store_true",
)
parser.add_argument(
    "-r", "--risky", help="make the program faster, probably better risk of ban", dest="fast", action="store_true"
)

parser.add_argument(
    "-c", "--config", help="Choose a specific config file", type=argparse.FileType('r')
)

args = parser.parse_args()
CUSTOM_START = args.override
LOG = args.log
FULL_LOG = args.fulllog
FAST = args.fast
if CUSTOM_START :
    LOG = True

# gloabal variables used later in the code
LINUX_HOST = platform == "linux" # if the computer running this programm is linux, it allow more things 
START_TIME = time()
driver = None


if LINUX_HOST:
    import enquiries
else:
    system("")  # enable colors in windows cmd

#reading configuration

config_path = f"{path.abspath( path.dirname( __file__ ) )}/user_data/config.cfg"
if args.config :
    config_path = path.abspath(args.config.name)



config = configparser.ConfigParser()
config.read(config_path)

# path configurations
MotPath = config["PATH"]["motpath"]
CREDENTIALS_PATH = config["PATH"]["logpath"]


# discord configuration
DISCORD_SUCCESS_LINK = config["DISCORD"]["successlink"]
DISCORD_ERROR_LINK = config["DISCORD"]["errorlink"]
DISCORD_ENABLED_ERROR = config["DISCORD"]["DiscordErrorEnabled"] == "True"
DISCORD_ENABLED_SUCCESS = config["DISCORD"]["DiscordSuccessEnabled"]== "True"

if DISCORD_ENABLED_ERROR:
    webhookFailure = Webhook.from_url(DISCORD_ERROR_LINK, adapter=RequestsWebhookAdapter())
if DISCORD_ENABLED_SUCCESS:
    webhookSuccess = Webhook.from_url(DISCORD_SUCCESS_LINK, adapter=RequestsWebhookAdapter())

# base settings
FidelityLink = config["SETTINGS"]["FidelityLink"]
DISCORD_EMBED = config["SETTINGS"]["embeds"] == "True" #print new point value in an embed
Headless = config["SETTINGS"]["headless"] == "True"

# proxy settings
proxy_enabled = config["PROXY"]["proxy_enabled"] == "True"
proxy_address = config["PROXY"]["url"]
proxy_port = config["PROXY"]["port"]

# MySQL settings
sql_enabled = config["SQL"]["sql_enabled"] == "True"
sql_usr = config["SQL"]["usr"]
sql_pwd = config["SQL"]["pwd"]
sql_host = config["SQL"]["host"]
sql_database = config["SQL"]["database"]

# Other seetings 
IPV6_CHECKED = config["OTHER"]["ipv6"]
CLAIM_AMAZON = config["OTHER"]["claim_amazon"]


g = open(MotPath, "r", encoding="utf-8")
lines = g.readlines()
if len(lines) < 3 : 
    Liste_de_mot = list(lines[0].split(","))
else :
    Liste_de_mot = [x.replace('\n', "") for x in lines]
g.close()


