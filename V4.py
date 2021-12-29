#!/usr/bin/python3
import os
from time import sleep
from random import uniform, choice, randint,shuffle
from re import search,findall
from os import path, sys, system
import discord
import asyncio
from sys import platform
from csv import reader 

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions

main = True
Headless = True
Log = False

def printf(txt):
    if not Log :
        print(txt)
    else :
        CustomSleep(5)
        LogError(txt)


IsLinux = platform == "linux"
print("Linux : "+ str(IsLinux))


def resource_path(relative_path): #permet de recuperer l'emplacement de chaque fichier, su linux et windows
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = path.dirname(__file__)
    return path.join(base_path, relative_path)


def FirefoxMobile(Headless = Headless):
    MOBILE_USER_AGENT = ('Mozilla/5.0 (iPhone; CPU iPhone OS 14_1_2 like Mac OS X)'
                    'AppleWebKit/603.1.30 (KHTML, like Gecko)'
                    'Version/14.1 Mobile/14E304 Safari/602.1')
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


if IsLinux :
    MotPath = "/home/pi/MsReward/liste.txt"
    LogPath= "/home/pi/MsReward/login.csv"
    TokenPath = "/home/pi/MsReward/token.txt"
else :
    MotPath = resource_path('D:\Documents\Dev\MsReward\liste/liste.txt')
    LogPath = resource_path('D:\Documents\Dev\MsReward\login/login.csv')
    TokenPath = resource_path('D:\Documents\Dev\MsReward/token/token.txt')
    system("")



g =  open(MotPath, "r" , encoding="utf-8")
Liste_de_mot=(list(g.readline().split(',')))
g.close()
g = open(TokenPath,"r")
Token = g.readline()
g.close


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
            print('                ', end="\r")
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


def LogError(message,log = Log, Mobdriver = None):
    if Mobdriver :
        gdriver = Mobdriver
    else :
        gdriver = driver

    if not IsLinux :
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        print(f'\033[93m Erreur : {str(message)}  \033[0m')
    else :

        with open('page.html', 'w') as f:
            f.write(gdriver.page_source)


        gdriver.save_screenshot("screenshot.png")
        asyncio.set_event_loop(asyncio.new_event_loop())

        client = discord.Client()
        @client.event
        async def on_ready():
            channel = client.get_channel(861181899987484692)
            if log :
                channel = client.get_channel(833275838837030912) #channel de log
            await channel.send("------------------------------------\n" + _mail)
            
            await channel.send(ListTabs(Mdriver=Mobdriver))
            await channel.send(str(message))
            CustomSleep(1)
            await channel.send(file=discord.File('screenshot.png'))
            await channel.send(file=discord.File('page.html'))
            await channel.send("------------------------------------")
            await client.close()


        client.run(Token)


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
    driver.implicitly_wait(3)
    try :
        driver.find_element(By.ID, 'bnp_btn_accept').click()
    except :
        pass
    
    try :
        driver.find_element(By.ID, 'bnp_hfly_cta2').click()
    except :
        pass
    driver.implicitly_wait(5)


def PlayQuiz2(override = None):
    if not override :
        override = 10

    for j in range (override):
        try : 
            CustomSleep(uniform(3,5))
            
            txt = driver.page_source
            IG = search('IG:\"([^\"]+)\"', txt)[1] #variable dans la page, pour calculer le offset
            reponse1 = search("data-option=\"([^\"]+)\"", txt)[1]
            offset = int(IG[-2:],16) # la conversion ec decimal des deux dernier caracteres de IG
            reponse = search("correctAnswer\":\"([0-9]+)", txt)[1]

            somme = 0 

            for i in reponse1 :
                somme += ord(i)

            RGPD()
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


def PlayQuiz8(override = None):
    
    if not override :
        override = 3
    print(f"override : {override}")
    try : 
        #RGPD()
        
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
                    if override :
                        LogError(e)
                    else :
                        LogError(e)
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
                        LogError(e)
                except Exception as e :
                    if override :
                        printf(e)
                    else :
                        LogError(e)
          
    except Exception as e :
        LogError("PlayQuiz8" + str(e) + str(ListeOfGood))        
    

def PlayQuiz4(override = None):
    if not override :
        try : #permet de gerer les truc de fidélité, qui sont plus long
            override = int(findall("rqQuestionState([\d]{1,2})\"", driver.page_source)[-1])
        except :
            override = 3    
    
    try :
        
        
        for i in range(override):
            #RGPD()
            CustomSleep(uniform(3,5))
            txt = driver.page_source
            
            reponse = search("correctAnswer\":\"([^\"]+)", txt)[1] #je suis pas sur qu'il y ait un espace
            reponse = reponse.replace('\\u0027',"'") #il faut cancel l'unicode avec un double \ (on replacer les caracteres en unicode en caracteres utf-8)
            
            
            print(f"validation de la reponse                                     " , end="\r")
            print(f"validation de la reponse {i+1}/{override} {reponse}" , end="\r")
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
            print(f"on ferme la fenetre {driver.current_url}")
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            reset(Partie2)

    def dailyCards():
        try :
            for i in range(3):
                sleep(1)
                driver.find_element(By.XPATH, f'/html/body/div/div/div[3]/div[2]/div[1]/div[2]/div/div[{i+1}]/a/div/div[2]').click()
                sleep(1)
                TryPlay(driver.title)
                sleep(1)
                reset()
                printf(f"carte {i} ok ")
        except Exception as e :
            LogError(f'erreur dans la premiere partie de AllCard (les daily card). cela arrive si on relance le proramme une deuxieme fois sur le meme compte \n {e}')

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
        c = 0
        while True:
            printf("debut de l'une des cartes")
            driver.find_element(By.XPATH, '/html/body/div/div/div[3]/div[2]/div[2]/div[3]/div/div[1]/a/div/div[2]').click()
            printf("carte cliqué")
            driver.switch_to.window(driver.window_handles[len(driver.window_handles) - 1])
            sleep(1)
            try : 
                titre = driver.title
            except Exception as e :
                titre = "inconnu"
                LogError(f"impossible de recuperer le titre. {e}")

            TryPlay(titre)
            reset(True)
            sleep(1)
            c += 1
            if c ==20 :
                break
            try :
                link = findall('href="([^<]+)" title=""',driver.page_source)[3] #verifie si on a toujours des cartes 
            except :
                break
    except Exception as e:
        LogError(f'2eme partie de AllCard (weekly card)\n {e}')


def send_keys_wait(element,keys):
    for i in keys :
        element.send_keys(i)
        CustomSleep(uniform(0, 0.5))


def login() :
    try :
        driver.get('https://www.bing.com/rewardsapp/flyout')

        try :

            driver.find_element(By.CSS_SELECTOR, f'[title="Rejoindre"]').click()

        except :

            driver.find_element(By.CSS_SELECTOR, f'[title="Join now"]').click()
        
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
            printf(f"erreur validation bouton KmsiCheckboxField. pas forcement grave {e}") 
        CustomSleep(5)
        try : 
            driver.find_element(By.ID, 'idSIButton9').click()
        except Exception as e  :
            printf(f"erreur validation bouton idSIButton9. pas forcement grave {e}") 

        printf("login completed")
        
        RGPD()

        driver.get('https://www.bing.com/rewardsapp/flyout')
        
        MainWindows = driver.current_window_handle
        return(MainWindows)

    except Exception as e:
        LogError(e)
        

def BingPcSearch(override = randint(30,35)):
    driver.get(f'https://www.bing.com/search?q={choice([x for x in range (999999)])}&form=QBLH&sp=-1&pq=test&sc=8-4&qs=n&sk=&cvid=1DB80744B71E40B8896F5C1AD2DE95E9')
    CustomSleep(uniform(1,2))
    RGPD()
    CustomSleep(uniform(1,1.5))
    send_keys_wait( driver.find_element(By.ID, 'sb_form_q'),Keys.BACKSPACE+Keys.BACKSPACE+Keys.BACKSPACE+Keys.BACKSPACE+Keys.BACKSPACE+Keys.BACKSPACE)
    
    
    for i in range(override):
        mot = str(Liste_de_mot[randint(0,9999)] )
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


def BingMobileSearch(override = randint(20,25)):
    try :
        MobileDriver = FirefoxMobile()
        echec = 0
        def Mlogin(echec):
            
            try : 
                MobileDriver.get(f'https://www.bing.com/search?q={choice([x for x in range (999999)])}&form=QBLH&sp=-1&pq=test&sc=8-4&qs=n&sk=&cvid=1DB80744B71E40B8896F5C1AD2DE95E9')
                CustomSleep(uniform(3,5))

                MobileDriver.find_element(By.ID, 'mHamburger').click()
                CustomSleep(uniform(1,2))
                MobileDriver.find_element(By.ID, 'hb_s').click()
                CustomSleep(uniform(1,2))

                mail = MobileDriver.find_element(By.ID, 'i0116')
                send_keys_wait(mail, _mail)
                mail.send_keys( Keys.ENTER)
                CustomSleep(uniform(1,2))
                #MobileDriver.find_element(By.ID, 'idLbl_PWD_KMSI_Cb').click()
                pwd = MobileDriver.find_element(By.ID, 'i0118')
                send_keys_wait(pwd, _password)
                pwd.send_keys( Keys.ENTER)
            except Exception as e :
                echec += 1
                if echec <= 3 :
                    printf(f'echec du login sur la version mobile. on reesaye ({echec}/3), {e}')
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

                mot = str(Liste_de_mot[randint(0,9999)] )
                send_keys_wait( MobileDriver.find_element(By.ID, 'sb_form_q'),mot)
                MobileDriver.find_element(By.ID, 'sb_form_q').send_keys(Keys.ENTER)
                progressBar(i,override,name="Mobile")

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
            LogError(f"can't close mobile driveerr . {e}")


def TryPlay(nom ="inconnu"):

    RGPD()
    def play(number, override = None) : 
        match number :
            case 9 | 8 :
                try :
                    print(f'Quiz 8 détécté sur la page {nom}')
                    RGPD()
                    PlayQuiz8(override)
                except Exception as e :
                    printf(f'echec de PlayQuiz 8. Aborted {e}')
            case 5 | 4 :
                try :
                    print(f'Quiz 4 détécté sur la page {nom}')
                    RGPD()
                    PlayQuiz4(override)
                    print('Quiz 4 reussit')
                except Exception as e :
                    printf(f'echec de PlayQuiz 4. Aborted {e}')
            case 3 | 2 : 
                try :
                    RGPD()
                    print(f'Quiz 2 détécté sur la page {nom}')
                    PlayQuiz2(override)
                except Exception as e :
                    printf(f'echec de PlayQuiz 2. Aborted {e}')
            case _ :
                LogError('probleme dans la carte : il y a un bouton play et aucun quiz')
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
                printf(f'Poll aborted {e}')

        elif "rqQuestionState" in driver.page_source :
            try : 
                number = driver.page_source.count('rqAnswerOption')
                restant = len(findall("\"rqQuestionState.?.\" class=", driver.page_source)) - len(findall("\"rqQuestionState.?.\" class=\"filledCircle\"", driver.page_source))
                printf(f"recovery détécté. quiz : {number}, restant : {restant +1}")
                play(number, override=restant + 1 )
            except Exception as e :
                printf(e)

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

    elem = driver.find_element(By.CSS_SELECTOR, '[title="Microsoft Rewards"]')
    elem.click()
    driver.switch_to.window(driver.window_handles[len(driver.window_handles) - 1])
    CustomSleep(uniform(10,20))
    try :
        point = search("availablePoints\":([\d]+)",driver.page_source)[1]
    except Exception as e :
        LogError(e)
        point = "erreur"

    CustomSleep(uniform(3,20))
    
    account = account.split('@')[0]
    client = discord.Client()
    @client.event
    async def on_ready():
        channel = client.get_channel(841338253625917450)

        await channel.send(f'{account} actuellement à {str(point)} points')
        CustomSleep(1)
        await client.close()


    client.run(Token)


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


def CheckPoint():# a fix, ne marche pas dans  80% des cas
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


with open(LogPath) as f:
    reader = reader(f)
    data = list(reader)

Credentials = data

CustomSleep(2)

shuffle(Credentials)


for i in Credentials :
    
    
    _mail =i[0]
    _password = i[1]

    print('\n\n')
    print(_mail)
    CustomSleep(1)
    if main: 
        driver = FirefoxPC()
        driver.implicitly_wait(5)

        try :
            DailyRoutine()
            driver.quit()
            timer = uniform(120,360)
            print(f"finis. attente de {timer}s")
            CustomSleep(timer)
            
        except KeyboardInterrupt :
            print('canceled')
            close()

