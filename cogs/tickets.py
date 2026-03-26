import discord
import asyncio
from discord.ext import commands
from discord import ui
from utils.database import execute, fetch_one, fetch_all

class TicketModal(ui.Modal, title='Formulário de Suporte/Denúncia'):
    reason = ui.TextInput(label='Motivo', style=discord.TextStyle.paragraph, placeholder='Descreva o motivo do ticket...', required=True, min_length=10)

    async def on_submit(self, interaction: discord.Interaction):
        # Busca canal da staff
        config = await fetch_one("SELECT staff_channel_id, staff_role_id FROM server_config WHERE guild_id = ?", (interaction.guild_id,))
        if not config or not config[0]:
            return await interaction.response.send_message("⚠️ Canal da staff não configurado. Use `/setup`.", ephemeral=True)

        staff_channel = interaction.guild.get_channel(config[0])
        staff_role = interaction.guild.get_role(config[1])

        embed = discord.Embed(title="🎟️ Novo Ticket Solicitado", color=discord.Color.yellow())
        embed.add_field(name="Autor", value=interaction.user.mention, inline=True)
        embed.add_field(name="Motivo", value=self.reason.value, inline=False)

        view = TicketStaffView(interaction.user, self.reason.value)
        content = staff_role.mention if staff_role else None
        await staff_channel.send(content=content, embed=embed, view=view)
        await interaction.response.send_message("✅ Sua solicitação foi enviada para análise da staff.", ephemeral=True)

        # Enviar notificações na DM para staff inscrita
        staff_list = await fetch_all("SELECT user_id FROM staff_notifications WHERE notify_dm = 1")
        for staff_data in staff_list:
            staff_member = interaction.guild.get_member(staff_data[0])
            if staff_member:
                try:
                    dm_embed = discord.Embed(
                        title="🎫 Novo Ticket Aberto",
                        description=f"Um novo ticket foi solicitado no servidor **{interaction.guild.name}**.",
                        color=discord.Color.yellow()
                    )
                    dm_embed.add_field(name="Autor", value=interaction.user.name)
                    dm_embed.add_field(name="Motivo", value=self.reason.value)
                    await staff_member.send(embed=dm_embed)
                except:
                    pass # DM fechada do moderador

class TicketStaffView(ui.View):
    def __init__(self, author, reason):
        super().__init__(timeout=None)
        self.author = author
        self.reason = reason

    @ui.button(label="Aceitar", style=discord.ButtonStyle.green, custom_id="ticket_accept")
    async def accept(self, interaction: discord.Interaction, button: ui.Button):
        config = await fetch_one("SELECT ticket_category_id FROM server_config WHERE guild_id = ?", (interaction.guild_id,))
        category = interaction.guild.get_channel(config[0]) if config else None

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            self.author: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        channel = await interaction.guild.create_text_channel(
            name=f"ticket-{self.author.name}",
            category=category,
            overwrites=overwrites,
            topic=f"Ticket de {self.author} | Motivo: {self.reason}"
        )

        await execute("INSERT INTO tickets (channel_id, user_id) VALUES (?, ?)", (channel.id, self.author.id))
        
        embed = discord.Embed(title="🎫 Ticket Aberto", description=f"Olá {self.author.mention}, este é seu canal de suporte.\nMotivo: {self.reason}", color=discord.Color.green())
        await channel.send(content=f"{self.author.mention} | Staff: {interaction.user.mention}", embed=embed)
        
        await interaction.message.delete()
        await interaction.response.send_message(f"✅ Ticket criado: {channel.mention}", ephemeral=True)

    @ui.button(label="Recusar", style=discord.ButtonStyle.red, custom_id="ticket_deny")
    async def deny(self, interaction: discord.Interaction, button: ui.Button):
        await self.author.send(f"❌ Sua solicitação de ticket foi recusada pela staff.")
        await interaction.message.delete()
        await interaction.response.send_message("✅ Ticket recusado.", ephemeral=True)

class TicketPersistentView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Abrir Ticket", style=discord.ButtonStyle.primary, emoji="🎟️", custom_id="open_ticket_btn")
    async def open_ticket(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(TicketModal())

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ticket_panel", description="Envia o painel de abertura de tickets no canal atual.")
    @commands.has_permissions(administrator=True)
    async def ticket_panel(self, ctx):
        embed = discord.Embed(
            title="🎫 Central de Suporte & Denúncias",
            description="Precisa de ajuda com alguma funcionalidade ou deseja reportar algo?\n\n"
                        "**Como funciona:**\n"
                        "1. Clique no botão **Abrir Ticket**.\n"
                        "2. Preencha o motivo de sua solicitação.\n"
                        "3. Aguarde a análise de um moderador.\n\n"
                        "*Lembre-se: Abuse do sistema e você poderá sofrer punições.*",
            color=discord.Color.from_rgb(47, 49, 54) # Cor escura "Discord-like"
        )
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/1067/1067562.png") # Ícone de ticket genérico
        
        # Se for Slash Command, enviamos como efêmero a confirmação se desejar, 
        # mas aqui o painel PRECISA ser público.
        await ctx.send(embed=embed, view=TicketPersistentView())

    @commands.hybrid_command(name="close", description="Fecha o ticket atual.")
    async def close_ticket(self, ctx):
        await ctx.defer(ephemeral=True)
        ticket_data = await fetch_one("SELECT user_id FROM tickets WHERE channel_id = ? AND status = 'open'", (ctx.channel.id,))
        if not ticket_data:
            return await ctx.send("❌ Este canal não é um ticket ativo.", ephemeral=True)

        await execute("UPDATE tickets SET status = 'closed' WHERE channel_id = ?", (ctx.channel.id,))
        await ctx.send("🔒 Este ticket será fechado e deletado em 5 segundos...", ephemeral=True)
        await asyncio.sleep(5)
        await ctx.channel.delete()

async def setup(bot):
    await bot.add_cog(Tickets(bot))
    # Registra a view persistente para que funcione após o bot reiniciar
    bot.add_view(TicketPersistentView())
