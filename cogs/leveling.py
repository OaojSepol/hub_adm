import discord
from discord.ext import commands, tasks
import time
import random
from datetime import datetime
from utils.database import execute, fetch_one, fetch_all

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.xp_cooldown = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild: return
        
        user_id = message.author.id
        guild_id = message.guild.id
        current_time = time.time()

        # Cooldown de 60s
        if user_id in self.xp_cooldown and current_time - self.xp_cooldown[user_id] < 60:
            return

        self.xp_cooldown[user_id] = current_time
        xp_to_add = random.randint(15, 25)

        # Atualiza XP no DB
        data = await fetch_one("SELECT xp, level FROM leveling WHERE user_id = ? AND guild_id = ?", (user_id, guild_id))
        if not data:
            await execute("INSERT INTO leveling (user_id, guild_id, xp, level) VALUES (?, ?, ?, ?)", (user_id, guild_id, xp_to_add, 0))
        else:
            new_xp = data[0] + xp_to_add
            new_level = int(new_xp ** (1/4)) # Fórmula simples de level
            
            if new_level > data[1]:
                await message.channel.send(f"🎉 Parabéns {message.author.mention}, você subiu para o nível **{new_level}**!")
                await execute("UPDATE leveling SET xp = ?, level = ? WHERE user_id = ? AND guild_id = ?", (new_xp, new_level, user_id, guild_id))
            else:
                await execute("UPDATE leveling SET xp = ? WHERE user_id = ? AND guild_id = ?", (new_xp, user_id, guild_id))

    @commands.hybrid_command(name="leaderboard")
    async def leaderboard(self, ctx):
        await ctx.defer(ephemeral=True)
        users = await fetch_all("SELECT user_id, xp, level FROM leveling WHERE guild_id = ? ORDER BY xp DESC LIMIT 10", (ctx.guild.id,))
        embed = discord.Embed(title="🏆 Ranking de XP", color=discord.Color.gold())
        
        for i, user_data in enumerate(users, 1):
            user = self.bot.get_user(user_data[0]) or await self.bot.fetch_user(user_data[0])
            embed.add_field(name=f"{i}. {user.name}", value=f"Nível {user_data[2]} | {user_data[1]} XP", inline=False)
        
        await ctx.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Leveling(bot))
