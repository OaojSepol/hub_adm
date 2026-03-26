import discord
from discord.ext import commands
from discord import ui
from utils.database import execute, fetch_one

# --- View de Gerenciamento de Mesa (Para Mestres) ---
class MasterMenuView(ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @ui.button(label="Criar Minha Categoria", style=discord.ButtonStyle.success, emoji="🏰")
    async def create_cat(self, interaction: discord.Interaction, button: ui.Button):
        master_data = await fetch_one("SELECT category_id FROM rpg_masters WHERE user_id = ? AND status = 'approved'", (interaction.user.id,))
        if not master_data:
            return await interaction.response.send_message("❌ Você não está aprovado como mestre.", ephemeral=True)
        if master_data[0]:
            return await interaction.response.send_message("❌ Você já possui uma categoria de mesa criada.", ephemeral=True)

        category = await interaction.guild.create_category(
            name=f"🏰 Mesa de {interaction.user.name}",
            overwrites={
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, manage_channels=True, manage_permissions=True)
            }
        )
        await interaction.guild.create_text_channel("chat-da-mesa", category=category)
        await interaction.guild.create_voice_channel("Voz da Mesa", category=category)

        await execute("UPDATE rpg_masters SET category_id = ? WHERE user_id = ?", (category.id, interaction.user.id))
        await interaction.response.send_message(f"✅ Categoria {category.name} criada com sucesso!", ephemeral=True)

    @ui.select(cls=ui.UserSelect, placeholder="Selecione um Jogador para Convidar...")
    async def invite_player(self, interaction: discord.Interaction, select: ui.UserSelect):
        member = select.values[0]
        master_data = await fetch_one("SELECT category_id FROM rpg_masters WHERE user_id = ? AND status = 'approved'", (interaction.user.id,))
        
        if not master_data or not master_data[0]:
            return await interaction.response.send_message("❌ Você não possui uma categoria de mesa ativa.", ephemeral=True)

        category = interaction.guild.get_channel(master_data[0])
        if category:
            await category.set_permissions(member, read_messages=True, send_messages=True, connect=True)
            await interaction.response.send_message(f"✅ {member.mention} foi convidado para sua mesa!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Categoria não encontrada. Contate a staff.", ephemeral=True)

# --- Modals e Views de Candidatura ---
class MasterApplicationModal(ui.Modal, title='Candidatura a Mestre'):
    experience = ui.TextInput(label='Experiência', style=discord.TextStyle.paragraph, required=True)
    system = ui.TextInput(label='Sistemas', placeholder='D&D, Tormenta...', required=True)

    async def on_submit(self, interaction: discord.Interaction):
        config = await fetch_one("SELECT staff_channel_id FROM server_config WHERE guild_id = ?", (interaction.guild_id,))
        staff_channel = interaction.guild.get_channel(config[0]) if config else None
        
        if not staff_channel:
            return await interaction.response.send_message("⚠️ Canal da staff não configurado.", ephemeral=True)
        
        embed = discord.Embed(title="⚔️ Nova Candidatura de Mestre", color=discord.Color.purple())
        embed.add_field(name="Candidato", value=interaction.user.mention)
        embed.add_field(name="Experiência", value=self.experience.value, inline=False)
        embed.add_field(name="Sistemas", value=self.system.value, inline=False)

        from cogs.rpg import MasterApprovalView 
        await staff_channel.send(embed=embed, view=MasterApprovalView(interaction.user))
        await interaction.response.send_message("✅ Sua candidatura foi enviada!", ephemeral=True)

        # Notificações DM para Staff
        staff_list = await fetch_all("SELECT user_id FROM staff_notifications WHERE notify_dm = 1")
        for staff_data in staff_list:
            staff_member = interaction.guild.get_member(staff_data[0])
            if staff_member:
                try:
                    dm_embed = discord.Embed(
                        title="⚔️ Nova Candidatura de Mestre",
                        description=f"Um membro se candidatou a mestre em **{interaction.guild.name}**.",
                        color=discord.Color.purple()
                    )
                    dm_embed.add_field(name="Candidato", value=interaction.user.name)
                    await staff_member.send(embed=dm_embed)
                except: pass

class MasterApprovalView(ui.View):
    def __init__(self, candidate):
        super().__init__(timeout=None)
        self.candidate = candidate

    @ui.button(label="Aprovar", style=discord.ButtonStyle.green)
    async def approve(self, interaction: discord.Interaction, button: ui.Button):
        config = await fetch_one("SELECT master_role_id FROM server_config WHERE guild_id = ?", (interaction.guild_id,))
        master_role = interaction.guild.get_role(config[0]) if config else None
        if master_role: await self.candidate.add_roles(master_role)
        await execute("INSERT INTO rpg_masters (user_id, status) VALUES (?, 'approved') ON CONFLICT(user_id) DO UPDATE SET status='approved'", (self.candidate.id,))
        await self.candidate.send("🎉 Sua candidatura a Mestre foi aprovada!")
        await interaction.message.delete()

class RPG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="rpg", description="Dashboard de RPG para jogadores e mestres.")
    async def rpg(self, ctx):
        await ctx.defer(ephemeral=True)
        
        is_master = await fetch_one("SELECT status FROM rpg_masters WHERE user_id = ? AND status = 'approved'", (ctx.author.id,))
        
        embed = discord.Embed(
            title="🏰 Central de RPG",
            description="Bem-vindo ao sistema de RPG do servidor.\n\n"
                        "• Se você é um **Jogador**, pode se candidatar a mestre.\n"
                        "• Se você já é um **Mestre**, pode gerenciar sua mesa abaixo.",
            color=discord.Color.purple()
        )
        
        view = ui.View()
        if not is_master:
            btn_apply = ui.Button(label="Candidatar-se a Mestre", style=discord.ButtonStyle.primary, emoji="📝")
            async def apply_cb(it): await it.response.send_modal(MasterApplicationModal())
            btn_apply.callback = apply_cb
            view.add_item(btn_apply)
        else:
            btn_manage = ui.Button(label="Gerenciar Minha Mesa", style=discord.ButtonStyle.success, emoji="🛡️")
            async def manage_cb(it): await it.response.send_message("Painel do Mestre:", view=MasterMenuView(), ephemeral=True)
            btn_manage.callback = manage_cb
            view.add_item(btn_manage)

        await ctx.send(embed=embed, view=view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(RPG(bot))
