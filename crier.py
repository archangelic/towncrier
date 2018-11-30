import re
import random

import discord
from discord.ext import commands
from mastodon import Mastodon

bot = commands.Bot(command_prefix='!')
masto = Mastodon(
    client_id='towncrier_client.secret',
    access_token='towncrier_usercred.secret',
    api_base_url='https://tiny.tilde.website'
)
dicepattern = re.compile('(?P<amount>\d+)?d(?P<sides>\d+) ?(?P<posneg>[\+\-])? ?(?P<modifier>\d+)?')
dice = [4, 6, 8, 10, 12, 20, 100]

def get_emojos():
    return {i.name: i for i in bot.get_all_emojis()}

@bot.event
async def on_ready():
    print(bot.user.name)
    print([i.name for i in bot.get_all_emojis()])

@bot.command()
async def roll(*, message):
    print(dir(message))
    matches = dicepattern.match(message)
    emojos = get_emojos()
    if matches:
        amount = matches.group('amount')
        if amount:
            amount = int(amount)
        else:
            amount = 1
        sides = int(matches.group('sides'))
        if sides not in dice:
            await bot.say("Please use one of these dice: d4, d6, d8, d10, d12, d20, d100")
            return None
        elif sides == 100 and 'd10' in emojos:
            d10 = '<d10:{}>'.format(emojos['d10'].id)
            emoji = f'{d10}{d10}'
        elif 'd{}'.format(sides) in emojos:
            emoji = '<d{}:{}>'.format(sides, emojos[f'd{sides}'].id)
        else:
            emoji = ''
        emoji = '' # undo all my work
        modifier = matches.group('modifier')
        if sides > 100 or amount > 50:
            await bot.say("That number is too high!")
            return None
        posneg = matches.group('posneg')
        results = [random.randint(1, sides) for i in range(amount)]
        output = ' + '.join([emoji + str(i) for i in results]).strip(' +')
        output = '({})'.format(output)
        rollsum = sum(results)
        if posneg == '+':
            output += ' + {}'.format(modifier)
            rollsum += int(modifier)
        elif posneg == '-':
            output += ' - {}'.format(modifier)
            rollsum -= int(modifier)
        await bot.say('{} = {}'.format(output, rollsum))

@bot.command(pass_context=True)
async def announce(ctx, message):
    if ctx.message.server:
        admin = discord.utils.get(ctx.message.server.roles, name='admin')
    else:
        await bot.say('oops!')
    if admin in ctx.message.author.roles:
        post = masto.toot(message)
        em = discord.Embed(
            title=post['account']['display_name'],
            description=message,
            color=0xE0B0FF,
            url=post['url']
        )
        em.set_thumbnail(url=post['account']['avatar_static'])
        await bot.send_message(ctx.message.channel, embed=em)
    else:
        await bot.say("I can't let you do that")

@bot.command(pass_context=True)
async def sleep(ctx):
    print(dir(ctx.bot))
    author = ctx.message.author
    user = '{}#{}'.format(author.name, author.discriminator)
    if user == 'archangelic#9773':
        await bot.logout()
    else:
        await bot.say("I can't let you do that {}".format(author.mention))

with open('discord.secret') as d:
    token = d.read().strip()
bot.run(token)

