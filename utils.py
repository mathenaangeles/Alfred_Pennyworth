import asyncio
import discord

async def get_channel_name(bot, ctx):
    await ctx.send("What is the channel name?")
    try:
        channel_name_message = await bot.wait_for(
            'message',
            timeout=60.0,
            check=lambda message: message.author == ctx.author and message.channel == ctx.channel
        )
        channel_name = channel_name_message.content
        return channel_name
    except asyncio.TimeoutError:
        await ctx.send("You took too long to respond. I am cancelling this command.")
        return
    
async def get_category_name(bot, ctx):
    await ctx.send("What is the channel category? Type `none` if this command should not be associated to a category.")
    try:
        category_message = await bot.wait_for(
            'message',
            timeout=60.0,
            check=lambda message: message.author == ctx.author and message.channel == ctx.channel
        )
        category_name = category_message.content
        return category_name
    except asyncio.TimeoutError:
        await ctx.send("You took too long to respond. I am cancelling this command.")
        return

async def get_channel(ctx, category, channel_name):
    if category:
        channel = discord.utils.get(category.channels, name=channel_name, category=category)
    else:
        channel = discord.utils.get(ctx.guild.channels, name=channel_name, category=None)
    if not channel:
        await ctx.send(f"Channel `{channel_name}` does not exist in the specified category.")
        return
    return channel

async def get_members(bot, ctx):
    await ctx.send("Please mention the member/s to be included.")
    try:
        members_message = await bot.wait_for(
            "message", 
            timeout=30.0, 
            check=lambda m: m.author == ctx.author and m.channel == ctx.channel
        )
    except asyncio.TimeoutError:
        await ctx.send("You took too long to respond. I am cancelling this command.")
        return
    members = members_message.mentions
    if not members:
        await ctx.send("No valid members were found.")
        return []
    return members
