from time import sleep
from datetime import timedelta
from random import uniform
import discord
from discord import (  # Importing discord.Webhook and discord.RequestsWebhookAdapter
    Colour,
    Webhook,
)

from modules.config import *

_mail = "undefined"

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


def LogError(message, driver, _mail, log=FULL_LOG):
    print(f"\n\n\033[93m Erreur : {str(message)}  \033[0m\n\n")
    if DISCORD_ENABLED_ERROR:
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



# add the time arround the text given in [text]
# [text] : string
def Timer(text="undefined", mail=_mail):
    return(f"[{_mail} - {timedelta(seconds = round(float(time() - START_TIME)))}] " + str(text))


# replace the function print, with more options
# [txt] : string, [driver] : selenium wbdriver
def printf(txt, mail = _mail, LOG = LOG):
    if LOG:
        print(Timer(txt, _mail))



# check if the user is using IPV4 using ipify.org
# [driver] : selenium webdriver

def check_ipv4(driver):
    driver.get("https://api64.ipify.org")
    elm = driver.find_element(By.TAG_NAME, "body")
    if len(elm.text.split('.')) == 4 :
        return True
    return False


