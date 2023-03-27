from modules.imports import *


# create a webdriver 
def firefox_driver(mobile=False, headless=False):
    PC_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        "AppleWebKit/537.36 (KHTML, like Gecko)"
        "Chrome/112.0.0.0 Safari/537.36 Edg/110.0.1587.56")
    MOBILE_USER_AGENT = (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_5 like Mac OS X)"
        "AppleWebKit/605.1.15 (KHTML, like Gecko)"
        "CriOS/107.0.5060.63 Mobile/15E148 Safari/604.1"
    )
    options = Options()
    options.set_preference('intl.accept_languages', 'fr-FR, fr')
    if proxy_enabled :
        setup_proxy(proxy_address,proxy_port, options)
    options.set_preference("browser.link.open_newwindow", 3)
    if FAST :
        options.set_preference("permissions.default.image", 2) #disable image loading. You shouldn't use it except if really nessecary 
    if headless:
        options.add_argument("-headless")
    if mobile :
        options.set_preference("general.useragent.override", MOBILE_USER_AGENT)
        driver = webdriver.Firefox(options=options)
        driver.set_window_size(1070 + hash(_mail)%20 , 1900 + hash(_password + "salt")%10) # mobile resolution are crazy high now, right ?
    else :
        options.set_preference("general.useragent.override", PC_USER_AGENT)
        driver = webdriver.Firefox(options=options)
        driver.set_window_size(1900 + hash(_mail)%20 , 1070 + hash(_password + "salt")%10)
    return(driver)

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

#Deal with rgpd popup as well as some random popup like 'are you satisfied' one
def rgpd_popup(driver) -> None:
    for i in ["bnp_btn_accept", "bnp_hfly_cta2", "bnp_hfly_close"] :
        try:
            driver.find_element(By.ID, i).click()
        except:
            pass

# save webdriver cookies
def save_cookies():
    pickle.dump(driver.get_cookies(), open(f"{'/'.join(__file__.split('/')[:-1])}/user_data/cookies/{_mail}.pkl", "wb"))

# load cookies previously saved to the driver
def load_cookies(driver):
    cookies = pickle.load(open(f"{'/'.join(__file__.split('/')[:-1])}/user_data/cookies/{_mail}.pkl", "rb"))
    for cookie in cookies:
        driver.add_cookie(cookie)

"""
send_keys_wait([selenium element:element, str:keys]) send the different keys to the field element, with a random time between each press to simulate human action.
keys can be an string, but also selenium keys
"""
def send_keys_wait(element, keys):
    for i in keys:
        element.send_keys(i)
        if FAST :
            pass
        else :
            sleep(uniform(0.1, 0.3))



# Wait for the presence of the element identifier or [timeout]s
def wait_until_visible(search_by: str, identifier: str, timeout = 20, browser = driver) -> None:
    try :
        WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((search_by,identifier)), "element not found")
    except TimeoutException as e:
        print(f"element not found after {timeout}s")

