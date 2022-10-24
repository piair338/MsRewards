#!/usr/bin/python3.10
import asyncio
from csv import reader
from os import sys, system, path
from random import choice, randint, shuffle, uniform
from re import findall, search
from sys import platform
from time import sleep
from requests import get
from datetime import timedelta
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from modules.db import add_to_database
from modules.config import *
from modules.tools import *

global driver


def WaitUntilVisible(by, id, to = 20, browser = driver):
    try :
        WebDriverWait(browser, to).until(EC.visibility_of_element_located((by,id)), "element not found")
    except TimeoutException as e:
        print(f"element not found after {to}s")



def claim_amazon(): 
    try : 
        driver.get("https://rewards.microsoft.com/redeem/000803000031")
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
            driver.get("https://rewards.microsoft.com/redeem/orderhistory")
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
                webhookFailure.send(_mail +" - "+ fcode)
                return(1)
            else :
                LogError("impossible de localiser le code ", driver)
                return(1)
            
        else :
            LogError("la recuperation ne peux pas être automatique", driver)
            return(0)
    except Exception as e :
        LogError(f'problème dans la recuperation : {str(e)}', driver)


def setup_proxy(ip, port) :
    PROXY = f"{ip}:{port}"
    webdriver.DesiredCapabilities.FIREFOX['proxy'] = {
        "httpProxy": PROXY,
        "sslProxy": PROXY,
        "proxyType": "MANUAL",
    }


def FirefoxDriver(mobile=False, Headless=Headless):
    if proxy_enabled :
        setup_proxy(proxy_address,proxy_port)
    PC_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        "AppleWebKit/537.36 (KHTML, like Gecko)"
        "Chrome/104.0.5112.102 Safari/537.36 Edg/104.0.1293.70"
    )
    MOBILE_USER_AGENT = (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_5 like Mac OS X)"
        "AppleWebKit/605.1.15 (KHTML, like Gecko)"
        "CriOS/103.0.5060.63 Mobile/15E148 Safari/604.1"
    )
    
    options = Options()
    options.set_preference("browser.link.open_newwindow", 3)
    if Headless:
        options.add_argument("-headless")
    if mobile :
        options.set_preference("general.useragent.override", MOBILE_USER_AGENT)
    else :
        options.set_preference("general.useragent.override", PC_USER_AGENT)
    driver = webdriver.Firefox(options=options)
    driver.set_window_size(1900 + hash(_mail)%20 , 1070 + hash(_password + "salt")%10)
    return driver


def CustomSleep(temps):
    try : 
        if FAST and temps > 50:
            sleep(temps/10)
            return()
        if not LOG or not LINUX_HOST: #only print sleep when user see it
            points = ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]
            passe = 0
            for i in range(int(temps)):
                for i in range(8):
                    sleep(0.125)
                    passe += 0.125
                    print(f"{points[i]}  -  {round(float(temps) - passe, 3)}", end="\r")
            print("                        ", end="\r")

        else:
            sleep(temps)
    except KeyboardInterrupt :
        printf("attente annulée")



def progressBar(current, total=30, barLength=20, name="Progress"):
    percent = float(current + 1) * 100 / total
    arrow = "-" * int(percent / 100 * barLength - 1) + ">"
    spaces = " " * (barLength - len(arrow))
    print(name + ": [%s%s] %d %%" % (arrow, spaces, percent), end="\r")


def Close(fenetre, SwitchTo=0):
    driver.switch_to.window(fenetre)
    driver.close()
    driver.switch_to.window(driver.window_handles[SwitchTo])


#Deal with RGPD popup as well as some random popup like 'are you satisfied' one
def RGPD():
    try:
        driver.find_element(By.ID, "bnp_btn_accept").click()
    except:
        pass
    try:
        driver.find_element(By.ID, "bnp_hfly_cta2").click()
    except:
        pass
    try : 
        driver.find_element(By.id, "bnp_hfly_close").click() #are you satisfied popup
    except :
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
            LogError("PlayQuiz2" + str(e), driver)
            break
    printf("PlayQuiz2 finis")


def PlayQuiz8(override=3):
    printf(f"PlayQuiz8 : start, override : {override}")
    try:
        c = 0
        for i in range(override):
            RGPD()
            CustomSleep(uniform(3, 5))
            ListeOfGood = []
            for i in range(1, 9):
                try:
                    Card = driver.find_element(By.ID, f"rqAnswerOption{i-1}")
                    if 'iscorrectoption="True" ' in Card.get_attribute("outerHTML"):
                        ListeOfGood.append(f"rqAnswerOption{i-1}")  # premier div = 3 ?
                except Exception as e:
                    LogError(f"playquiz8 - 1 - {e}", driver)
            shuffle(ListeOfGood)

            for i in ListeOfGood:
                CustomSleep(uniform(3, 5))
                c += 1
                progressBar(c, 16, name="Quiz 8 ")
                try:
                    elem = driver.find_element(By.ID, i)
                    elem.click()
                except exceptions.ElementNotInteractableException as e:
                    try:
                        driver.execute_script("arguments[0].click();", elem)
                    except Exception as e:
                        LogError(f"playquizz8 - 2 - {e}", driver)
                except exceptions.NoSuchElementException as e :
                    try : 
                        driver.refresh()
                        CustomSleep(10)
                        elem = driver.find_element(By.ID, i)
                        elem.click()
                    except Exception as e :
                        LogError(f"playquizz8 - 5 -  {e}", driver)
                except Exception as e:
                    if CUSTOM_START:
                        printf(f"playquiz8 - 3 -  {e}") # may append during 
                    else:
                        LogError(f"playquizz8 - 3 -  {e}", driver)

    except Exception as e:
        LogError(f"PlayQuiz8 - 4 - {e} \n ListOfGood : {str(ListeOfGood)}", driver)
        
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
        LogError(f"PlayQuiz4 {str(e)}", driver)
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
        LogError("PlayPoll" + str(e), driver)
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
            for i in range(3):
                CustomSleep(uniform(3, 5))
                try:
                    printf("dailycards - show pannels")
                    titre = "erreur"
                    driver.find_element(
                        By.XPATH,f"/html/body/div/div/div[3]/div[2]/div[1]/div[2]/div/div[{i+1}]/a/div/div[2]",
                    ).click()
                    sleep(1)
                    titre = driver.title
                    TryPlay(titre)
                    sleep(1)
                    reset()
                    printf(f"DailyCard {titre} ok ")
                except Exception as e:
                    printf(f"Allcard card {titre} error ({e})")
        except Exception as e:
            LogError(f"Dailycards {e}", driver)

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
    for i in range(2): # don't seem useful for fixing error
        try :
            weekly_cards()
            break
        except Exception as e:
            LogError(f"weekly_cards, try n°{i+1} \n {e}", driver)
            if i == 0 :
                driver.refresh()
            else :
                CustomSleep(1800) 
                driver.refresh()



"""
login() tries to login to your micrososft account.
it uses global variable _mail and _password to login
"""
def login():
    global driver
    def sub_login():
        printf("sublogin : start")
        driver.get("https://www.bing.com/rewardsapp/flyout")
        try:
            driver.find_element(By.CSS_SELECTOR, f'[title="Rejoindre"]').click()  # depend of the language of the page
        except:
            try :
                driver.find_element(By.CSS_SELECTOR, f'[title="Join now"]').click()  # depend of the language of the page
            except :
                raise ValueError('already logged in')

        WaitUntilVisible(By.ID, "i0116", browser = driver)
        mail = driver.find_element(By.ID, "i0116")
        send_keys_wait(mail, _mail)
        mail.send_keys(Keys.ENTER)
        WaitUntilVisible(By.ID, "i0118", browser = driver)
        pwd = driver.find_element(By.ID, "i0118")
        send_keys_wait(pwd, _password)
        pwd.send_keys(Keys.ENTER)
        CustomSleep(5)
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
        except Exception as e:
            LogError("login - 3 - " + str(e), driver)
            driver.close()
            CustomSleep(1200)
            driver = FirefoxDriver()
    return("STOP")


def BingPcSearch(override=randint(35, 40)):
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

        progressBar(i, override, name="PC")
        CustomSleep(uniform(5, 20))

        try:
            driver.find_element(By.ID, "sb_form_q").clear()
        except Exception as e:
            printf(e)
            try:
                driver.get('https://www.bing.com/search?q=pls')
                driver.find_element(By.ID, "sb_form_q").clear()
            except Exception as e:
                LogError(f"BingPcSearch - clear la barre de recherche - {e}", driver)

    print("\n\n")




def TryPlay(nom="inconnu"):
    RGPD()
    printf("TryPlay en cours")

    def play(number, override=None):
        if number == 8 or number == 9:
            try:
                printf(f"\033[96m Quiz 8 détecté sur la page {nom} \033[0m")
                PlayQuiz8()
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
            LogError("probleme dans la carte : il y a un bouton play et aucun quiz detecté", driver)

    try:
        driver.find_element(By.ID, "rqStartQuiz").click()  # start the quiz
        number = driver.page_source.count("rqAnswerOption")
        play(number)

    except Exception as e:
        # printf(e) normal error here
        if "bt_PollRadio" in driver.page_source:
            try:
                printf("Poll détected", end="\r")
                RGPD()
                PlayPoll()
                printf("Poll reussit  ")
            except Exception as e:
                printf(f"TryPlay - 1 - Poll aborted {e}")

        elif "rqQuestionState" in driver.page_source:
            try:
                number = driver.page_source.count("rqAnswerOption")
                restant = len(
                    findall('"rqQuestionState.?." class=', driver.page_source)
                ) - len(
                    findall(
                        '"rqQuestionState.?." class="filledCircle"', driver.page_source
                    )
                )
                printf(f"recovery détecté. quiz : {number}, restant : {restant +1}")
                play(number-1, override=restant + 1)
            except Exception as e:
                printf("TryPlay - 2 - " + e)

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
        LogError(f"impossible d'avoir les points : {e}", driver)
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
            points -= 7500

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
            printf(lien)

            if (lien.split(":")[0] == "https") or (lien.split(":")[0] == "http") : 
                
                driver.get(lien)
                CustomSleep(5)
                try :
                    choix = driver.find_element(By.CSS_SELECTOR, 'div[class="pull-left spacer-48-bottom punchcard-row"]')  # pull-left spacer-48-bottom punchcard-row? USELESS ?
                except :
                    CustomSleep(300)
                    choix = driver.find_element(By.CSS_SELECTOR, 'div[class="pull-left spacer-48-bottom punchcard-row"]')  # pull-left spacer-48-bottom punchcard-row? USELESS ?
                    
                nb = search("([0-9]) of ([0-9]) completed", driver.page_source)
                if not nb:
                    nb = search("([0-9]) de ([0-9]) finalisé", driver.page_source)
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
                            t = driver.find_element(By.XPATH,'/html/body/div[1]/div[2]/main/div[2]/div[2]/div[7]/div[3]/div[1]')
                            t.click()
                        except Exception as e2 :
                            LogError(f"fidélité - double erreur - e1 : {e1} - e2 {e2}", driver)
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
        LogError("Fidélité" + str(e), driver)


def Mlogin(echec):
    try:
        MobileDriver.get("https://www.bing.com/search?q=test+speed")
        MRGPD()
        printf("début du login")
        MobileDriver.find_element(By.ID, "mHamburger").click()
        CustomSleep(uniform(1, 2))
        MobileDriver.find_element(By.ID, "hb_s").click()
        CustomSleep(uniform(1, 2))
        mail = MobileDriver.find_element(By.ID, "i0116")
        send_keys_wait(mail, _mail)
        mail.send_keys(Keys.ENTER)
        CustomSleep(uniform(7, 9))
        pwd = MobileDriver.find_element(By.ID, "i0118")
        send_keys_wait(pwd, _password)
        pwd.send_keys(Keys.ENTER)
        CustomSleep(uniform(1, 2))
        try:
            MobileDriver.find_element(By.ID, "KmsiCheckboxField").click()
        except Exception as e:
            pass
        try:
            MobileDriver.find_element(By.ID, "iLooksGood").click()
        except Exception as e:
            pass
        try:
            MobileDriver.find_element(By.ID, "idSIButton9").click()
        except Exception as e:
            pass
        printf("fin du Mlogin")

    except Exception as e:
        echec += 1
        if echec <= 3:
            printf(
                f"echec du login sur la version mobile. on reesaye ({echec}/3), {e}"
            )
            CustomSleep(uniform(5, 10))
            Mlogin(echec)
        else:
            LogError(
                f"login impossible 3 fois de suite. {e}", MobileDriver
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
        LogError(
            f"mobile.py -> Alerte : {e}",
            driver=MobileDriver,
        )


def BingMobileSearch(override=randint(22, 25)):
    global MobileDriver
    MobileDriver = "unable to start"
    try:
        try:
            MobileDriver = FirefoxDriver(mobile=True)
            MobileDriver.implicitly_wait(15)
        except Exception as e:
            LogError("BingMobileSearch - 1 - echec de la creation du driver mobile", MobileDriver)
        echec = 0

        if not Mlogin(echec):

            CustomSleep(uniform(1, 2))
            MRGPD()
            CustomSleep(uniform(1, 1.5))
    
            for i in range(override):  # 20
                try :
                    mot = choice(Liste_de_mot)
                    send_keys_wait(MobileDriver.find_element(By.ID, "sb_form_q"), mot)
                    MobileDriver.find_element(By.ID, "sb_form_q").send_keys(Keys.ENTER)
                    progressBar(i, override, name="Mobile")
                    printf(MobileDriver.current_url)
                    CustomSleep(uniform(5, 20))

                    Alerte()  # verifie si il y a des alertes (demande de positions ....)

                    MobileDriver.find_element(By.ID, "sb_form_q").clear()
                except :
                    driver.refresh()
                    CustomSleep(30)
                    i -= 1
            MobileDriver.quit()

    except Exception as e:
        LogError("BingMobileSearch - 4 - " + str(e), MobileDriver)
        MobileDriver.quit()


def DailyRoutine(custom = False):
    if not custom :
        MainWindows = login()
    else :
        MainWindows = ""
        
    if MainWindows != "STOP" :
        try:
            AllCard()
        except Exception as e:
            LogError(f"DailyRoutine - AllCard - \n{e}", driver)

        try:
            BingPcSearch()
        except Exception as e:
            LogError(f"DailyRoutine - BingPcSearch - \n{e}", driver)
        CustomSleep(uniform(3, 20))

        try:
            Fidelite()
        except Exception as e:
            LogError(f"DailyRoutine - Fidelité - \n{e}", driver)
         
        try:
            BingMobileSearch()
        except Exception as e:
            LogError(f"DailyRoutine - BingMobileSearch - \n{e}", driver)
        CustomSleep(uniform(3, 20))

        try:
            LogPoint(_mail)
        except Exception as e:
            LogError(f"DailyRoutine - LogPoint - \n{e}", driver)
    else : 
        LogError(f"probleme de login sur le comte {_mail}", driver)


def close():
    driver.quit()
    quit()


def dev():
    pass


def CustomStart(Credentials):
    if not LINUX_HOST :
        raise NameError('You need to be on linux to do that, due to the utilisation of a module named enquieries, sorry.') 
    global driver
    global _mail
    global _password

    ids = [x[0] for x in Credentials]  # list of all email adresses
    actions = ["tout", "daily", "pc", "mobile", "LogPoint","Fidelite", "dev"]

    system("clear")  # clear from previous command to allow a clean choice
    Comptes = enquiries.choose("quels comptes ?", ids, multi=True)
    Actions = enquiries.choose("quels Actions ?", actions, multi=True)

    for i in Comptes:

        _mail = Credentials[ids.index(i)][0]
        _password = Credentials[ids.index(i)][1]
        driver = FirefoxDriver()
        driver.implicitly_wait(10)

        if login() != "STOP":
            if "tout" in Actions:
                DailyRoutine(True)

            if "daily" in Actions:
                try:
                    AllCard()
                except Exception as e:
                    LogError(f"AllCards - {e} -- override", driver)

            if "pc" in Actions:
                try:
                    BingPcSearch()
                except Exception as e:
                    LogError(f"il y a eu une erreur dans BingPcSearch, {e} -- override", driver)

            if "mobile" in Actions:
                try:
                    BingMobileSearch()
                except Exception as e:
                    LogError(f"BingMobileSearch - {e} -- override", driver)

            if "Fidelite" in Actions:
                try :
                    Fidelite()
                except Exception as e :
                    LogError(f"Fidelite - {e} -- override", driver)

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
                    print("CustomStart " + str(e))
        driver.close()


with open(CREDENTIALS_PATH) as f:
    reader = reader(f)
    Credentials = list(reader)

shuffle(Credentials)

if CUSTOM_START:
    CustomStart(Credentials)
else:
    for _mail, _password in Credentials:
        system("pkill -9 firefox")
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
