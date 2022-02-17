#!/usr/bin/python3
"""
Module used to log errors and success
"""
from discord import (  # Importing discord.Webhook and discord.RequestsWebhookAdapter
    Colour,
    Embed,
    RequestsWebhookAdapter,
    Webhook,
    File,
)

from modules.variables import *

webhook_success = Webhook.from_url(SuccessLink, adapter=RequestsWebhookAdapter())
webhook_failure = Webhook.from_url(ErrorLink, adapter=RequestsWebhookAdapter())


def error(message="An error occured", url=None, mail="None"):
    """Sends an error message using discord webhooks"""
    if embeds:
        embed = Embed(
            title="An Error has occured",
            description=str(message),
            url=url,
            colour=Colour.red(),
        )
        file = File("screenshot.png")
        embed.set_image(url="attachment://screenshot.png")
        embed.set_footer(text=mail)
        webhook_failure.send(embed=embed, file=file)
        webhook_failure.send(file=File("page.html"))
    else:
        webhook_failure.send(content="------------------------------------\n" + mail)
        webhook_failure.send(url)
        webhook_failure.send(str(message))
        webhook_failure.send(file=File("screenshot.png"))
        webhook_failure.send(file=File("page.html"))
        webhook_failure.send("------------------------------------")


def point(account=None, points=None):
    """Sends a message (success) in most cases with Discord webhooks"""
    message = f"{account} actuellement à {str(points)} points"
    if embeds:
        embed = Embed(title=message, colour=Colour.green())
        embed.set_footer(text=account)
        webhook_success.send(embed=embed)
    else:
        webhook_success.send(message)
