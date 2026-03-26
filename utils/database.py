import aiosqlite
import os
from dotenv import load_dotenv

load_dotenv()
DB_NAME = os.getenv("DATABASE_NAME", "hub_adm.db")

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        # Configuração Geral do Servidor
        await db.execute("""
            CREATE TABLE IF NOT EXISTS server_config (
                guild_id INTEGER PRIMARY KEY,
                ticket_channel_id INTEGER,
                ticket_category_id INTEGER,
                log_channel_id INTEGER,
                staff_channel_id INTEGER,
                welcome_channel_id INTEGER,
                goodbye_channel_id INTEGER,
                staff_role_id INTEGER,
                master_role_id INTEGER,
                xp_role_veteran_id INTEGER
            )
        """)

        # Migração: Tenta adicionar staff_channel_id se não existir
        try:
            await db.execute("ALTER TABLE server_config ADD COLUMN staff_channel_id INTEGER")
            await db.commit()
            print("Coluna staff_channel_id adicionada com sucesso.")
        except aiosqlite.OperationalError:
            # Coluna já existe, ignorar
            pass

        # Sistema de Tickets
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                channel_id INTEGER PRIMARY KEY,
                user_id INTEGER,
                status TEXT DEFAULT 'open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Sistema de RPG (Mestres e Mesas)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS rpg_masters (
                user_id INTEGER PRIMARY KEY,
                category_id INTEGER,
                status TEXT DEFAULT 'pending'
            )
        """)

        # Sistema de Leveling
        await db.execute("""
            CREATE TABLE IF NOT EXISTS leveling (
                user_id INTEGER,
                guild_id INTEGER,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 0,
                last_message_at TIMESTAMP,
                voice_join_at TIMESTAMP,
                PRIMARY KEY (user_id, guild_id)
            )
        """)

        # Canais de Voz Temporários
        await db.execute("""
            CREATE TABLE IF NOT EXISTS temp_voice (
                channel_id INTEGER PRIMARY KEY,
                owner_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Notificações da Staff
        await db.execute("""
            CREATE TABLE IF NOT EXISTS staff_notifications (
                user_id INTEGER PRIMARY KEY,
                notify_dm INTEGER DEFAULT 0
            )
        """)

        await db.commit()

async def execute(query, parameters=()):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(query, parameters)
        await db.commit()

async def fetch_one(query, parameters=()):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(query, parameters) as cursor:
            return await cursor.fetchone()

async def fetch_all(query, parameters=()):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(query, parameters) as cursor:
            return await cursor.fetchall()
