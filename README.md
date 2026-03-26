# 🤖 Hub Adm Bot - Discord

O **Hub Adm** é um bot modular para Discord focado em automação de administração, suporte (tickets), RPG e gamificação (XP/Leveling). Desenvolvido com `discord.py` e focado 100% em **Slash Commands** e interfaces modernas (Botões, Menus e Modals).

## ✨ Funcionalidades Principais

*   **⚙️ Dashboard de Configuração (`/setup`)**: Interface visual única para configurar canais de log, staff, tickets e cargos sem digitar IDs.
*   **🎫 Sistema de Tickets**: Abertura de suporte via formulário (Modal), aprovação pela staff e criação de canais privados automáticos.
*   **⚔️ Gestão de RPG (`/rpg`)**: Painel para mestres criarem categorias de mesa e convidarem jogadores via menu de seleção.
*   **🔨 Painel de Moderação (`/mod`)**: Ações rápidas de Kick, Ban e Mute selecionando o usuário em uma lista.
*   **🏆 Sistema de Leveling (`/leaderboard`)**: Ganho de XP por mensagens com cooldown para evitar spam.
*   **🔊 Canais de Voz Temporários**: Sistema "Join to Create" com autolimpeza e trava de segurança para novos membros.
*   **🔔 Notificações na DM (`/notificacoes`)**: Escolha individual de cada moderador para receber alertas de novos tickets no privado.
*   **👋 Boas-vindas & Saída**: Mensagens automáticas em Embeds com o avatar do usuário.

## 🛠️ Tecnologias Utilizadas

*   **Linguagem:** Python 3.10+
*   **Biblioteca:** `discord.py` (Interactions v2)
*   **Banco de Dados:** SQLite (`aiosqlite` - Assíncrono)
*   **Ambiente:** `python-dotenv`

## 🚀 Como Instalar e Rodar

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/seu-usuario/hub-adm.git
    cd hub-adm
    ```

2.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure as variáveis de ambiente:**
    Crie um arquivo `.env` na raiz do projeto (use o `.env.template` como base):
    ```env
    DISCORD_TOKEN=seu_token_aqui
    GUILD_ID=id_do_servidor_de_testes
    OWNER_ID=seu_id_discord
    DATABASE_NAME=hub_adm.db
    ```

4.  **Inicie o bot:**
    ```bash
    python main.py
    ```

## 📂 Estrutura do Projeto

```text
hub_adm/
├── main.py              # Inicialização e Sincronização
├── utils/
│   └── database.py      # Gerenciamento de Dados (SQLite)
├── cogs/                # Módulos do Bot
│   ├── setup.py         # Configurações e Dashboard
│   ├── tickets.py       # Suporte e Formulários
│   ├── rpg.py           # Gestão de Mesas e Mestres
│   ├── moderation.py    # Painel de Moderação e Logs
│   ├── leveling.py      # XP e Ranking
│   ├── voice.py         # Canais Temporários
│   ├── welcome.py       # Boas-vindas
│   └── help.py          # Menu de Ajuda Dinâmico
├── requirements.txt     # Lista de dependências
└── .env                 # Configurações sensíveis (não commitado)
```

## 📝 Licença

Este projeto é de uso livre para comunidades de Discord. Sinta-se à vontade para contribuir!
