#!/usr/bin/python3.10
from modules.imports import *
from modules.config import *
from modules.db import add_to_database
from modules.tools import *
from modules.error import *
from modules.driver_tools import *
from modules.cards import *
import modules.globals as g


driver = g.driver
display = g.display


# create a webdriver 
def firefox_driver(mobile=False, headless=False):
    PC_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        "AppleWebKit/537.36 (KHTML, like Gecko)"
        "Chrome/112.0.0.0 Safari/537.36 Edg/110.0.1587.56")
    MOBILE_USER_AGENT = (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_5 like Mac OS X)"
        "AppleWebKit/606.0.2 (KHTML, like Gecko)"
        "CriOS/107.0.5060.64 Mobile/15E148 Safari/604.1"
    )
    options = Options()
    options.set_preference('intl.accept_languages', 'fr-FR, fr')
    options.set_preference("browser.link.open_newwindow", 3)
    options.set_preference("dom.confirm_repost.testing.always_accept", True)
    if g.fast:
        options.set_preference("permissions.default.image", 2)
    if headless:
        options.add_argument("-headless")
    if mobile :
        options.set_preference("general.useragent.override", MOBILE_USER_AGENT)
        driver = webdriver.Firefox(options=options)
        driver.set_window_size(1070 + hash(g._mail)%10 , 1900 + hash(g._password + "salt")%20) # mobile resolution are crazy high now, right ?
    else :
        options.set_preference("general.useragent.override", PC_USER_AGENT)
        driver = webdriver.Firefox(options=options)
        driver.set_window_size(1900 + hash(g._mail)%20 , 1070 + hash(g._password + "salt")%10)
    return(driver)


def log_error(error, ldriver=driver, log=g.full_log):
    global driver
    if ldriver is None:
        ldriver = driver
    if type(error) != str :
        error = format_error(error)
    printf(f"\n\n\033[93m Erreur : {str(error)}  \033[0m\n\n")
    if g.discord_enabled_error:
        with open("page.html", "w") as f:
            try :
                f.write(ldriver.page_source)
            except :
                f.write("the driver has closed or crashed. Can't access page content")
        try : 
            img = display.waitgrab()
            img.save("screenshot.png")
        except :
            ldriver.save_screenshot("screenshot.png")
        if not log:
            embed = Embed(
                title="An Error has occured",
                description=str(error),
                colour=Colour.red(),
            )
        else:
            embed = Embed(
                title="Full log is enabled",
                description=str(error),
                colour=Colour.blue(),
            )
        file = File("screenshot.png")
        embed.set_image(url="attachment://screenshot.png")
        embed.set_footer(text=g._mail)
        webhookFailure.send(embed=embed, username="error", file=file, avatar_url = g.avatar_url)
        webhookFailure.send(username="error", file=File("page.html"), avatar_url = g.avatar_url)


# close the tab currently on and go back to the one first, or the one specified
def close_tab(tab, SwitchTo=0) -> None:
    driver.switch_to.window(tab)
    driver.close()
    driver.switch_to.window(driver.window_handles[SwitchTo])


# play_quiz[N]([int : override]) make the quiz with N choice each time. They usually have between 4 and 10 questions. 
# override is the number of question, by default, it's the number of question in this specific quiz. Can be useful in some case, where the program crashes before finishing the quiz
def play_quiz2(override=10) -> None:
    printf("starting play_quiz2")
    for j in range(override):
        try:
            # rgpd_popup(driver)
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
                if g.log:
                    progressBar(j, 10, name="quiz 2")
            else:
                answer_elem = driver.find_element(By.ID, "rqAnswerOption1")
                answer_elem.click()
                if g.log:
                    progressBar(j, 10, name="quiz 2")

        except exceptions.ElementNotInteractableException as e:
            driver.execute_script("arguments[0].click();", answer_elem)
        except Exception as e:
            log_error(e)
            break
    printf("play_quiz2 done")
    custom_sleep(3)


def play_quiz8():
    override = len(findall("<span id=\"rqQuestionState.\" class=\"emptyCircle\"></span>", driver.page_source))+1
    printf(f"play_quiz8 : start, override : {override}")
    try:
        counter = 0
        # rgpd_popup(driver)
        for _ in range(override):  
            sleep(uniform(3, 5))
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
                if g.log :
                    progressBar(counter, 16, name="Quiz 8")
                try:
                    answer_elem = driver.find_element(By.ID, answer_id)
                    answer_elem.click()
                    sleep(1)
                except exceptions.NoSuchElementException :
                    driver.refresh()
                    sleep(10)
                    answer_elem = driver.find_element(By.ID, answer_id)
                    answer_elem.click()
                except ElementClickInterceptedException :
                    rgpd_popup(driver)
                    correct_answers.append(answer_id)

    except Exception as e:
        log_error(f"{format_error(e)} \n Good answers : {' '.join(correct_answers)}")
    printf("play_quiz8 : fin ")
    custom_sleep(3)


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
            # rgpd_popup(driver)
            answer_option = search('correctAnswer":"([^"]+)', txt)[1]
            answer_option = answer_option.replace("\\u0027", "'")    # replace Unicode weird symbols
            try:
                answer_element = driver.find_element(By.CSS_SELECTOR, f'[data-option="{answer_option}"]')
                answer_element.click()
            except exceptions.ElementNotInteractableException:
                driver.execute_script("arguments[0].click();", answer_element)

    except Exception as e:
        log_error(e)
        raise ValueError(e)
    printf("play_quiz4 : end")
    custom_sleep(3)


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
        log_error(error)
        raise ValueError(error)
    printf("do_poll : end")
    custom_sleep(3)


def all_cards():
    driver.get("https://rewards.bing.com")
    wait_until_visible(By.CLASS_NAME, "c-card-content", 10, driver)
    liste = driver.find_elements(By.CLASS_NAME, "c-card-content")
    custom_sleep(2)
    if "welcometour" in driver.current_url:
        welcome_tour_NO(driver)
    try :
        promo()
    except Exception as e:
        printf("no promo card")
    if(len(liste) < 10): #most likely an error during loading
        if "suspendu" in driver.page_source:
            raise Banned()
        driver.refresh()
        liste = driver.find_elements(By.CLASS_NAME, "c-card-content")
        if(len(liste) < 10):
            log_error("Less than 10 cards. Most likely an error with login.", driver)
            return("PAS ASSEZ DE CARTES")
    if (len(liste) < 20): # most likely not in france
        printf("moins de 20 cartes. Probablement pas en France.")
    for i in range(len(liste)):
        printf(f"carte {i}")
        try : 
            checked = ("mee-icon-AddMedium" in liste[i].get_attribute("innerHTML"))
        except StaleElementReferenceException :
            driver.refresh()
            liste = driver.find_elements(By.CLASS_NAME, "c-card-content")
            printf(f"staled, {len(liste)}")
            checked = ("mee-icon-AddMedium" in liste[i].get_attribute("innerHTML"))
        except IndexError:
            driver.get("https://rewards.bing.com")
            custom_sleep(10)
            liste = driver.find_elements(By.CLASS_NAME, "c-card-content")
            try : 
                checked = ("mee-icon-AddMedium" in liste[i].get_attribute("innerHTML"))
            except IndexError :
                if i == len(liste) & i > 15 :
                    checked = False
        if checked:
            custom_sleep(1.5)
            driver.execute_script("arguments[0].scrollIntoView();", liste[i])
            custom_sleep(1.5)
            liste[i].click()
            if len(driver.window_handles) > 1 :
                driver.switch_to.window(driver.window_handles[1])
                try_play(driver.title)
                close_tab(driver.window_handles[1])
                try : 
                    driver.refresh()
                    liste = driver.find_elements(By.CLASS_NAME, "c-card-content")
                    if ("mee-icon-AddMedium" in liste[i].get_attribute("innerHTML")) :
                        printf(f"carte {i} not okay. Retrying.")
                        try :
                            liste[i].click()
                        except :
                            log_error("problème inconnu ? sauf si c'est un element obscure...", driver)
                            driver.get("https://rewards.bing.com")
                            checked = ("mee-icon-AddMedium" in liste[i].get_attribute("innerHTML"))
                        driver.switch_to.window(driver.window_handles[1])
                        try_play(driver.title)
                        close_tab(driver.window_handles[1])
                        if ("mee-icon-AddMedium" in liste[i].get_attribute("innerHTML")):
                            driver.execute_script("arguments[0].scrollIntoView();", liste[i])
                            log_error(f"Card {i} Can't be completed. Why MS ?", driver)
                            liste[i].click()
                            driver.switch_to.window(driver.window_handles[1])
                            log_error(f"Cart completion - log - 2", driver)
                            custom_sleep(10)
                            log_error(f"Cart completion - log - 3 - after 10 sec", driver)
                            try:
                                try_play(driver.title) # go back to the main page
                            except :
                                driver.get("https://rewards.bing.com")
                except :
                    pass
            else : 
                try : 
                    welcome_tour(liste[i], driver)
                except Exception as e:
                    printf("no new windows" + format_error(e))
                    driver.get("https://rewards.bing.com")
            custom_sleep(3)


def promo():
    for i in range(5):
        elm = driver.find_element(By.ID, "promo-item")
        wait_until_visible(By.ID, "promo-item", 5, driver)
        if not elm:
            break
        if i > 3 :
            log_error("plus de 3 promo cards, probablement une pa skipable", driver)
        try :
            elm.click()
        except Exception as e:
            #log_error(e, driver)
            driver.execute_script("arguments[0].click();", elm)
            #log_error(e, driver)
            printf(f"that should't be there (promo), but the workarround seemed to work {e}")
        custom_sleep(3)
        if len(driver.window_handles) > 1 :
            driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
            try_play(driver.title)
            close_tab(driver.window_handles[1])
        else : 
            try : 
                spotify(driver)
            except :
                printf("no new windows", driver)
                driver.get("https://rewards.bing.com")
        driver.refresh()
        custom_sleep(3)


# Find out which type of action to do
def try_play(nom="inconnu"):
    def play(number):
        if number == 8 or number == 9:
            try:
                printf(f"\033[96mQuiz 8 detected on `{nom}` \033[0m")
                play_quiz8()
                printf(f"\033[92mQuiz 8 succeeded on `{nom}` \033[0m")
                custom_sleep(uniform(3, 5))
            except Exception as e:
                printf(f"fail of PlayQuiz 8. Aborted {e} \033[0m")

        elif number == 5 or number == 4:
            try:
                printf(f"\033[96mQuiz 4 detected on `{nom}` \033[0m")
                play_quiz4()
                printf(f"\033[92mQuiz 4 succeeded on `{nom}` \033[0m")
                custom_sleep(uniform(3, 5))
            except Exception as e:
                printf(f"Fail of PlayQuiz 4. Aborted {e} \033[0m")

        elif number == 3 or number == 2:
            try:
                printf(f"\033[96mQuiz 2 detected on `{nom}`\033[0m")
                play_quiz2()
                printf(f"\033[92mQuiz 2 succeeded on `{nom}`\033[0m")
            except Exception as e:
                printf(f"fail of PlayQuiz 2. Aborted {e}")
        else:
            printf("There is an error. rqAnswerOption present in page but no action to do. skipping.")

    if "pas connecté à Microsoft Rewards" in driver.page_source:
        driver.find_element(By.CSS_SELECTOR, '[onclick="setsrchusr()"]').click()
        custom_sleep(5)
        printf("not connected, fixed")

    try:
        if wait_until_visible(By.ID, "rqStartQuiz", 5, driver):
            custom_sleep(3)
            driver.find_element(By.ID, "rqStartQuiz").click()  # start the quiz
            answer_number = driver.page_source.count("rqAnswerOption")
            play(answer_number)
        else :
            raise(NameError("going to next part"))
    except Exception as e: # if there is no start button, an error is thrown
        if "bt_PollRadio" in driver.page_source:
            try:
                printf("Poll detected")
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
            printf("fidélité")
            fidelity()

        else:
            printf(f"rien à faire sur la page {nom}")
            custom_sleep(uniform(3, 5))


# Login with password or with cookies.
# The driver should be in the same state on both case 
def pwd_login(ldriver):    
    printf("pwd_login : start")
    ldriver.get("https://login.live.com")
    wait_until_visible(By.ID, "i0116", browser = ldriver)
    mail_elem = ldriver.find_element(By.ID, "i0116")
    send_keys_wait(mail_elem, g._mail)
    mail_elem.send_keys(Keys.ENTER)
    wait_until_visible(By.ID, "i0118", browser = ldriver)
    pwd_elem = ldriver.find_element(By.ID, "i0118")
    send_keys_wait(pwd_elem, g._password)
    pwd_elem.send_keys(Keys.ENTER)
    custom_sleep(2)
    # 2FA
    if "Entrez le code de sécurité" in ldriver.page_source : 
        try : 
            a2f_elem = ldriver.find_element(By.ID, "idTxtBx_SAOTCC_OTC")
            a2f_elem.send_keys(g._otp.now())
            a2f_elem.send_keys(Keys.ENTER)
        except Exception as e :
            log_error(e)


def cookie_login(ldriver):
    printf("cookies_login : start")
    ldriver.get("https://login.live.com")
    try : 
        load_cookies(ldriver)
    except FileNotFoundError :
        printf("No cookies file Found.")
        return(False)
    except Exception as e:
        log_error(f"Error performing cookies login. Trying with password instead. \n{str(e)}", driver)
        return(False)
    try :
        ldriver.refresh()
    except Exception as e:
        printf(format_error(e))
        printf("FIX YOUR SITE MS.......")
        
    return(True)


# Accept all cookies question, and check if the account is locked
def login_part_2(ldriver, cookies = False):
    custom_sleep(5)
    if ('Abuse' in ldriver.current_url) : 
        raise Banned()
    if ('identity' in ldriver.current_url) : 
        raise Identity()
    if ('notice' in ldriver.current_url) : 
        ldriver.find_element(By.ID, "id__0").click()
    if ("proof" in ldriver.current_url):
        ldriver.find_element(BY.ID, "iLooksGood")
    if cookies:
        save_cookies(ldriver)
    for id in ["KmsiCheckboxField", "id__0", "iLooksGood", "idSIButton9", "iCancel"]:
        if get_domain(ldriver) == "account.microsoft.com":
            break
        try:
            ldriver.find_element(By.ID, id).click()
            restart = True
        except Exception as e:
            pass
    wait_until_visible(By.CSS_SELECTOR, '[data-bi-id="sh-sharedshell-home"]', 20, ldriver)
    ldriver.get("https://www.bing.com/")
    rgpd_popup(ldriver)
    ldriver.refresh()
    rgpd_popup(ldriver)


# login() tries to login to your Microsoft account.
# it uses global variable g._mail and g._password to login
def login(ldriver):
    try : 
        success_cookies = cookie_login(ldriver)
        if not success_cookies:
            pwd_login(ldriver)
        login_part_2(ldriver, not success_cookies)
        ldriver.get("https://rewards.bing.com/")
    except Banned:
        raise Banned()
    except Identity:
        raise Banned()
    except Exception as e:
        log_error(e)
        ldriver.quit()
        return(False)


# Makes 30 search as PC Edge
def bing_pc_search(override=randint(35, 40)):
    mot = choice(Liste_de_mot).replace(" ","+")
    driver.get(f"https://www.bing.com/search?q={mot}")  # {choice(Liste_de_mot)}')
    custom_sleep(uniform(1, 2))
    rgpd_popup(driver)
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
        custom_sleep(uniform(3, 7))
        try:
            driver.find_element(By.ID, "sb_form_q").clear()
        except Exception as e:
            printf(e)
            try:
                driver.get('https://www.bing.com/search?q=plans')
                driver.find_element(By.ID, "sb_form_q").clear()
            except Exception as e:
                log_error(f"clear la barre de recherche - {format_error(e)}")


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
        driver.get("https://rewards.bing.com")
        custom_sleep(1)
        if "/proofs/" in driver.current_url:
            for id in ["KmsiCheckboxField","iLooksGood", "idSIButton9", "iCancel"]:
                try:
                    driver.find_element(By.ID, id).click()
                    restart = True
                except Exception as e:
                    pass
        wait_until_visible(By.CSS_SELECTOR, 'span[mee-element-ready="$ctrl.loadCounterAnimation()"]', browser=driver)
        try : 
            point = search('availablePoints\":([\d]+)', driver.page_source)[1]
        except Exception as e:
            sleep(5)
            log_error(f"Dev error, checking why it doesn't work (waited a bit, is this still white ?) {format_error(e)}", driver, True)
            driver.refresh()
            sleep(5)
            point = search('availablePoints\":([\d]+)', driver.page_source)[1]
        return(point)

    for _ in range (3):
        try : 
            points = get_points()
            break
        except Exception as e:
            custom_sleep(300)
            log_error(e)
            points = None
            
    if not points : 
        log_error(f"impossible d'avoir les points")

    custom_sleep(uniform(3, 20))
    account_name = account.split("@")[0]

    if g.discord_enabled_success:
        if g.discord_embed:
            embed = Embed(
                title=f"{account_name} actuellement à {str(points)} points", colour=Colour.green()
            )
            embed.set_footer(text=account_name)
            webhookSuccess.send(embed=embed)
        else:
            webhookSuccess.send(f"{account_name} actuellement à {str(points)} points")

    if g.sql_enabled :
        try :
            add_to_database(account_name, points, g.sql_host, g.sql_usr, g.sql_pwd, g.sql_database)
        except Exception as e:
            if g.database_error_override:
                printf("database error.")
            else : 
                log_error(e)

                
def fidelity():
    def sub_fidelity(): 
        try:
            wait_until_visible(By.CSS_SELECTOR, 'div[class="pull-left spacer-48-bottom punchcard-row"]', browser=driver)
            answer_number = search("([0-9]) of ([0-9]) completed", driver.page_source)
            if answer_number is None :
                answer_number = search("([0-9])&nbsp;défi\(s\) terminé\(s\) sur ([0-9])", driver.page_source)
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
                        log_error(f"fidélité - double erreur - e1 : {format_error(e1)} - e2 {format_error(e2)}")
                        break
                custom_sleep(uniform(3, 5))
                driver.switch_to.window(driver.window_handles[2])
                try_play(driver.title)
                custom_sleep(uniform(3, 5))
                try:
                    close_tab(driver.window_handles[2], 1)
                except Exception as e:
                    printf(e)
            printf("fidelity - done")
        except Exception as e:
            log_error(e)
    if driver.current_url != "https://rewards.bing.com":
        driver.get("https://rewards.bing.com")
    try :
        pause = driver.find_element(By.CSS_SELECTOR, f'[class="c-action-toggle c-glyph f-toggle glyph-pause"]') # mettre le truc en pause
        pause.click()
    except Exception as e:
        printf(f"erreur : probablement pas de cartes {e}")
        return("no cards")
    cartes = driver.find_elements(By.CSS_SELECTOR, f'[ng-repeat="item in $ctrl.transcludedItems"]')
    nb_cartes = len(cartes)
    checked_list_all = driver.find_elements(By.CSS_SELECTOR, f'[ng-if="$ctrl.complete"]')
    for i in range(nb_cartes):
        cartes[i].click() # affiche la bonne carte
        checked_txt = checked_list_all[i].get_attribute("innerHTML")
        ok = checked_txt.count("StatusCircleOuter checkmark")
        total = checked_txt.count("StatusCircleOuter")
        if (ok != total) :
            elm = driver.find_elements(By.CLASS_NAME, 'clickable-link')[i]
            if not "moviesandtv" in elm.get_attribute("innerHTML"): # not the film card
                elm.click()
                driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
                sub_fidelity()
                close_tab(driver.window_handles[1])
        custom_sleep(1)
        cartes = driver.find_elements(By.CSS_SELECTOR, f'[ng-repeat="item in $ctrl.transcludedItems"]')
        checked_list_all = driver.find_elements(By.CSS_SELECTOR, f'[ng-if="$ctrl.complete"]')

def mobile_alert_popup():
    try:
        alert = mobile_driver.switch_to.alert
        alert.dismiss()
    except exceptions.NoAlertPresentException as e:
        pass
    except Exception as e:
        log_error(e, mobile_driver)


def bing_mobile_search(override=randint(22, 25)):
    global mobile_driver
    mobile_driver = firefox_driver(mobile=True)
    try:
        login(mobile_driver)
        mot = choice(Liste_de_mot).replace(" ","+")
        mobile_driver.get(f"https://www.bing.com/search?q={mot}")
        custom_sleep(uniform(1, 2))
        rgpd_popup(mobile_driver)
        custom_sleep(uniform(1, 1.5))
        for i in range(override):  # 20
            try :
                mot = choice(Liste_de_mot)
                send_keys_wait(mobile_driver.find_element(By.ID, "sb_form_q"), mot)
                mobile_driver.find_element(By.ID, "sb_form_q").send_keys(Keys.ENTER)
                custom_sleep(uniform(3, 7))
                mobile_alert_popup()  # check for alert (asking for position or for allowing notifications)
                mobile_driver.find_element(By.ID, "sb_form_q").clear()
            except Exception as e:
                printf(e)
                mobile_driver.refresh()
                custom_sleep(30)
                i -= 1
        mobile_driver.quit()

    except Exception as e:
        log_error(e, mobile_driver)
        mobile_driver.quit()


def daily_routine(custom = False):
    try : 
        if not custom: # custom already login 
            login(driver)
    except Banned :
        log_error("This account is locked. Fix that. (-U ?)", driver)
        return()
    except Identity :
        log_error("This account has an issue. Fix that.", driver)
        return()

    try:
        all_cards()
    except Banned:
        log_error("banned", driver)
        return("BANNED")
    except Exception as e:
        log_error(e)

    try:
        fidelity()
    except Exception as e:
        log_error(e)

    try:
        bing_pc_search()
    except Exception as e:
        log_error(e)

    try:
        bing_mobile_search()
    except Exception as e:
        log_error(e)

    try:
        log_points(g._mail)
    except Exception as e:
        log_error(e)


def dev():
    pass



def CustomStart():
    if not g.islinux :
        raise NameError('You need to be on linux to do that, due to the utilisation of a module named enquieries, sorry.') 
    global driver

    system("clear")  # clear from previous command to allow a clean choice
    actions = ["tout", "daily", "pc", "mobile", "log_points","fidelity", "dev"]
    Actions = enquiries.choose("quels Actions ?", actions, multi=True)
    liste = select_accounts()
    g.start_time = time() # Reset timer to the start of the actions

    for cred in liste:
        g._mail = cred[0]
        g._password = cred[1]
        if len(cred) == 3:
            g._otp = TOTP(cred[2])

        driver = firefox_driver()
        driver.implicitly_wait(3)
        if login(driver) != "STOP":
            if "tout" in Actions:
                daily_routine(True)
            if "daily" in Actions:
                try:
                    all_cards()
                except Exception as e:
                    log_error(e)
            if "pc" in Actions:
                try:
                    bing_pc_search()
                except Exception as e:
                    log_error(e)
            if "mobile" in Actions:
                try:
                    bing_mobile_search()
                except Exception as e:
                    log_error(e)
            if "fidelity" in Actions:
                try :
                    fidelity()
                except Exception as e :
                    log_error(e)
            if "dev" in Actions:
                try:
                    dev()
                except Exception as e:
                    printf(e)
                    break
            if not "tout" in Actions:
                try:
                    log_points(g._mail)
                except Exception as e:
                    printf(f"CustomStart {e}")
            driver.quit()


if g.vnc_enabled : 
    display = SmartDisplay(backend="xvnc", size=(2160, 2160), rfbport=g.vnc_port, color_depth=24) 
else :
    display = SmartDisplay(size=(2160, 2160)) 
display.start()


if g.custom_start:
    CustomStart()
elif g.unban:
    g._mail, g._password  = select_accounts(False)[0]
    driver = firefox_driver()
    try : 
        login(driver)
    except Banned:
        unban()
    driver.quit()
elif g.points_file != "":
    save_points_from_file(g.points_file)
else:
    if g.update_version != "None":
        if g.discord_enabled_error:
            webhookFailure.send(f"Updated to {g.update_version}", username="UPDATE", avatar_url="https://cdn-icons-png.flaticon.com/512/1688/1688988.png")
    for cred in g._cred:
        g._mail = cred[0]
        g._password = cred[1]
        if len(cred) == 3:
            g._otp = TOTP(cred[2])
        custom_sleep(1)
        printf("Début du driver.")
        driver = firefox_driver()
        printf("Driver demarré.")
        driver.implicitly_wait(3)
        try:
            daily_routine()
            driver.quit()
            attente = uniform(1200, 3600)
            printf(f"finis. attente de {round(attente/60)}min")
            custom_sleep(attente)
        except KeyboardInterrupt:
            printf("Canceled. Closing driver and display.")
            driver.quit()
            display.stop()
        except Exception as e:
            log_error(f"Error not catched. Skipping this account. " + format_error(e), driver)
            printf(f"Error not catched. Skipping this account. {e}")
            driver.quit()

display.stop()
