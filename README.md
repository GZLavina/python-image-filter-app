# Python OpenCV Image Filter App

## Desenvolvido por Gustavo Lavina e Vitor Goulart

Aplicativo Python que permite aplicar e manipular filtros de imagem em tempo real. Desenvolvido utilizando as bibliotecas opencv-python, PyQt5 e NumPy.

## Como executar

- Clonar o repositório;
- Abrir um terminal no diretório raiz e executar `pip install -r requirements.txt`;
- Executar `python main.py`;

## Como utilizar o aplicativo

- O aplicativo utiliza a câmera como primeira opção de fonte;
- Caso o computador utilizado não possua câmera, ocorrerá um erro, mas a execução do programa não deve ser interrompida;
- Também é possível selecionar qualquer imagem em formatos usuais para utilizar ao invés do feed da câmera;
- Para aplicar um filtro, basta clicar no respectivo botão; se o filtro tiver parâmetros editáveis, os sliders aparecerão à direita da câmera;
- A ordem na qual os filtros estão sendo aplicados é informada abaixo da imagem;
- Para parar de aplicar um filtro, basta clicar no respectivo botão novamente;
- Para adicionar um sticker, basta clicar no botão "Add Sticker" e selecionar um arquivo ".png" (obrigatoriamente);
- O diretório "pictures" contém algumas imagens PNG gratuitas para testes;
- Após adicionar um sticker, é possível movê-lo utilizando WASD; **apenas o último sticker adicionado pode ser movido**;
- O botão "Remove Sticker" aparece após a inserção do primeiro sticker; **os stickers são removidos na mesma ordem que foram adicionados**.