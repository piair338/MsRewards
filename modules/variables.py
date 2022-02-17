#!/usr/bin/python3
"""
Module loading variables from config file
"""
import configparser

CONFIG_PATH = "./config"
config = configparser.ConfigParser()
config.read(CONFIG_PATH)

MotPath = config["DEFAULT"]["motpath"]
LogPath = config["DEFAULT"]["logpath"]
SuccessLink = config["DEFAULT"]["successlink"]
ErrorLink = config["DEFAULT"]["errorlink"]

embeds = config["DEFAULT"]["embeds"] == "True"
Headless = config["DEFAULT"]["headless"] == "True"
Log = config["DEFAULT"]["log"] == "True"
