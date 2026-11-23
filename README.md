# Live Court

Placar de vôlei do grupo: cadastro de jogadores, montagem de times com mascotes, quadra com rotação clicável, rodízio no saque, histórico de partidas e ranking de evolução.

## Como abrir

**Link do app:** <https://felipeg-dev.github.io/live-court/>

- **No PC:** ícone **Live Court** na área de trabalho.
- **No iPhone:** abra o link acima no **Safari**, toque em **Compartilhar** e depois em **Adicionar à Tela de Início**. O app abre em tela cheia, como um aplicativo, e funciona mesmo sem internet na quadra.
- **No Android:** abra o link no Chrome e toque em **Instalar app**.

## Dados e organizadores

Os jogadores e as partidas ficam no banco do grupo (Firebase Firestore, projeto `live-court`) e aparecem iguais em todos os aparelhos. Sem internet na quadra, o app continua marcando e envia tudo quando a conexão volta.

- **Espectadores:** qualquer pessoa com o link vê o placar ao vivo, o histórico e o ranking.
- **Organizadores:** tocam em **Entrar** e usam e-mail e senha para cadastrar, montar times e marcar pontos.
- **Novo organizador:** no [console do Firebase](https://console.firebase.google.com/project/live-court/authentication/users), em Authentication → Usuários → Adicionar usuário.
- **Regras de segurança:** ficam em `firestore.rules`. Depois de mudar o arquivo, cole o conteúdo no console (Firestore → Regras → Publicar).
- **Configuração do app web:** fica em `firebase.config.json` (não é secreta; os dados são protegidos pelas regras e pelo login).

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
