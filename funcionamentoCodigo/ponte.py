import websockets
import asyncio
from funcionamentoCodigo.visaocomputacional.detectar import Aplicacao as ModoObjetos
from funcionamentoCodigo.visaocomputacional.leitura import Aplicacao as ModoTexto
from funcionamentoCodigo.neoview_piso.aplicacao import Aplicacao as ModoPiso

ESP32_IP = '192.168.1.101'
PORT = 8765

modo_objetos = ModoObjetos()
modo_texto = ModoTexto()
modo_piso = ModoPiso()

async def conectar_esp32():
    uri = f"ws://{ESP32_IP}:{PORT}"
    print(f"Conectando ao servidor ESP32 em {uri}...")

    try:
        async with websockets.connect(uri) as websocket:
            print("Conectado ao ESP32 via WebSocket.")

            async for mensagem in websocket:
                comando = mensagem.strip().upper()
                print(f"Comando recebido: {comando}")

                if comando == "OBJETO":
                    print("Iniciando modo detecção de objetos...")
                    modo_objetos.executar()

                elif comando == "TEXTO":
                    print("Iniciando modo leitura de texto...")
                    modo_texto.executar()

                elif comando == "PISO":
                    print("Iniciando modo de mapeamento de piso...")
                    modo_piso.executar()

                else:
                    print(f"Comando desconhecido: {comando}")

    except ConnectionRefusedError:
        print("Não foi possível conectar ao ESP32. Verifique o IP e a rede Wi-Fi.")
    except websockets.exceptions.ConnectionClosed:
        print("Conexão encerrada.")


if __name__ == "__main__":
    asyncio.run(conectar_esp32())