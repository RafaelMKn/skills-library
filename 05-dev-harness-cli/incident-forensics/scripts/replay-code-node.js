#!/usr/bin/env node
/**
 * Replay offline de um Code node do n8n, contra payloads reais de execucoes
 * passadas, SEM tocar em nenhuma API externa.
 *
 * Para que serve: validar correcao em fluxo ATIVO cujo caminho feliz tem efeito
 * colateral real (manda WhatsApp/e-mail, grava em banco, chama API de cliente).
 * Disparar o webhook para "ver se funciona" entrega mensagem de verdade ao
 * cliente. Este script roda o codigo VIVO do no fora do n8n e aplica a condicao
 * do no de guarda que vem depois dele.
 *
 * Preparacao — extraia sempre da instancia, nunca de snapshot do repo:
 *
 *   INST=PROD; WF=<workflow-id>
 *   python3 skills/n8n-manager/scripts/n8n_api.py --instance $INST \
 *       get-workflow $WF > /tmp/wf.json
 *   python3 -c "import json;w=json.load(open('/tmp/wf.json'));\
 *     open('/tmp/code_node.js','w').write([n for n in w['nodes'] \
 *     if n['name']=='<Nome do Code node>'][0]['parameters']['jsCode'])"
 *
 *   # payload real de uma execucao que deu certo e de uma que falhou:
 *   python3 skills/n8n-manager/scripts/n8n_api.py --instance $INST \
 *       get-execution <ID> --include-data > /tmp/ex.json
 *   # os dados de cada no ficam em:
 *   #   data.resultData.runData.<No>[0].data.main[0][0].json
 *
 * Uso:
 *   node replay-code-node.js casos/*.json
 *   CODE_NODE_JS=/tmp/outro.js node replay-code-node.js casos/*.json
 *
 * Formato de cada caso (ver templates/caso-replay.json):
 *   { "nome": str, "upstream": {...}, "trigger": {...},
 *     "campoGuarda": "number", "esperado": "segue" | "para" }
 *
 * Sai 0 se todos os casos casam com o esperado, 1 se algum falha — da para
 * usar em verificacao automatizada.
 *
 * ADAPTE `runCodeNode` ao no real: os globais que o n8n injeta variam conforme
 * o codigo (items/$input/$json, $item(i).$node[...], $items(nome, out, run)).
 * Leia o jsCode extraido e emule so o que ele usa.
 */
const fs = require("fs");
const path = require("path");

const CODE_PATH = process.env.CODE_NODE_JS || "/tmp/code_node.js";
if (!fs.existsSync(CODE_PATH)) {
  console.error(`ERRO: ${CODE_PATH} nao existe.`);
  console.error("Extraia o jsCode da instancia primeiro (ver topo deste arquivo).");
  process.exit(2);
}
const JS_CODE = fs.readFileSync(CODE_PATH, "utf8");

/**
 * Nome do no de trigger/upstream como o jsCode o referencia. Ajuste conforme
 * o codigo real — e o nome literal usado em $node[...] / $items(...).
 */
const NOME_NO_TRIGGER = process.env.NO_TRIGGER || "Webhook";

/**
 * Emula o ambiente do Code node no modo "Run Once for All Items".
 * `upstream` e o item que entra no no; `trigger` e o body do no de gatilho.
 */
function runCodeNode(upstream, trigger) {
  const items = [{ json: upstream }];
  const triggerItem = { json: { body: trigger } };

  // $item(i).$node["<Trigger>"].json.body — forma antiga
  const $item = () => ({ $node: { [NOME_NO_TRIGGER]: triggerItem } });
  // $items("<Trigger>", 0, 0).json.body — forma de fallback
  const $items = (nodeName) => (nodeName === NOME_NO_TRIGGER ? [triggerItem] : []);
  // $input.first().json / $input.all() — usado por codigo mais novo
  const $input = { first: () => items[0], all: () => items, last: () => items[items.length - 1] };

  const fn = new Function("items", "$item", "$items", "$input", JS_CODE);
  return fn(items, $item, $items, $input);
}

/**
 * Operador `string / notEmpty / singleValue` do no If, com typeValidation
 * strict: falso para "" e para null/undefined. Se o no de guarda usar outro
 * operador, troque esta funcao — nao a condicao do caso.
 */
function guardaNotEmpty(value) {
  if (value === null || value === undefined) return false;
  return String(value).length > 0;
}

const arquivos = process.argv.slice(2);
if (arquivos.length === 0) {
  console.error("uso: node replay-code-node.js <caso.json> ...");
  process.exit(2);
}

let falhas = 0;
for (const arq of arquivos) {
  const caso = JSON.parse(fs.readFileSync(arq, "utf8"));
  const { nome, upstream, trigger, campoGuarda = "number", esperado } = caso;

  console.log("=".repeat(70));
  console.log(`CASO: ${nome}   (${path.basename(arq)})`);

  let out;
  try {
    out = runCodeNode(upstream, trigger);
  } catch (e) {
    console.log(`  RESULTADO ... EXCECAO no Code node: ${e.message}`);
    console.log(`  VEREDITO .... FALHOU (Code node quebrou)`);
    falhas++;
    continue;
  }

  const valor = out?.[0]?.json?.[campoGuarda];
  console.log(`  ${campoGuarda} apos o Code ... ${JSON.stringify(valor)}`);

  const passa = guardaNotEmpty(valor);
  const ramo = passa ? "segue" : "para";
  console.log(`  guarda notEmpty ... ${passa}  ->  ramo "${ramo}"`);
  console.log(`  ESPERADO .......... ${esperado}`);

  const ok = ramo === esperado;
  console.log(`  VEREDITO .......... ${ok ? "PASSOU" : "FALHOU"}`);
  if (!ok) falhas++;
}

console.log("=".repeat(70));
console.log(
  falhas === 0
    ? `TODOS OS ${arquivos.length} CASOS PASSARAM`
    : `${falhas} CASO(S) FALHARAM`
);
process.exit(falhas === 0 ? 0 : 1);
