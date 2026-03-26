import discord
from discord.ext import commands
from discord import ui
from datetime import timedelta
from utils.database import fetch_one

class ModPanelView(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=60)
        self.bot = bot
        self.selected_user = None

    async def send_log(self, guild, embed):
        config = await fetch_one("SELECT log_channel_id FROM server_config WHERE guild_id = ?", (guild.id,))
        if config and config[0]:
            channel = guild.get_channel(config[0])
            if channel: await channel.send(embed=embed)

    @ui.select(cls=ui.UserSelect, placeholder="Selecione o usuário para moderar...")
    async def select_user(self, interaction: discord.Interaction, select: ui.UserSelect):
        self.selected_user = select.values[0]
        await interaction.response.send_message(f"👤 Usuário **{self.selected_user.name}** selecionado. Escolha a ação abaixo:", ephemeral=True)

    @ui.button(label="Expulsar (Kick)", style=discord.ButtonStyle.orange, emoji="👢")
    async def kick_btn(self, interaction: discord.Interaction, button: ui.Button):
        if not self.selected_user: return await interaction.response.send_message("❌ Selecione um usuário primeiro!", ephemeral=True)
        await self.selected_user.kick(reason="Pelo Painel de Moderação")
        embed = discord.Embed(title="👢 Membro Expulso", color=discord.Color.orange())
        embed.add_field(name="Membro", value=self.selected_user.mention)
        embed.add_field(name="Moderador", value=interaction.user.mention)
        await self.send_log(interaction.guild, embed)
        await interaction.response.send_message(f"✅ {self.selected_user.name} expulso.", ephemeral=True)

    @ui.button(label="Banir (Ban)", style=discord.ButtonStyle.red, emoji="🔨")
    async def ban_btn(self, interaction: discord.Interaction, button: ui.Button):
        if not self.selected_user: return await interaction.response.send_message("❌ Selecione um usuário primeiro!", ephemeral=True)
        await self.selected_user.ban(reason="Pelo Painel de Moderação")
        embed = discord.Embed(title="🔨 Membro Banido", color=discord.Color.red())
        embed.add_field(name="Membro", value=self.selected_user.mention)
        embed.add_field(name="Moderador", value=interaction.user.mention)
        await self.send_log(interaction.guild, embed)
        await interaction.response.send_message(f"✅ {self.selected_user.name} banido.", ephemeral=True)

    @ui.button(label="Silenciar (10m)", style=discord.ButtonStyle.secondary, emoji="🔇")
    async def mute_btn(self, interaction: discord.Interaction, button: ui.Button):
        if not self.selected_user: return await interaction.response.send_message("❌ Selecione um usuário primeiro!", ephemeral=True)
        await self.selected_user.timeout(timedelta(minutes=10), reason="Pelo Painel de Moderação")
        embed = discord.Embed(title="🔇 Membro Silenciado", color=discord.Color.yellow())
        embed.add_field(name="Membro", value=self.selected_user.mention)
        embed.add_field(name="Duração", value="10 minutos")
        await self.send_log(interaction.guild, embed)
        await interaction.response.send_message(f"✅ {self.selected_user.name} silenciado.", ephemeral=True)

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="mod", description="Abre o painel de moderação rápida.")
    @commands.has_permissions(kick_members=True)
    async def mod_panel(self, ctx):
        embed = discord.Embed(
            title="🔨 Painel de Moderação",
            description="Use o menu abaixo para selecionar um membro e aplique a punição necessária com um clique.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, view=ModPanelView(self.bot), ephemeral=True)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot: return
        config = await fetch_one("SELECT log_channel_id FROM server_config WHERE guild_id = ?", (message.guild.id,))
        if config and config[0]:
            log_chan = message.guild.get_channel(config[0])
            embed = discord.Embed(title="🗑️ Mensagem Deletada", color=discord.Color.light_grey())
            embed.add_field(name="Autor", value=message.author.mention)
            embed.add_field(name="Canal", value=message.channel.mention)
            embed.add_field(name="Conteúdo", value=message.content or "Sem texto", inline=False)
            await log_chan.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
