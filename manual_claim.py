from easyprocess import EasyProcess
from pyvirtualdisplay import Display
from modules.config import *
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select


def setup_proxy(ip, port, options, socks=False) :
    PROXY = f"{ip}:{port}"
    if socks :
        options.set_preference('network.proxy.type', 1)
        options.set_preference('network.proxy.socks', ip)
        options.set_preference('network.proxy.socks_port', int(port))
        options.set_preference("browser.link.open_newwindow", 3)
    else :
        webdriver.DesiredCapabilities.FIREFOX['proxy'] = {
            "httpProxy": PROXY,
            "sslProxy": PROXY,
            "proxyType": "MANUAL",
        }

def firefox_driver(mobile=False, Headless=False):
    PC_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        "AppleWebKit/537.36 (KHTML, like Gecko)"
        "Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.56")
    MOBILE_USER_AGENT = (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_5 like Mac OS X)"
        "AppleWebKit/605.1.15 (KHTML, like Gecko)"
        "CriOS/103.0.5060.63 Mobile/15E148 Safari/604.1"
    )
    
    options = Options()
    options.set_preference('intl.accept_languages', 'fr-FR, fr')
    if proxy_enabled :
        setup_proxy(proxy_address,proxy_port, options)
    options.set_preference("browser.link.open_newwindow", 3)
    if FAST :
        options.set_preference("permissions.default.image", 2) #disable image loading. May add this without the fast option soon
    if Headless:
        options.add_argument("-headless")
    if mobile :
        options.set_preference("general.useragent.override", MOBILE_USER_AGENT)
    else :
        options.set_preference("general.useragent.override", PC_USER_AGENT)
    driver = webdriver.Firefox(options=options)
    driver.set_window_size(1900 + hash(_mail)%20 , 1070 + hash(_password + "salt")%10)
    return(driver)

def select_accounts(multiple = True):
    system("clear")  # clear from previous command to allow a clean choice
    emails = [x[0] for x in Credentials]  # list of all email adresses
    emails_selected = enquiries.choose(f"quel{'s' if multiple else ''} compte{'s' if multiple else ''} ?", emails, multi=multiple)
    return([x for x in Credentials if x[0] in emails_selected])



with Display(backend="xvnc", size=(2000, 1000), rfbport=5904) as disp:
    _mail, _password  = select_accounts(False)[0]
    driver = firefox_driver()
    print(f"connect via VNC to port 5904. \nID: {_mail}\npwd : {_password}")
    i = input('stop ? ')
    driver.close()
