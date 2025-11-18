#include <WebSocketsServer.h>
#include <WiFi.h>

String destino = "Mercado Carrefour";

const char* ssid = "neoview_rede";
const char* password = "neoview_testes123";

WebSocketsServer webSocket = WebSocketsServer(81);

void webSocketEvent(uint8_t, WStype_t type, uint8_t* payload, size_t) {
  if(type == WStype_CONNECTED){
    Serial.println("Cliente conectado");
    webSocket.sendTXT(0, "Destino: " + destino);
  }
  else if(type == WStype_TEXT) {
    String msg = String((char*)payload);
    Serial.println("Mensagem recebida: " + msg);
  }
}

void setup() {
  Serial.begin(115200);
  WiFi.softAP(ssid, password);

  webSocket.begin();
  webSocket.onEvent(webSocketEvent);

  Serial.println("WebSocket iniciado!");
}

void loop() {
  webSocket.loop();
}
