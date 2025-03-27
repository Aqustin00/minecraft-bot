import discord
import asyncio
from mcstatus import JavaServer
import os

TOKEN = os.getenv("TOKEN")  # Token del bot de Discord
MC_SERVER_IP = os.getenv("MC_SERVER_IP")  # IP del servidor de Minecraft
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # ID del canal donde enviará los avisos
CHECK_INTERVAL = 30  # Segundos entre chequeos

intents = discord.Intents.default()
client = discord.Client(intents=intents)

server_was_online = False  # Estado previo del servidor
message = None  # Variable para almacenar el mensaje enviado

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
            player_names = status.players.sample  # Obtiene una lista de los jugadores conectados

            # Crear un mensaje con los nombres de los jugadores si hay jugadores conectados
            if player_names:
                player_list = "\n".join([player.name for player in player_names])
            else:
                player_list = "No hay jugadores conectados."

            if not server_was_online:  # Si el servidor está ONLINE por primera vez
                message = await channel.send(f"🎮 El servidor de Minecraft está **ONLINE**! 🟢\nJugadores: {player_count}/{max_players}\n{player_list}")
                server_was_online = True
            else:
                # Actualiza el mensaje con la nueva cantidad de jugadores y sus nombres
                await message.edit(content=f"🎮 El servidor de Minecraft está **ONLINE**! 🟢\nJugadores: {player_count}/{max_players}\n{player_list}")

        except:
            if server_was_online:
                # Si el servidor está offline, envía el mensaje de apagado
                await channel.send("⚠️ El servidor de Minecraft se ha **apagado**. 🔴")
            server_was_online = False
            message = None  # Restablecer el mensaje cuando el servidor está apagado

        await asyncio.sleep(CHECK_INTERVAL)

@client.event
async def on_ready():
    print(f"✅ Bot conectado como {client.user}")
    client.loop.create_task(check_server())

client.run(TOKEN)



