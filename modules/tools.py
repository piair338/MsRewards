from modules.imports import *
from modules.config import *


# add the time arround the text given in [text]&
def Timer(text: str, mail: str) -> str:
    return(f"[{mail.split('@')[0]} - {datetime.today().strftime('%d/%m')} - {timedelta(seconds = round(float(time() - START_TIME)))}] " + str(text))


# replace the function print, with more options
# [txt] : string, [driver] : selenium webdriver
def printf2(txt, mail, LOG = LOG):
    print(Timer(txt, mail))



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
        if FAST and temps > 50:
            sleep(temps/10)
        elif LOG: #only print sleep when user see it
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
        reader = csv.reader(f)
        points_list = list(reader)

    for item in points_list:
        compte, points = item[0], item[1]
        add_to_database(compte, points, sql_host,sql_usr,sql_pwd,sql_database, save_if_fail=False)

    with open(file, "w") as f:
        f.write("")


def select_accounts(multiple = True):
    system("clear")  # clear from previous command to allow a clean choice
    emails = [x[0] for x in Credentials]  # list of all email adresses
    emails_selected = enquiries.choose(f"quel{'s' if multiple else ''} compte{'s' if multiple else ''} ?", emails, multi=multiple)
    return([x for x in Credentials if x[0] in emails_selected])

