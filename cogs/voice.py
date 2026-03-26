import discord
import asyncio
from discord.ext import commands
from datetime import datetime, timezone
from utils.database import execute, fetch_one

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.join_to_create_id = None # Deve ser definido via setup se desejar automatizar

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # Join to Create Logic (Placeholder ID, idealmente carregar do banco)
        # Supondo que o admin usou um comando para definir o ID do canal mestre
        if after.channel and after.channel.name == "➕ Join to Create":
            # Requisito: 3 dias de servidor
            join_date = member.joined_at
            days_on_server = (datetime.now(timezone.utc) - join_date).days
            if days_on_server < 3:
                await member.move_to(None)
                return await member.send("❌ Você precisa de pelo menos 3 dias de servidor para criar uma sala privada.")

            # Criação do Canal
            category = after.channel.category
            new_channel = await member.guild.create_voice_channel(
                name=f"🔊 Sala de {member.name}",
                category=category,
                overwrites={
                    member.guild.default_role: discord.PermissionOverwrite(connect=False),
                    member: discord.PermissionOverwrite(connect=True, manage_channels=True, manage_permissions=True)
                }
            )
            await member.move_to(new_channel)
            await execute("INSERT INTO temp_voice (channel_id, owner_id) VALUES (?, ?)", (new_channel.id, member.id))

        # Auto-cleanup logic (vazio por 5 minutos)
        if before.channel:
            temp_channel = await fetch_one("SELECT channel_id FROM temp_voice WHERE channel_id = ?", (before.channel.id,))
            if temp_channel and len(before.channel.members) == 0:
                await asyncio.sleep(300) # 5 minutos
                if len(before.channel.members) == 0:
                    await before.channel.delete()
                    await execute("DELETE FROM temp_voice WHERE channel_id = ?", (before.channel.id,))

    @commands.hybrid_command(name="v_invite")
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
