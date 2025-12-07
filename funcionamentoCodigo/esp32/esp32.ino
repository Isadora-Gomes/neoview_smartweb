#include <WiFi.h>
#include <WebSocketsServer.h>

#define botaoPiso   18
#define botaoObjeto 19
#define botaoTexto  23

// pinos do módulo de aúdio
// #define I2S_BCLK 26
// #define I2S_LRC  25
// #define I2S_DIN  22

const char* ssid = "FAMILIA BRITO";
const char* password = "febiel#2020";

WebSocketsServer webSocket = WebSocketsServer(8765);

void webSocketEvent(uint8_t num, WStype_t type, uint8_t *payload, size_t length) {
  switch (type) {
    case WStype_CONNECTED: {
      IPAddress ip = webSocket.remoteIP(num);
      Serial.printf("Cliente conectado: %d.%d.%d.%d\n", ip[0], ip[1], ip[2], ip[3]);
      break;
    }
    case WStype_DISCONNECTED:
      Serial.printf("Cliente %u desconectado\n", num);
      break;
    case WStype_TEXT:
      Serial.printf("Mensagem recebida: %s\n", payload);
      break;
  }
}

void setup() {
  pinMode(botaoPiso, INPUT_PULLUP);
  pinMode(botaoObjeto, INPUT_PULLUP);
  pinMode(botaoTexto, INPUT_PULLUP);

  Serial.begin(115200);
  WiFi.begin(ssid, password);

  Serial.println("Conectando ao Wi-Fi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWi-Fi conectado.");
  Serial.print("IP ESP32: ");
  Serial.println(WiFi.localIP());

  webSocket.begin();
  webSocket.onEvent(webSocketEvent);

  Serial.println("Servidor WebSocket iniciado na porta 8765");
}

void loop() {
  webSocket.loop();

  if (digitalRead(botaoPiso) == LOW) {
    Serial.println("Enviando 'PISO'");
    webSocket.broadcastTXT("PISO");
    delay(500);
  }

  if (digitalRead(botaoObjeto) == LOW) {
    Serial.println("Enviando 'OBJETO'");
    webSocket.broadcastTXT("OBJETO");
    delay(500);
  }

  if (digitalRead(botaoTexto) == LOW) {
    Serial.println("Enviando 'TEXTO'");
    webSocket.broadcastTXT("TEXTO");
    delay(500);
  }
}
