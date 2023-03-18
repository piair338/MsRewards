#!/usr/bin/python3.10
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

from pyvirtualdisplay import Display
from pyvirtualdisplay.smartdisplay import SmartDisplay

from rich.progress import BarColumn, Progress, TextColumn, Progress, TimeElapsedColumn, TaskProgressColumn, TimeRemainingColumn

from modules.db import add_to_database
from modules.config import *
from modules.tools import *
from modules.error import *
import modules.progress

global driver
driver = None
global _mail, _password

# TODO : replace by a better print (with logging, cf https://realpython.com/python-logging/)
def printf(e, f = ""):
    print(e+f)

# TODO
# handle "panda"'s error: error while logging in preventing some task to be done
# replace driver's screenshot by Display's one
# test PlayQuiz8 fix
# check that each card worked (lot of misses lately)
# add date and account before print

custom_sleep = CustomSleep

# Wait for the presence of the element identifier or [timeout]s
def wait_until_visible(search_by: str, identifier: str, timeout = 20, browser = driver) -> None:
    try :
        WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((search_by,identifier)), "element not found")
    except TimeoutException as e:
        print(f"element not found after {timeout}s")


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

# create a webdriver 
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
        options.set_preference("permissions.default.image", 2) #disable image loading. You shouldn't use it except if really nessecary 
    if Headless:
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



# close the tab currently on and go back to the one first, or the one specified
def close_tab(tab, SwitchTo=0) -> None:
    driver.switch_to.window(tab)
    driver.close()
    driver.switch_to.window(driver.window_handles[SwitchTo])


#Deal with rgpd popup as well as some random popup like 'are you satisfied' one
def rgpd_popup() -> None:
    for i in ["bnp_btn_accept", "bnp_hfly_cta2", "bnp_hfly_close"] :
        try:
            driver.find_element(By.ID, i).click()
        except:
            pass


# play_quiz[N]([int : override]) make the quiz with N choice each time. They usually have between 4 and 10 questions. 
# override is the number of question, by default, it's the number of question in this specific quiz. Can be useful in some case, where the program crashes before finishing the quiz
def play_quiz2(override=10) -> None:
    printf("starting play_quiz2")
    for j in range(override):
        try:
            rgpd_popup()
            custom_sleep(uniform(3, 5))
            page_html = driver.page_source
            secret_answer = search('IG:"([^"]+)"', page_html)[1]                      # variable used to calculate offset
            answers_values = search('data-option="([^"]+)"', page_html)[1]
            offset = int(secret_answer[-2:], 16)                                      # the last two character converted to int are the offset
            correct_answer_value = search('correctAnswer":"([0-9]+)', page_html)[1]
            
            somme = 0
            for answer in answers_values:
                somme += ord(answer)

            if somme + offset == int(correct_answer_value):
                answer_elem = driver.find_element(By.ID, "rqAnswerOption0")
                answer_elem.click()
                progressBar(j, 10, name="quiz 2")
            else:
                answer_elem = driver.find_element(By.ID, "rqAnswerOption1")
                answer_elem.click()
                progressBar(j, 10, name="quiz 2")

        except exceptions.ElementNotInteractableException as e:
            driver.execute_script("arguments[0].click();", answer_elem)
        except Exception as e:
            log_error(e, driver, _mail)
            break
    printf("play_quiz2 done")


def play_quiz8(task = None):
    override = len(findall("<span id=\"rqQuestionState.\" class=\"emptyCircle\"></span>", driver.page_source))+1
    printf(f"play_quiz8 : start, override : {override}")
    try:
        counter = 0
        rgpd_popup()
        for _ in range(override):  
            custom_sleep(uniform(3, 5))
            correct_answers = []
            for i in range(1,9):
                try : 
                    element = driver.find_element(By.ID, f"rqAnswerOption{i-1}")
                    if 'iscorrectoption="True"' in element.get_attribute("outerHTML"):
                        correct_answers.append(f'rqAnswerOption{i-1}')
                except Exception as e :
                    printf(f"can't find rqAnswerOption{i-1}. Probably already clicked" + str(e))
            shuffle(correct_answers)
            for answer_id in correct_answers:
                wait_until_visible(By.ID, answer_id, timeout = 20, browser=driver)
                counter += 1
                progressBar(counter, 16, name="Quiz 8")
                try:
                    answer_elem = driver.find_element(By.ID, answer_id)
                    answer_elem.click()
                    custom_sleep(1)
                    if not task is None:
                        AdvanceTask(task, 1/override / len(correct_answers) * 100)
                except exceptions.NoSuchElementException :
                    driver.refresh()
                    custom_sleep(10)
                    answer_elem = driver.find_element(By.ID, answer_id)
                    answer_elem.click()
                except ElementClickInterceptedException :
                    rgpd_popup()
                    correct_answers.append(answer_id)

    except Exception as e:
        log_error(f"{format_error(e)} \n Good answers : {' '.join(correct_answers)}", driver, _mail)
    printf("play_quiz8 : fin ")


def play_quiz4(override=None):
    printf("play_quiz4 : start")
    if not override:
        try:  # fidelity quiz are much longer than usual ones
            override = int(findall('rqQuestionState([\d]{1,2})"', driver.page_source)[-1])
            printf(f"Override : {override}")
        except:
            override = 3

    try:
        for i in range(override):
            custom_sleep(uniform(3, 5))
            txt = driver.page_source
            rgpd_popup()
            answer_option = search('correctAnswer":"([^"]+)', txt)[1]
            answer_option = answer_option.replace("\\u0027", "'")    # replace Unicode weird symbols
            try:
                answer_element = driver.find_element(By.CSS_SELECTOR, f'[data-option="{answer_option}"]')
                answer_element.click()
            except exceptions.ElementNotInteractableException:
                driver.execute_script("arguments[0].click();", answer_element)

    except Exception as e:
        log_error(e, driver, _mail)
        raise ValueError(e)
    printf("play_quiz4 : end")


# do_poll() answer a random thing to poll, on of daily activities
def do_poll():
    printf("do_poll : start")
    try:
        try:
            answer_elem = driver.find_element(By.ID, f"btoption{choice([0,1])}")
            answer_elem.click()
        except exceptions.ElementNotInteractableException:
            driver.execute_script("arguments[0].click();", answer_elem)
        custom_sleep(uniform(2, 2.5))
    except Exception as error:
        log_error(error , driver, _mail)
        raise ValueError(error)
    printf("do_poll : end")


# finds all task to do, and launch them
def all_cards():
    def reset(part2=False): 
        if len(driver.window_handles) == 1:
            driver.get("https://www.bing.com/rewardsapp/flyout")
            if part2:
                driver.find_element(
                    By.XPATH, "/html/body/div/div/div[3]/div[2]/div[2]/div[2]/div[1]"
                ).click()
        else:
            driver.switch_to.window(driver.window_handles[1])
            printf(f"fermeture : {driver.current_url}")
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            reset(part2)

    def daily_cards():
        try:
            StartTask(task["daily"][f"all"])
            for i in range(3):
                StartTask(task["daily"][f"carte{i}"])
                custom_sleep(uniform(3, 5))
                try:
                    titre = "erreur"
                    driver.find_element(
                        By.XPATH,f"/html/body/div/div/div[3]/div[2]/div[1]/div[2]/div/div[{i+1}]/a/div/div[2]",
                    ).click()
                    sleep(1)
                    titre = driver.title
                    try_play(titre, task=task["daily"][f"carte{i}"])
                    AdvanceTask(task["daily"][f"carte{i}"], 100)
                    ChangeColor(task["daily"][f"carte{i}"], "green")
                    sleep(1)
                    reset()
                    printf(f"DailyCard {titre} ok")
                except Exception as e:
                    printf(f"all_cards card {titre} error ({e})")
            """ Check if everything worked fine TODO
            try : # devrait renvoyer vrai si la carte i est faite ou pas, a l'aide su symbole en haut a droite de la carte
                elm = driver.get(By.XPATH, f"/html/body/div/div/div[3]/div[2]/div[1]/div[2]/div/div[{i+1}]/a/div/div[2]/div[1]/div[2]/div")
                print("complete" in elm.get_attribute("innerHTML"))
            except : 
                pass
            """
        except Exception as e:
            log_error(e, driver, _mail)
    

    def weekly_cards():
        try:
            driver.find_element(
                By.XPATH, "/html/body/div/div/div[3]/div[2]/div[2]/div[2]/div[1]"
            ).click()  # declenche la premiere partie ?
        except:
            reset()
            try:
                driver.find_element(
                    By.XPATH, "/html/body/div/div/div[3]/div[2]/div[2]/div[2]/div[1]"
                ).click()  # declenche la deuxieme partie ?
            except:
                pass

        for i in range(20):
            printf("début de l'une des cartes")
            driver.find_element(
                By.XPATH,
                "/html/body/div/div/div[3]/div[2]/div[2]/div[3]/div/div[1]/a/div/div[2]",
            ).click()
            driver.switch_to.window(driver.window_handles[len(driver.window_handles) - 1])
            sleep(1)
            titre = driver.title
            print(f"carte {titre} en cours")
            try_play(titre)
            reset(True)
            sleep(1)
            try:
                findall('href="([^<]+)" title=""', driver.page_source)[3]  # return error if there is no cards left to do
            except:
                break


    def top_cards():
        for _ in range(10):
            try : 
                driver.find_element(By.ID, "/html/body/div/div/div[3]/div[1]/div/div[1]/div[2]").click()
                close_tab(driver.window_handles[1])
            except Exception as e:
                print(e)
                break
    
    try :
        top_cards()
    except Exception as e:
        log_error(e, driver, _mail)

    try:
        daily_cards()
    except Exception as e:
        log_error(e, driver, _mail)

    try :
        weekly_cards()
    except Exception as e:
        log_error(e, driver, _mail)


# Find out which type of action to do
def try_play(nom="inconnu", task = None):
    rgpd_popup()
    printf("try_play en cours")

    def play(number):
        if number == 8 or number == 9:
            try:
                printf(f"\033[96m Quiz 8 detected on {nom} \033[0m")
                play_quiz8(task=task)
                printf(f"\033[92m Quiz 8 succeeded on {nom} \033[0m")
                custom_sleep(uniform(3, 5))
            except Exception as e:
                printf(f"fail of PlayQuiz 8. Aborted {e} \033[0m")

        elif number == 5 or number == 4:
            try:
                printf(f"\033[96m Quiz 4 detected on {nom} \033[0m")
                play_quiz4()
                printf(f"\033[92m Quiz 4 succeeded on {nom} \033[0m")
                custom_sleep(uniform(3, 5))
            except Exception as e:
                printf(f"fail of PlayQuiz 4. Aborted {e} \033[0m")

        elif number == 3 or number == 2:
            try:
                printf(f"\033[96m Quiz 2 detected on {nom}\033[0m")
                play_quiz2()
                printf(f"\033[92m Quiz 2 succeeded on {nom}\033[0m")
            except Exception as e:
                printf(f"fail of PlayQuiz 2. Aborted {e}")
        else:
            log_error("There is an error. rqAnswerOption present in page but no action to do. skipping.", driver, _mail)

    try:
        driver.find_element(By.ID, "rqStartQuiz").click()  # start the quiz
        answer_number = driver.page_source.count("rqAnswerOption")
        play(answer_number)

    except Exception as e: # if there is no start button, an error is thrown
        if "bt_PollRadio" in driver.page_source:
            try:
                printf("Poll detected")
                rgpd_popup()
                do_poll()
                printf("Poll succeeded")
            except Exception as e:
                printf(f"try_play - 1 - Poll aborted {e}")

        elif "rqQuestionState" in driver.page_source:
            try:
                number = driver.page_source.count("rqAnswerOption")
                printf(f"recovery détecté. quiz : {number}")
                play(number-1)
            except Exception as e:
                printf(f"try_play - 2 - {e}")

        elif search("([0-9]) de ([0-9]) finalisée", driver.page_source):
            print("fidélité")
            rgpd_popup()
            fidelity()

        else:
            printf(f"rien à faire sur la page {nom}")
            rgpd_popup()
            custom_sleep(uniform(3, 5))


# login() tries to login to your Microsoft account.
# it uses global variable _mail and _password to login
def login():
    global driver
    def sub_login():    
        printf("sub_login : start")
        driver.get("https://login.live.com")
        wait_until_visible(By.ID, "i0116", browser = driver)
        mail_elem = driver.find_element(By.ID, "i0116")
        send_keys_wait(mail_elem, _mail)
        mail_elem.send_keys(Keys.ENTER)
        wait_until_visible(By.ID, "i0118", browser = driver)
        pwd_elem = driver.find_element(By.ID, "i0118")
        send_keys_wait(pwd_elem, _password)
        pwd_elem.send_keys(Keys.ENTER)
        custom_sleep(5)

        if ('Abuse' in driver.current_url) : 
            log_error("account suspended", driver, _mail)
            raise Banned()

        for id in ["KmsiCheckboxField","iLooksGood", "idSIButton9", "iCancel"]:
            try:
                driver.find_element(By.ID, id).click()
                restart = True
            except Exception as e:
                pass

        try : 
            body_elem = driver.find_element(By.TAG_NAME, "body")
            body_elem.send_keys(Keys.ENTER)
        except :
            pass
        printf("login completed - going to MsRewards")
        custom_sleep(uniform(3,5))
        driver.get("https://www.bing.com/rewardsapp/flyout")
        custom_sleep(uniform(3,5))
        for i in [f'[title="Rejoindre maintenant"]', f'[title="Rejoindre"]', f'[title="Join now"]'] :
            try:
                driver.find_element(By.CSS_SELECTOR, i).click()  # depend of the language of the page
            except:
                print(f"element {i} not found")
        rgpd_popup()
        custom_sleep(uniform(3,5))

        driver.get("https://www.bing.com/rewardsapp/flyout")
        try:
            driver.find_element(By.CSS_SELECTOR, '[title="Rejoindre maintenant"]').click()  # depend of the language of the page
        except:
            print(f"unlock test: fail, probably normal")
            
        print('on MsRewards')
        
    for _ in range(3) :
        try : 
            sub_login()
            return (driver.current_window_handle)
        except Banned:
            raise Banned()
        except Exception as e:
            log_error(e, driver, _mail)
            driver.quit()
            custom_sleep(1200)
            driver = firefox_driver()
    return("STOP")


# Makes 30 search as PC Edge
def bing_pc_search(override=randint(35, 40)):
    StartTask(task["PC"])
    driver.get(f"https://www.bing.com/search?q=bing")  # {choice(Liste_de_mot)}')
    custom_sleep(uniform(1, 2))
    rgpd_popup()
    send_keys_wait(
        driver.find_element(By.ID, "sb_form_q"),
          Keys.BACKSPACE + Keys.BACKSPACE + Keys.BACKSPACE + Keys.BACKSPACE + Keys.BACKSPACE + Keys.BACKSPACE
    )

    for _ in range(override):
        word = choice(Liste_de_mot)
        try:
            send_keys_wait(driver.find_element(By.ID, "sb_form_q"), word)
            driver.find_element(By.ID, "sb_form_q").send_keys(Keys.ENTER)
        except Exception as e :
            printf(e)
            sleep(10)
            driver.get(f'https://www.bing.com/search?q={word}')
            sleep(3)
            send_keys_wait(driver.find_element(By.ID, "sb_form_q"), word)
            driver.find_element(By.ID, "sb_form_q").send_keys(Keys.ENTER)

        AdvanceTask(task["PC"], 1/override * 100 )
        custom_sleep(uniform(5, 20))

        try:
            driver.find_element(By.ID, "sb_form_q").clear()
        except Exception as e:
            printf(e)
            try:
                driver.get('https://www.bing.com/search?q=plans')
                driver.find_element(By.ID, "sb_form_q").clear()
            except Exception as e:
                log_error(f"clear la barre de recherche - {format_error(e)}", driver, _mail)
    AdvanceTask(task["PC"], 100 )
    ChangeColor(task["PC"], "green")


# Unban an account, called with -u parameter. You will need a phone number
def unban() -> None:
    driver.find_element(By.ID, "StartAction").click()
    custom_sleep(2)
    txt = driver.page_source
    uuid0 = findall('wlspispHIPCountrySelect([a-z0-9]+)', txt)[0]
    uuid1 = findall('wlspispHIPPhoneInput([a-z0-9]+)', txt)[0]
    uuid2 = findall('wlspispHipSendCode([a-z0-9]+)', txt)[0]
    uuid3 = findall('wlspispSolutionElement([a-z0-9]+)', txt)[0]
    country_code_select = Select(driver.find_element(By.ID, "wlspispHIPCountrySelect" + uuid0))
    country_code_input = input("enter Country code (FR, ...) ")
    country_code_select.select_by_value(country_code_input)
    wait_until_visible(By.ID, "wlspispHIPPhoneInput" + uuid1, browser=driver)
    phone_input = input("phone number : +33")
    phone_elem = driver.find_element(By.ID, "wlspispHIPPhoneInput" + uuid1)
    phone_elem.send_keys(phone_input)
    wait_until_visible(By.ID, "wlspispHipSendCode" + uuid2, browser=driver)
    send_sms_elem = driver.find_element(By.ID, "wlspispHipSendCode" + uuid2)
    send_sms_elem.click()
    wait_until_visible(By.ID, "wlspispSolutionElement" + uuid3, browser=driver)
    sms_code_elem = driver.find_element(By.ID, "wlspispSolutionElement" + uuid3)
    sms_code_input = input("entrez le contenu du msg : ")
    sms_code_elem.send_keys(sms_code_input)
    send_box = driver.find_element(By.ID, "ProofAction")
    send_box.click()
    wait_until_visible(By.ID, "FinishAction", browser=driver)
    end_elem = driver.find_element(By.ID, "FinishAction")
    end_elem.click()


# Sends points to database, discord and whatever service you want
def log_points(account="unknown"): 
    def get_points():
        driver.get("https://www.bing.com/rewardsapp/flyout")
        regex1 = '<a href="https://rewards\.bing\.com/" title="((.{1,3}),(.{1,3})) points" target="_blank"'
        try:
            point = search(regex1, driver.page_source)[1].replace(",", "")

        except Exception as e:
            elem = driver.find_element(By.CSS_SELECTOR, '[title="Microsoft Rewards"]')
            elem.click()
            custom_sleep(5)
            driver.switch_to.window(driver.window_handles[len(driver.window_handles) - 1])
            custom_sleep(uniform(5,7))
            point = search('availablePoints":([\d]+)', driver.page_source)[1]

        return(point)

    for _ in range (3):
        try : 
            points = get_points()
            break
        except Exception as e:
            custom_sleep(300)
            log_error(e, driver, _mail)
            points = None
            
    if not points : 
        log_error(f"impossible d'avoir les points", driver, _mail)

    custom_sleep(uniform(3, 20))
    account_name = account.split("@")[0]

    if DISCORD_ENABLED_SUCCESS:
        if DISCORD_EMBED:
            embed = discord.Embed(
                title=f"{account_name} actuellement à {str(points)} points", colour=Colour.green()
            )
            embed.set_footer(text=account_name)
            webhookSuccess.send(embed=embed)
        else:
            webhookSuccess.send(f"{account_name} actuellement à {str(points)} points")

    if sql_enabled :
        add_to_database(account_name, points, sql_host, sql_usr, sql_pwd, sql_database)


def fidelity():
    try:
        while 1: #close all tabs
            try:
                close_tab(1)
            except:
                break
        try : 
            fidelity_link_page = get(FidelityLink) #get the url of fidelity page
        except Exception as e :
            printf(e)
            fidelity_link_page = False

        if fidelity_link_page : 
            fidelity_link = fidelity_link_page.content.decode("UTF-8")

            if (fidelity_link.split(":")[0] == "https") or (fidelity_link.split(":")[0] == "http") : 
                
                driver.get(fidelity_link)
                wait_until_visible(By.CSS_SELECTOR, 'div[class="pull-left spacer-48-bottom punchcard-row"]', browser=driver)
                choix = driver.find_element(By.CSS_SELECTOR, 'div[class="pull-left spacer-48-bottom punchcard-row"]')  # pull-left spacer-48-bottom punchcard-row? USELESS ?

                answer_number = search("([0-9]) of ([0-9]) completed", driver.page_source)
                if answer_number is None:
                    answer_number = search("([0-9]) de ([0-9]) finalisé", driver.page_source)
                if answer_number is None :
                    answer_number = search("([0-9]) licence\(s\) sur ([0-9]) disponible\(s\)", driver.page_source)
                if answer_number is None :
                    answer_number = [0,0,0]

                for _ in range(int(answer_number[2]) - int(answer_number[1])):
                    driver.refresh()
                    custom_sleep(2)
                    card_elem = driver.find_element(By.CLASS_NAME, "spacer-48-bottom")
                    try : 
                        button_text = search('<span class="pull-left margin-right-15">([^<^>]+)</span>',card_elem.get_attribute("innerHTML"))[1]
                        bouton_card = driver.find_element(By.XPATH, f'//span[text()="{button_text}"]')
                        bouton_card.click()
                    except Exception as e1 :
                        try : 
                            recover_elem = driver.find_element(By.XPATH,'/html/body/div[1]/div[2]/main/div[2]/div[2]/div[7]/div[3]/div[1]/a')
                            recover_elem.click()
                        except Exception as e2 :
                            log_error(f"fidélité - double erreur - e1 : {format_error(e1)} - e2 {format_error(e2)}", driver, _mail)
                            break
                    custom_sleep(uniform(3, 5))
                    driver.switch_to.window(driver.window_handles[1])
                    try_play(driver.title)
                    driver.get(fidelity_link) # USELESS ?
                    custom_sleep(uniform(3, 5))
                    try:
                        close_tab(driver.window_handles[1])
                    except Exception as e:
                        printf(e)
                printf("fidelity - done")
            else :
                printf("invalid fidelity link.")
    except Exception as e:
        log_error(e, driver, _mail)


def mobile_login(error):
    try:
        # TODO 
        # aller direct sur bin pour ne pas avoir a utiliser le menu hamburger
        mobile_driver.get("https://www.bing.com/search?q=test+speed")
        mobile_rgpd()
        printf("start of Mobile login")
        try :
            mobile_driver.find_element(By.ID, "mHamburger").click()
        except Exception as e :
            log_error(f"trying something. 1 {e}", mobile_driver, _mail)
            mobile_driver.find_element(By.TAG_NAME, "body").send_keys(Keys.UP) #force apparition of hamurger menu
            log_error(f"trying something. 2 {e}", mobile_driver, _mail)
            mobile_driver.find_element(By.ID, "mHamburger").click()

        wait_until_visible(By.ID, "hb_s", browser=mobile_driver)
        mobile_driver.find_element(By.ID, "hb_s").click()
        wait_until_visible(By.ID, "i0116", browser=mobile_driver)
        mail_elem = mobile_driver.find_element(By.ID, "i0116")
        send_keys_wait(mail_elem, _mail)
        mail_elem.send_keys(Keys.ENTER)
        wait_until_visible(By.ID, "i0118", browser=mobile_driver)
        pwd_elem = mobile_driver.find_element(By.ID, "i0118")
        send_keys_wait(pwd_elem, _password)
        pwd_elem.send_keys(Keys.ENTER)
        custom_sleep(uniform(1, 2))
        for i in ["KmsiCheckboxField", "iLooksGood", "idSIButton9"]:
            try:
                mobile_driver.find_element(By.ID,i ).click()
            except Exception as e:
                pass

        printf("end of Mobile login")

    except Exception as e:
        error += 1
        if error <= 3:
            printf(f"failure on mobile_login. Retrying({error}/3), {e}")
            custom_sleep(uniform(5, 10))
            mobile_login(error)
        else:
            log_error(
                f"login impossible 3 fois de suite. {e}", mobile_driver, _mail
            )
            mobile_driver.quit()
            return(True)


def mobile_rgpd():
    for id in ["bnp_btn_accept", "bnp_hfly_cta2"]:
        try:
            mobile_driver.find_element(By.ID, id).click()
        except Exception:
            pass


def mobile_alert_popup():
    try:
        alert = mobile_driver.switch_to.alert
        alert.dismiss()
    except exceptions.NoAlertPresentException as e:
        pass
    except Exception as e:
        log_error(e, mobile_driver, _mail)


def bing_mobile_search(override=randint(22, 25)):
    global mobile_driver
    mobile_driver = firefox_driver(mobile=True)
    try:
        if not mobile_login(0):
            StartTask(task["Mobile"])
            custom_sleep(uniform(1, 2))
            mobile_rgpd()
            custom_sleep(uniform(1, 1.5))
    
            for i in range(override):  # 20
                try :
                    mot = choice(Liste_de_mot)
                    send_keys_wait(mobile_driver.find_element(By.ID, "sb_form_q"), mot)
                    mobile_driver.find_element(By.ID, "sb_form_q").send_keys(Keys.ENTER)
                    AdvanceTask(task["Mobile"], 1/override * 100)
                    custom_sleep(uniform(5, 20))
                    mobile_alert_popup()  # check for alert (asking for position or for allowing notifications)
                    mobile_driver.find_element(By.ID, "sb_form_q").clear()
                except :
                    driver.refresh()
                    custom_sleep(30)
                    i -= 1
            mobile_driver.quit()
            ChangeColor(task["Mobile"], "green")

    except Exception as e:
        log_error(e, mobile_driver, _mail)
        mobile_driver.quit()


def daily_routine(custom = False):
    ShowDefaultTask()
    try : 
        if not custom: # custom already login 
            login()
    except Banned :
        log_error("THIS ACCOUNT IS BANNED. FIX THIS ISSUE WITH -U", driver, _mail)
        return()

    try:
        all_cards()
    except Exception as e:
        log_error(e, driver, _mail)

    try:
        bing_pc_search()
    except Exception as e:
        log_error(e, driver, _mail)
        
    try:
        bing_mobile_search()
    except Exception as e:
        log_error(e, driver, _mail)

    try:
        fidelity()
    except Exception as e:
        log_error(e, driver, _mail)

    try:
        log_points(_mail)
    except Exception as e:
        log_error(e, driver, _mail)


def dev():
    pass


def CustomStart(Credentials):
    global START_TIME
    if not LINUX_HOST :
        raise NameError('You need to be on linux to do that, due to the utilisation of a module named enquieries, sorry.') 
    global driver, _mail, _password, p, task

    system("clear")  # clear from previous command to allow a clean choice
    actions = ["tout", "daily", "pc", "mobile", "log_points","fidelity", "dev"]
    Actions = enquiries.choose("quels Actions ?", actions, multi=True)
    liste = select_accounts()
    START_TIME = time() # Reset timer to the start of the actions
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        TimeElapsedColumn(),
    ) as p:
        task = modules.progress.dico(p)
        for _mail, _password in liste:

            driver = firefox_driver()
            driver.implicitly_wait(3)

            if login() != "STOP":
                if "tout" in Actions:
                    daily_routine(True)

                if "daily" in Actions:
                    try:
                        all_cards()
                    except Exception as e:
                        log_error(e, driver, _mail)

                if "pc" in Actions:
                    try:
                        ShowTask(task["PC"])
                        bing_pc_search()
                    except Exception as e:
                        log_error(e, driver, _mail)

                if "mobile" in Actions:
                    try:
                        ShowTask(task["Mobile"])
                        bing_mobile_search()
                    except Exception as e:
                        log_error(e, driver, _mail)

                if "fidelity" in Actions:
                    try :
                        fidelity()
                    except Exception as e :
                        log_error(e, driver, _mail)

                if "dev" in Actions:
                    try:
                        dev()
                    except Exception as e:
                        printf(e)
                        break

                if not "tout" in Actions:
                    try:
                        log_points(_mail)
                    except Exception as e:
                        print(f"CustomStart {e}")
            driver.close()


def select_accounts(multiple = True):
    system("clear")  # clear from previous command to allow a clean choice
    emails = [x[0] for x in Credentials]  # list of all email adresses
    emails_selected = enquiries.choose(f"quel{'s' if multiple else ''} compte{'s' if multiple else ''} ?", emails, multi=multiple)
    return([x for x in Credentials if x[0] in emails_selected])


def SavePointsFromFile(file):
    with open(file) as f:
        reader = csv.reader(f)
        points_list = list(reader)

    for item in points_list:
        compte, points = item[0], item[1]
        add_to_database(compte, points, sql_host,sql_usr,sql_pwd,sql_database, save_if_fail=False)
    
    with open(file, "w") as f:
        f.write("")


def StartTask(task):
    ChangeColor(task, "blue")
    p.start_task(task)
    p.update(task, advance=0) # Reset the Task if it was already filled to 100%

def ShowTask(task):
    p.update(task, visible=True)

def AdvanceTask(task, pourcentage):
    p.update(task, advance=pourcentage)

def ChangeColor(task, newcolor):
    old = p.tasks[task].description
    old = old.split(']')
    old[0] = f"[{newcolor}"
    new = "]".join(old)
    p.update(task,description=new)

def ShowDefaultTask():
    for i in ["all", "carte1", "carte2", "carte0"]:
        ShowTask(task["daily"][i])
    
    for i in ["PC", "Mobile"]:
        ShowTask(task[i])


if VNC_ENABLED : 
    display = Display(backend="xvnc", size=(2000, 1100), rfbport=VNC_PORT, color_depth=24) 
else :
    display = SmartDisplay(size=(2000, 1100)) 
display.start()


if CUSTOM_START:
        CustomStart(Credentials)
elif UNBAN:
    _mail, _password  = select_accounts(False)[0]
    driver = firefox_driver()
    try : 
        login()
    except Banned:
        unban()

    driver.quit()

elif POINTS_FILE != "":
    SavePointsFromFile(POINTS_FILE)
else:
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        TimeElapsedColumn(),
    ) as p:
        task = modules.progress.dico(p)
    
        for _mail, _password in Credentials:
            #system("pkill -9 firefox")
            print("\n\n")
            print(_mail)
            custom_sleep(1)
            printf("début du driver")
            driver = firefox_driver()
            printf("driver demarré")
            driver.implicitly_wait(3)

            try:
                daily_routine()
                driver.quit()
                attente = uniform(1200, 3600)
                printf(f"finis. attente de {round(attente/60)}min")
                custom_sleep(attente)

            except KeyboardInterrupt:
                print("canceled. Closing driver and display.")
                driver.quit()
                display.stop()
            except Exception as e:
                print(f"error not catch. skipping this account. {e}")
                driver.quit()


display.stop()
