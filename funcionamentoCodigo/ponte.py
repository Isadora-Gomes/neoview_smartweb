import websockets
import asyncio
from funcionamentoCodigo.visaocomputacional.detectar import Aplicacao as ModoObjetos
from funcionamentoCodigo.visaocomputacional.leitura import Aplicacao as ModoTexto
from funcionamentoCodigo.neoview_piso.aplicacao import Aplicacao as ModoPiso

ESP32_IP = '192.168.43.101'
PORT = 8765

modo_objetos = ModoObjetos()
modo_texto = ModoTexto()
modo_piso = ModoPiso()

async def conectar_esp32():
    uri = f"ws://{ESP32_IP}:{PORT}"
    print(f"\nConectando ao NeoView...")

    try:
        async with websockets.connect(uri) as websocket:
            print("Conexão ao NeoView bem-sucedida.")

            print("\nAguardando comando...\n")

            async for mensagem in websocket:
                comando = mensagem.strip().upper()
                print(f"Comando recebido: {comando}")

                if comando == "OBJETO":
                    print("Iniciando modo de detecção de objetos...")
                    modo_objetos.executar()
                    print("\nAguardando comando...\n")

                elif comando == "TEXTO":
                    print("Iniciando modo de leitura de texto...")
                    modo_texto.executar()
                    print("\nAguardando comando...\n")

                elif comando == "PISO":
                    print("Iniciando modo de mapeamento de piso...")
                    modo_piso.executar()
                    print("\nAguardando comando...\n")

                else:
                    print(f"Comando desconhecido: {comando}")

    except ConnectionRefusedError:
        print("Não foi possível conectar ao ESP32. Verifique o IP e a rede Wi-Fi.")
    except websockets.exceptions.ConnectionClosed:
        print("Conexão encerrada.")


if __name__ == "__main__":
    asyncio.run(conectar_esp32())