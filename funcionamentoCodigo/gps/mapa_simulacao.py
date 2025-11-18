import asyncio
import websockets
import json
import openrouteservice

API_KEY = 'eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjY4MGU3ZmVlOGRiNGMwZTFmMmNlN2NmZDg0OTg5YjczNmQ1NDM0NDBkZTk0NjVhZDI2ZmI4NjQ2IiwiaCI6Im11cm11cjY0In0='
client = openrouteservice.Client(key=API_KEY)

ESP32_IP = "192.168.4.1"
ESP32_PORT = 81
uri = f"ws://{ESP32_IP}:{ESP32_PORT}"

origem_geo = [-45.70485776662708, -23.10249927971439]

async def main():
    async with websockets.connect(uri) as ws:
        print("Conectado ao ESP32")

        destino_msg = await ws.recv()
        print("Mensagem recebida:", destino_msg)

        if destino_msg.startswith("Destino: "):
            destino_split = destino_msg.split("Destino: ")[1].strip()
            print("Destino recebido:", destino_split)

            resultado = client.pelias_search(destino_split)
            destino_geo = resultado['features'][0]['geometry']['coordinates']
            print("Coordenadas do destino:", destino_geo)

            rota = client.directions(
                coordinates=[origem_geo, destino_geo],
                profile='foot-walking',
                format='geojson'
            )

            distancia_m = rota['features'][0]['properties']['summary']['distance']
            duracao_s = rota['features'][0]['properties']['summary']['duration']

            distancia_km = distancia_m / 1000
            duracao_min = duracao_s / 60

            texto = f"Distância: {distancia_km:.2f} km | Duração: {duracao_min:.1f} min"
            print("Enviando para ESP32:", texto)

            msg = {"type": "instruction", "text": texto}
            await ws.send(json.dumps(msg))

asyncio.run(main())