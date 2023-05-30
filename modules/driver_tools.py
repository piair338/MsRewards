from modules.imports import *
from modules.config import *
from modules.tools import *
import modules.globals as g


def setup_proxy(ip: str, port: str) -> None:
    PROXY = f"{ip}:{port}"
    webdriver.DesiredCapabilities.FIREFOX['proxy'] = {
        "httpProxy": PROXY,
        "sslProxy": PROXY,
        "proxyType": "MANUAL",
    }


#Deal with RGPD popup as well as some random popup like 'are you satisfied' one
def rgpd_popup(driver) -> None:
    for i in ["bnp_btn_accept", "bnp_hfly_cta2", "bnp_hfly_close"] :
        try:
            driver.find_element(By.ID, i).click()
        except:
            pass


# save webdriver cookies
def save_cookies(driver) -> None:
    if g.dev:
        f = open(f"{'/'.join(__file__.split('/')[:-2])}/user_data/cookies/{g._mail}_unsafe.pkl", "w")
        for i in driver.get_cookies():
            f.write(str(i) + "\n")
        f.close()
    else :
        pickle.dump(driver.get_cookies(), open(f"{'/'.join(__file__.split('/')[:-2])}/user_data/cookies/{g._mail}.pkl", "wb"))


# load cookies previously saved to the driver
def load_cookies(driver) -> None:
    if g.dev:
        f = open(f"{'/'.join(__file__.split('/')[:-2])}/user_data/cookies/{g._mail}_unsafe.pkl", "r")
        lines = f.readlines()
        f.close()
        cookies = [literal_eval(x) for x in lines]
    else :
        cookies = pickle.load(open(f"{'/'.join(__file__.split('/')[:-2])}/user_data/cookies/{g._mail}.pkl", "rb"))
    for cookie in cookies:
        driver.add_cookie(cookie)

"""
send_keys_wait([selenium element:element, str:keys]) send the different keys to the field element, with a random time between each press to simulate human action.
keys can be an string, but also selenium keys
"""
def send_keys_wait(element, keys: str) -> None:
    for i in keys:
        element.send_keys(i)
        sleep(uniform(0.1, 0.3))



# Wait for the presence of the element identifier or [timeout]s
def wait_until_visible(search_by: str, identifier: str, timeout = 20, browser = None) -> None:
    try :
        WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((search_by,identifier)), "element not found")
        return(True)
    except TimeoutException as e:
        printf(f"element {identifier} not found after {timeout}s")
        return(False)

