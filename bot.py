import discord
import asyncio
from mcstatus import JavaServer
import os

# Ya no necesitas load_dotenv() aquí si lo estás manejando desde Railway

TOKEN = os.getenv("TOKEN")  # Asegúrate de que esta variable esté configurada en Railway
MC_SERVER_IP = os.getenv("MC_SERVER_IP")  # Asegúrate de que esta variable esté configurada en Railway
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # Asegúrate de que esta variable esté configurada en Railway

intents = discord.Intents.default()
client = discord.Client(intents=intents)

server_was_online = False
message = None

async def check_server():
    global server_was_online, message
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    while not client.is_closed():
        try:
            server = JavaServer.lookup(MC_SERVER_IP)
            status = server.status()
            player_count = status.players.online
            max_players = status.players.max
            player_names = status.players.sample

            if player_names:
                player_list = "\n".join([player.name for player in player_names])
            else:
                player_list = "No hay jugadores conectados."

            if not server_was_online:
                message = await channel.send(f"🎮 El servidor de Minecraft está **ONLINE**! 🟢\nJugadores: {player_count}/{max_players}\n{player_list}")
                server_was_online = True
            else:
                await message.edit(content=f"🎮 El servidor de Minecraft está **ONLINE**! 🟢\nJugadores: {player_count}/{max_players}\n{player_list}")

        except Exception as e:
            print(f"Error al obtener el estado del servidor: {e}")
            if server_was_online:
                await channel.send("⚠️ El servidor de Minecraft se ha **apagado**. 🔴")
            server_was_online = False
            message = None

        await asyncio.sleep(30)

@client.event
async def on_ready():
    print(f"✅ Bot conectado como {client.user}")
    client.loop.create_task(check_server())

client.run(TOKEN)
