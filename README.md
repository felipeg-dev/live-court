# Live Court

Placar de vôlei do grupo: cadastro de jogadores, montagem de times com mascotes, quadra com rotação clicável, rodízio no saque, histórico de partidas e ranking de evolução.

## Como abrir

- **No PC:** ícone **Live Court** na área de trabalho.
- **No iPhone:** abra o link do app no **Safari**, toque em **Compartilhar** e depois em **Adicionar à Tela de Início**. O app abre em tela cheia, como um aplicativo, e funciona mesmo sem internet na quadra.
- **No Android:** abra o link no Chrome e toque em **Instalar app**.

> Os dados (jogadores e partidas) ficam salvos **no aparelho** onde foram registrados. O que for marcado no iPhone não aparece no PC, e vice-versa. Use sempre o mesmo aparelho para marcar os jogos.

## Estrutura

```
LiveCourt/
├── src/live-court.html     código do app (edite aqui)
├── scripts/build.py        gera a versão web a partir do src
├── index.html              versão web gerada (não edite à mão)
├── sw.js                   funcionamento offline (gerado)
├── manifest.webmanifest    nome, cores e ícones do app (gerado)
└── icons/                  ícones do app, do iPhone e do atalho do PC
```

## Como atualizar o app

1. Edite `src/live-court.html`.
2. Gere a versão web:
   ```
   py scripts/build.py
   ```
   (`py scripts/build.py --icons` também redesenha os ícones.)
3. Envie para o GitHub:
   ```
   git add -A
   git commit -m "Descreva a mudança"
   git push
   ```
   O GitHub Pages publica a nova versão em cerca de um minuto. Quem já instalou recebe a atualização na próxima vez que abrir o app com internet.

## Testar no PC antes de publicar

```
py -m http.server 8765
```

Depois abra <http://localhost:8765> no navegador.
