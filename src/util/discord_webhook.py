import config
from discord_webhook import DiscordWebhook, DiscordEmbed


def send_message(message):
    webhook_url = config.WEBHOOK
    webhook = DiscordWebhook(url=webhook_url)

    title = 'Yahoo Forwarder'

    embed = DiscordEmbed(title=title, description=message, color=242424)

    webhook.add_embed(embed)
    if webhook_url != "":
        webhook.execute()


def yahoo_email_forwarded(email, forward):
    webhook_url = config.WEBHOOK
    webhook = DiscordWebhook(url=webhook_url)

    embed = DiscordEmbed(title='Yahoo Account Forwarded!', description='', color=242424)

    embed.add_embed_field(name='Email', value=email)
    embed.add_embed_field(name='Forward', value=forward)

    webhook.add_embed(embed)
    if webhook_url != "":
        webhook.execute()


def yahoo_forward_complete():
    webhook_url = config.WEBHOOK
    webhook = DiscordWebhook(url=webhook_url)

    title = 'All Yahoo accounts have been forwarded!'

    embed = DiscordEmbed(title=title, description='Forwarding complete', color=242424)

    webhook.add_embed(embed)
    if webhook_url != "":
        webhook.execute()


def yahoo_email_spam(account, winner):
    webhook_url = config.WEBHOOK
    webhook = DiscordWebhook(url=webhook_url)

    embed = DiscordEmbed(title='Yahoo Account Spam Moved!', description='', color=242424)

    embed.add_embed_field(name='Email', value=account['email'])
    embed.add_embed_field(name='Winner', value=winner)

    webhook.add_embed(embed)
    if webhook_url != "":
        webhook.execute()


def yahoo_spam_complete():
    webhook_url = config.WEBHOOK
    webhook = DiscordWebhook(url=webhook_url)

    title = 'All Yahoo accounts have moved their spam!'

    embed = DiscordEmbed(title=title, description='Forwarding complete', color=242424)

    webhook.add_embed(embed)
    if webhook_url != "":
        webhook.execute()
