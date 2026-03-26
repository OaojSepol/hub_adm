import discord
from discord.ext import commands
from utils.database import fetch_one

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        config = await fetch_one("SELECT welcome_channel_id FROM server_config WHERE guild_id = ?", (member.guild.id,))
        if config and config[0]:
            channel = member.guild.get_channel(config[0])
            if channel:
                embed = discord.Embed(
                    title="👋 Bem-vindo(a)!",
                    description=f"Olá {member.mention}, ficamos felizes em ter você no **{member.guild.name}**!\n\n"
                                f"📅 Membro nº **{len(member.guild.members)}**\n"
                                f"💡 Leia as regras e divirta-se!",
                    color=discord.Color.green()
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_footer(text=f"ID do usuário: {member.id}")
                await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        config = await fetch_one("SELECT goodbye_channel_id FROM server_config WHERE guild_id = ?", (member.guild.id,))
        if config and config[0]:
            channel = member.guild.get_channel(config[0])
            if channel:
                embed = discord.Embed(
                    title="💔 Até logo!",
                    description=f"**{member.name}** saiu do servidor.",
                    color=discord.Color.red()
                )
                await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
