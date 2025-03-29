import discord
import asyncio
import requests
from mcstatus import JavaServer
import os

# Configuración desde Railway
TOKEN = os.getenv("TOKEN")
MC_SERVER_IP = os.getenv("MC_SERVER_IP")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
SERVER_CONTROL_IP = os.getenv("SERVER_CONTROL_IP")  # IP del servidor Flask
SERVER_CONTROL_PORT = 5000  # Asegúrate de que Flask corre en este puerto

intents = discord.Intents.default()
client = discord.Client(intents=intents)

server_was_online = False
message = None

async def check_server():
    """Verifica cada 30 segundos si el servidor está online o no."""
    global server_was_online, message
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    while not client.is_closed():
        try:
            server = JavaServer.lookup(MC_SERVER_IP)
            status = server.status()
            player_count = status.players.online
            max_players = status.players.max
            player_names = status.players.sample or []

            player_list = "\n".join([player.name for player in player_names]) if player_names else "No hay jugadores conectados."

            if not server_was_online:
                message = await channel.send(f"\U0001F3AE El servidor de Minecraft está **ONLINE**! \U0001F7E2\nJugadores: {player_count}/{max_players}\n{player_list}")
                server_was_online = True
            else:
                if message:
                    await message.edit(content=f"\U0001F3AE El servidor de Minecraft está **ONLINE**! \U0001F7E2\nJugadores: {player_count}/{max_players}\n{player_list}")
        
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

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!start_mc"):
        await message.channel.send("🔄 Encendiendo el servidor de Minecraft...")
        response = requests.post(f"http://{SERVER_CONTROL_IP}:{SERVER_CONTROL_PORT}/start")
        if response.status_code == 200:
            await message.channel.send("✅ El servidor se está encendiendo. 🟢")
        else:
            await message.channel.send("⚠️ Error al intentar encender el servidor.")

    if message.content.startswith("!stop_mc"):
        await message.channel.send("🔄 Apagando el servidor de Minecraft...")
        response = requests.post(f"http://{SERVER_CONTROL_IP}:{SERVER_CONTROL_PORT}/stop")
        if response.status_code == 200:
            await message.channel.send("✅ El servidor se ha apagado. 🔴")
        else:
            await message.channel.send("⚠️ Error al intentar apagar el servidor.")
    
    if message.content.startswith("!restart_mc"):
        await message.channel.send("🔄 Reiniciando el servidor de Minecraft...")
        response_stop = requests.post(f"http://{SERVER_CONTROL_IP}:{SERVER_CONTROL_PORT}/stop")
        if response_stop.status_code == 200:
            await message.channel.send("✅ El servidor se ha apagado. 🔴")
            response_start = requests.post(f"http://{SERVER_CONTROL_IP}:{SERVER_CONTROL_PORT}/start")
            if response_start.status_code == 200:
                await message.channel.send("✅ El servidor se está encendiendo. 🟢")
            else:
                await message.channel.send("⚠️ Error al intentar encender el servidor.")
        else:
            await message.channel.send("⚠️ Error al intentar apagar el servidor.")

client.run(TOKEN)
