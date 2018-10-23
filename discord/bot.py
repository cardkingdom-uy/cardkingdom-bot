import discord
import json
import requests
from collections import OrderedDict
try:
    from local_settings import *
except ImportError:
    pass

"""Return bot help message"""
def bot_help():
    help_msg = """
    **cardkingdom-bot** — Help\n\n**Commands list**\n_{0}bots_ — Bot reports itself\nUsage: `{0}bots`\n\n_{0}help_ — Shows this message\nUsage: `{0}help`\n\n_{0}quit_ — Bot quits (please use in private chat only)\nUsage: `{0}quit <token>`\n\n_{0}card_ — Gets all the information of a single card\nUsage: `{0}card <unique uuid>`\n\n_{0}cards_ — Gets all the cards matching the criteria\nUsage: `{0}cards <card name>[&set=id][&page=number]`""".format(CMD_PREFIX)
    return help_msg

"""Validate incoming command"""
def validate_command(content, command):
    proper_len = len(command) + 1
    if content[1:proper_len] == command and content[proper_len:(proper_len + 1)] == " ":
        return True
    return False

"""Return command text only"""
def command_text(content, command):
    proper_len = len(command) + 2
    return content[proper_len:]

"""Get discord icons"""
def get_discord_icons(content):
    content = content.replace("{X}", ":regional_indicator_x:")
    content = content.replace("{1}", ":one:")
    content = content.replace("{2}", ":two:")
    content = content.replace("{3}", ":three:")
    content = content.replace("{4}", ":four:")
    content = content.replace("{5}", ":five:")
    content = content.replace("{6}", ":six:")
    content = content.replace("{7}", ":seven:")
    content = content.replace("{8}", ":eight:")
    content = content.replace("{9}", ":nine:")
    content = content.replace("{10}", ":keycap_ten:")
    content = content.replace("{W}", ":white_circle:")
    content = content.replace("{R}", ":red_circle:")
    content = content.replace("{B}", ":black_circle:")
    content = content.replace("{U}", ":large_blue_circle:")
    content = content.replace("{G}", ":nauseated_face:")
    content = content.replace("{C}", ":nauseated_face:")
    return content

"""Get all cards matching the criteria"""
def get_cards(uuid=None, name=None):

    # Build url based on search mode
    url = API_CARDS_URL
    if uuid == None:
        # Cards marching the criteria
        url = "%s?name=%s&token=%s" % (url, name, API_TOKEN)
    else:
        # Single card search
        url = "%s?uuid=%s&token=%s" % (url, uuid, API_TOKEN)

    # Try to get JSON data
    try:
        result = requests.get(url)
    except Exception as ex:
        return "**Unable to get data!**\nPlease try again later (err. 001)"

    # Check for HTTP 200
    if result.status_code == 200:

        # Decode JSON
        raw_content = result.content.decode('utf-8')
        json_data = json.loads(raw_content, object_pairs_hook=OrderedDict)

        # Last check (API status response)
        if json_data["status"] == 200:

            # Empty return text
            return_text = "**cardkingdom-bot** — Result\n\n"

            # Loop thru cards
            for card in json_data["data"]:

                # Cards data
                card_data = "**%s**  %s\n_%s_" % (card["name"], card["manaCost"], card["type"])

                # Get single-card-only data
                if uuid != None:
                    if card["text"] != "":
                        card_data = "%s\n%s" % (card_data, card["text"])
                    if card["flavorText"] != "":
                        card_data = "%s\n_«%s»_" % (card_data, card["flavorText"])
                    if card["imageUrl"] != "":
                        card_data = "%s\nimage: %s" % (card_data, card["imageUrl"])

                # Get ck prices
                ck_prices = card["prices"]["cardkingdom.com"]
                if len(ck_prices) > 0:
                    card_data = "%s\n`nm: %.2f | ex: %.2f | vg: %.2f | g: %.2f`" % (card_data, ck_prices[0], ck_prices[1], ck_prices[2], ck_prices[3])
                else:
                    card_data = "%s\n`nm: 0 | ex: 0 | vg: 0 | g: 0`" % (card_data)

                # More cards data
                card_data = "%s\n(set: **%s**, uuid: **%s**)\n\n" % (card_data, card["set"], card["uuid"])

                # Add to return text
                return_text = "%s%s" % (return_text, card_data)

            # Get emojis
            return_text = get_discord_icons(return_text)

            # Return all cards
            return return_text

        else:
            return "**Unable to get data!**\nPlease try again later (err. 003)"
        
    else:
        return "**Unable to get data!**\nPlease try again later (err. 002)"

"""Process incoming commands"""
def process_command(content):
    if content[0] == CMD_PREFIX:
        # "bots"
        if content[1:] == "bots":
            return "_Reporting in!_ :wink: :flag_uy:\n\n**cardkingdom-bot** — https://github.com/cardkingdom-uy/cardkingdom-bot"
        # "help"
        if content[1:] == "help":
            return bot_help()
        # "quit <token>"
        if validate_command(content, "quit"):
            if command_text(content, "quit") == BOT_TOKEN:
                exit()
        # "card <unique uuid>"
        if validate_command(content, "card"):
            return get_cards(command_text(content, "card"), None)
        # "cards <card name>[&set=id][&page=number]"
        if validate_command(content, "cards"):
            return get_cards(None, command_text(content, "cards"))
        return None
    else:
        return None

def main():

    # Show welcome message
    print("cardkingdom-bot - discord")
    print("Contribute on https://github.com/cardkingdom-uy/cardkingdom-bot\n")

    # Discord bot client
    client = discord.Client()

    # Define on_ready event behaviour
    @client.event
    async def on_ready():

        # Set "Playing..." status
        await client.change_presence(game=discord.Game(name="Magic: The Gathering"))

    # Define on_message event behaviour
    @client.event
    async def on_message(message):

        # Ignore own messages
        if message.author == client.user:
            return

        # Process messages
        response = process_command(message.content)
        if response is not None:
            await client.send_message(message.channel, response)

    # Run bot
    client.run(BOT_TOKEN)

if __name__ == "__main__":
    main()