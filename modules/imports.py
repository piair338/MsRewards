import argparse
import asyncio
import configparser
import pickle
from csv import reader
from datetime import datetime, timedelta
from os import path, sys, system
from random import choice, randint, shuffle, uniform
from re import findall, search
from sys import platform
from time import sleep, time

from discord import Colour, Embed, File, RequestsWebhookAdapter, Webhook
from pyotp import TOTP
from pyvirtualdisplay import Display
from pyvirtualdisplay.smartdisplay import SmartDisplay
from requests import get
from selenium import webdriver
from selenium.common import exceptions
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        NoSuchElementException,
                                        StaleElementReferenceException,
                                        TimeoutException, WebDriverException)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
try:
    import enquiries
except:
    system("")  # enable colors in windows cmd