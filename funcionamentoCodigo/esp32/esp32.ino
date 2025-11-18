#include <WebSocketsServer.h>
#include <WiFi.h>

#define botaoPiso 4
#define botaoAmbiente 16
#define botaoLeitura 17

#define I2S_BCLK 18
#define I2S_LRC 19
#define I2S_DIN 23

const char* ssid = "NEOVIEW";
const char* password = "7RD2S1P5F8";

WebSocketsServer webSocket = WebSocketsServer(81);

void webSocketEvent(uint8_t, WStype_t type, uint8_t* payload, size_t) {
  if(type == WStype_CONNECTED){
    Serial.println("Cliente conectado");
    webSocket.sendTXT(0, "Teste");
  }
  else if(type == WStype_TEXT) {
    String msg = String((char*)payload);
    Serial.println("Mensagem recebida: " + msg);
  }
}

void setup() {
  pinMode(botaoPiso, INPUT_PULLUP);
  pinMode(botaoAmbiente, INPUT_PULLUP);
  pinMode(botaoLeitura, INPUT_PULLUP);

  Serial.begin(115200);

  Serial.println("WebSocket iniciado");

  WiFi.softAP(ssid, password);

  webSocket.begin();
  webSocket.onEvent(webSocketEvent);
}

void loop() {
  webSocket.loop();
}