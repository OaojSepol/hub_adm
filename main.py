import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
from utils.database import init_db

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", 0))

class HubAdmBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix=commands.when_mentioned, # Apenas menção ou Slash
            intents=intents,
            help_command=None,
            owner_id=OWNER_ID
        )

    async def setup_hook(self):
        # Inicializa o Banco de Dados
        await init_db()
        
        # Carrega extensões (Cogs)
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                try:
                    await self.load_extension(f"cogs.{filename[:-3]}")
                    print(f"Loaded extension: {filename}")
                except Exception as e:
                    print(f"Failed to load extension {filename}: {e}")

        # Sincroniza comandos Slash
        try:
            guild_id = os.getenv("GUILD_ID")
            if guild_id:
                guild = discord.Object(id=int(guild_id))
                
                # Limpa a árvore do servidor antes de copiar os novos
                self.tree.clear(guild=guild)
                
                self.tree.copy_global_to(guild=guild)
                await self.tree.sync(guild=guild)
                print(f"Comandos sincronizados no servidor {guild_id}")
            else:
                # Limpa globalmente (pode demorar)
                # self.tree.clear(guild=None) 
                await self.tree.sync()
                print("Comandos sincronizados globalmente")
        except Exception as e:
            print(f"Erro ao sincronizar comandos: {e}")

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            msg = "❌ Você não tem permissão para usar este comando."
        elif isinstance(error, commands.CommandOnCooldown):
            msg = f"⏳ Calma! Tente novamente em {error.retry_after:.2f} segundos."
        elif isinstance(error, commands.CommandNotFound):
            return
        else:
            print(f"Error in command {ctx.command}: {error}")
            msg = f"⚠️ Ocorreu um erro ao processar o comando: {error}"

        # Lógica para responder de forma segura (Slash ou Prefixo)
        try:
            if ctx.interaction:
                if ctx.interaction.response.is_done():
                    await ctx.interaction.followup.send(msg, ephemeral=True)
                else:
                    await ctx.interaction.response.send_message(msg, ephemeral=True)
            else:
                await ctx.send(msg)
        except Exception as e:
            print(f"Não foi possível enviar mensagem de erro: {e}")

bot = HubAdmBot()

if __name__ == "__main__":
    if not TOKEN:
        print("ERRO: DISCORD_TOKEN não encontrado no arquivo .env")
    else:
        bot.run(TOKEN)
