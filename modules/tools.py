from modules.imports import *
from modules.config import *
from modules.db import *
import modules.globals as g
# add the time arround the text given in [text]&
def Timer(text: str) -> str:
    return(f"[{g._mail.split('@')[0]} - {datetime.today().strftime('%d/%m')} - {timedelta(seconds = round(float(time() - g.start_time)))}] " + str(text))


# replace the function print, with more options
# [txt] : string, [driver] : selenium webdriver
def printf(txt):
    print(Timer(txt))


# return current page domain
def get_domain(driver):
    return(driver.current_url.split("/")[2])

    
# check if the user is using IPV4 using ipify.org
# [driver] : selenium webdriver
# never used here
# can be useful as Ms had issues with IPV6 at some point
def check_ipv4(driver):
    driver.get("https://api64.ipify.org")
    elm = driver.find_element(By.TAG_NAME, "body")
    if len(elm.text.split('.')) == 4 :
        return True
    return False


def custom_sleep(temps):
    try : 
        if g.log : #only print sleep when user see it
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
        print("attente annulée")


def format_error(e) -> str:
    tb = e.__traceback__
    txt = ""
    while tb != None :
        txt = txt + f" -> {tb.tb_frame.f_code.co_name} ({tb.tb_lineno}) "
        tb = tb.tb_next
    return(txt + "\n" + str(e))


def progressBar(current, total=30, barLength=20, name="Progress"):
    percent = float(current + 1) * 100 / total
    arrow = "-" * int(percent / 100 * barLength - 1) + ">"
    spaces = " " * (barLength - len(arrow))
    print(name + ": [%s%s] %d %%" % (arrow, spaces, percent), end="\r")


def save_points_from_file(file):
    with open(file) as f:
        read = reader(f)
        points_list = list(read)
    for item in points_list:
        compte, points = item[0], item[1]
        add_to_database(compte, points, g.sql_host,g.sql_usr,g.sql_pwd,g.sql_database, save_if_fail=False)
    with open(file, "w") as f:
        f.write("")


def select_accounts(multiple = True):
    system("clear")  # clear from previous command to allow a clean choice
    emails = [x[0] for x in g._cred]  # list of all email adresses
    emails_selected = enquiries.choose(f"quel{'s' if multiple else ''} compte{'s' if multiple else ''} ?", emails, multi=multiple)
    return([x for x in g._cred if x[0] in emails_selected])

