# NeoView - SmartWeb 

> Óculos inteligente para auxílio a pessoas com deficiência visual — integrando hardware e visão computacional para promover autonomia, segurança e inclusão social.

## Visão geral

NeoView é um sistema de óculos inteligente pensado para ajudar pessoas com deficiência visual em tarefas do dia a dia. A proposta é combinar conectividade em tempo real (via ESP32) com técnicas de visão computacional, oferecendo uma solução prática, acessível e de fácil uso, capaz de dar mais autonomia e segurança aos usuários.

## Funcionalidades principais

- Captura de ambiente através de câmera acoplada aos óculos;  
- Processamento por visão computacional para detecção de obstáculos, objetos ou textos relevantes (ex.: leitura de placas, identificação de portas, etc.);  
- Comunicação em tempo real (via ESP32) — permitindo, por exemplo, envio de alertas, integração com outros serviços ou dispositivos, ou atualização imediata de dados;  
- Foco em acessibilidade: interface simples, uso orientado à necessidade da pessoa com deficiência visual;  
- Mobilidade e independência: pensado para uso no dia a dia, para tarefas cotidianas e de locomoção.

## Problema que o projeto resolve

Muitas pessoas com deficiência visual enfrentam desafios constantes para se movimentar com segurança e realizar atividades cotidianas simples — desde atravessar uma rua, identificar obstáculos em ambientes desconhecidos, até localizar objetos ou ler informações visuais.  

NeoView busca reduzir essas barreiras, promovendo maior inclusão social e autonomia para essas pessoas. A ideia é tornar a tecnologia acessível e prática, ajudando a transformar a rotina de quem precisa desse suporte.

## Tecnologias usadas

- **ESP32** — para conectividade em tempo real e interface hardware;  
- Técnicas de **Visão Computacional** YOLO — para análise de imagens e detecção de objetos/ambientes;  
- OpenCV
- Python

## Como rodar / configurar o projeto

```bash
# Clone o repositório
git clone https://github.com/Isadora-Gomes/neoview_smartweb.git
cd neoview_smartweb

# (Se houver parte Python ou script) Instale dependências
pip install -r requirements.txt

# Execute a aplicação / firmware conforme instruções



