from enum import IntFlag
import os
import discord
import random
import json
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import datetime

BOT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BOT_DIR)

#------------------------------globals------------------------------------

PREFIX = "o"

GROUP_DATA = None
with open('groups.json', 'rb') as f:
        GROUP_DATA = json.load(f)

secret_token = os.getenv("TOKEN")

times = [
    ("year", 365*24*60*60),
    ("day", 24*60*60),
    ("hour", 60*60),
    ("min", 60),
    ("sec", 1)
]
HOUR = 60*60
MINUTE = 60

EMOJIS = {
    'coin': '<:X1Coin:926954191279231067>',
    'check': '<:check:927618520039166014>',
    'heart': '🤍'
}

COOLDOWN_COMMANDS = ['drop', 'work', 'daily']

BOT_NAME = 'Hangyul'


#----------------------------accounts----------------------------------------------------


BANK_FILE = 'mainbank.json'

def get_bank_data():
    try:
        with open(BANK_FILE, "r") as bank_file:
            bank_data = json.load(bank_file)
        return bank_data
    except FileNotFoundError:
        return {}

def set_bank_data(bank_data):
    with open(BANK_FILE, "w") as bank_file:
        json.dump(bank_data, bank_file)

INV_FILE = 'inv.json'

def get_inv_data():
    try:
        with open(INV_FILE, "r") as inv_file:
            user_inventories = json.load(inv_file)
        return user_inventories
    except FileNotFoundError:
        return {}

def set_inv_data(inv_data):
    with open(INV_FILE, "w") as inv_file:
        json.dump(inv_data, inv_file)

def get_card(id):
    return GROUP_DATA["pictures"].get(id, None)

BIO_FILE = "biography.json"

def get_bio_data():
    try:
        with open(BIO_FILE, "r") as bio_file:
            bio_data = json.load(bio_file)
        return bio_data
    except FileNotFoundError:
        return {}

def set_bio_data(bio_data):
    with open(BIO_FILE, "w") as bio_file:
        json.dump(bio_data, bio_file)

class UserBiography:
    def __init__(self, id):
        self.id = str(id)
        self.bios = None
        self.load()

    def load(self):
        user = get_bio_data().get(self.id, None)
        if user is None:
            self.bios = "Nothing to see here"
        else:
            self.bios = user.get('biography', {})

    def save(self):
        users = get_bio_data()
        if self.id in users:
            users[self.id]['biography'] = self.bios
        else:
            users[self.id] = { 'biography': self.bios }
        set_bio_data(users)
    
    def get_bio(self):
        return self.bios

    def set_bio(self, texte):
        self.bios = texte 
        self.save()
    
    def add_bio(self, texte):
        self.bios = texte
        self.save()


class UserAccount:
    def __init__(self, id):
        self.id = str(id)
        self.wallet = None
        self.load()

    def load(self):
        user = get_bank_data().get(self.id, None)
        if user is None:
            self.wallet = 0
        else:
            self.wallet = user.get('wallet', 0)

    def save(self):
        users = get_bank_data()
        if self.id in users:
            users[self.id]['wallet'] = self.wallet
        else:
            users[self.id] = { 'wallet': self.wallet }
        set_bank_data(users)

    def get_balance(self):
        return self.wallet
    
    def set_balance(self, balance):
        self.wallet = balance
        self.save()
    
    def remove_balance(self, balance): 
        self.wallet -= balance
        self.save()

    def add_balance(self, balance):
        self.wallet += balance
        self.save()


class UserInventory:
    def __init__(self, id):
        self.id = str(id)
        self.cards = None
        self.load()

    def load(self):
        user = get_inv_data().get(self.id, None)

        if user is None:
            self.cards = set()
        else:
            self.cards = set(user.get('cards', []))

    def save(self):
        users = get_inv_data()
        if self.id in users:
            users[self.id]['cards'] = list(self.cards)
        else:
            users[self.id] = { 'cards': list(self.cards) }
        set_inv_data(users)

    def add_card(self, card_id):
        self.cards.add(card_id)
        self.save()
    
    def remove_card(self, card_id): 
        self.cards.remove(card_id)
        self.save()

    def has_card(self, card_id):
        return card_id in self.cards
    
    def list_cards(self):
        for card_id in self.cards:
            
            yield (card_id, get_card(card_id))
    


#-----------------------------ready-----------------------------------------------------

bot = commands.Bot(command_prefix=PREFIX)
bot.remove_command('help')

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

#-----------------------------help------------------------------------------------------

@bot.command()
async def help(ctx, *, arg = None):
    if arg is None:
        embed = discord.Embed(
        title = f'{BOT_NAME} Help Commands',
        color = 0x1ad39f
        )
        embed.set_author(name= bot.user.name, icon_url = bot.user.avatar_url)
        embed.add_field(
            name = 'User 👤',
            value = "`profile` `bio` `favorite`",
            inline = False
        )
        embed.add_field(
            name = 'Cards 🎴',
            value = "`daily` `drop` `inventory` `burn` `gift` `view` `cooldown`",
            inline = False
        )
        embed.add_field(
            name = 'Currency 💰 ',
            value = "`balance` `work` `give`",
            inline = False
        )
        embed.add_field(
            name = 'Shop 🛒',
            value = "`shop` `buy` `sell` `sales` `withdraw`",
            inline = False
        )
        embed.add_field(
            name = 'Wishlist ❤️',
            value = "`wishlist` `wishlistadd` `wishlistremove`",
            inline = False
        )
        embed.add_field(
            name = 'Settings ⚙️',
            value = "`help` `prefix` `support` `remind` `vote`",
            inline = False
        )
        embed.set_footer(text=f'Use {PREFIX}help [command] for more details')
        return await ctx.send(embed = embed)
    else:
        if arg == "profile":
            em = discord.Embed(
            title = '**Profile Help**',
            color = 0x1ad39f
            )
            em.add_field(
            name = "Aliases", 
            value = "p", 
            inline = False
            )
            em.add_field(
            name = "Description", 
            value = "Show your profile", 
            inline = False
            )
            em.add_field(
            name = "Usage", 
            value = f"{PREFIX}profile [mention/id]", 
            inline = False
            )
            em.set_author(name= bot.user.name, icon_url = bot.user.avatar_url)
            await ctx.send(embed = em)
        elif arg == "bio":
            em = discord.Embed(
            title = '**Bio Help**',
            color = 0x1ad39f
            )
            em.add_field(
            name = "Aliases", 
            value = "b", 
            inline = False
            )
            em.add_field(
            name = "Description", 
            value = "Sets your bio", 
            inline = False
            )
            em.add_field(
            name = "Usage", 
            value = f"{PREFIX}bio [text]", 
            inline = False
            )
            em.set_author(name= bot.user.name, icon_url = bot.user.avatar_url)
            await ctx.send(embed = em)
        
        elif arg == "favorite":
            em = discord.Embed(
            title = '**Favorite Help**',
            color = 0x1ad39f
            )
            em.add_field(
            name = "Aliases", 
            value = "fav / f", 
            inline = False
            )
            em.add_field(
            name = "Description", 
            value = "Sets a card as your favorite", 
            inline = False
            )
            em.add_field(
            name = "Usage", 
            value = f"{PREFIX}favorite [card code]", 
            inline = False
            )
            em.set_author(name= bot.user.name, icon_url = bot.user.avatar_url)
            await ctx.send(embed = em)
        
        elif arg == "daily":
            em = discord.Embed(
            title = '**Daily Help**',
            color = 0x1ad39f
            )
            em.add_field(
            name = "Aliases", 
            value = "None", 
            inline = False
            )
            em.add_field(
            name = "Description", 
            value = "Claim your daily card and currency", 
            inline = False
            )
            em.add_field(
            name = "Usage", 
            value = f"{PREFIX}daily", 
            inline = False
            )
            em.set_author(name= bot.user.name, icon_url = bot.user.avatar_url)
            await ctx.send(embed = em)
        
        elif arg == "drop":
            em = discord.Embed(
            title = '**Drop Help**',
            color = 0x1ad39f
            )
            em.add_field(
            name = "Aliases", 
            value = "d", 
            inline = False
            )
            em.add_field(
            name = "Description", 
            value = "Drops a random card", 
            inline = False
            )
            em.add_field(
            name = "Usage", 
            value = f"{PREFIX}drop", 
            inline = False
            )
            em.set_author(name= bot.user.name, icon_url = bot.user.avatar_url)
            await ctx.send(embed = em)

        elif arg == "inventory":
            em = discord.Embed(
            title = '**Inventory Help**',
            color = 0x1ad39f
            )
            em.add_field(
            name = "Aliases", 
            value = "inv", 
            inline = False
            )
            em.add_field(
            name = "Description", 
            value = "Shows your inventory", 
            inline = False
            )
            em.add_field(
            name = "Usage", 
            value = f"{PREFIX}inventory [mention/id] [group/idol/rarity]", 
            inline = False
            )
            em.set_author(name= bot.user.name, icon_url = bot.user.avatar_url)
            await ctx.send(embed = em)

        elif arg == "burn":
            em = discord.Embed(
            title = '**Burn Help**',
            color = 0x1ad39f
            )
            em.add_field(
            name = "Aliases", 
            value = "b", 
            inline = False
            )
            em.add_field(
            name = "Description", 
            value = "Burns the card", 
            inline = False
            )
            em.add_field(
            name = "Usage", 
            value = f"{PREFIX}burn [cards codes]", 
            inline = False
            )
            em.set_author(name= bot.user.name, icon_url = bot.user.avatar_url)
            await ctx.send(embed = em)

        elif arg == "gift":
            em = discord.Embed(
            title = '**Gift Help**',
            color = 0x1ad39f
            )
            em.add_field(
            name = "Aliases", 
            value = "None", 
            inline = False
            )
            em.add_field(
            name = "Description", 
            value = "Gift cards to other users", 
            inline = False
            )
            em.add_field(
            name = "Usage", 
            value = f"{PREFIX}gift [mention/id] [cards codes]", 
            inline = False
            )
            em.set_author(name= bot.user.name, icon_url = bot.user.avatar_url)
            await ctx.send(embed = em)
        
        elif arg == "view":
            em = discord.Embed(
            title = '**Drop Help**',
            color = 0x1ad39f
            )
            em.add_field(
            name = "Aliases", 
            value = "v / vw", 
            inline = False
            )
            em.add_field(
            name = "Description", 
            value = "View a card of your inventory", 
            inline = False
            )
            em.add_field(
            name = "Usage", 
            value = f"{PREFIX}view [card code]", 
            inline = False
            )
            em.set_author(name= bot.user.name, icon_url = bot.user.avatar_url)
            await ctx.send(embed = em)

        elif arg == "cooldown":
        
            em = discord.Embed(
            title = '**Cooldown Help**',
            color = 0x1ad39f
            )
            em.add_field(
            name = "Aliases", 
            value = "cd", 
            inline = False
            )
            em.add_field(
            name = "Description", 
            value = "Checks your cooldowns", 
            inline = False
            )
            em.add_field(
            name = "Usage", 
            value = f"{PREFIX}cd", 
            inline = False
            )
            em.set_author(name= bot.user.name, icon_url = bot.user.avatar_url)
            await ctx.send(embed = em)

        elif arg == "balance":
            em = discord.Embed(
            title = '**Balance Help**',
            color = 0x1ad39f
            )
            em.add_field(
            name = "Aliases", 
            value = "bal", 
            inline = False
            )
            em.add_field(
            name = "Description", 
            value = "Shows your currency", 
            inline = False
            )
            em.add_field(
            name = "Usage", 
            value = f"{PREFIX}balance", 
            inline = False
            )
            em.set_author(name= bot.user.name, icon_url = bot.user.avatar_url)
            await ctx.send(embed = em)

        elif arg == "work":
            em = discord.Embed(
            title = '**Work Help**',
            color = 0x1ad39f
            )
            em.add_field(
            name = "Aliases", 
            value = "None", 
            inline = False
            )
            em.add_field(
            name = "Description", 
            value = "Get paid for your work", 
            inline = False
            )
            em.add_field(
            name = "Usage", 
            value = f"{PREFIX}work", 
            inline = False
            )
            em.set_author(name= bot.user.name, icon_url = bot.user.avatar_url)
            await ctx.send(embed = em)

        elif arg == "give":
            em = discord.Embed(
            title = '**Give Help**',
            color = 0x1ad39f
            )
            em.add_field(
            name = "Aliases", 
            value = "None", 
            inline = False
            )
            em.add_field(
            name = "Description", 
            value = "Give money to other users", 
            inline = False
            )
            em.add_field(
            name = "Usage", 
            value = f"{PREFIX}give [mention/id] [amount]", 
            inline = False
            )
            em.set_author(name= bot.user.name, icon_url = bot.user.avatar_url)
            await ctx.send(embed = em)

        elif arg == "shop":
            em = discord.Embed(
            title = '**Give Help**',
            color = 0x1ad39f
            )
            em.add_field(
            name = "Aliases", 
            value = "None", 
            inline = False
            )
            em.add_field(
            name = "Description", 
            value = "Search for cards to buy", 
            inline = False
            )
            em.add_field(
            name = "Usage", 
            value = f"{PREFIX}shop [group/idol/rarity]", 
            inline = False
            )
            em.set_author(name= bot.user.name, icon_url = bot.user.avatar_url)
            await ctx.send(embed = em)

        elif arg == "buy":
            em = discord.Embed(
            title = '**Buy Help**',
            color = 0x1ad39f
            )
            em.add_field(
            name = "Aliases", 
            value = "None", 
            inline = False
            )
            em.add_field(
            name = "Description", 
            value = "Buy a card from the shop", 
            inline = False
            )
            em.add_field(
            name = "Usage", 
            value = f"{PREFIX}buy [card code] [price]", 
            inline = False
            )
            em.set_author(name= bot.user.name, icon_url = bot.user.avatar_url)
            await ctx.send(embed = em)

        elif arg == "sell":
            em = discord.Embed(
            title = '**Sell Help**',
            color = 0x1ad39f
            )
            em.add_field(
            name = "Aliases", 
            value = "None", 
            inline = False
            )
            em.add_field(
            name = "Description", 
            value = "Sell a card on the shop", 
            inline = False
            )
            em.add_field(
            name = "Usage", 
            value = f"{PREFIX}sell [card code] [price]", 
            inline = False
            )
            em.set_author(name= bot.user.name, icon_url = bot.user.avatar_url)
            await ctx.send(embed = em)
        
        elif arg == "Sales":
            em = discord.Embed(
            title = '**Sales Help**',
            color = 0x1ad39f
            )
            em.add_field(
            name = "Aliases", 
            value = "None", 
            inline = False
            )
            em.add_field(
            name = "Description", 
            value = "Shows the code of the cards your buying or selling", 
            inline = False
            )
            em.add_field(
            name = "Usage", 
            value = f"{PREFIX}sales", 
            inline = False
            )
            em.set_author(name= bot.user.name, icon_url = bot.user.avatar_url)
            await ctx.send(embed = em)
        
        elif arg == "withdraw":
            em = discord.Embed(
            title = '**Withdraw Help**',
            color = 0x1ad39f
            )
            em.add_field(
            name = "Aliases", 
            value = "wd", 
            inline = False
            )
            em.add_field(
            name = "Description", 
            value = "Witdraw a card from the shop", 
            inline = False
            )
            em.add_field(
            name = "Usage", 
            value = f"{PREFIX}withdraw [card code]", 
            inline = False
            )
            em.set_author(name= bot.user.name, icon_url = bot.user.avatar_url)
            await ctx.send(embed = em)

        elif arg == "wishlist":
            em = discord.Embed(
            title = '**Wishlist Help**',
            color = 0x1ad39f
            )
            em.add_field(
            name = "Aliases", 
            value = "wl", 
            inline = False
            )
            em.add_field(
            name = "Description", 
            value = "Shows your wishlist or of the other users", 
            inline = False
            )
            em.add_field(
            name = "Usage", 
            value = f"{PREFIX}wishlist [mention/id]", 
            inline = False
            )
            em.set_author(name= bot.user.name, icon_url = bot.user.avatar_url)
            await ctx.send(embed = em)

        elif arg == "wishlist add":
            em = discord.Embed(
            title = '**Wishlist add Help**',
            color = 0x1ad39f
            )
            em.add_field(
            name = "Aliases", 
            value = "wl add / wa", 
            inline = False
            )
            em.add_field(
            name = "Description", 
            value = "Adds a card to your wishlist", 
            inline = False
            )
            em.add_field(
            name = "Usage", 
            value = f"{PREFIX}wishlistadd [card code]", 
            inline = False
            )
            em.set_author(name= bot.user.name, icon_url = bot.user.avatar_url)
            await ctx.send(embed = em)

        elif arg == "wishlist remove":
            em = discord.Embed(
            title = '**Wishlist remove Help**',
            color = 0x1ad39f
            )
            em.add_field(
            name = "Aliases", 
            value = "wl remove / wr ", 
            inline = False
            )
            em.add_field(
            name = "Description", 
            value = "Removes a card from your wishlist", 
            inline = False
            )
            em.add_field(
            name = "Usage", 
            value = f"{PREFIX}wishlist remove [card code]", 
            inline = False
            )
            em.set_author(name= bot.user.name, icon_url = bot.user.avatar_url)
            await ctx.send(embed = em)

        elif arg == "prefix":
            em = discord.Embed(
            title = '**Prefix Help**',
            color = 0x1ad39f
            )
            em.add_field(
            name = "Aliases", 
            value = "None", 
            inline = False
            )
            em.add_field(
            name = "Description", 
            value = "Sets prefix for the server", 
            inline = False
            )
            em.add_field(
            name = "Usage", 
            value = f"{PREFIX}prefix [prefix]", 
            inline = False
            )
            em.set_author(name= bot.user.name, icon_url = bot.user.avatar_url)
            await ctx.send(embed = em)

        elif arg == "support":
            em = discord.Embed(
            title = '**Support Help**',
            color = 0x1ad39f
            )
            em.add_field(
            name = "Aliases", 
            value = "sup", 
            inline = False
            )
            em.add_field(
            name = "Description", 
            value = "Sends the link to the Hangyul Support Server", 
            inline = False
            )
            em.add_field(
            name = "Usage", 
            value = f"{PREFIX}support", 
            inline = False
            )
            em.set_author(name= bot.user.name, icon_url = bot.user.avatar_url)
            await ctx.send(embed = em)

        elif arg == "remind":
            em = discord.Embed(
            title = '**Reminder Help**',
            color = 0x1ad39f
            )
            em.add_field(
            name = "Aliases", 
            value = "r", 
            inline = False
            )
            em.add_field(
            name = "Description", 
            value = "Sets a reminder", 
            inline = False
            )
            em.add_field(
            name = "Usage", 
            value = f"{PREFIX}remind [duration] [text]", 
            inline = False
            )
            em.set_author(name= bot.user.name, icon_url = bot.user.avatar_url)
            em.set_footer(text = f"example: {PREFIX}remind 1h30min work")
            await ctx.send(embed = em)

        elif arg == "vote":
            em = discord.Embed(
            title = '**Vote Help**',
            color = 0x1ad39f
            )
            em.add_field(
            name = "Aliases", 
            value = "None", 
            inline = False
            )
            em.add_field(
            name = "Description", 
            value = "Shows a vote link", 
            inline = False
            )
            em.add_field(
            name = "Usage", 
            value = f"{PREFIX}vote", 
            inline = False
            )
            em.set_author(name= bot.user.name, icon_url = bot.user.avatar_url)
            await ctx.send(embed = em)

#-----------------------------profile--------------------------------------------------------

@bot.command(aliases=["p"])
async def profile(ctx, user:discord.Member=None):
    user = user or ctx.author
    balance = UserAccount(user.id)
    emoji = EMOJIS["coin"]
    biography = UserBiography(user.id)
    
    em = discord.Embed(title = f"{user.name}'s Profile")
    em.add_field(name = f"bio : `{biography.get_bio ()}`" , value = f"👤 User: {user.mention} \n \
        🗃️ Cards: \n 💰 Balance: {balance.get_balance()} {emoji} \n 💙 Favorite:")
    em.set_author(name = ctx.author.name, icon_url=ctx.author.avatar_url)
    await ctx.send(embed = em)

@bot.command(aliases=["bio"])
async def biography(ctx, message=None):
    if message == None:
        message = " "
    bio = UserBiography(ctx.author.id)
    em = discord.Embed(description = "Your Bio was successfully updated.", color=0x1ad39f)
    em.set_author(name = f"{ctx.author.name}'s Bio", icon_url=ctx.author.avatar_url)
    await ctx.send(embed = em)
    bio.add_bio(message)

@bot.command(aliases=["fav", "f"])
async def favorite(ctx, card_id=None):
    if card_id == None:
        return await ctx.send("You need to supply the card ID !")
    card = get_card(card_id)
    if card is None:
        return await ctx.send("That card doesn't exist !")
    user = ctx.author
    inventory = UserInventory(user.id)
    if not inventory.has_card(card_id):
        return await ctx.send("You don't have that card !")
    em = discord.Embed(description = f"You successfully add {format_name(card['member'])} as your favorite", color = 0x1ad39f)
    em.set_author(name = f"{ctx.author.name} is setting a favorite card", icon_url = ctx.author.avatar_url)
    await ctx.send(embed = em)
    favorite.add_card(card_id)

#-----------------------------balance--------------------------------------------------------

@bot.command(aliases=["bal"])
async def balance(ctx):
    account = UserAccount(ctx.author.id)
    emojis = EMOJIS['coin']
    em = discord.Embed(description = f'**{ctx.author.mention} \
        has {account.get_balance()} {emojis}**', color=0x1ad39f)

    em.set_author(name = ctx.author.name, icon_url=ctx.author.avatar_url)
    em.set_footer(text = 'You can earn coins by working')
    await ctx.send(embed = em)

#----------------------------work-------------------------------------------------------

@bot.command(name='work', aliases = ["w"])
@commands.cooldown(rate=1, per=1*HOUR, type=BucketType.user)
async def work(ctx):
    account = UserAccount(ctx.author.id)
    earnings = random.randrange(101)

    em = discord.Embed(
        title = f"You worked hard and got {earnings} {EMOJIS['coin']}!!",
        color=0x1ad39f
    )
    await ctx.send(embed = em)

    account.add_balance(earnings)

#----------------------------daily------------------------------------------------------

def get_random_card():
    card_id = random.choice(list(GROUP_DATA["pictures"].keys()))
    return card_id, get_card(card_id)

@bot.command()
@commands.cooldown(rate=1, per=24*HOUR, type=BucketType.user)
async def daily(ctx):
    user = ctx.author
    account = UserAccount(user.id)
    inventory = UserInventory(user.id)
    card_id, card = get_random_card()
    daily_coins = random.randrange(101)

    em = discord.Embed(
        title = f"{ctx.author.name} here are your daily cards !\n\
        You also get {daily_coins} coins!",
        color = 0x1ad39f
    )
    em.set_image(url = card['url'])
    await ctx.send(embed = em)
    
    inventory.add_card(card_id)
    account.add_balance(daily_coins)


#----------------------------inventory---------------------------------------------------------

@bot.command(aliases=["inventory"])
async def inv(ctx, user:discord.Member=None):
    user = user or ctx.author
    inventory = UserInventory(user.id)

    names = [
        format_name(card['member']) + "\n" + card['code'] + '\n' + card['rarity'] + '\n'
        for (_, card) in inventory.list_cards()
    ]
    names = sorted(names)
    if len(names) > 0:
        names = ''.join(names)
    else:
        names = 'Empty'

    em = discord.Embed(
        color = 0x1ad39f
    )
    em.set_author(
        name= f"{ctx.author}'s request ",
        icon_url = ctx.author.avatar_url
    )
    em.add_field(name = f"{user.name}'s inventory", value = names, inline=False)
    await ctx.send(embed = em)

def format_name(id):
    parts = id.split(':')
    name = parts[1]
    group = parts[0]
    return "**" + group + "**" + ' ' + name

#----------------------------drop---------------------------------------------------------

@bot.command(aliases=["d"])
@commands.cooldown(rate=1, per=10*MINUTE, type=BucketType.user)
async def drop(ctx):
    user = ctx.author
    inventory = UserInventory(user.id)
    card_id, card = get_random_card()

    em = discord.Embed(
        title = f"{ctx.author.name}, you got a new card !",
        color = 0x1ad39f
    )
    em.set_image(url=card["url"])
    await ctx.send(embed = em)
    
    inventory.add_card(card_id)

#-----------------------------burn--------------------------------------------------------

@bot.command(aliases=["bn", "b"])
async def burn(ctx, card_id=None):
    if card_id == None:
        return await ctx.send("You need to supply the card ID !")
    card = get_card(card_id)
    if card is None:
        return await ctx.send("That card doesn't exist !")
    user = ctx.author
    inventory = UserInventory(user.id)
    if not inventory.has_card(card_id):
        return await ctx.send("You don't have that card !")
    em = discord.Embed(description = f"You successfully burn {format_name(card['member'])}", color = 0x1ad39f)
    em.set_author(name = f"{ctx.author.name} is burning a card", icon_url = ctx.author.avatar_url)
    await ctx.send(embed = em)
    inventory.remove_card(card_id)

#----------------------------view-------------------------------------------------------

@bot.command(aliases = ["vw", "v"])
async def view(ctx, card_id=None):
  if card_id == None:
    return await ctx.send("You need to supply the card ID!")
  card = get_card(card_id)
  if card is None:
    return await ctx.send("That card doesn't exist!")
  user = ctx.author
  inventory = UserInventory(user.id)
  if not inventory.has_card(card_id):
     return await ctx.send("You don't have that card!")
  em = discord.Embed(description = f"{format_name(card['member'])}" +
    "\n" + f"`{card_id}`", color = 0x1ad39f)
  em.set_image(url = card['url'])
  em.set_author(name = f"{ctx.author.name} is viewing a card", icon_url = ctx.author.avatar_url)
  await ctx.send(embed = em)

#----------------------------gift/give-------------------------------------------------------

@bot.command()
async def gift(ctx, member:discord.Member=None, card_id=None):
    
    if member == None:
        return await ctx.send("You need to mention someone!")   
    if card_id == None:
        return await ctx.send("You need to supply card ID!")
    card = get_card(card_id)
    if card is None:
        return await ctx.send("That card doesn't exist !")
    user = ctx.author
    inventory_send = UserInventory(user.id)
    inventory_receive = UserInventory(member.id)
    if not inventory_send.has_card(card_id):
        return await ctx.send("You don't have that card !")
    em = discord.Embed(description = f"You successfully gift {format_name(card['member'])}", color = 0x1ad39f)
    em.set_author(name = f"{ctx.author.name} is gifting a card", icon_url = ctx.author.avatar_url)
    await ctx.send(embed = em)
    inventory_send.remove_card(card_id)
    inventory_receive.add_card(card_id)
@gift.error
async def gift_error(ctx, error):
    if isinstance(error, commands.MemberNotFound):
        await ctx.send("This member doesn't exist !")

@bot.command()
async def give(ctx, member:discord.Member=None, amount:int=None):
    emojis = EMOJIS["coin"]
    
    if member == None:
        return await ctx.send("You need to mention someone!")   
    if amount == None:
        return await ctx.send("You need to supply an amount!")
    user = ctx.author
    bank_send = UserAccount(user.id)
    bank_receive = UserAccount(member.id)
    if amount > bank_send.get_balance():
        return await ctx.send("You don't have enough !")
    em = discord.Embed(description = f"You successfully give {amount}{emojis}", color = 0x1ad39f)
    em.set_author(name = f"{ctx.author.name} is giving money", icon_url = ctx.author.avatar_url)
    await ctx.send(embed = em)
    bank_send.remove_balance(amount)
    bank_receive.add_balance(amount)
@gift.error
async def gift_error(ctx, error):
    if isinstance(error, commands.MemberNotFound):
        await ctx.send("This member doesn't exist !")

#----------------------------cooldown-------------------------------------------------------

def get_cooldown_readable(ctx, command):
    seconds = bot.get_command(command).get_cooldown_retry_after(ctx)
    return cooldown_readable(seconds)

@work.error
@drop.error
async def cooldown_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        return
    timeleft = round(error.retry_after) // MINUTE
    em = discord.Embed(
        description=f"Try again in {timeleft}m.",
        color= 0x1ad39f
    )
    await ctx.send(embed=em, delete_after=5)

@bot.command(aliases = ["cd"]) 
async def cooldown(ctx):
    em = discord.Embed(
        title='Here are your cooldowns',
        color= 0x1ad39f
    )
    for command in COOLDOWN_COMMANDS:
        em.add_field(
            name = command,
            value = get_cooldown_readable(ctx, command),
            inline=False
        )
    await ctx.send(embed = em)

def cooldown_readable(seconds):
    if seconds < 1:
        return EMOJIS['check']
    return format_duration(seconds)



def format_duration(seconds):
    if not seconds:
        return "now"

    chunks = []
    for name, secs in times:
        qty = seconds // secs
        qty = int(qty)
        if qty:
            if qty > 1:
                name += "s"
            chunks.append(str(qty)+" "+name)

        seconds = seconds % secs

    return ','.join(chunks[:-1]) + ' and ' + chunks[-1] \
        if len(chunks) > 1 \
        else chunks[0]

#end of the commands abt the cards
#----------------------------embeds-------------------------------------------------------


@bot.command()
async def embed(ctx, woosung):
    embed = discord.Embed(title = "Woosung supremacy", description = "Stan Woosung for better life :3", color = 0x1ad39f, url = "https://www.youtube.com/watch?v=3YFZyOpF7tU")
    embed.set_author(name= ctx.author.name, icon_url = ctx.author.avatar_url, url = "https://www.youtube.com/watch?v=ERE_HVGaW-o")
    embed.set_thumbnail(url = "https://cdn.discordapp.com/attachments/789103333113200720/895385227571101716/Woosung_11.JPG")
    embed.add_field(name = "Usefull informations", value = "Kim Woosung born on the __25 février 1993__.\nHe is from America and his Americain's name is Sammy. \n--------------------------------- \n", inline = False)
    embed.add_field(name = "The Rose", value = "He is known to be part of a group : the Rose, a group of 4 members.\nHe is the main singer and the guitarist.\n--------------------------------- \n", inline = False)
    embed.add_field(name = "WOOSUNG", value = 'He is also an amazing soloist. He made his debut with the mini album "WOLF" and his first MV "Face".', inline = False)
    embed.set_footer(text = "He is so talented, I promise you won't be disappointed in stanning him !")
    embed.set_image(url = "https://cdn.discordapp.com/attachments/789103333113200720/895385051045433404/Woosung_1.JPG")
    await ctx.channel.send(embed = embed)

#beginning of mod commands

@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def clean(ctx, number):
    if number == 'all':
        await ctx.channel.purge()
    else:
        await ctx.channel.purge(limit=int(number) +1)

@clean.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You can't do this!")

#end of mod commands

with open("token.0", "r") as f:
    bottoken = f.read()

bot.run(bottoken)