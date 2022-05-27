#!/usr/bin/python3.10
import asyncio
import configparser
import os
from csv import reader
from os import sys, system
from random import choice, randint, shuffle, uniform
from re import findall, search
from sys import platform
from time import sleep, time
from requests import get
from datetime import timedelta
import discord
from discord import (  # Importing discord.Webhook and discord.RequestsWebhookAdapter
    Colour,
    Embed,
    RequestsWebhookAdapter,
    Webhook,
)
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import argparse
import mysql.connector

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
    help="enable full logging in terminal",
    action="store_true",
)

args = parser.parse_args()
override = args.override
Log = args.log
FullLog = args.fulllog

IsLinux = platform == "linux"
start_time = time()

global driver
driver = None


def Timer(text="undefined"):
    return(f"[{timedelta(seconds = round(float(time() - start_time)))}] : " + str(text))


if IsLinux:
    import enquiries
else:
    system("")  # enable colors in cmd

config_path = "/home/pi/MsReward/config"
config = configparser.ConfigParser()
config.read(config_path)
#path comfigurations
MotPath = config["PATH"]["motpath"]
LogPath = config["PATH"]["logpath"]
#discord configurations
SuccessLink = config["DISCORD"]["successlink"]
ErrorLink = config["DISCORD"]["errorlink"]
discord_enabled = config["DISCORD"]["enabled"]
#base settings
FidelityLink = config["SETTINGS"]["FidelityLink"]
embeds = config["SETTINGS"]["embeds"] == "True" #print new point value in an embed
Headless = config["SETTINGS"]["headless"] == "True"
#proxy settings
proxy_enabled = config["PROXY"]["enabled"] == "True"
proxy_address = config["PROXY"]["url"]
proxy_port = config["PROXY"]["port"]
#MySQL settings
sql_enabled = config["SQL"]["enabled"] == "True"
sql_usr = config["SQL"]["usr"]
sql_pwd = config["SQL"]["pwd"]
sql_host = config["SQL"]["host"]
sql_database = config["SQL"]["database"]

g = open(MotPath, "r", encoding="utf-8")
lines = g.readlines()
if len(lines) < 3 : 
    Liste_de_mot = list(lines[0].split(","))
else :
    Liste_de_mot = [x.replace('\n', "") for x in lines]
g.close()


webhookFailure = Webhook.from_url(ErrorLink, adapter=RequestsWebhookAdapter())


if discord_enabled:
    webhookSuccess = Webhook.from_url(SuccessLink, adapter=RequestsWebhookAdapter())

def setup_proxy(ip, port) :
    PROXY = f"{ip}:{port}"
    webdriver.DesiredCapabilities.FIREFOX['proxy'] = {
        "httpProxy": PROXY,
        "sslProxy": PROXY,
        "proxyType": "MANUAL",
    }


def add_row(compte, points, mycursor, mydb):
    sql = "INSERT INTO daily (compte, points, date) VALUES (%s, %s, current_date())"
    val = (compte, points)
    mycursor.execute(sql, val)
    mydb.commit()
    printf(mycursor.rowcount, "record creatted.")


def update_row(compte, points, mycursor, mydb):
    sql = f"UPDATE daily SET points = {points} WHERE compte = '{compte}' AND date = current_date() ;"
    mycursor.execute(sql)
    mydb.commit()
    printf(mycursor.rowcount, "record(s) updated")


def get_row(compte, points, mycursor, same_points = True): #return if there is a line with the same ammount of point or with the same name as well as the same day
    if same_points :
        mycursor.execute(f"SELECT * FROM daily WHERE points = {points} AND compte = '{compte}' AND date = current_date() ;")
    else :
        mycursor.execute(f"SELECT * FROM daily WHERE compte = '{compte}' AND date = current_date() ;")
    myresult = mycursor.fetchall()
    return(len(myresult) == 1)


def add_to_database(compte, points):
    mydb = mysql.connector.connect(
        host=sql_host,
        user=sql_usr,
        password=sql_pwd,
        database = sql_database
    )
    mycursor = mydb.cursor()

    if get_row(compte, points,mycursor, True): #check if the row exist with the same ammount of points and do nothind if it does
        printf("les points sont deja bon")
    elif get_row(compte, points,mycursor, False) : #check if the row exist, but without the same ammount of points and update the point account then
        update_row(compte, points,mycursor,mydb)
        printf("row updated")
    else : # if the row don't exist, create it with the good ammount of points
        add_row(compte, points,mycursor,mydb)
        printf("row added")

    mycursor.close()
    mydb.close()


def FirefoxDriver(mobile=False, Headless=Headless):
    if proxy_enabled :
        setup_proxy(proxy_address,proxy_port)

    PC_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134"
    )
    MOBILE_USER_AGENT = (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_8_1 like Mac OS X)"
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1"
    )

    options = Options()
    options.set_preference("browser.link.open_newwindow", 3)
    if Headless:
        options.add_argument("-headless")
    if mobile :
        options.set_preference("general.useragent.override", MOBILE_USER_AGENT)
    else :
        options.set_preference("general.useragent.override", PC_USER_AGENT)
    return webdriver.Firefox(options=options)


def printf(txt, end="", Mobdriver=driver):
    if Log:
        print(Timer(txt))
    elif FullLog:
        try :
            LogError(Timer(txt), Mobdriver=Mobdriver)
        except Exception as e:
            print("\n" + Timer(e) + "\n")


def CustomSleep(temps):
    if Log or not IsLinux: #only print sleep when user see it
        c = False
        points = [
            " .   ",
            "  .  ",
            "   . ",
            "    .",
            "    .",
            "   . ",
            "  .  ",
            " .   ",
        ]
        for i in range(int(temps)):
            c = True
            for i in range(8):
                sleep(0.125)
                print(points[i], end="\r")

        if c:
            print(".   ", end="\r")
        sleep(temps - int(temps))
        print("\n")
    else:
        sleep(temps)


def ListTabs(Mdriver=None):
    tabs = []
    if Mdriver:
        ldriver = Mdriver
    else:
        ldriver = driver
    for i in ldriver.window_handles:
        ldriver.switch_to.window(i)
        tabs.append(ldriver.current_url)
    return tabs

#il faut fix le fait qu'il essaye d'envoyer un truc sans url, listtab[0] = about:blank
def LogError(message, log=FullLog, Mobdriver=None):
    if Mobdriver:
        gdriver = Mobdriver
    else:
        gdriver = driver
    if not log:
        print(f"\n\n\033[93m Erreur : {str(message)}  \033[0m\n\n")
    if IsLinux:
        with open("page.html", "w") as f:
            f.write(gdriver.page_source)

        gdriver.save_screenshot("screenshot.png")
        if not log:
            embed = discord.Embed(
                title="An Error has occured",
                description=str(message),
                colour=Colour.red(),
            )
        else:
            embed = discord.Embed(
                title="Full log is enabled",
                description=str(message),
                colour=Colour.blue(),
            )

        file = discord.File("screenshot.png")
        embed.set_image(url="attachment://screenshot.png")
        embed.set_footer(text=_mail)
        webhookFailure.send(embed=embed, file=file)
        webhookFailure.send(file=discord.File("page.html"))


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
PlayQuiz2([int : override]) make the quizz with 2 choice each time. They usually have 10 questions. 
override is the number of question, by default, it's 10. Can be usefull in some case, where the programm crashes before finishing the quizz
"""
def PlayQuiz2(override=10):
    printf("debut de PlayQuiz2")
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
            LogError("PlayQuiz2" + str(e))
            break
    printf("PlayQuiz2 finis")


def PlayQuiz8(override=3):
    printf(f"PlayQuiz8 : start, override : {override}")
    try:
        c = 0
        for i in range(override):
            RGPD()
            sleep(uniform(3, 5))
            ListeOfGood = []
            for i in range(1, 9):
                try:
                    Card = driver.find_element(By.ID, f"rqAnswerOption{i-1}")
                    if 'iscorrectoption="True" ' in Card.get_attribute("outerHTML"):
                        ListeOfGood.append(f"rqAnswerOption{i-1}")  # premier div = 3 ?
                except Exception as e:
                    LogError("playquiz8 - 1 - " + e)
            shuffle(ListeOfGood)

            for i in ListeOfGood:
                sleep(uniform(3, 5))
                c += 1
                progressBar(c, 16, name="Quiz 8 ")
                try:
                    elem = driver.find_element(By.ID, i)
                    elem.click()
                except exceptions.ElementNotInteractableException as e:
                    try:
                        driver.execute_script("arguments[0].click();", elem)
                    except Exception as e:
                        LogError("playquizz8 - 2 - " + e)
                except Exception as e:
                    if override:
                        printf("playquiz8 - 3 -" + e)
                    else:
                        LogError("playquizz8 - 3 - " + e)

    except Exception as e:
        LogError("PlayQuiz8 - 4 - " + str(e))
        print(str(ListeOfGood))
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
            printf(f"validation de la reponse                                     ",end="\r",)
            printf(f"validation de la reponse {i+1}/{override} {reponse}", end="\r")
            try:
                elem = driver.find_element(
                    By.CSS_SELECTOR, f'[data-option="{reponse}"]'
                )
                elem.click()
            except exceptions.ElementNotInteractableException:
                driver.execute_script("arguments[0].click();", elem)

    except Exception as e:
        LogError("PlayQuiz4" + str(e))
        raise ValueError(e)
    printf("PlayQuiz4 : end")


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
        LogError("PlayPoll" + str(e))
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
                sleep(1)
                try:
                    titre = "erreur"
                    driver.find_element(
                        By.XPATH,f"/html/body/div/div/div[3]/div[2]/div[1]/div[2]/div/div[{i+1}]/a/div/div[2]",
                    ).click()
                    sleep(1)
                    titre = driver.title
                    TryPlay(titre)
                    sleep(1)
                    reset()
                    print(f"DailyCard {titre} ok ")
                except Exception as e:
                    printf(f"Allcard card {titre} error ({e})")
        except Exception as e:
            LogError(f"Dailycards {e}")

    try:
        dailyCards()
    except:
        printf("erreur ici")

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
            printf("debut de l'une des cartes")
            driver.find_element(
                By.XPATH,
                "/html/body/div/div/div[3]/div[2]/div[2]/div[3]/div/div[1]/a/div/div[2]",
            ).click()
            printf("carte cliqué")
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
    for i in range(3):
        try :
            weekly_cards()
            break
        except Exception as e:
            LogError(f"weekly_cards, try n°{i+1} \n {e}")
            if i == 0 :
                driver.refresh()
            else :
                CustomSleep(1800)
                driver.refresh()


def send_keys_wait(element, keys):
    for i in keys:
        element.send_keys(i)
        sleep(uniform(0.1, 0.3))


def login():
    printf("login : start")
    try:
        driver.get("https://www.bing.com/rewardsapp/flyout")
        try:
            driver.find_element(By.CSS_SELECTOR, f'[title="Rejoindre"]').click()  # depend of the language of the page
        except:
            driver.find_element(By.CSS_SELECTOR, f'[title="Join now"]').click()  # depend of the language of the page

        mail = driver.find_element(By.ID, "i0116")
        send_keys_wait(mail, _mail)
        mail.send_keys(Keys.ENTER)
        CustomSleep(5)
        pwd = driver.find_element(By.ID, "i0118")
        send_keys_wait(pwd, _password)
        pwd.send_keys(Keys.ENTER)
        CustomSleep(5)
        printf("pwd envoyé")

        try:
            driver.find_element(By.ID, "KmsiCheckboxField").click()
        except Exception as e:
            printf(f"login - 1 - erreur validation bouton KmsiCheckboxField. pas forcement grave {e}")

        try:
            driver.find_element(By.ID, "iLooksGood").click()
        except Exception as e:
            printf(f"login - 2 - erreur validation bouton iLooksGood. pas forcement grave {e}")

        try:
            driver.find_element(By.ID, "idSIButton9").click()
        except Exception as e:
            printf(f"login - 2 - erreur validation bouton idSIButton9. pas forcement grave {e}")

        try:
            driver.find_element(By.ID, "iCancel").click()
        except Exception as e:
            printf(f"login - 2 - erreur validation bouton iCancel. pas forcement grave {e}")



        printf("login completed")
        RGPD()
        driver.get("https://www.bing.com/rewardsapp/flyout")

        MainWindows = driver.current_window_handle
        return MainWindows

    except Exception as e:
        LogError("login - 3 - " + str(e))


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
            driver.refresh()
            sleep(3)
            send_keys_wait(driver.find_element(By.ID, "sb_form_q"), mot)
            driver.find_element(By.ID, "sb_form_q").send_keys(Keys.ENTER)

        progressBar(i, override, name="PC")
        sleep(uniform(5, 20))

        try:
            driver.find_element(By.ID, "sb_form_q").clear()
        except Exception as e:
            printf(e)
            try:
                driver.refresh()
                driver.find_element(By.ID, "sb_form_q").clear()
            except Exception as e:
                LogError(f"BingPcSearch - clear la barre de recherche - {e}")

    print("\n\n")


def BingMobileSearch(override=randint(22, 25)):
    MobileDriver = (
        "si il y a ca dans les logs, c'est que Mobiledriver n'a pas demarrer "
    )
    try:
        try:
            MobileDriver = FirefoxDriver(mobile=True)
        except Exception as e:
            sleep(30)
            LogError("BingMobileSearch - 1 - echec de la creation du driver mobile")
            MobileDriver = FirefoxDriver(mobile=True)

        echec = 0

        def Mlogin(echec):

            try:
                MobileDriver.get(
                    "https://www.bing.com/search?q=test+speed&qs=LS&pq=test+s&sk=PRES1&sc=8-6&cvid=19&FORM=QBRE&sp=1"
                )
                CustomSleep(uniform(3, 5))
                printf("debut du login", Mobdriver=MobileDriver)
                MRGPD()
                MobileDriver.find_element(By.ID, "mHamburger").click()
                CustomSleep(uniform(1, 2))
                printf("login - 1", Mobdriver=MobileDriver)
                MobileDriver.find_element(By.ID, "hb_s").click()
                CustomSleep(uniform(1, 2))
                printf("login - 2", Mobdriver=MobileDriver)
                mail = MobileDriver.find_element(By.ID, "i0116")
                send_keys_wait(mail, _mail)
                printf("login - 3", Mobdriver=MobileDriver)
                mail.send_keys(Keys.ENTER)
                CustomSleep(uniform(1, 2))
                printf("login - 4", Mobdriver=MobileDriver)
                pwd = MobileDriver.find_element(By.ID, "i0118")
                printf("login - 5", Mobdriver=MobileDriver)
                send_keys_wait(pwd, _password)
                printf("login - 6", Mobdriver=MobileDriver)
                pwd.send_keys(Keys.ENTER)
                CustomSleep(uniform(1, 2))
                printf("fin du login", Mobdriver=MobileDriver)

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
                        f"login impossible 3 fois de suite. {e}", Mobdriver=MobileDriver
                    )
                    MobileDriver.quit()
                    return True

        def MRGPD():
            try:
                MobileDriver.find_element(By.ID, "bnp_btn_accept").click()
            except Exception as e:
                printf(f"MRGPD , pas grave, {e}")
            try:
                MobileDriver.find_element(By.ID, "bnp_hfly_cta2").click()
            except Exception as e:
                printf(f"MRGPD , pas grave, {e}")
            try:
                MobileDriver.find_element(By.ID, "dismissNotification").click()
            except Exception as e:
                printf(f"MRGPD , pas grave, {e}")

        def Alerte():
            try:
                alert = MobileDriver.switch_to.alert
                alert.dismiss()
            except exceptions.NoAlertPresentException as e:
                pass
            except Exception as e:
                LogError(
                    f"error sur une alerte dans le driver mobile. {e}",
                    Mobdriver=MobileDriver,
                )

        if not Mlogin(echec):

            CustomSleep(uniform(1, 2))
            MRGPD()
            CustomSleep(uniform(1, 1.5))
            send_keys_wait(
                MobileDriver.find_element(By.ID, "sb_form_q"),
                Keys.BACKSPACE
                + Keys.BACKSPACE
                + Keys.BACKSPACE
                + Keys.BACKSPACE
                + Keys.BACKSPACE
                + Keys.BACKSPACE,
            )

            for i in range(override):  # 20

                mot = choice(Liste_de_mot)
                send_keys_wait(MobileDriver.find_element(By.ID, "sb_form_q"), mot)
                MobileDriver.find_element(By.ID, "sb_form_q").send_keys(Keys.ENTER)
                progressBar(i, override, name="Mobile")
                printf(MobileDriver.current_url, Mobdriver=MobileDriver)
                sleep(uniform(5, 20))

                Alerte()  # verifie si il y a des alertes (demande de positions ....)

                for i in range(len(mot)):
                    MobileDriver.find_element(By.ID, "sb_form_q").clear()

            MobileDriver.quit()

    except Exception as e:
        LogError("BingMobileSearch" + str(e), Mobdriver=MobileDriver)
        try:
            MobileDriver.quit()
        except Exception as e:
            LogError(f"can't close mobile driveer . {e}")


def TryPlay(nom="inconnu"):
    RGPD()
    printf("TryPlay en cours")

    def play(number, override=None):
        if number == 8 or number == 9:
            try:
                printf(f"\033[96m Quiz 8 détécté sur la page {nom} \033[0m")
                PlayQuiz8()
                printf(f"\033[92m Quiz 8 reussit sur {nom} \033[0m")
            except Exception as e:
                printf(f"echec de PlayQuiz 8. Aborted {e} \033[0m")

        elif number == 5 or number == 4:
            try:
                printf(f"\033[96m Quiz 4 détécté sur la page {nom} \033[0m")
                PlayQuiz4()
                print(f"\033[92m Quiz 4 reussit sur {nom} \033[0m")
            except Exception as e:
                printf(f"echec de PlayQuiz 4. Aborted {e} \033[0m")

        elif number == 3 or number == 2:
            try:
                printf(f"\033[96m Quiz 2 détécté sur la page {nom}\033[0m")
                PlayQuiz2()
                print(f"\033[92m Quiz 2 reussit sur la page {nom}\033[0m")
            except Exception as e:
                printf(f"echec de PlayQuiz 2. Aborted {e}")
        else:
            LogError(
                "probleme dans la carte : il y a un bouton play et aucun quiz detecté"
            )

    try:
        driver.find_element(By.ID, "rqStartQuiz").click()  # start the quiz
        number = driver.page_source.count("rqAnswerOption")
        play(number)

    except Exception as e:
        # printf(e) normal error here
        if "bt_PollRadio" in driver.page_source:
            try:
                print("Poll détected", end="\r")
                RGPD()
                PlayPoll()
                print("Poll reussit  ")
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
                printf(f"recovery détécté. quiz : {number}, restant : {restant +1}")
                play(number, override=restant + 1)
            except Exception as e:
                printf("TryPlay - 2 - " + e)

        elif search("([0-9]) de ([0-9]) finalisée", driver.page_source):
            print("fidélité")
            RGPD()
            Fidelite()

        else:
            print(f"rien a faire sur la page {nom}")
            RGPD()
            CustomSleep(uniform(3, 5))


def LogPoint(account="unknown"):  # log des points sur discord
    def get_points():
        driver.get("https://www.bing.com/rewardsapp/flyout")
        if not IsLinux:
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
            CustomSleep(uniform(10, 20))
            try:
                point = search('availablePoints":([\d]+)', driver.page_source)[1]
            except Exception as e:
                LogError(f"LogPoint - 2 - {e}")
                point = -1
        return(point)

    points = get_points()
    CustomSleep(uniform(3, 20))

    account = account.split("@")[0]

    if discord_enabled:

        if embeds:
            embed = discord.Embed(
                title=f"{account} actuellement à {str(points)} points", colour=Colour.green()
            )
            embed.set_footer(text=account)
            webhookSuccess.send(embed=embed)
        else:
            webhookSuccess.send(f"{account} actuellement à {str(points)} points")

    if sql_enabled :
        add_to_database(account, points)

def Fidelite():
    try:
        while 1: #close all tabs
            try:
                Close(1)
            except:
                break

        result = get(FidelityLink) #get the url of fidelity page
        lien = result.content.decode("UTF-8")
        printf(lien)

        if (lien.split(":")[0] == "https") or (lien.split(":")[0] == "http") : 
            
            driver.get(lien)
            sleep(2)
            choix = driver.find_element(By.CSS_SELECTOR, 'div[class="pull-left spacer-48-bottom punchcard-row"]')  # pull-left spacer-48-bottom punchcard-row
            nb = search("([0-9]) of ([0-9]) completed", driver.page_source)
            if not nb:
                nb = search("([0-9]) de ([0-9]) finalisé", driver.page_source)
            for i in range(int(nb[2]) - int(nb[1])):
                driver.refresh()
                CustomSleep(2)
                choix = driver.find_element(By.CLASS_NAME, "spacer-48-bottom")
                ButtonText = search('<span class="pull-left margin-right-15">([^<^>]+)</span>',choix.get_attribute("innerHTML"))[1]
                bouton = driver.find_element(By.XPATH, f'//span[text()="{ButtonText}"]')
                bouton.click()
                CustomSleep(uniform(3, 5))
                driver.switch_to.window(driver.window_handles[1])
                TryPlay(driver.title)
                driver.get(lien)
                CustomSleep(uniform(3, 5))
                try:
                    Close(driver.window_handles[1])
                except Exception as e:
                    printf(e)

            printf("on a reussit la partie fidélité")
        else :
            printf("lien invalide")
    except Exception as e:
        LogError("Fidélité" + str(e))


def DailyRoutine():
    try:
        BingMobileSearch()
    except Exception as e:
        LogError(f"DalyRoutine - BingMobileSearch - {e}")
    CustomSleep(uniform(3, 20))

    MainWindows = login()
    try:
        AllCard()
    except Exception as e:
        LogError(
            f"DalyRoutine - AllCard - \n {e}"
        )

    try:
        BingPcSearch()
    except Exception as e:
        LogError(f"DalyRoutine - BingPcSearch - \n {e}")
    CustomSleep(uniform(3, 20))


    try:
        Fidelite()
    except:
        pass

    try:
        LogPoint(_mail)
    except Exception as e:
        LogError(f"DalyRoutine - LogPoint - \n{e}")


def close():
    driver.quit()
    quit()


def dev():
    printf("il n'y a pas de fonction en cours de dev")


def CustomStart(Credentials):
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
        driver.implicitly_wait(7)

        login()
        if "tout" in Actions:
            DailyRoutine()

        if "daily" in Actions:
            try:
                AllCard()
            except Exception as e:
                LogError(f"AllCards - {e} -- override")

        if "pc" in Actions:
            try:
                BingPcSearch()
            except Exception as e:
                LogError(f"il y a eu une erreur dans BingPcSearch, {e} -- override")

        if "mobile" in Actions:
            try:
                BingMobileSearch()
            except Exception as e:
                LogError(f"BingMobileSearch - {e} -- override")

        if "Fidelite" in Actions:
            try :
                Fidelite()
            except Exception as e :
                LogError(f"Fidelite - {e} -- override")

        if "dev" in Actions:
            try:
                dev()
            except Exception as e:
                printf(e)
                break

        try:
            LogPoint(_mail)
        except Exception as e:
            print("CustomStart " + str(e))
        driver.close()


with open(LogPath) as f:
    reader = reader(f)
    Credentials = list(reader)

shuffle(Credentials)

if override:
    CustomStart(Credentials)
else:
    for i in Credentials:
        system("pkill -9 firefox")
        _mail = i[0]
        _password = i[1]

        print("\n\n")
        print(_mail)
        CustomSleep(1)
        printf("debut du driver")
        driver = FirefoxDriver()
        printf("driver demarré")
        driver.implicitly_wait(7)

        try:
            DailyRoutine()
            driver.quit()
            attente = uniform(1200, 3600)
            print(f"finis. attente de {round(attente/60)}min")
            CustomSleep(attente)

        except KeyboardInterrupt:
            print("canceled")
            close()

if IsLinux:
    system("pkill -9 firefox")
