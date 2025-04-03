import discord
import asyncio
import os
import sys
from discord.ext import commands
from discord.ui import Button, View
from music_cog import music_cog

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True
intents.members = True

# Bot setup
bot = commands.Bot(command_prefix="!", intents=intents)

#secure token
token = os.getenv("DISCORD_BOT_TOKEN") #-e DISCORD_BOT_TOKEN=your_actual_token
if not token:
    print("DISCORD_BOT_TOKEN var is missing")
    exit(1)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found. Try `!help` to see available commands.")
    else:
        print(f"Unhandled error: {error}")
        await ctx.send("⚠️ An unexpected error occurred. Check logs...")

async def main():
    async with bot:
        await bot.add_cog(music_cog(bot))
        await bot.start(token)

asyncio.run(main())
