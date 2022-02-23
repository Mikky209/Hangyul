import os
import discord
import random
import json
import os
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import datetime

os.chdir("E://Kpop//Autres//Bot//Hangyul")

#------------------------------globals------------------------------------

PREFIX = "o"

GROUP_DATA = None
with open('groups.json', 'rb') as f:
        GROUP_DATA = json.load(f)

secret_token = os.getenv("TOKEN")

MINUTE = 60
HOUR = 60*MINUTE

EMOJIS = {
    'coin': '<:X1Coin:926954191279231067>',
    'check': '<:check:927618520039166014>',
    'heart': '🤍'
}

COMMAND_CATEGORIES = [
    {
        'name': 'user',
        'icon': '👤',
        'commands': {
            'profile': { 'help': 'this command does stuff' },
            'bio': {},
            'favorite': {},
        }
    },
    {
        'name': 'cards',
        'icon': '🎴',
        'commands': {
            'daily': {},
            'drop': {},
            'inventory': {},
            'burn': {},
            'gift': {},
            'view': {},
            'cooldown': {}
        }
    },
    {
        'name': 'currency',
        'icon': '💰',
        'commands': {
            'balance': {},
            'work': {},
            'give': {},
        }
    },
    {
        'name': 'shop',
        'icon': '🛒',
        'commands': {
            'shop': {},
            'buy': {},
            'sell': {},
            'sales': {},
            'withdraw': {}
        },
        'new_section': True
    },
    {
        'name': 'settings',
        'icon': '⚙️',
        'commands': {
            'help': {  
                'help': f'This command shows the list of available commands. \
                Use `{PREFIX}help command` for help with a certain command.'
            },
            'prefix': {},
            'support': {},
            'reminder': {},
            'vote': {}
        }
    }
]

# it's a good idea to put a sanity check here
# and verify that all of these commands actually exist
# otherwise you won't know what broke when you change stuff
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

# a factory for making UserAccount objects
class UserAccount:
    # what happens when you make a new UserAccount object
    # `self` gets pre-filled with the object
    # the result of arguments are given normally
    def __init__(self, id):
        self.id = str(id)
        self.wallet = None
        self.load()

    # a method you can call like account.load()
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

        # the cards are used like:
        #     do i have this card? yes / no
        # not
        #     what position do i have this card at? 5
        #
        # so we convert the card list into a set
        # which is a better kind of collection for this use case
        # removing from a set is also quicker
        # and we dont have to worry about duplicate cards

        if user is None:
            self.cards = set()
        else:
            self.cards = set(user.get('cards', []))

    def save(self):
        users = get_inv_data()
        # self.cards is a set so we convert back to a list
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
            # `yield` says what appears as `stuff` when you do
            #   for stuff in inventory.list_cards():
            #      ...

            # items with commas in between is called a tuple
            #     (card_id, get_card(card_id))
            # which is like a list intended for items of different types
            # but a tuple can't be changed like a list can
            # it can have parentheses around it
            # in case you didn't know

            # it makes it easy to do stuff like
            #     a, b = b, a
            # which switches the values of two variables, and
            #     for item_number, item in enumerate(items):
            #         ...
            # which takes the tuple from enumerate 
            # so you get (0, 'item 1'), then (1, 'item 2')
            # and immediately unpacks it into the two variables
            
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
async def help(ctx, arg):
    if arg == None:
        em = discord.Embed(
            title = f'{BOT_NAME} Help Commands',
            color = 0x1ad39f
        )
        em.set_author(name= bot.user.name, icon_url = bot.user.avatar_url)
        for category in COMMAND_CATEGORIES:
        # this allows to set an empty icon by default if it does not exist
        # basically it says:
        #category['icon'] or '' if it doesn't exist
            name = category['name'].capitalize()
            icon = category.get('icon', '')
            separator = '\n' if category.get('new_section', False) else ''
            command_list = category['commands'].keys()
            command_list = [f'`{command}`' for command in command_list]
            em.add_field(
                name = f'{separator}{name}{icon}', 
                value = ' '.join(command_list), 
                inline = False
            )
        em.set_footer(text=f'Use {PREFIX}help [category] for more details')
        await ctx.send(embed = em)
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
        


#-----------------------------balance--------------------------------------------------------

@bot.command()
async def balance(ctx):
    await command_balance(ctx)

@bot.command()
async def bal(ctx):
    await command_balance(ctx)

@bot.command()
async def command_balance(ctx):
    account = UserAccount(ctx.author.id)
    emojis = EMOJIS['coin']
    em = discord.Embed(description = f'**{ctx.author.mention} \
        has {account.get_balance()} {emojis}**', color=0x1ad39f)

    em.set_author(name = ctx.author.name, icon_url=ctx.author.avatar_url)
    em.set_footer(text = 'You can earn coins by working')
    await ctx.send(embed = em)

#----------------------------work-------------------------------------------------------

@bot.command(name='work')
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
        title = f"{ctx.author.name} Here are your daily cards !\n\
        You also get {daily_coins} coins!",
        color = 0x1ad39f
    )
    em.set_image(url = card['url'])
    await ctx.send(embed = em)
    
    inventory.add_card(card_id)
    account.add_balance(daily_coins)


#----------------------------inventory---------------------------------------------------------

@bot.command()
async def inv(ctx):
    user = ctx.author
    inventory = UserInventory(user.id)

    names = [
        format_name(card['member']) + "\n" + card['code'] + ' ' + card['rarity'] + '\n'
        for (_, card) in inventory.list_cards()
    ]
    if len(names) > 0:
        names = ''.join(names)
    else:
        names = 'Empty'

    em = discord.Embed(
        title = f"{user.name}'s inventory",
        color = 0x1ad39f
    )
    em.set_author(
        name= f"{user.name}'s inventory",
        icon_url = user.avatar_url
    )
    em.add_field(name = 'Inventory', value = names, inline=False)
    await ctx.send(embed = em)

def format_name(id):
    parts = id.split(':')
    name = parts[1]
    group = parts[0]
    return "**" + group + "**" + ' ' + name    

#----------------------------drop---------------------------------------------------------

@bot.command()
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

#----------------------------view-------------------------------------------------------

@bot.command()
async def view(ctx, card_id):
  if not card_id:
    return await ctx.send("You need to supply the card ID!")
  card = get_card(card_id)
  if card is None:
    return await ctx.send("That card doesn't exist!")
  user = ctx.author
  inventory = UserInventory(user.id)
  if not inventory.has_card(card_id):
     return await ctx.send("You don't have that card!")
  em = discord.Embed(description = f"{format_name(card['member'])}" +
    "\n" + f"{card_id}" + "\n" + f"{card['rarity']}", color = 0x1ad39f)
  em.set_image(url = card['url'])
  em.set_author(name = f"{ctx.author.name} is viewing a card", icon_url = ctx.author.avatar_url)
  await ctx.send(embed = em)

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

@bot.command()
async def cd(ctx):
    await command_cooldown(ctx)

@bot.command()
async def cooldown(ctx):
    await command_cooldown(ctx)

@bot.command() 
async def command_cooldown(ctx):
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

def cooldown_readable(duration):
    if duration < 1:
        return EMOJIS['check']
    return duration_readable(duration)

def duration_readable(duration):
   durations = []
   duration = int(duration)
   for (unit, magnitude) in [('h', HOUR), ('m', MINUTE), ('s', 1)]:
        if duration < magnitude:
            count = duration // magnitude
            durations.append(f'{count}{unit}')
            duration -= count * unit
   if len(durations) == 0:
       return 'just now'
   return ', '.join(durations)

#end of the commands abt the cards
#----------------------------embeds-------------------------------------------------------

# im not touching this - entity

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