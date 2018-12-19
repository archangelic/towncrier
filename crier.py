import discord
from discord.ext import commands
from mastodon import Mastodon

bot = commands.Bot(command_prefix='!')
masto = Mastodon(
    client_id='towncrier_client.secret',
    access_token='towncrier_usercred.secret',
    api_base_url='https://tiny.tilde.website'
)

def get_emojos():
    return {i.name: i for i in bot.get_all_emojis()}

@bot.event
async def on_ready():
    print(bot.user.name)

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

@bot.command(pass_context=True)
async def pronouns(ctx, role):
    if ctx.message.server:
        server = ctx.message.server
    else:
        return None
    pronouns = [
        'he/him',
        'she/her',
        'xey/xem',
        'they/them'
    ]
    roles = {str(i).lower(): i for i in server.roles if str(i).lower() in pronouns}
    if role.lower() in roles:
        await bot.add_roles(ctx.message.author, roles[role.lower()])
        em = discord.Embed(
            description='pronouns {} set for {}'.format(roles[role.lower()], ctx.message.author.mention),
            color=0xE0B0FF
        )
        await bot.send_message(ctx.message.channel, embed=em)

with open('discord.secret') as d:
    token = d.read().strip()
bot.run(token)

