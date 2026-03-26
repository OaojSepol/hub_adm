import discord
from discord.ext import commands
from discord import ui

class HelpSelect(ui.Select):
    def __init__(self, bot):
        self.bot = bot
        options = [
            discord.SelectOption(label="Setup", description="Configurações do servidor", emoji="⚙️"),
            discord.SelectOption(label="Tickets", description="Sistema de suporte", emoji="🎫"),
            discord.SelectOption(label="RPG", description="Gestão de mestres e mesas", emoji="⚔️"),
            discord.SelectOption(label="Moderação", description="Comandos administrativos", emoji="🔨"),
            discord.SelectOption(label="Leveling", description="Sistema de XP e Ranking", emoji="🏆"),
            discord.SelectOption(label="Voice", description="Canais de voz temporários", emoji="🔊"),
        ]
        super().__init__(placeholder="Escolha uma categoria...", options=options)

    async def callback(self, interaction: discord.Interaction):
        cog_name = self.values[0]
        cog = self.bot.get_cog(cog_name)
        
        if not cog:
            return await interaction.response.send_message("❌ Categoria não encontrada.", ephemeral=True)

        commands_list = cog.get_commands()
        help_text = ""
        for cmd in commands_list:
            help_text += f"`/{cmd.name}` - {cmd.help or 'Sem descrição'}\n"

        embed = discord.Embed(
            title=f"Categoria: {cog_name}",
            description=help_text or "Nenhum comando disponível.",
            color=discord.Color.blue()
        )
        await interaction.response.edit_message(embed=embed)

class HelpView(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=60)
        self.add_item(HelpSelect(bot))

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="📚 Central de Ajuda",
            description="Selecione uma categoria no menu abaixo para ver os comandos disponíveis.",
            color=discord.Color.blue()
        )
        if ctx.interaction:
            await ctx.interaction.response.send_message(embed=embed, view=HelpView(self.bot), ephemeral=True)
        else:
            await ctx.send(embed=embed, view=HelpView(self.bot))

async def setup(bot):
    await bot.add_cog(Help(bot))
