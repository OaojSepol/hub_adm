import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
from utils.database import init_db

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", 0))

# Cores para o console
class Color:
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    END = "\033[0m"

class HubAdmBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=intents,
            help_command=None,
            owner_id=OWNER_ID
        )

    async def setup_hook(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Color.BLUE}{Color.BOLD}")
        print("  _   _ _   _ ____       _    ____  __  __ ")
        print(" | | | | | | | __ )     / \  |  _ \|  \/  |")
        print(" | |_| | | | |  _ \    / _ \ | | | | |\/| |")
        print(" |  _  | |_| | |_) |  / ___ \| |_| | |  | |")
        print(" |_| |_|\___/|____/  /_/   \_\____/|_|  |_|")
        print(f"\n{Color.CYAN}--- INICIALIZANDO MÓDULOS ---{Color.END}")
        
        # Inicializa o Banco de Dados
        await init_db()
        
        # Carrega extensões (Cogs)
        loaded = 0
        failed = 0
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                try:
                    await self.load_extension(f"cogs.{filename[:-3]}")
                    print(f"{Color.GREEN} [✓] {Color.END} Módulo carregado: {Color.BOLD}{filename}{Color.END}")
                    loaded += 1
                except Exception as e:
                    print(f"{Color.RED} [✗] {Color.END} Erro no módulo {filename}: {e}")
                    failed += 1

        # Sincroniza comandos Slash
        print(f"\n{Color.CYAN}--- SINCRONIZAÇÃO SLASH ---{Color.END}")
        try:
            guild_id = os.getenv("GUILD_ID")
            if guild_id:
                guild = discord.Object(id=int(guild_id))
                self.tree.clear(guild=guild)
                self.tree.copy_global_to(guild=guild)
                await self.tree.sync(guild=guild)
                print(f"{Color.GREEN} [✓] {Color.END} Comandos sincronizados no Servidor: {Color.YELLOW}{guild_id}{Color.END}")
            else:
                await self.tree.sync()
                print(f"{Color.GREEN} [✓] {Color.END} Comandos sincronizados Globalmente")
        except Exception as e:
            print(f"{Color.RED} [✗] {Color.END} Erro de sincronização: {e}")

    async def on_ready(self):
        print(f"\n{Color.GREEN}{Color.BOLD}HUB ADM ESTÁ ONLINE!{Color.END}")
        print(f"{Color.CYAN}Logado como: {Color.YELLOW}{self.user}{Color.END}")
        print(f"{Color.CYAN}ID do Bot:   {Color.YELLOW}{self.user.id}{Color.END}")
        print(f"{Color.CYAN}Servidores:  {Color.YELLOW}{len(self.guilds)}{Color.END}")
        print(f"{Color.CYAN}Membros:     {Color.YELLOW}{sum(g.member_count for g in self.guilds)}{Color.END}")
        print(f"{Color.CYAN}----------------------------------{Color.END}")

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
