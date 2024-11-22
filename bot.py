import os
import discord
import asyncio
import random
from discord.ext import commands

from dotenv import load_dotenv
from utils import *

load_dotenv()
TOKEN = os.getenv('TOKEN')

bot = commands.Bot(intents=discord.Intents().all(), command_prefix="Alfred, ")

@bot.event
async def on_ready():
    print(f'{bot.user} is connected to the following guilds:\n')
    for guild in bot.guilds:
        print(f'- {guild} (ID: {guild.id})\n')

@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hello, {member.name}. Welcome to the server.'
    )

@bot.event
async def on_command_error(ctx, error):
    print(f"ERROR: {error}")
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send(f'I encountered an error. Don\'t worry, {ctx.author.mention}. Things always get worse before they get better.')
    elif isinstance(error, commands.errors.CommandNotFound):
        await ctx.send(f'I\'m sorry, {ctx.author.mention}. I don\'t recognize that command. Please check your spelling or use a valid command. You can run `Alfred, help` to see a list of valid commands.')


@bot.command(name="set_timer", help='Sets a timer for the specified number of minutes')
async def set_timer(ctx, minutes: float):
    timer = minutes
    seconds = minutes * 60
    if minutes == 1:
        message = await ctx.send(f'{ctx.author.mention} set a timer for {timer} minute.')
    else:
        message = await ctx.send(f'{ctx.author.mention} set a timer for {timer} minutes.')
    while seconds>0:
        seconds -= 1
        if seconds%60 == 0:
            minutes = seconds // 60
            if minutes>1:
                await message.edit(content=f'Timer: {seconds//60} minutes left')
            else: 
                await message.edit(content=f'Timer: {seconds//60} minute left')
        await asyncio.sleep(1)
    await message.edit(content=f'Timer: 0 minutes left')
    await ctx.send(content=f'The timer {ctx.author.mention} set for {timer} minutes has ended.')


@bot.command(name='eight_ball', help='Simulates a Magic 8 Ball')
async def eight_ball(ctx):
    magic_eight_ball_answers = [
        'It is certain.',
        'Don\'t count on it.',
        'As I see it, yes.',
        'You can rely on it.',
        'Ask me again later.',
        'My sources say no.',
        'The outlook is not so good.',
        'Very doubtful...',
        'Concentrate and ask again.',
        'The signs point to yes.',
        'It is likely.',
    ]
    response = random.choice(magic_eight_ball_answers)
    await ctx.send(response)
       
@bot.command(name='roll', help='Rolls a 6-sided dice')
async def roll(ctx):
    await ctx.send(f'{ctx.author.mention} rolls a {random.randint(1,6)}.')

@bot.command(name='create_channel', help="Creates a new voice or text channel in a given category, if any")
@commands.check(lambda ctx: ctx.author == ctx.guild.owner or ctx.author.guild_permissions.administrator)
async def create_channel(ctx):
    guild = ctx.guild
    channel_name = await get_channel_name(bot, ctx)
    category_name = await get_category_name(bot, ctx)
    if category_name.lower() != "none":
        category = discord.utils.get(guild.categories, name=category_name)
        if not category:
            await ctx.send(f"Category `{category_name}` could not be found. Creating a new category...")
            category = await guild.create_category(category_name)
    
    existing_channel = discord.utils.get(guild.channels, name=channel_name, category=category)
    if existing_channel:
        await ctx.send(f"A channel named `{channel_name}` already exists in `{category}`.")
        return
    await ctx.send("Type `text` if this should be a text channel. Type `voice` if this should be a voice channel.")
    try:
        channel_type_msg = await bot.wait_for(
            'message',
            timeout=60.0,
            check=lambda message: message.author == ctx.author and message.channel == ctx.channel
        )
        channel_type = channel_type_msg.content.lower()
    except asyncio.TimeoutError:
        await ctx.send("You took too long to respond. I am cancelling the channel creation.")
        return
    if channel_type == "text":
        await guild.create_text_channel(channel_name, category=category)
    elif channel_type == "voice":
        await guild.create_voice_channel(channel_name, category=category)
    else:
        await ctx.send(f'Invalid channel type `{channel_type}`. Please choose either "text" or "voice".')
        return
    await ctx.send(f"The `{channel_type}` channel `{channel_name}` has been created successfully.")

@bot.command(name='delete_channel', help="Deletes an existing channel in a given category, if any")
@commands.check(lambda ctx: ctx.author == ctx.guild.owner or ctx.author.guild_permissions.administrator)
async def delete_channel(ctx):
    guild = ctx.guild
    channel_name = await get_channel_name(bot, ctx)
    category_name = await get_category_name(bot, ctx)
    category = None
    if category_name.lower() != "none":
        category = discord.utils.get(guild.categories, name=category_name)
        if not category:
            await ctx.send(f"Category `{category_name}` does not exist.")
            return
    channel = await get_channel(ctx, category, channel_name)
    await channel.delete()
    await ctx.send(f"The channel `{channel_name}` has been successfully deleted.")


@bot.command(name='create_invite', help="Creates an invite link to the server that is valid for 1 user")
@commands.check(lambda ctx: ctx.author.guild_permissions.create_instant_invite)
async def create_invite(ctx):
    if not ctx.guild.me.guild_permissions.create_instant_invite:
        await ctx.send("I don't have the `Create Instant Invite` permission. Please enable it for me to proceed.")
        return
    try:
        invite = await ctx.channel.create_invite(max_uses=1, unique=True)
        await ctx.send(f"Here is your invite link - valid for 1 user: {invite}")
    except Exception:
        await ctx.send(f"I could not create an invite link")

@bot.command(name='add_members', help="Adds member/s to a specific channel")
@commands.check(lambda ctx: ctx.author == ctx.guild.owner or ctx.author.guild_permissions.manage_channels)
async def add_members(ctx):
    if not ctx.guild.me.guild_permissions.manage_roles:
        await ctx.send("I don't have the `Manage Permissions` permission. Please enable it for me to proceed.")
        return
    category_name = await get_category_name(bot, ctx)
    if category_name.lower() != 'none':
        category = discord.utils.get(ctx.guild.categories, name=category_name)
        if not category:
            await ctx.send(f"Category `{category_name}` does not exist.")
            return
    channel_name = await get_channel_name(bot, ctx)
    channel = await get_channel(ctx, category, channel_name)
    members = await get_members(bot, ctx)
    for member in members:
        try:
            overwrite = channel.overwrites_for(member)
            overwrite.view_channel = True
            await channel.set_permissions(member, overwrite=overwrite)
            await ctx.send(f"Member {member.mention} has been added to `{channel_name}`.")
        except Exception:
            await ctx.send(f"An error occurred while adding {member.mention} to `{channel_name}`.")

@bot.command(name='remove_members', help="Removes members/s from a specific channel")
@commands.check(lambda ctx: ctx.author == ctx.guild.owner or ctx.author.guild_permissions.manage_channels)
async def remove_members(ctx):
    if not ctx.guild.me.guild_permissions.manage_roles:
        await ctx.send("I don't have the `Manage Permissions` permission. Please enable it for me to proceed.")
        return
    category_name = await get_category_name(bot, ctx)
    if category_name.lower() != 'none':
        category = discord.utils.get(ctx.guild.categories, name=category_name)
        if not category:
            await ctx.send(f"Category `{category_name}` does not exist.")
            return
    channel_name = await get_channel_name(bot, ctx)
    channel = await get_channel(ctx, category, channel_name)
    members = await get_members(bot, ctx)
    for member in members:
        try:
            overwrite = channel.overwrites_for(member)
            overwrite.view_channel = False 
            await channel.set_permissions(member, overwrite=overwrite)
            await ctx.send(f"Member {member.mention} has been removed from `{channel_name}`.")
        except Exception:
            await ctx.send(f"An error occurred while removing {member.mention} from `{channel_name}`.")

bot.run(TOKEN)