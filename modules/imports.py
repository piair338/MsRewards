import asyncio
import csv
from os import sys, system, path
from random import choice, randint, shuffle, uniform
from re import findall, search
from sys import platform
from time import sleep
from requests import get
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException

from pyotp import TOTP
from pyvirtualdisplay import Display
from pyvirtualdisplay.smartdisplay import SmartDisplay
import pickle
from datetime import timedelta, datetime
from discord import Embed, Colour, File