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
from rich.progress import BarColumn, Progress, TextColumn, Progress, TimeElapsedColumn, TaskProgressColumn, TimeRemainingColumn

from modules.db import add_to_database
from modules.config import *
from modules.tools import *
from modules.error import *
import modules.progress
global driver


def printf(x):
    printf2(x, _mail)


def WaitUntilVisible(by, id, to = 20, browser = driver):
    try :
        WebDriverWait(browser, to).until(EC.visibility_of_element_located((by,id)), "element not found")
    except TimeoutException as e:
        print(f"element not found after {to}s")


def claim_amazon(): 
    try : 
        driver.get("https://rewards.bing.com/redeem/000803000031")
        try :
            driver.find_element(By.XPATH, "//span[contains( text( ), 'ÉCHANGER UNE RÉCOMPENSE')]").click()
        except :
            driver.find_element(By.XPATH, "//span[contains( text( ), 'REDEEM REWARD')]").click()
        sleep(5)
        try : 
            driver.find_element(By.XPATH, "//span[contains( text( ), 'CONFIRMER LA RÉCOMPENSE')]").click()
        except :
            driver.find_element(By.XPATH, "//span[contains( text( ), 'CONFIRM REWARD')]").click()

        sleep(5)

        if ("/rewards/redeem/orderhistory" in driver.page_source) :
            driver.get("https://rewards.bing.com/redeem/orderhistory")
            try :
                driver.find_element(By.XPATH, "//span[contains( text( ), 'Détails de la commande')]").click()
            except :
                driver.find_element(By.XPATH, "//span[contains( text( ), 'Get code')]").click()
            sleep(5)
            code = driver.find_element(By.CLASS_NAME, "tango-credential-value").get_attribute('innerHTML')
            lien = driver.find_elements(By.CLASS_NAME, "tango-credential-key")[1].get_attribute('innerHTML')
            lien = search('\"([^\"]+)\"',lien)[1]
            driver.get(lien)
            sleep(10)
            box = driver.find_element(By.ID, "input-45")
            box.click()
            box.send_keys(code)
            driver.find_element(By.XPATH, "//span[contains( text( ), 'Déverrouillez votre récompense')]").click()
            sleep(5)
            #amazon = search("> ([^ ]+) <", fcode)[1]
            fcode = driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/main/div/div/div/div/div[1]/div/div[1]/div[2]/div[2]/div/div/div/div/div/div[2]/span").get_attribute("innerHTML")
            if fcode :
                webhookSuccess.send(_mail)
                webhookSuccess.send(fcode)
                return(1)
            else :
                LogError("impossible de localiser le code ", driver, _mail)
                return(1)
            
        else :
            LogError("la recuperation ne peux pas être automatique", driver, _mail)
            return(0)
    except Exception as e :
        LogError(f'problème dans la recuperation : {str(e)}', driver, _mail)


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


def FirefoxDriver(mobile=False, Headless=Headless):
    PC_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        f"AppleWebKit/{hash(_mail)%500}.{hash(_mail)%50}(KHTML, like Gecko)"
        f"Chrome/{100 + (hash(_mail)%8)}.{hash(_mail)%10}.{hash(_mail)%5000}.102 Safari/537.36 Edg/104.0.1293.70"
    )
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
    return driver


def Close(fenetre, SwitchTo=0):
    driver.switch_to.window(fenetre)
    driver.close()
    driver.switch_to.window(driver.window_handles[SwitchTo])


#Deal with RGPD popup as well as some random popup like 'are you satisfied' one
def RGPD():
    for i in ["bnp_btn_accept", "bnp_hfly_cta2", "bnp_hfly_close"] :
        try:
            driver.find_element(By.ID, i).click()
        except:
            pass


"""
PlayQuiz[N]([int : override]) make the quizz with N choice each time. They usually have between 4 and 10 questions. 
override is the number of question, by default, it's the number of question in this specific quizz. Can be usefull in some case, where the programm crashes before finishing the quizz
"""
def PlayQuiz2(override=10):
    printf("début de PlayQuiz2")
    for j in range(override):
        try:
            RGPD()
            CustomSleep(uniform(3, 5))
            txt = driver.page_source
            secret = search('IG:"([^"]+)"', txt)[1]  # variable dans la page, pour calculer le offset
            reponse1 = search('data-option="([^"]+)"', txt)[1]
            offset = int(secret[-2:], 16)  # la conversion ec decimal des deux dernier caracteres de IG
            reponse = search('correctAnswer":"([0-9]+)', txt)[1]
            somme = 0

            for i in reponse1:
                somme += ord(i)

            if somme + offset == int(reponse):
                elem = driver.find_element(By.ID, "rqAnswerOption0")
                elem.click()
                progressBar(j, 10, name="quiz 2")

            else:
                elem = driver.find_element(By.ID, "rqAnswerOption1")
                elem.click()
                progressBar(j, 10, name="quiz 2")

        except exceptions.ElementNotInteractableException as e:
            driver.execute_script("arguments[0].click();", elem)

        except Exception as e:
            LogError(f"PlayQuiz2 {e}", driver, _mail)
            break
    printf("PlayQuiz2 finis")


def PlayQuiz8(task = None):
    override = len(findall("<span id=\"rqQuestionState.\" class=\"emptyCircle\"></span>", driver.page_source))+1
    printf(f"PlayQuiz8 : start, override : {override}")
    try:
        c = 0
        RGPD()
        for i in range(override):  
            CustomSleep(uniform(3, 5))
            AnswerOptions = [ (driver.find_element(By.ID, f"rqAnswerOption{i-1}"),f'rqAnswerOption{i-1}')  for i in range(1,9)]
            isCorrect = [x[1] for x in AnswerOptions if 'iscorrectoption="True" ' in x[0].get_attribute("outerHTML") ]
            shuffle(isCorrect)

            for i in isCorrect:
                WaitUntilVisible(By.ID, i, to = 20, browser=driver)
                c += 1
                progressBar(c, 16, name="Quiz 8 ")
                try:
                    elem = driver.find_element(By.ID, i)
                    elem.click()
                    if not task is None:
                        AdvanceTask(task, 1/override / len(isCorrect) * 100)
                except exceptions.NoSuchElementException :
                    driver.refresh()
                    CustomSleep(10)
                    elem = driver.find_element(By.ID, i)
                    elem.click()
                except ElementClickInterceptedException :
                    RGPD()
                    isCorrect.append(i)


    except Exception as e:
        LogError(f"PlayQuiz8 - 4 - {e} \n ListOfGood : {str(isCorrect)}", driver, _mail)
        
    printf("PlayQuiz8 : fin ")


def PlayQuiz4(override=None):
    printf("PlayQuiz4 : start")
    if not override:
        try:  # permet de gerer les truc de fidélité, qui sont plus long
            override = int(findall('rqQuestionState([\d]{1,2})"', driver.page_source)[-1])
            printf(f"Override : {override}")
        except:
            override = 3

    try:
        for i in range(override):
            CustomSleep(uniform(3, 5))
            txt = driver.page_source
            RGPD()
            reponse = search('correctAnswer":"([^"]+)', txt)[1]  # je suis pas sur qu'il y ait un espace
            reponse = reponse.replace("\\u0027", "'")  # il faut cancel l'unicode avec un double \ (on replacer les caracteres en unicode en caracteres utf-8)
            printf(f"validation de la reponse                                     ")
            printf(f"validation de la reponse {i+1}/{override} {reponse}")
            try:
                elem = driver.find_element(
                    By.CSS_SELECTOR, f'[data-option="{reponse}"]'
                )
                elem.click()
            except exceptions.ElementNotInteractableException:
                driver.execute_script("arguments[0].click();", elem)

    except Exception as e:
        LogError(f"PlayQuiz4 {str(e)}", driver, _mail)
        raise ValueError(e)
    printf("PlayQuiz4 : end")


"""
PlayPoll() reply a random thing to poll, on of daily activities
"""
def PlayPoll():
    printf("PlayPoll : start")
    try:
        try:
            elem = driver.find_element(By.ID, f"btoption{choice([0,1])}")
            elem.click()
        except exceptions.ElementNotInteractableException as e:
            driver.execute_script("arguments[0].click();", elem)
        CustomSleep(uniform(2, 2.5))
    except Exception as e:
        LogError(f"PlayPoll {e}" , driver, _mail)
        raise ValueError(e)
    printf("PlayPoll : end")


def AllCard():  # fonction qui clique sur les cartes
    def reset(Partie2=False):  # retourne sur la page de depart apres avoir finis
        if len(driver.window_handles) == 1:
            driver.get("https://www.bing.com/rewardsapp/flyout")
            if Partie2:
                driver.find_element(
                    By.XPATH, "/html/body/div/div/div[3]/div[2]/div[2]/div[2]/div[1]"
                ).click()
        else:
            driver.switch_to.window(driver.window_handles[1])
            printf(f"fermeture : {driver.current_url}")
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            reset(Partie2)

    def dailyCards():
        try:
            StartTask(task["daily"][f"all"])
            for i in range(3):
                StartTask(task["daily"][f"carte{i}"])
                CustomSleep(uniform(3, 5))
                try:
                    titre = "erreur"
                    driver.find_element(
                        By.XPATH,f"/html/body/div/div/div[3]/div[2]/div[1]/div[2]/div/div[{i+1}]/a/div/div[2]",
                    ).click()
                    sleep(1)
                    titre = driver.title
                    TryPlay(titre, task=task["daily"][f"carte{i}"])
                    AdvanceTask(task["daily"][f"carte{i}"], 100)
                    ChangeColor(task["daily"][f"carte{i}"], "green")
                    sleep(1)
                    reset()
                    printf(f"DailyCard {titre} ok ")
                except Exception as e:
                    printf(f"Allcard card {titre} error ({e})")
        except Exception as e:
            LogError(f"Dailycards {e}", driver, _mail)

    try:
        dailyCards()
    except Exception as e:
        printf(f"erreur dans les quetes de la semaine {e}")

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
            printf("carte cliquée")
            driver.switch_to.window(driver.window_handles[len(driver.window_handles) - 1])
            sleep(1)
            titre = driver.title
            print(f"carte {titre} en cours")
            TryPlay(titre)
            reset(True)
            sleep(1)
            try:
                link = findall('href="([^<]+)" title=""', driver.page_source)[
                    3
                ]  # verifie si on a toujours des cartes
            except:
                break


    try :
        weekly_cards()
    except Exception as e:
        LogError(f"weekly_cards {e}", driver, _mail)



"""
login() tries to login to your micrososft account.
it uses global variable _mail and _password to login
"""
def login():
    global driver
    def sub_login():    
        printf("sublogin : start")
        driver.get("https://www.bing.com/rewardsapp/flyout")
        for i in [f'[title="Rejoindre"]', f'[title="Join now"]', f'[title="Rejoindre maintenant"]'] :
            try:
                driver.find_element(By.CSS_SELECTOR, i).click()  # depend of the language of the page
                break
            except:
                pass
        try:
            driver.find_element(By.XPATH, "/html/body/div/div/div/div/div[2]/a").click()  # may need to be clicked if the language is english
        except:
            pass

        WaitUntilVisible(By.ID, "i0116", browser = driver)
        mail = driver.find_element(By.ID, "i0116")
        send_keys_wait(mail, _mail)
        mail.send_keys(Keys.ENTER)
        WaitUntilVisible(By.ID, "i0118", browser = driver)
        pwd = driver.find_element(By.ID, "i0118")
        send_keys_wait(pwd, _password)
        pwd.send_keys(Keys.ENTER)
        CustomSleep(5)

        if ('Abuse' in driver.current_url) : 
            LogError("account suspended", driver, _mail)
            raise Banned()


        for i in ["KmsiCheckboxField","iLooksGood", "idSIButton9", "iCancel"]:
            try:
                driver.find_element(By.ID, i).click()
            except Exception as e:
                pass
        try : 
            elm = driver.find_element(By.TAG_NAME, "body")
            elm.send_keys(Keys.ENTER)
        except :
            pass
        printf("login completed")
        RGPD()
        CustomSleep(uniform(3,5))
        driver.get("https://www.bing.com/rewardsapp/flyout")
        CustomSleep(uniform(3,5))

    for i in range(3) :
        try : 
            sub_login()
            return (driver.current_window_handle)
        except Banned:
            raise Banned()
        except Exception as e:
            LogError(f"login - 3 - {e}", driver, _mail)
            driver.close()
            CustomSleep(1200)
            driver = FirefoxDriver()
    return("STOP")


def BingPcSearch(override=randint(35, 40)):
    StartTask(task["PC"])
    driver.get(f"https://www.bing.com/search?q=test")  # {choice(Liste_de_mot)}')
    CustomSleep(uniform(1, 2))
    RGPD()
    send_keys_wait(
        driver.find_element(By.ID, "sb_form_q"),
        Keys.BACKSPACE
        + Keys.BACKSPACE
        + Keys.BACKSPACE
        + Keys.BACKSPACE
        + Keys.BACKSPACE
        + Keys.BACKSPACE,
    )

    for i in range(override):
        mot = choice(Liste_de_mot)
        try:
            send_keys_wait(driver.find_element(By.ID, "sb_form_q"), mot)
            driver.find_element(By.ID, "sb_form_q").send_keys(Keys.ENTER)
        except Exception as e :
            printf(e)
            sleep(10)
            driver.get('https://www.bing.com/search?q=pls')
            sleep(3)
            send_keys_wait(driver.find_element(By.ID, "sb_form_q"), mot)
            driver.find_element(By.ID, "sb_form_q").send_keys(Keys.ENTER)

        AdvanceTask(task["PC"], 1/override * 100 )
        CustomSleep(uniform(5, 20))

        try:
            driver.find_element(By.ID, "sb_form_q").clear()
        except Exception as e:
            printf(e)
            try:
                driver.get('https://www.bing.com/search?q=pls')
                driver.find_element(By.ID, "sb_form_q").clear()
            except Exception as e:
                LogError(f"BingPcSearch - clear la barre de recherche - {e}", driver, _mail)
    AdvanceTask(task["PC"], 100 )
    ChangeColor(task["PC"], "green")


def unban():
    driver.find_element(By.ID, "StartAction").click()
    CustomSleep(2)
    txt = driver.page_source
    uuid0 = findall('wlspispHIPCountrySelect([a-z0-9]+)', txt)[0]
    uuid1 = findall('wlspispHIPPhoneInput([a-z0-9]+)', txt)[0]
    uuid2 = findall('wlspispHipSendCode([a-z0-9]+)', txt)[0]
    uuid3 = findall('wlspispSolutionElement([a-z0-9]+)', txt)[0]
    sel = Select(driver.find_element(By.ID, "wlspispHIPCountrySelect" + uuid0))
    CC = input("enter Contry code (FR, ...) ")
    sel.select_by_value(CC)
    WaitUntilVisible(By.ID, "wlspispHIPPhoneInput" + uuid1, browser=driver)
    phone = input("entrez le numero de téléphone : +33")
    phone_box = driver.find_element(By.ID, "wlspispHIPPhoneInput" + uuid1)
    phone_box.send_keys(phone)
    WaitUntilVisible(By.ID, "wlspispHipSendCode" + uuid2, browser=driver)
    send_link = driver.find_element(By.ID, "wlspispHipSendCode" + uuid2)
    send_link.click()
    WaitUntilVisible(By.ID, "wlspispSolutionElement" + uuid3, browser=driver)
    LogError("test", driver,"phone test")
    answer_box = driver.find_element(By.ID, "wlspispSolutionElement" + uuid3)
    answer = input("entrez le contenu du msg : ")
    answer_box.send_keys(answer)
    send_box = driver.find_element(By.ID, "ProofAction")
    send_box.click()
    WaitUntilVisible(By.ID, "FinishAction", browser=driver)
    continue_box = driver.find_element(By.ID, "FinishAction")
    continue_box.click()
 

def TryPlay(nom="inconnu", task = None):
    RGPD()
    printf("TryPlay en cours")

    def play(number):
        if number == 8 or number == 9:
            try:
                printf(f"\033[96m Quiz 8 détecté sur la page {nom} \033[0m")
                PlayQuiz8(task=task)
                printf(f"\033[92m Quiz 8 reussit sur {nom} \033[0m")
            except Exception as e:
                printf(f"echec de PlayQuiz 8. Aborted {e} \033[0m")

        elif number == 5 or number == 4:
            try:
                printf(f"\033[96m Quiz 4 détecté sur la page {nom} \033[0m")
                PlayQuiz4()
                printf(f"\033[92m Quiz 4 reussit sur {nom} \033[0m")
            except Exception as e:
                printf(f"echec de PlayQuiz 4. Aborted {e} \033[0m")

        elif number == 3 or number == 2:
            try:
                printf(f"\033[96m Quiz 2 détecté sur la page {nom}\033[0m")
                PlayQuiz2()
                printf(f"\033[92m Quiz 2 reussit sur la page {nom}\033[0m")
            except Exception as e:
                printf(f"echec de PlayQuiz 2. Aborted {e}")
        else:
            LogError("probleme dans la carte : il y a un bouton play et aucun quiz detecté", driver, _mail)

    try:
        driver.find_element(By.ID, "rqStartQuiz").click()  # start the quiz
        number = driver.page_source.count("rqAnswerOption")
        play(number)

    except Exception as e:
        # printf(e) normal error here
        if "bt_PollRadio" in driver.page_source:
            try:
                printf("Poll détected")
                RGPD()
                PlayPoll()
                printf("Poll reussit  ")
            except Exception as e:
                printf(f"TryPlay - 1 - Poll aborted {e}")

        elif "rqQuestionState" in driver.page_source:
            try:
                number = driver.page_source.count("rqAnswerOption")
                printf(f"recovery détecté. quiz : {number}")
                play(number-1)
            except Exception as e:
                printf(f"TryPlay - 2 - {e}")

        elif search("([0-9]) de ([0-9]) finalisée", driver.page_source):
            print("fidélité")
            RGPD()
            Fidelite()

        else:
            printf(f"rien à faire sur la page {nom}")
            RGPD()
            CustomSleep(uniform(3, 5))


def LogPoint(account="unknown"):  # log des points sur discord
    def get_points():
        driver.get("https://www.bing.com/rewardsapp/flyout")
        if not LINUX_HOST:
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        else:
            asyncio.set_event_loop(asyncio.new_event_loop())

        regex1 = '<a href="https://rewards\.bing\.com/" title="((.{1,3}),(.{1,3})) points" target="_blank"'
        try:
            point = search(regex1, driver.page_source)[1].replace(",", "")

        except Exception as e:
            elem = driver.find_element(By.CSS_SELECTOR, '[title="Microsoft Rewards"]')
            elem.click()
            CustomSleep(5)
            driver.switch_to.window(driver.window_handles[len(driver.window_handles) - 1])
            CustomSleep(uniform(5,7))
            
            point = search('availablePoints":([\d]+)', driver.page_source)[1]
        return(point)
    for i in range (3):
        try : 
            points = get_points()
            break
        except Exception as e:
            CustomSleep(300)
            printf(f"LogPoints : {e}")
            points = None
            
    if not points : 
        LogError(f"impossible d'avoir les points :", driver, _mail)
    CustomSleep(uniform(3, 20))

    account = account.split("@")[0]

    if DISCORD_ENABLED_SUCCESS:

        if DISCORD_EMBED:
            embed = discord.Embed(
                title=f"{account} actuellement à {str(points)} points", colour=Colour.green()
            )
            embed.set_footer(text=account)
            webhookSuccess.send(embed=embed)
        else:
            webhookSuccess.send(f"{account} actuellement à {str(points)} points")
            
    if CLAIM_AMAZON and int(points) >= 7500:
        if (claim_amazon() == 1) :
            points = str( int(points) - 7500)

    if sql_enabled :
        add_to_database(account, points, sql_host, sql_usr, sql_pwd, sql_database)


def Fidelite():
    try:
        while 1: #close all tabs
            try:
                Close(1)
            except:
                break
        try : 
            result = get(FidelityLink) #get the url of fidelity page
        except Exception as e :
            printf(e)
            result = False

        if result : 
            lien = result.content.decode("UTF-8")

            if (lien.split(":")[0] == "https") or (lien.split(":")[0] == "http") : 
                
                driver.get(lien)
                
                WaitUntilVisible(By.CSS_SELECTOR, 'div[class="pull-left spacer-48-bottom punchcard-row"]', browser=driver)
                choix = driver.find_element(By.CSS_SELECTOR, 'div[class="pull-left spacer-48-bottom punchcard-row"]')  # pull-left spacer-48-bottom punchcard-row? USELESS ?

                nb = search("([0-9]) of ([0-9]) completed", driver.page_source)
                if nb is None:
                    nb = search("([0-9]) de ([0-9]) finalisé", driver.page_source)
                if nb is None :
                    nb = search("([0-9]) licence\(s\) sur ([0-9]) disponible\(s\)", driver.page_source)
                if nb is None :
                    nb = [0,0,0]
                for i in range(int(nb[2]) - int(nb[1])):
                    driver.refresh()
                    CustomSleep(2)
                    choix = driver.find_element(By.CLASS_NAME, "spacer-48-bottom")
                    try : 
                        ButtonText = search('<span class="pull-left margin-right-15">([^<^>]+)</span>',choix.get_attribute("innerHTML"))[1]
                        bouton = driver.find_element(By.XPATH, f'//span[text()="{ButtonText}"]')
                        bouton.click()
                    except Exception as e1 :
                        try : 
                            t = driver.find_element(By.XPATH,'/html/body/div[1]/div[2]/main/div[2]/div[2]/div[7]/div[3]/div[1]/a')
                            t.click()
                        except Exception as e2 :
                            LogError(f"fidélité - double erreur - e1 : {e1} - e2 {e2}", driver, _mail)
                            break
                    CustomSleep(uniform(3, 5))
                    driver.switch_to.window(driver.window_handles[1])
                    TryPlay(driver.title)
                    driver.get(lien) # USELESS ?
                    CustomSleep(uniform(3, 5))
                    try:
                        Close(driver.window_handles[1])
                    except Exception as e:
                        printf(e)
                printf("fidelité - done")
            else :
                printf("lien invalide")
    except Exception as e:
        LogError(f"Fidélité {e}", driver, _mail)


def Mlogin(echec):
    try:
        MobileDriver.get("https://www.bing.com/search?q=test+speed")
        MRGPD()
        printf("start of Mobile login")
        MobileDriver.find_element(By.ID, "mHamburger").click()
        WaitUntilVisible(By.ID, "hb_s", browser=MobileDriver)
        MobileDriver.find_element(By.ID, "hb_s").click()
        WaitUntilVisible(By.ID, "i0116", browser=MobileDriver)
        mail = MobileDriver.find_element(By.ID, "i0116")
        send_keys_wait(mail, _mail)
        mail.send_keys(Keys.ENTER)
        WaitUntilVisible(By.ID, "i0118", browser=MobileDriver)
        pwd = MobileDriver.find_element(By.ID, "i0118")
        send_keys_wait(pwd, _password)
        pwd.send_keys(Keys.ENTER)
        CustomSleep(uniform(1, 2))
        for i in ["KmsiCheckboxField", "iLooksGood", "idSIButton9"]:
            try:
                MobileDriver.find_element(By.ID,i ).click()
            except Exception as e:
                pass

        printf("end of Mobile login")

    except Exception as e:
        echec += 1
        if echec <= 3:
            printf(f"echec du login sur la version mobile. on reesaye ({echec}/3), {e}")
            CustomSleep(uniform(5, 10))
            Mlogin(echec)
        else:
            LogError(
                f"login impossible 3 fois de suite. {e}", MobileDriver, _mail
            )
            MobileDriver.quit()
            return True


def MRGPD():
    try:
        MobileDriver.find_element(By.ID, "bnp_btn_accept").click()
    except Exception as e:
        pass
    try:
        MobileDriver.find_element(By.ID, "bnp_hfly_cta2").click()
    except Exception as e:
        pass


def Alerte():
    try:
        alert = MobileDriver.switch_to.alert
        alert.dismiss()
    except exceptions.NoAlertPresentException as e:
        pass
    except Exception as e:
        LogError(f"mobile.py -> Alerte : {e}", MobileDriver, _mail)


def BingMobileSearch(override=randint(22, 25)):
    global MobileDriver
    MobileDriver = "unable to start"
    try:
        try:
            MobileDriver = FirefoxDriver(mobile=True)
            MobileDriver.implicitly_wait(15)
        except Exception as e:
            LogError("BingMobileSearch - 1 - echec de la creation du driver mobile", MobileDriver, _mail)
            ChangeColor(task["Mobile"], "red")
        echec = 0

        if not Mlogin(echec):
            StartTask(task["Mobile"])
            CustomSleep(uniform(1, 2))
            MRGPD()
            CustomSleep(uniform(1, 1.5))
    
            for i in range(override):  # 20
                try :
                    mot = choice(Liste_de_mot)
                    send_keys_wait(MobileDriver.find_element(By.ID, "sb_form_q"), mot)
                    MobileDriver.find_element(By.ID, "sb_form_q").send_keys(Keys.ENTER)
                    AdvanceTask(task["Mobile"], 1/override * 100)
                    #printf(MobileDriver.current_url)
                    CustomSleep(uniform(5, 20))
                    Alerte()  # verifie si il y a des alertes (demande de positions ....)
                    MobileDriver.find_element(By.ID, "sb_form_q").clear()
                except :
                    driver.refresh()
                    CustomSleep(30)
                    i -= 1
            MobileDriver.quit()
            ChangeColor(task["Mobile"], "green")

    except Exception as e:
        LogError(f"BingMobileSearch - 4 - {e}", MobileDriver, _mail)
        MobileDriver.quit()


def DailyRoutine(custom = False):
    
    ShowDefaultTask()
    try : 
        if not custom: # custom already login 
            login()
    except Banned :
        LogError("THIS ACCOUND IS BANNED. FIX THIS ISSUE WITH -U", driver, _mail)
        return()

    try:
        AllCard()
    except Exception as e:
        LogError(f"DailyRoutine - AllCard - \n{e}", driver, _mail)

    try:
        BingPcSearch()
    except Exception as e:
        LogError(f"DailyRoutine - BingPcSearch - \n{e}", driver, _mail)
        
    try:
        BingMobileSearch()
    except Exception as e:
        LogError(f"DailyRoutine - BingMobileSearch - \n{e}", driver, _mail)

    try:
        Fidelite()
    except Exception as e:
        LogError(f"DailyRoutine - Fidelité - \n{e}", driver, _mail)

    try:
        LogPoint(_mail)
    except Exception as e:
        LogError(f"DailyRoutine - LogPoint - \n{e}", driver, _mail)


def close():
    driver.quit()
    quit()


def dev():
    pass


def CustomStart(Credentials):
    global START_TIME
    if not LINUX_HOST :
        raise NameError('You need to be on linux to do that, due to the utilisation of a module named enquieries, sorry.') 
    global driver, _mail, _password, p, task

    system("clear")  # clear from previous command to allow a clean choice
    actions = ["tout", "daily", "pc", "mobile", "LogPoint","Fidelite", "dev"]
    Actions = enquiries.choose("quels Actions ?", actions, multi=True)
    liste = SelectAccount()
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

            driver = FirefoxDriver()
            driver.implicitly_wait(10)

            if login() != "STOP":
                if "tout" in Actions:
                    DailyRoutine(True)

                if "daily" in Actions:
                    try:
                        AllCard()
                    except Exception as e:
                        LogError(f"AllCards - {e} -- override", driver, _mail)

                if "pc" in Actions:
                    try:
                        ShowTask(task["PC"])
                        BingPcSearch()
                    except Exception as e:
                        LogError(f"il y a eu une erreur dans BingPcSearch, {e} -- override", driver, _mail)

                if "mobile" in Actions:
                    try:
                        ShowTask(task["Mobile"])
                        BingMobileSearch()
                    except Exception as e:
                        LogError(f"BingMobileSearch - {e} -- override", driver, _mail)

                if "Fidelite" in Actions:
                    try :
                        Fidelite()
                    except Exception as e :
                        LogError(f"Fidelite - {e} -- override", driver, _mail)

                if "dev" in Actions:
                    try:
                        dev()
                    except Exception as e:
                        printf(e)
                        break

                if not "tout" in Actions:
                    try:
                        LogPoint(_mail)
                    except Exception as e:
                        print(f"CustomStart {e}")
            driver.close()


def SelectAccount(multiple = True):
    system("clear")  # clear from previous command to allow a clean choice
    emails = [x[0] for x in Credentials]  # list of all email adresses
    emailsSelected = enquiries.choose("quels comptes ?", emails, multi=multiple)
    return([x for x in Credentials if x[0] in emailsSelected])


def unban2():
    global _mail, _password, driver
    _mail, _password  = SelectAccount(False)[0]
    try :
        driver = FirefoxDriver()
        login()
        raise NotBanned
    except Banned :
        unban()
    except NotBanned :
        printf("you are not currently banned on this account")


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

if CUSTOM_START:
        CustomStart(Credentials)
elif UNBAN:
    unban2()
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
            CustomSleep(1)
            printf("début du driver")
            driver = FirefoxDriver()
            printf("driver demarré")
            driver.implicitly_wait(7)

            try:
                DailyRoutine()
                driver.quit()
                attente = uniform(1200, 3600)
                printf(f"finis. attente de {round(attente/60)}min")
                CustomSleep(attente)

            except KeyboardInterrupt:
                print("canceled")
                close()
