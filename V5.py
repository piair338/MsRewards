#!/usr/bin/python3.10
from modules.imports import *
from modules.db import add_to_database
from modules.config import *
from modules.tools import *
from modules.error import *
from modules.driver_tools import *
import modules.globals as g


driver = g.driver
display = g.display


# TODO
# handle "panda"'s error: error while logging in preventing some task to be done SadPanda.svg:


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
    if proxy_enabled :
        setup_proxy(proxy_address,proxy_port, options)
    options.set_preference("browser.link.open_newwindow", 3)
    options.set_preference("dom.confirm_repost.testing.always_accept", True)
    if FAST :
        options.set_preference("permissions.default.image", 2) #disable image loading. You shouldn't use it except if really nessecary 
    if headless:
        options.add_argument("-headless")
    if mobile :
        options.set_preference("general.useragent.override", MOBILE_USER_AGENT)
        driver = webdriver.Firefox(options=options)
        driver.set_window_size(1070 + hash(g._mail)%20 , 1900 + hash(g._password + "salt")%10) # mobile resolution are crazy high now, right ?
    else :
        options.set_preference("general.useragent.override", PC_USER_AGENT)
        driver = webdriver.Firefox(options=options)
        driver.set_window_size(1900 + hash(g._mail)%20 , 1070 + hash(g._password + "salt")%10)
    return(driver)


def log_error(error, ldriver=driver, log=FULL_LOG):
    global driver
    if ldriver is None:
        ldriver = driver
    if type(error) != str :
        error = format_error(error)
    printf(f"\n\n\033[93m Erreur : {str(error)}  \033[0m\n\n")
    if DISCORD_ENABLED_ERROR:
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
        webhookFailure.send(embed=embed, username="error", file=file, avatar_url = AVATAR_URL)
        webhookFailure.send(username="error", file=File("page.html"), avatar_url = AVATAR_URL)


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
                progressBar(j, 10, name="quiz 2")
            else:
                answer_elem = driver.find_element(By.ID, "rqAnswerOption1")
                answer_elem.click()
                progressBar(j, 10, name="quiz 2")

        except exceptions.ElementNotInteractableException as e:
            driver.execute_script("arguments[0].click();", answer_elem)
        except Exception as e:
            log_error(e)
            break
    printf("play_quiz2 done")


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


def all_cards():
    driver.get("https://rewards.bing.com")
    liste = driver.find_elements(By.CLASS_NAME, "c-card-content")
    custom_sleep(2)
    try :
        promo()
    except Exception as e:
        #printf(format_error(e))
        printf("no promo card")

    for i in range(len(liste)):
        printf(f"carte {i}")
        try : 
            checked = ("mee-icon-AddMedium" in liste[i].get_attribute("innerHTML"))
        except StaleElementReferenceException :
            liste = driver.find_elements(By.CLASS_NAME, "c-card-content")
            printf(f"staled, {len(liste)}")
            checked = ("mee-icon-AddMedium" in liste[i].get_attribute("innerHTML"))
        if checked:
            custom_sleep(3)
            driver.execute_script("arguments[0].scrollIntoView();", liste[i])
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
                        liste[i].click()
                        driver.switch_to.window(driver.window_handles[1])
                        try_play(driver.title)
                        close_tab(driver.window_handles[1])
                except :
                    pass
            else : 
                try : 
                    welcome_tour(liste[i])
                except Exception as e:
                    print(format_error(e))
                    log_error("no new windows", driver)
            custom_sleep(3)


def welcome_tour(elm):
    try : 
        driver.find_element(By.CSS_SELECTOR, '[class="welcome-tour-next-button c-call-to-action c-glyph"]').click()
    except :
        pass
    driver.find_element(By.CSS_SELECTOR, '[class="quiz-link gray-button c-call-to-action c-glyph f-lightweight"]').click()
    sleep(5)
    driver.find_element(By.CSS_SELECTOR, '[class="c-glyph glyph-cancel"]').click()
    elm.click()
    driver.find_element(By.CSS_SELECTOR, '[class="quiz-link gray-button c-call-to-action c-glyph f-lightweight"]').click()
    sleep(5)
    driver.find_element(By.CSS_SELECTOR, '[class="c-glyph glyph-cancel"]').click()
    elm.click()
    driver.find_element(By.CSS_SELECTOR, '[class="quiz-link gray-button c-call-to-action c-glyph f-lightweight"]').click()
    sleep(5)
    driver.find_element(By.CSS_SELECTOR, '[class="c-glyph glyph-cancel"]').click()


def spotify():
    custom_sleep(5)
    driver.find_element(By.CSS_SELECTOR, '[data-bi-id="spotify-premium gratuit"]').click()
    custom_sleep(5)
    close_tab(driver.window_handles[1])


def promo():
    elm = driver.find_element(By.ID, "promo-item")
    for i in range(10):
        if not elm:
            break
        if i > 8 :
            log_error("chelou, plus de 8 truc", driver)
        driver.execute_script("arguments[0].click();", elm)
        custom_sleep(3)
        if len(driver.window_handles) > 1 :
            driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
            try_play(driver.title)
            close_tab(driver.window_handles[1])
        else : 
            try : 
                spotify()
            except :
                log_error("no new windows", driver)
                driver.get("https://rewards.bing.com")
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
            log_error("There is an error. rqAnswerOption present in page but no action to do. skipping.")

    try:
        if wait_until_visible(By.ID, "rqStartQuiz", 5, driver):
            custom_sleep(3)
            driver.find_element(By.ID, "rqStartQuiz").click()  # start the quiz
            answer_number = driver.page_source.count("rqAnswerOption")
            play(answer_number)
        else :
            raise (NameError("going to next part"))
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
    ldriver.refresh()
    return(True)


# Accept all cookies question, and check if the account is locked
def login_part_2(ldriver, cookies = False):
    custom_sleep(5)
    if ('Abuse' in ldriver.current_url) : 
        raise Banned()
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
    ldriver.get("https://www.bing.com")
    rgpd_popup(ldriver)
    ldriver.refresh()
    rgpd_popup(ldriver)
    ldriver.get("https://account.microsoft.com/")
    if wait_until_visible(By.CSS_SELECTOR, '[data-bi-id="sh-sharedshell-home"]', 30, ldriver) :
        return(True) #the account logging was successful
    else :
        log_error("Error during login. Trying to refresh")
        ldriver.refresh()
        return(wait_until_visible(By.CSS_SELECTOR, '[data-bi-id="sh-sharedshell-home"]', 30, ldriver))


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

    if DISCORD_ENABLED_SUCCESS:
        if DISCORD_EMBED:
            embed = Embed(
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
                try : 
                    choix = driver.find_element(By.CSS_SELECTOR, 'div[class="pull-left spacer-48-bottom punchcard-row"]')  # pull-left spacer-48-bottom punchcard-row? USELESS ?
                except : # tentative de fix
                    driver.execute_script("location.reload(true);")
                    wait_until_visible(By.CSS_SELECTOR, 'div[class="pull-left spacer-48-bottom punchcard-row"]', browser=driver)
                    choix = driver.find_element(By.CSS_SELECTOR, 'div[class="pull-left spacer-48-bottom punchcard-row"]')
                answer_number = search("([0-9]) of ([0-9]) completed", driver.page_source)
                if answer_number is None:
                    answer_number = search("([0-9]) de ([0-9]) finalisé", driver.page_source)
                if answer_number is None :
                    answer_number = search("([0-9]) licence\(s\) sur ([0-9]) disponible\(s\)", driver.page_source)
                if answer_number is None :
                    answer_number = search("([0-9])&nbsp;défi\(s\) terminé\(s\) sur ([0-9])", driver.page_source)
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
        log_error(e)


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
        log_error("THIS ACCOUNT IS BANNED. FIX THIS ISSUE WITH -U")
        return()

    try:
        all_cards()
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
    input("paused")


def CustomStart(Credentials):
    global START_TIME
    if not LINUX_HOST :
        raise NameError('You need to be on linux to do that, due to the utilisation of a module named enquieries, sorry.') 
    global driver, p

    system("clear")  # clear from previous command to allow a clean choice
    actions = ["tout", "daily", "pc", "mobile", "log_points","fidelity", "dev"]
    Actions = enquiries.choose("quels Actions ?", actions, multi=True)
    liste = select_accounts()
    START_TIME = time() # Reset timer to the start of the actions

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
            driver.close()


if VNC_ENABLED : 
    display = SmartDisplay(backend="xvnc", size=(2160, 2160), rfbport=VNC_PORT, color_depth=24) 
else :
    display = SmartDisplay(size=(2160, 2160)) 
display.start()


if CUSTOM_START:
        CustomStart(Credentials)
elif UNBAN:
    g._mail, g._password  = select_accounts(False)[0]
    driver = firefox_driver()
    try : 
        login(driver)
    except Banned:
        unban()

    driver.quit()
elif POINTS_FILE != "":
    save_points_from_file(POINTS_FILE)
else:
    if UPDATE_VERSION != "None":
        if DISCORD_ENABLED_ERROR:
            webhookFailure.send(f"Updated to {UPDATE_VERSION}", username="UPDATE", avatar_url="https://cdn-icons-png.flaticon.com/512/1688/1688988.png")
    for cred in Credentials:
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
            printf(f"Error not catched. Skipping this account. {e}")
            driver.quit()

display.stop()
