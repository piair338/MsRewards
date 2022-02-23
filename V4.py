#!/usr/bin/python3
import asyncio
import configparser
import os
from csv import reader
from os import path, sys, system
from queue import Full
from random import choice, randint, shuffle, uniform
from re import findall, search
from sys import platform
from time import sleep

import discord
from discord import (  # Importing discord.Webhook and discord.RequestsWebhookAdapter
    Colour, Embed, RequestsWebhookAdapter, Webhook)
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("-o" , "--override", help="override", dest="override", action = "store_true")
parser.add_argument("-l", "--log",dest="log",help="enable logging in terminal", action ="store_true")
parser.add_argument("-fl", "--fulllog",dest="fulllog",help="enable full logging in terminal", action ="store_true")

args = parser.parse_args()
override = args.override
Log = args.log
FullLog = args.fulllog

IsLinux = platform == "linux"


if not IsLinux :
    system("") #enable colors in cmd

config_path = "/home/pi/MsReward/config"
config = configparser.ConfigParser()
config.read(config_path)

MotPath = config["DEFAULT"]["motpath"]
LogPath = config["DEFAULT"]["logpath"]
SuccessLink = config["DEFAULT"]["successlink"]
ErrorLink = config["DEFAULT"]["errorlink"]

embeds = config["DEFAULT"]["embeds"] == "True"
Headless = config["DEFAULT"]["headless"] == "True"


g =  open(MotPath, "r" , encoding="utf-8")
Liste_de_mot=(list(g.readline().split(',')))
g.close()

webhookSuccess = Webhook.from_url(SuccessLink, adapter=RequestsWebhookAdapter())
webhookFailure = Webhook.from_url(ErrorLink, adapter=RequestsWebhookAdapter())

def resource_path(relative_path): #permet de recuperer l'emplacement de chaque fichier, sur linux et windows
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = path.dirname(__file__)
    return path.join(base_path, relative_path)


def FirefoxMobile(Headless = Headless):
    MOBILE_USER_AGENT = ('Mozilla/5.0 (iPhone; CPU iPhone OS 14_8_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1')
    options = Options()
    options.set_preference("browser.link.open_newwindow", 3)
    if Headless :
        options.add_argument("-headless") 
    options.set_preference("general.useragent.override", MOBILE_USER_AGENT)
    return(webdriver.Firefox(options=options))


def FirefoxPC(Headless = Headless):
    PC_USER_AGENT = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134')

    options = Options()
    options.set_preference("browser.link.open_newwindow", 3)
    
    if Headless :
        options.add_argument("-headless")

    options.set_preference("general.useragent.override", PC_USER_AGENT)
    return(webdriver.Firefox(options=options))


def printf(txt, end=""):
    if Log :
        print(txt, end=end)
        CustomSleep(5)
    if FullLog :
        LogError(txt)


def CustomSleep(temps):
    if Log or not IsLinux :
        c = False
        points = [" .   ", "  .  ", "   . ", "    .", "    .", "   . ", "  .  "," .   "]
        for i in range (int(temps)):
            c = True
            for i in range (8):
                
                sleep(0.125)
                print(points[i], end='\r')

        if c:
            print('.   ', end="\r")
        sleep(temps - int(temps))
        print("\n")
    else : 
        sleep(temps)


def ListTabs(Mdriver = None ):
    tabs = []
    if Mdriver :
        ldriver = Mdriver
    else :
        ldriver = driver
    for i in ldriver.window_handles :
        ldriver.switch_to.window(i)
        tabs.append(ldriver.current_url)
    return(tabs)


def LogError(message,log = FullLog, Mobdriver = None):
    if Mobdriver :
        gdriver = Mobdriver
    else :
        gdriver = driver
    if not log :
        print(f'\033[93m Erreur : {str(message)}  \033[0m')
    if IsLinux :
        with open('page.html', 'w') as f:
            f.write(gdriver.page_source)

        gdriver.save_screenshot("screenshot.png")
        if not log : 
            embed = discord.Embed(
                title="An Error has occured",
                description=str(message),
                url = ListTabs(Mdriver=Mobdriver)[0],
                colour = Colour.red()
            )
        else : 
            embed = discord.Embed(
                title="Full log is enabled",
                description=str(message),
                url = ListTabs(Mdriver=Mobdriver)[0],
                colour = Colour.blue()
            )

        file = discord.File("screenshot.png")
        embed.set_image(url="attachment://screenshot.png")
        embed.set_footer(text=_mail)
        webhookFailure.send(embed=embed, file=file)
        webhookFailure.send(file=discord.File('page.html'))


def progressBar(current, total=30, barLength = 20, name ="Progress"):
    percent = float(current+1) * 100 / total
    arrow   = '-' * int(percent/100 * barLength - 1) + '>'
    spaces  = ' ' * (barLength - len(arrow))
    print(name + ': [%s%s] %d %%' % (arrow, spaces, percent), end='\r')


def Close(fenetre, SwitchTo = 0):
    driver.switch_to.window(fenetre)
    driver.close()
    driver.switch_to.window(driver.window_handles[SwitchTo])


def RGPD():
    try :
        driver.find_element(By.ID, 'bnp_btn_accept').click()
    except :
        pass
    
    try :
        driver.find_element(By.ID, 'bnp_hfly_cta2').click()
    except :
        pass


def PlayQuiz2(override):
    if not override :
        override = 10
    for j in range (override):
        try :
            CustomSleep(uniform(3,5))
            txt = driver.page_source
            secret = search('IG:\"([^\"]+)\"', txt)[1] #variable dans la page, pour calculer le offset
            reponse1 = search("data-option=\"([^\"]+)\"", txt)[1]
            offset = int(secret[-2:],16) # la conversion ec decimal des deux dernier caracteres de IG
            reponse = search("correctAnswer\":\"([0-9]+)", txt)[1]
            somme = 0 

            for i in reponse1 :
                somme += ord(i)

            if somme + offset == int(reponse) :
                elem = driver.find_element(By.ID, 'rqAnswerOption0')
                elem.click()
                progressBar(j,10, name="quiz 2")
                
            else : 
                elem = driver.find_element(By.ID, 'rqAnswerOption1')
                elem.click()
                progressBar(j,10, name="quiz 2")

        except exceptions.ElementNotInteractableException as e :
            driver.execute_script("arguments[0].click();", elem) 

        except Exception as e:
            LogError("PlayQuiz2" + str(e))
            break


def PlayQuiz8(override = 3):
    printf(f"override : {override}")
    try : 
        c = 0
        for i in range(override):
            sleep(uniform(3,5))
            ListeOfGood =[]
            for i in range(1,9):
                try : 
                    Card= driver.find_element(By.ID, f'rqAnswerOption{i-1}')
                    if 'iscorrectoption="True" 'in Card.get_attribute('outerHTML') :
                        ListeOfGood.append(f'rqAnswerOption{i-1}') #premier div = 3 ?
                except Exception as e :
                    LogError("playquiz8 - 1 - " + e)
            shuffle(ListeOfGood)

            for i in ListeOfGood :
                sleep(uniform(3,5))
                c+=1
                progressBar(c,16, name="Quiz 8 ")
                try : 
                    elem = driver.find_element(By.ID, i)
                    elem.click()
                except exceptions.ElementNotInteractableException as e:
                    try : 
                        driver.execute_script("arguments[0].click();", elem)   
                    except Exception as e :
                        LogError("playquizz8 - 2 - " + e)
                except Exception as e :
                    if override :
                        printf("playquiz8 - 3 -" +e)
                    else :
                        LogError("playquizz8 - 3 - " + e)
          
    except Exception as e :
        LogError("PlayQuiz8 - 4 - " + str(e) + str(ListeOfGood))        
    

def PlayQuiz4(override = None):
    if not override :
        try : #permet de gerer les truc de fidélité, qui sont plus long
            override = int(findall("rqQuestionState([\d]{1,2})\"", driver.page_source)[-1])
        except :
            override = 3    
    
    try :
        for i in range(override):
            CustomSleep(uniform(3,5))
            txt = driver.page_source
            
            reponse = search("correctAnswer\":\"([^\"]+)", txt)[1] #je suis pas sur qu'il y ait un espace
            reponse = reponse.replace('\\u0027',"'") #il faut cancel l'unicode avec un double \ (on replacer les caracteres en unicode en caracteres utf-8) 
            printf(f"validation de la reponse                                     " , end="\r")
            printf(f"validation de la reponse {i+1}/{override} {reponse}" , end="\r")
            try : 
                elem = driver.find_element(By.CSS_SELECTOR, f'[data-option="{reponse}"]')
                elem.click()
            except exceptions.ElementNotInteractableException:
                driver.execute_script("arguments[0].click();", elem)

    except Exception as e :
        LogError("PlayQuiz4" + str(e))
        raise ValueError(e)


def PlayPoll():
    try :
        try : 
            elem = driver.find_element(By.ID, f'btoption{choice([0,1])}')
            elem.click()
        except exceptions.ElementNotInteractableException as e:
            driver.execute_script("arguments[0].click();", elem)
        CustomSleep(uniform(2,2.5))
    except Exception as e :
        LogError("PlayPoll" +  str(e))
        raise ValueError(e)


def AllCard(): #fonction qui clique sur les cartes

    def reset(Partie2=False): #retourne sur la page de depart apres avoir finis
        if len(driver.window_handles) == 1 :
            driver.get('https://www.bing.com/rewardsapp/flyout')
            if Partie2 :
                driver.find_element(By.XPATH, '/html/body/div/div/div[3]/div[2]/div[2]/div[2]/div[1]').click()
        else : 
            driver.switch_to.window(driver.window_handles[1])
            printf(f"on ferme la fenetre {driver.current_url}")
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            reset(Partie2)

    def dailyCards():
        try :
            for i in range(3):
                sleep(1)
                try :
                    driver.find_element(By.XPATH, f'/html/body/div/div/div[3]/div[2]/div[1]/div[2]/div/div[{i+1}]/a/div/div[2]').click()
                    sleep(1)
                    titre = driver.title
                    TryPlay(titre)
                    sleep(1)
                    reset()
                    print(f"DailyCard {titre} ok ")
                except Exception as e :
                    printf(f"Allcard card {i+1} error")
        except Exception as e :
            LogError(f'Dailycards {e}')

    dailyCards()

    try :    
        try : 
            driver.find_element(By.XPATH, '/html/body/div/div/div[3]/div[2]/div[2]/div[2]/div[1]').click() #declenche la premiere partie ?
        except :
            reset()
            try :
                driver.find_element(By.XPATH, '/html/body/div/div/div[3]/div[2]/div[2]/div[2]/div[1]').click()#declenche la deuxieme partie ?
            except :
                pass
        
        for i in range(20):
            printf("debut de l'une des cartes")
            driver.find_element(By.XPATH, '/html/body/div/div/div[3]/div[2]/div[2]/div[3]/div/div[1]/a/div/div[2]').click()
            printf("carte cliqué")
            driver.switch_to.window(driver.window_handles[len(driver.window_handles) - 1])
            sleep(1) 
            titre = driver.title
            print(f"carte {titre} en cours")
            TryPlay(titre)
            reset(True)
            sleep(1)
            try :
                link = findall('href="([^<]+)" title=""',driver.page_source)[3] #verifie si on a toujours des cartes 
            except :
                break
    except Exception as e:
        LogError(f'2eme partie de AllCard (weekly card)\n {e}')


def send_keys_wait(element,keys):
    for i in keys :
        element.send_keys(i)
        sleep(uniform(0, 0.5))


def login() :
    try :
        driver.get('https://www.bing.com/rewardsapp/flyout')
        try :
            driver.find_element(By.CSS_SELECTOR, f'[title="Rejoindre"]').click() #depend of the language of the page
        except :
            driver.find_element(By.CSS_SELECTOR, f'[title="Join now"]').click() #depend of the language of the page
        
        mail = driver.find_element(By.ID, 'i0116')
        send_keys_wait(mail, _mail)
        mail.send_keys(Keys.ENTER)
        
        try :
            driver.find_element(By.ID, 'idChkBx_PWD_KMSI0Pwd').click()
        except :
            try :
                driver.find_element(By.CSS_SELECTOR, '''[data-bind="text: str['CT_PWD_STR_KeepMeSignedInCB_Text']"]''').click()
            except :
                pass
        CustomSleep(3)
        pwd = driver.find_element(By.ID, 'i0118')
        send_keys_wait(pwd, _password)
        pwd.send_keys(Keys.ENTER)
        CustomSleep(5)
        try : 
            driver.find_element(By.ID, 'KmsiCheckboxField').click()
        except Exception as e  :
            printf(f"login - 1 - erreur validation bouton KmsiCheckboxField. pas forcement grave {e}") 
        CustomSleep(5)
        try : 
            driver.find_element(By.ID, 'idSIButton9').click()
        except Exception as e  :
            printf(f"login - 2 - erreur validation bouton idSIButton9. pas forcement grave {e}") 

        print("login completed")
        sleep(3)
        RGPD()
        driver.get('https://www.bing.com/rewardsapp/flyout')
        
        MainWindows = driver.current_window_handle
        return(MainWindows)

    except Exception as e:
        LogError("login - 3 - " + str(e))
        

def BingPcSearch(override = randint(35,40)):
    driver.get(f'https://www.bing.com/search?q=test')#{choice(Liste_de_mot)}')
    CustomSleep(uniform(1,2))
    RGPD()
    send_keys_wait( driver.find_element(By.ID, 'sb_form_q'),Keys.BACKSPACE+Keys.BACKSPACE+Keys.BACKSPACE+Keys.BACKSPACE+Keys.BACKSPACE+Keys.BACKSPACE)
    
    
    for i in range(override):
        mot = choice(Liste_de_mot)
        try :
            send_keys_wait( driver.find_element(By.ID, 'sb_form_q'),mot)
            driver.find_element(By.ID, 'sb_form_q').send_keys(Keys.ENTER)
        except :
            sleep(10)
            driver.refresh()
            sleep(10)
            send_keys_wait( driver.find_element(By.ID, 'sb_form_q'),mot)
            driver.find_element(By.ID, 'sb_form_q').send_keys(Keys.ENTER)

        progressBar(i,override, name="PC")
        sleep(uniform(5,20)) 

        try :
            driver.find_element(By.ID, 'sb_form_q').clear()
        except :
            try :
                driver.refresh()
                driver.find_element(By.ID, 'sb_form_q').clear()
            except Exception as e:
                LogError(f"BingPcSearch - clear la barre de recherche - {e}")

    print('\n\n')


def BingMobileSearch(override = randint(22,25)):
    MobileDriver = "si il y a ca dans les logs, c'est que Mobiledriver n'a pas demarrer "
    try :
        try :
            MobileDriver = FirefoxMobile()
        except Exception as e :
            sleep(30)
            LogError('BingMobileSearch - 1 - echec de la creation du driver mobile')
            MobileDriver = FirefoxMobile()

        echec = 0
        def Mlogin(echec):
            
            try : 
                MobileDriver.get(f'https://www.bing.com/search?q=test')#{choice([Liste_de_mot])}')
                CustomSleep(uniform(3,5))

                MobileDriver.find_element(By.ID, 'mHamburger').click()
                CustomSleep(uniform(1,2))
                MobileDriver.find_element(By.ID, 'hb_s').click()
                CustomSleep(uniform(1,2))

                mail = MobileDriver.find_element(By.ID, 'i0116')
                send_keys_wait(mail, _mail)
                mail.send_keys( Keys.ENTER)
                CustomSleep(uniform(1,2))
                pwd = MobileDriver.find_element(By.ID, 'i0118')
                send_keys_wait(pwd, _password)
                pwd.send_keys( Keys.ENTER)
            except Exception as e :
                echec += 1
                if echec <= 3 :
                    print(f'echec du login sur la version mobile. on reesaye ({echec}/3), {e}')
                    CustomSleep(uniform(5,10))
                    Mlogin(echec)
                else :
                    LogError('recherche sur mobile impossible. On skip \n\n\n\n\n\n\n\n', Mobdriver=MobileDriver)
                    LogError(f"login impossible 3 fois de suite. {e}",Mobdriver=MobileDriver)
                    MobileDriver.quit()
                    return(True)
                    
        
        def MRGPD():
            try :
                MobileDriver.find_element(By.ID, 'bnp_btn_accept').click()
            except :
                pass
            try :
                MobileDriver.find_element(By.ID, 'bnp_hfly_cta2').click()
            except :
                pass        
        
        def Alerte():
            try:
                alert = MobileDriver.switch_to.alert
                alert.dismiss()
            except exceptions.NoAlertPresentException as e :
                pass
            except Exception as e:
                LogError(f"error sur une alerte dans le driver mobile. {e}",Mobdriver=MobileDriver)

        if not Mlogin(echec) :        

            CustomSleep(uniform(1,2))
            MRGPD()
            CustomSleep(uniform(1,1.5))
            send_keys_wait( MobileDriver.find_element(By.ID, 'sb_form_q'),Keys.BACKSPACE+Keys.BACKSPACE+Keys.BACKSPACE+Keys.BACKSPACE+Keys.BACKSPACE+Keys.BACKSPACE)
            
            for i in range(override): #20

                mot = choice(Liste_de_mot)
                send_keys_wait( MobileDriver.find_element(By.ID, 'sb_form_q'),mot)
                MobileDriver.find_element(By.ID, 'sb_form_q').send_keys(Keys.ENTER)
                progressBar(i,override,name="Mobile")
                printf(MobileDriver.current_url)
                sleep(uniform(5,20)) 

                Alerte() # verifie si il y a des alertes (demande de positions ....)
                
                for i in range (len(mot)):
                    MobileDriver.find_element(By.ID, 'sb_form_q').clear()


            MobileDriver.quit()
            

    except Exception as e:
        LogError("BingMobileSearch" + str(e),Mobdriver=MobileDriver)
        try :
            MobileDriver.quit()
        except Exception as e: 
            LogError(f"can't close mobile driveer . {e}")


def TryPlay(nom ="inconnu"):
    RGPD()
    def play(number, override = None) : 
        if number == 8 or number == 9 :
            try :
                printf(f'Quiz 8 détécté sur la page {nom}')
                PlayQuiz8(override)
                printf(f'Quiz 8 reussit sur {nom}')
            except Exception as e :
                printf(f'echec de PlayQuiz 8. Aborted {e}')

        elif number == 5 or number == 4 :
            try :
                printf(f'Quiz 4 détécté sur la page {nom}')
                PlayQuiz4(override)
                print(f'Quiz 4 reussit sur {nom}')
            except Exception as e :
                printf(f'echec de PlayQuiz 4. Aborted {e}')

        elif number == 3 or number == 2 :
            try :
                printf(f'Quiz 2 détécté sur la page {nom}')
                PlayQuiz2(override)
                print(f'Quiz 2 reussit sur la page {nom}')
            except Exception as e :
                printf(f'echec de PlayQuiz 2. Aborted {e}')
        else :
                LogError('probleme dans la carte : il y a un bouton play et aucun quiz detecté')
    try :
        driver.find_element(By.ID, 'rqStartQuiz').click() #start the quiz
        number = driver.page_source.count('rqAnswerOption')
        play(number)
            
    except :
        
        if "bt_PollRadio" in driver.page_source :
            try :
                print('Poll détected',  end ="\r")
                RGPD()
                PlayPoll()
                print('Poll reussit  ')
            except Exception as e :
                printf(f'TryPlay - 1 - Poll aborted {e}')

        elif "rqQuestionState" in driver.page_source :
            try : 
                number = driver.page_source.count('rqAnswerOption')
                restant = len(findall("\"rqQuestionState.?.\" class=", driver.page_source)) - len(findall("\"rqQuestionState.?.\" class=\"filledCircle\"", driver.page_source))
                printf(f"recovery détécté. quiz : {number}, restant : {restant +1}")
                play(number, override=restant + 1 )
            except Exception as e :
                printf("TryPlay - 2 - " + e)

        elif search("([0-9]) de ([0-9]) finalisée",driver.page_source) :
            print('fidélité')
            RGPD()
            Fidelité()
                
        else :
            print(f'rien a faire sur la page {nom}')
            RGPD()
            CustomSleep(uniform(3,5))


def LogPoint(account="unknown"): #log des points sur discord
    driver.get('https://www.bing.com/rewardsapp/flyout')
    if not IsLinux :
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    else :
        asyncio.set_event_loop(asyncio.new_event_loop())

    regex1 = "<a href=\"https://rewards\.bing\.com/\" title=\"((.{1,3}),(.{1,3})) points\" target=\"_blank\""
    try : 
        point = search(regex1, driver.page_source)[1].replace(',', '')
        
    except Exception as e :
        elem = driver.find_element(By.CSS_SELECTOR, '[title="Microsoft Rewards"]')
        elem.click()
        CustomSleep(5)
        driver.switch_to.window(driver.window_handles[len(driver.window_handles) - 1])
        CustomSleep(uniform(10,20))
        try :
            point = search("availablePoints\":([\d]+)",driver.page_source)[1]
        except Exception as e :
            LogError(f"LogPoint - 2 - {e}")
            point = "erreur"

    CustomSleep(uniform(3,20))
    
    account = account.split('@')[0]

    if embeds:
        embed = discord.Embed(
                title=f"{account} actuellement à {str(point)} points",
                colour = Colour.green()
        )
        embed.set_footer(text=account)
        webhookSuccess.send(embed=embed)
    else :
        webhookSuccess.send(f'{account} actuellement à {str(point)} points')


def Fidelité():
    try :
        driver.switch_to.window(driver.window_handles[1])
        choix = driver.find_element(By.CLASS_NAME,'spacer-48-bottom')
        nb = search("([0-9]) de ([0-9]) finalisée",driver.page_source)
        for i in range(int(nb[2])-int(nb[1])):
            choix = driver.find_element(By.CLASS_NAME,'spacer-48-bottom')
            ButtonText = search('<span class=\"pull-left margin-right-15\">([^<^>]+)</span>',choix.get_attribute("innerHTML"))[1]
            bouton = driver.find_element(By.XPATH, f'//span[text()="{ButtonText}"]')
            bouton.click()
            CustomSleep(uniform(3,5))
            driver.switch_to.window(driver.window_handles[len(driver.window_handles) - 1])
            TryPlay(driver.title)
            CustomSleep(uniform(3,5))
            Close(driver.window_handles[2],SwitchTo=1)
            driver.refresh()
            CustomSleep(uniform(3,5))

        Close(driver.window_handles[1])
        printf('on a passer la partie fidélité')
    except Exception as e :
        LogError("Fidélité" + str(e))


def CheckPoint():# a fix, ne marche pas dans  80% des cas pas appelé aujourd'hui
    driver.get("https://rewards.microsoft.com/pointsbreakdown")
    txt = driver.page_source
    pc = search('([0-9][0-9]|[0-9])</b> / 90',txt)
    mobile = search('([0-9][0-9]|[0-9])</b> / 60',txt)
    if mobile :
        if mobile[1] != 60:
            BingMobileSearch(22-(int(mobile[1])/3))      
    if pc :
        if pc[1] != 90:
            BingPcSearch(32-(int(pc[1])/3))
             

def DailyRoutine():
    
    MainWindows = login()
    
    try :
        AllCard()
    except Exception as e :
        LogError(f'pas normal sauf si relancer a la main, juste pour les recherches bing (DalyRoutine -> AllCard) \n {e}')

    try : 
        BingPcSearch()
    except Exception as e :
        LogError(f"il y a eu une erreur dans BingPcSearch, {e}")
    CustomSleep(uniform(3,20)) 
    

    try : 
        BingMobileSearch()
    except Exception as e:
        LogError(f'BingMobileSearch - {e}')
    print('\n')
    CustomSleep(uniform(3,20))
    
    try :
        LogPoint(_mail)
    except Exception as e:
        LogError(f'LogPoint : {e}')


def close():
    driver.quit()
    quit()


def CustomStart(Credentials):
    global driver
    global _mail
    global _password
    driver="chelou"
    ids = [x[0] for x in Credentials]
    actions=["tout", "daily", "pc", "mobile", "LogPoint"]

    for i in range(len(ids)) :
        print(f"{i} : {ids[i]}")

    choice1 = int(input(""))
    assert choice1 < len(ids)

    for i in range(len(actions)) :
        print(f"{i} : {actions[i]}")

    choice2 = int(input(""))
    assert choice2 < len(actions)

    _mail =Credentials[choice1][0]
    _password = Credentials[choice1][1]

    if choice2 == 0 : 
        driver = FirefoxPC()
        driver.implicitly_wait(15)
        login()
        DailyRoutine()
        driver.close()
    elif choice2 == 1 :
        try :
            driver = FirefoxPC()
            driver.implicitly_wait(15)
            login()
            AllCard()
            driver.close()
        except Exception as e :
            LogError(f'pas normal sauf si relancer a la main, juste pour les recherches bing (DalyRoutine -> AllCard) \n {str(e)}. -- override')
    elif choice2 == 2 :
        try : 
            driver = FirefoxPC()
            driver.implicitly_wait(15)
            login()
            BingPcSearch()
            driver.close()
        except Exception as e :
            LogError(f"il y a eu une erreur dans BingPcSearch, {e} -- override")
    elif choice2 == 3 :
        try : 
            BingMobileSearch()
        except Exception as e:
            LogError(f'BingMobileSearch - {e} -- override')
    print("done!")
    try :
        driver = FirefoxPC()
        driver.implicitly_wait(15)
        login()
        LogPoint(_mail)
        driver.close()
    except Exception as e :
        print("CustomStart " + str(e))

with open(LogPath) as f:
    reader = reader(f)
    data = list(reader)

Credentials = data

CustomSleep(2)

shuffle(Credentials)

if override :
    CustomStart(Credentials)
else : 
    for i in Credentials :

        _mail =i[0]
        _password = i[1]

        print('\n\n')
        print(_mail)
        CustomSleep(1)
    
        driver = FirefoxPC()
        driver.implicitly_wait(15)

        try :
            DailyRoutine()
            driver.quit()
            timer = uniform(1200,3600)
            print(f"finis. attente de {round(timer/60)}min")
            CustomSleep(timer)

        except KeyboardInterrupt :
            print('canceled')
            close()

if IsLinux :
    system("pkill -9 firefox")