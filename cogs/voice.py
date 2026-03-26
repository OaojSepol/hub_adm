import discord
import asyncio
from discord.ext import commands
from discord import ui
from datetime import datetime, timezone
from utils.database import execute, fetch_one, fetch_all

class VoicePanelView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Criar Sala Privada", style=discord.ButtonStyle.primary, emoji="🔊", custom_id="create_voice_btn")
    async def create_voice(self, interaction: discord.Interaction, button: ui.Button):
        # Requisito: 3 dias de servidor
        from datetime import datetime, timezone
        days_on_server = (datetime.now(timezone.utc) - interaction.user.joined_at).days
        if days_on_server < 3:
            return await interaction.response.send_message("❌ Você precisa de pelo menos 3 dias de servidor para criar uma sala.", ephemeral=True)

        # Busca categoria no banco
        config = await fetch_one("SELECT voice_category_id FROM server_config WHERE guild_id = ?", (interaction.guild_id,))
        category = interaction.guild.get_channel(config[0]) if config and config[0] else None

        if not category:
            return await interaction.response.send_message("⚠️ A categoria de voz não foi configurada pelo administrador.", ephemeral=True)

        # Criação da sala
        new_channel = await interaction.guild.create_voice_channel(
            name=f"🔊 Sala de {interaction.user.name}",
            category=category,
            overwrites={
                interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, connect=True, manage_channels=True, manage_permissions=True)
            }
        )
        
        await execute("INSERT INTO temp_voice (channel_id, owner_id) VALUES (?, ?)", (new_channel.id, interaction.user.id))
        
        msg = f"✅ Sua sala privada {new_channel.mention} foi criada!"
        if interaction.user.voice:
            await interaction.user.move_to(new_channel)
            msg += "\n*Você foi movido para ela automaticamente.*"
        
        await interaction.response.send_message(msg, ephemeral=True)

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="voice_panel", description="Envia o painel para criação de salas privadas.")
    @commands.has_permissions(administrator=True)
    async def voice_panel(self, ctx):
        embed = discord.Embed(
            title="🔊 Salas de Voz Privadas",
            description="Clique no botão abaixo para criar sua própria sala de voz.\n\n"
                        "**Vantagens:**\n"
                        "• Você tem controle total das permissões.\n"
                        "• Pode convidar amigos usando `/v_invite`.\n"
                        "• A sala é excluída automaticamente quando todos saírem.",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed, view=VoicePanelView())

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # Auto-cleanup logic (vazio por 5 minutos)
        if before.channel:
            temp_channel = await fetch_one("SELECT channel_id FROM temp_voice WHERE channel_id = ?", (before.channel.id,))
            if temp_channel and len(before.channel.members) == 0:
                await asyncio.sleep(300) # 5 minutos
                if len(before.channel.members) == 0:
                    try:
                        await before.channel.delete()
                        await execute("DELETE FROM temp_voice WHERE channel_id = ?", (before.channel.id,))
                    except: pass

    @commands.hybrid_command(name="v_invite", description="Convida um membro para entrar na sua sala privada.")
    async def voice_invite(self, ctx, member: discord.Member):
        await ctx.defer(ephemeral=True)
        
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send("❌ Você precisa estar em um canal de voz para usar este comando.", ephemeral=True)

        temp_data = await fetch_one("SELECT owner_id FROM temp_voice WHERE channel_id = ?", (ctx.author.voice.channel.id,))
        if not temp_data or temp_data[0] != ctx.author.id:
            return await ctx.send("❌ Você não é o dono desta sala privada.", ephemeral=True)
        
        await ctx.author.voice.channel.set_permissions(member, connect=True)
        await ctx.send(f"✅ {member.mention} foi convidado para sua sala!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Voice(bot))
))
