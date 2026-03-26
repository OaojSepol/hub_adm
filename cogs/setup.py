import discord
from discord.ext import commands
from discord import ui
from utils.database import execute, fetch_one, fetch_all

# --- Menus de Seleção (Canais e Cargos) ---

class LogsSelectView(ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @ui.select(cls=ui.ChannelSelect, channel_types=[discord.ChannelType.text], placeholder="Selecione o Canal de Auditoria (Logs)...")
    async def select_logs(self, interaction: discord.Interaction, select: ui.ChannelSelect):
        channel = select.values[0]
        await execute("UPDATE server_config SET log_channel_id = ? WHERE guild_id = ?", (channel.id, interaction.guild_id))
        await interaction.response.send_message(f"✅ Canal de Auditoria definido como {channel.mention}!", ephemeral=True)

    @ui.select(cls=ui.ChannelSelect, channel_types=[discord.ChannelType.text], placeholder="Selecione o Canal da Staff (Aprovações)...")
    async def select_staff(self, interaction: discord.Interaction, select: ui.ChannelSelect):
        channel = select.values[0]
        await execute("UPDATE server_config SET staff_channel_id = ? WHERE guild_id = ?", (channel.id, interaction.guild_id))
        await interaction.response.send_message(f"✅ Canal da Staff definido como {channel.mention}!", ephemeral=True)

class TicketsSelectView(ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @ui.select(cls=ui.ChannelSelect, channel_types=[discord.ChannelType.text], placeholder="Selecione o Canal do Painel de Tickets...")
    async def select_ticket_chan(self, interaction: discord.Interaction, select: ui.ChannelSelect):
        channel = select.values[0]
        await execute("UPDATE server_config SET ticket_channel_id = ? WHERE guild_id = ?", (channel.id, interaction.guild_id))
        await interaction.response.send_message(f"✅ Canal do Painel definido como {channel.mention}!", ephemeral=True)

    @ui.select(cls=ui.ChannelSelect, channel_types=[discord.ChannelType.category], placeholder="Selecione a Categoria dos Tickets...")
    async def select_ticket_cat(self, interaction: discord.Interaction, select: ui.ChannelSelect):
        category = select.values[0]
        await execute("UPDATE server_config SET ticket_category_id = ? WHERE guild_id = ?", (category.id, interaction.guild_id))
        await interaction.response.send_message(f"✅ Categoria de Tickets definida como **{category.name}**!", ephemeral=True)

class WelcomeSelectView(ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @ui.select(cls=ui.ChannelSelect, channel_types=[discord.ChannelType.text], placeholder="Selecione o Canal de Boas-vindas...")
    async def select_welcome(self, interaction: discord.Interaction, select: ui.ChannelSelect):
        channel = select.values[0]
        await execute("UPDATE server_config SET welcome_channel_id = ? WHERE guild_id = ?", (channel.id, interaction.guild_id))
        await interaction.response.send_message(f"✅ Canal de Boas-vindas definido como {channel.mention}!", ephemeral=True)

    @ui.select(cls=ui.ChannelSelect, channel_types=[discord.ChannelType.text], placeholder="Selecione o Canal de Saída...")
    async def select_goodbye(self, interaction: discord.Interaction, select: ui.ChannelSelect):
        channel = select.values[0]
        await execute("UPDATE server_config SET goodbye_channel_id = ? WHERE guild_id = ?", (channel.id, interaction.guild_id))
        await interaction.response.send_message(f"✅ Canal de Saída definido como {channel.mention}!", ephemeral=True)

class RolesSelectView(ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @ui.select(cls=ui.RoleSelect, placeholder="Selecione o Cargo da Staff...")
    async def select_staff_role(self, interaction: discord.Interaction, select: ui.RoleSelect):
        role = select.values[0]
        await execute("UPDATE server_config SET staff_role_id = ? WHERE guild_id = ?", (role.id, interaction.guild_id))
        await interaction.response.send_message(f"✅ Cargo Staff definido como **{role.name}**!", ephemeral=True)

    @ui.select(cls=ui.RoleSelect, placeholder="Selecione o Cargo de Mestre...")
    async def select_master_role(self, interaction: discord.Interaction, select: ui.RoleSelect):
        role = select.values[0]
        await execute("UPDATE server_config SET master_role_id = ? WHERE guild_id = ?", (role.id, interaction.guild_id))
        await interaction.response.send_message(f"✅ Cargo Mestre definido como **{role.name}**!", ephemeral=True)

# --- Dashboard Principal ---

class VoiceSelectView(ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @ui.select(cls=ui.ChannelSelect, channel_types=[discord.ChannelType.category], placeholder="Selecione a Categoria de Salas de Voz...")
    async def select_voice_cat(self, interaction: discord.Interaction, select: ui.ChannelSelect):
        category = select.values[0]
        await execute("UPDATE server_config SET voice_category_id = ? WHERE guild_id = ?", (category.id, interaction.guild_id))
        await interaction.response.send_message(f"✅ Categoria de Voz definida como **{category.name}**!", ephemeral=True)

class SetupView(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @ui.button(label="Canais Logs/Staff", style=discord.ButtonStyle.primary, emoji="📁")
    async def setup_logs(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message("Selecione os canais nos menus abaixo:", view=LogsSelectView(), ephemeral=True)

    @ui.button(label="Tickets (Canal/Cat)", style=discord.ButtonStyle.primary, emoji="🎫")
    async def setup_tickets(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message("Selecione o canal e a categoria:", view=TicketsSelectView(), ephemeral=True)

    @ui.button(label="Salas de Voz (Cat)", style=discord.ButtonStyle.primary, emoji="🔊")
    async def setup_voice(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message("Selecione a categoria para as salas privadas:", view=VoiceSelectView(), ephemeral=True)

    @ui.button(label="Boas-vindas/Saída", style=discord.ButtonStyle.primary, emoji="👋")
    async def setup_welcome(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message("Selecione os canais de Boas-vindas e Saída:", view=WelcomeSelectView(), ephemeral=True)

    @ui.button(label="Cargos Staff/Mestre", style=discord.ButtonStyle.primary, emoji="🛡️")
    async def setup_roles(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message("Selecione os cargos administrativos:", view=RolesSelectView(), ephemeral=True)

class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="notificacoes", description="Ativa/Desativa alertas de tickets e candidaturas na sua DM.")
    async def toggle_dm_cmd(self, ctx):
        await ctx.defer(ephemeral=True)
        
        # Verifica se o usuário tem o cargo de Staff configurado
        config = await fetch_one("SELECT staff_role_id FROM server_config WHERE guild_id = ?", (ctx.guild.id,))
        staff_role = ctx.guild.get_role(config[0]) if config and config[0] else None
        
        if not staff_role or staff_role not in ctx.author.roles:
            if not ctx.author.guild_permissions.administrator:
                return await ctx.send("❌ Apenas membros com o cargo de Staff podem configurar notificações.", ephemeral=True)

        current = await fetch_one("SELECT notify_dm FROM staff_notifications WHERE user_id = ?", (ctx.author.id,))
        if current and current[0] == 1:
            await execute("INSERT OR REPLACE INTO staff_notifications (user_id, notify_dm) VALUES (?, 0)", (ctx.author.id,))
            await ctx.send("❌ Você **não** receberá mais notificações na sua DM.", ephemeral=True)
        else:
            await execute("INSERT OR REPLACE INTO staff_notifications (user_id, notify_dm) VALUES (?, 1)", (ctx.author.id,))
            await ctx.send("✅ Você **receberá** notificações de Tickets e RPG na sua DM!", ephemeral=True)

    @commands.hybrid_command(name="setup", description="Dashboard visual para configurar o bot.")
    async def setup(self, ctx):
        if not ctx.author.guild_permissions.administrator:
            return await ctx.send("❌ Apenas administradores podem usar este comando.", ephemeral=True)

        await execute("INSERT OR IGNORE INTO server_config (guild_id) VALUES (?)", (ctx.guild.id,))
        
        embed = discord.Embed(
            title="⚙️ Dashboard de Configuração",
            description="Escolha uma categoria abaixo para configurar os canais e cargos usando os menus de seleção.\n\n"
                        "✅ **Fácil**: Basta clicar e selecionar na lista!",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed, view=SetupView(self.bot), ephemeral=True)

async def setup(bot):
    await bot.add_cog(Setup(bot))
