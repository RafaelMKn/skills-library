# Coleta de dados para relatório de cliente

## ERP cuja credencial só existe no n8n — fluxo temporário de leitura (validado)

Confirme com o usuário antes (é escrita em instância de produção). CLI no workspace:
`python skills/n8n-manager/scripts/n8n_api.py --instance <P> <cmd>`.

1. Ache `credentials` (id + nome) num nó HTTP existente do cliente: `get-workflow <ID>` e filtre
   `nodes[].credentials`.
2. Gere o JSON com Python: `Webhook` (GET, `responseMode: lastNode`, path aleatório) → `Code`
   emitindo um item por endpoint `{key, url, qs}` → `HTTP Request` com `url={{$json.url}}`,
   `specifyQuery: json`, `jsonQuery={{JSON.stringify($json.qs)}}`, `fullResponse` + `neverError`,
   batching 1 item / 1500 ms → `Code` que devolve só `statusCode` por chave (nenhuma PII sai no
   webhook). Nome `[TMP] [CLIENTE] ... - APAGAR`; settings `saveDataSuccessExecution: all`.
3. `create-workflow` → `activate-workflow` → `curl <base>/webhook/<path>` → `deactivate-workflow`,
   tudo no mesmo comando, para não deixar webhook aberto.
4. Corpo completo: `list-executions --workflow-id <tmp>` → `get-execution <id> --include-data` →
   `resultData.runData['<nó HTTP>'][0].data.main[0][i].json.body`, pareado por índice com os
   itens de `runData['<nó Code>']`.
5. `delete-workflow <tmp>` e prove com `get-workflow` = 404 antes de relatar.

## Exemplo: Clinicorp (ERP de referência)

- `subscriber_id=<cliente>`, `business_id=<id>`; credencial
  `<credencial>` (httpBasicAuth, id `<id>`) na instância `<instancia>`.
- `appointment/list` (exige `businessId`; `includeCanceled`): `CreatedBy` (`API` = <agente>),
  `StatusId`, `MobilePhone`, `Patient_PersonId`, `CreateDate`, `AtomicDate` (AAAAMMDD).
  Agenda inteira: um item por semestre (`from`/`to`) no mesmo fluxo temporário — uma chamada por semestre
  voltou milhares de agendamentos (anos antes da abertura voltam lista vazia). Use
  `to` meses depois da data da coleta para pegar consultas já marcadas para o futuro. Com a
  agenda inteira, `patient/list_appointments` por paciente fica desnecessário.
- `appointment/status_list` → `list[].{id, Description}` (`4-Atendido`, `8-Faltou`).
- `payment/list`: `Amount`, `PaymentReceived='X'`, `Canceled`, `PatientId`, `ReceivedDate`.
- `patient/list_appointments` (`PatientId`): histórico completo do paciente, necessário para
  separar novo × retorno. Registros antigos **não têm `CreateDate`** — use `AtomicDate` como
  proxy da criação, senão o cálculo quebra com `KeyError`.
- `sales/estimates_and_conversion` (`group_by=month`): `month`, `APPROVED.{TotalEstimates,
  TotalEstimatesAmount, AverageTicket}`, `Conversion` (%).
- Também respondem: `appointment/list_info`, `schedule_occupation`,
  `operational/list_misses_goals`, `financial/list_summary|list_cash_flow`,
  `sales/estimates_and_conversion|expertise_revenue`. `analytics/list_results` volta vazio.
- `dados_cliente` (Supabase) é criado antes do gate `IA fora do expediente?` — inclui contatos
  atendidos só pela equipe humana.
