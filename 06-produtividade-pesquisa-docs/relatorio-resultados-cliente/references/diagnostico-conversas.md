# Por que o lead não marcou — ler as conversas do agente

Número de conversão baixo só vira plano quando se sabe **onde** a conversa parou. A leitura é
da memória do agente, não do n8n: o histórico de execuções expira e não guarda a conversa inteira.

## 1. Achar onde a memória mora

No JSON do fluxo do agente, filtre nós `memoryRedisChat` / `memoryPostgresChat` e leia
`sessionKey` + credencial. Nos agentes da <empresa> com Redis: chave = número do WhatsApp
(`<numero>@s.whatsapp.net`), tipo `list`, cada item é JSON `{type: human|ai, data: {content,
tool_calls}}`. Outras chaves do mesmo Redis (`msg_seen:*`, `rate:*`, `msg_buffer:*`) são
controle, não conversa.

## 2. Exportar (read-only, via SSH na VPS)

- Senha: leia do comando real do container — `docker inspect -f '{{index .Config.Cmd 7}}'
  <redis>` (posição do valor após `--requirepass`). O `docker-compose.yml` pode ter `${VAR}` e o
  `.env` do diretório pode não ser o valor em uso → `WRONGPASS`. Passe por `REDISCLI_AUTH`, nunca
  na linha de comando nem na conversa.
- Exporte num único `docker exec ... sh -c` com `redis-cli --scan` filtrando `@s.whatsapp.net$`,
  `TYPE` = list, `LRANGE 0 -1 --raw`, prefixando linhas (`@@KEY`, `@@MSG`) para o parse em Python.
- A memória usa LPUSH: **inverta a lista** para ter ordem cronológica.
- Salve em `dados-brutos-<data>/` (gitignored) — é PII pura.

## 3. Cruzar com o ERP e escolher o alvo

Para cada conversa: normalize o telefone (DDD + 8 dígitos), ache o contato no banco do agente
(data do 1º contato) e a agenda **completa** do ERP. Perfil: `ja_ativo` (consulta há < 6 meses),
`inativo_6m`, `sem_historico`, `sem_vinculo` (chave sem contato no banco). Alvo da leitura =
elegível (`sem_historico` + `inativo_6m`) **e** não marcou.

A memória não cobre todos os contatos (TTL/limpeza) e não mostra o que a equipe respondeu pelo
celular — declare as duas lacunas no relato.

## 4. Ler

- **Conversas de 1 mensagem do lead**: leia você mesmo, 1 linha por conversa (1ª msg do lead +
  última da IA). Categorize a 1ª mensagem por regex: texto padrão de anúncio da Meta ("Posso ter
  mais informações sobre isso?" / "Tenho interesse e queria mais informações"), site/formulário
  ("vim do site", "Preenchi seu formulário"; o texto do site traz caracteres zero-width — limpe
  `[\u200b-\u200f\u2060\ufeff]`), saudação, outro. O achado típico é o agente responder pedido
  de informação com pedido de nome e o lead sumir.
- **Conversas com 2+ mensagens do lead**: gere `para_leitura_multi.json` (id, data, perfil, tools
  usadas, mensagens LEAD/<agente> truncadas) e divida em 2 subagentes por id par/ímpar, leitura
  **integral** sem amostragem. Taxonomia fechada de `motivo_principal` (sumiu após pergunta de
  roteiro · preço · procedimento não oferecido · distância · horário · passado para humano ·
  falha da IA · adiou · não era paciente · outro) + `chegou_a_ver_horarios`, `lead_pediu_preco`,
  `falha_ia`/`tipo_falha`, `etapa_onde_parou`, evidência literal ≤ 200 chars **anonimizada**.
  Saída em arquivo dentro de `dados-brutos-*/`; resposta do filho sem nome/telefone e com a
  contagem conferida por código contra os ids do arquivo.
- Confira a soma das classificações contra o total antes de relatar.

## 5. Revisar a classificação dos filhos

- Cheque ids: classificados == ids do arquivo, sem faltante nem extra.
- Leia 4–5 conversas sorteadas contra a classificação.
- A "evidência literal" costuma vir como colagem de trechos (`LEAD: …; <agente>: …`), não como
  citação única. Valide normalizando e buscando o maior fragmento, e declare isso no relato.
  Classificação coerente é suficiente; a citação não é prova.
- **Separe falhas do agente antes e depois da data em que o prompt mudou** (conte também termos
  proibidos, como diminutivos e "à disposição", e saudação repetida). Isso mostra ao cliente que o
  ajuste funcionou e aponta o que ainda falha depois dele.

## 6. Levar para o relatório

Passe para o JSON do relatório só os agregados: motivos com quantidade, contagem de
cada padrão, antes/depois da mudança. O texto de cada achado sai do documento de diagnóstico, e
os números saem do JSON. O plano de próximos passos abre com o conserto do maior vazamento
(normalmente o primeiro contato); as decisões que são do cliente, como faixa de preço, e as que
são do sócio, como segmentação do anúncio, ficam marcadas como tal.
