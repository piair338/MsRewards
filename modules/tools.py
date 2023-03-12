from time import sleep
from datetime import timedelta, datetime
from random import uniform
import discord
from discord import (  # Importing discord.Webhook and discord.RequestsWebhookAdapter
    Colour,
    Webhook,
)

from selenium.webdriver.common.by import By
from modules.config import *

"""
send_keys_wait([selenium element:element, str:keys]) send the different keys to the field element, with a random time between each press to simulate human action.
keys can be an string, but alos selenium keys
"""
def send_keys_wait(element, keys):
    for i in keys:
        element.send_keys(i)
        if FAST :
            pass
        else :
            sleep(uniform(0.1, 0.3))


def LogError(message, driver, mail, log=FULL_LOG):
    print(f"\n\n\033[93m Erreur : {str(message)}  \033[0m\n\n")
    if DISCORD_ENABLED_ERROR:
        with open("page.html", "w") as f:
            f.write(driver.page_source)

        driver.save_screenshot("screenshot.png")
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
        embed.set_footer(text=mail)
        webhookFailure.send(embed=embed, file=file)
        webhookFailure.send(file=discord.File("page.html"))



# add the time arround the text given in [text]&
def Timer(text: str, mail: str) -> str:
    return(f"[{mail} - {datetime.today().strftime('%d-%m-%Y')} - {timedelta(seconds = round(float(time() - START_TIME)))}] " + str(text))


# replace the function print, with more options
# [txt] : string, [driver] : selenium wbdriver
def printf2(txt, mail, LOG = LOG):
    if LOG:
        print(Timer(txt, mail))



# check if the user is using IPV4 using ipify.org
# [driver] : selenium webdriver

def check_ipv4(driver):
    driver.get("https://api64.ipify.org")
    elm = driver.find_element(By.TAG_NAME, "body")
    if len(elm.text.split('.')) == 4 :
        return True
    return False



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
        print("attente annulée")





def progressBar(current, total=30, barLength=20, name="Progress"):
    percent = float(current + 1) * 100 / total
    arrow = "-" * int(percent / 100 * barLength - 1) + ">"
    spaces = " " * (barLength - len(arrow))
    print(name + ": [%s%s] %d %%" % (arrow, spaces, percent), end="\r")
