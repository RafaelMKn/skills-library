# Credenciais n8n: as duas falhas que se confundem

| Mensagem | Significado | Conserto |
|---|---|---|
| `Credentials could not be decrypted ... a different "encryptionKey" was used` (+ `error:1C800064:Provider routines::bad decrypt`) | A credencial existe no banco, mas a `N8N_ENCRYPTION_KEY` atual não abre o texto cifrado. | Restaurar a chave antiga, ou recriar a credencial na UI. |
| `Credential with ID "<id>" does not exist for type "<tipo>"` | O nó guarda um ID órfão — a credencial foi apagada ou recriada com ID novo. | Reapontar o nó para uma credencial existente do mesmo tipo. |

As duas coexistem na mesma instância por causas e datas diferentes. Distinga pelo `createdAt`:
credencial com `createdAt` antigo e ID original **não foi recriada** — ficou no banco, ilegível.
Isso separa "troca de chave" de "credenciais apagadas e refeitas".

Em ambos os casos o fluxo é **vítima, não causa**. Não abra investigação de lógica do fluxo.

## `bad decrypt` não é erro do nó — nenhum error branch pega

O erro estoura na **resolução da credencial**, antes da execução do nó, e escapa do roteamento de
erro do n8n. Um nó com `onError: continueErrorOutput` pode ficar marcado `error: true` e **mesmo
assim emitir o item pela saída 0 (sucesso)**, com a saída de erro vazia — o fluxo segue e morre no
nó seguinte.

Consequência de projeto: proteção contra credencial quebrada vem **antes** do nó (enfileirar o
payload em data table ou Redis assim que chega), nunca depois.

## Datar a troca de chave pelo `updatedAt`

Salvar uma credencial a recifra com a chave vigente — e refresh de token OAuth também salva o
registro. Logo, a fronteira entre "decifra" e "não decifra" no eixo `updatedAt` é o momento em que
a `N8N_ENCRYPTION_KEY` mudou.

```python
# GET <N8N_<INST>_API_URL>/api/v1/credentials  com header X-N8N-API-KEY
# ordenar por updatedAt; comparar com a lista de quem comprovadamente decifra
```

Para saber quem decifra **sem tentar rodar nada**: pegue execuções com `status: success`, leia
`resultData.runData` e mapeie os nós executados contra o bloco `credentials` de cada nó no
workflow. Credencial presente numa execução verde está íntegra.

## Prioridade de conserto

1. **Procure a chave antiga primeiro.** `docker exec <n8n> cat /home/node/.n8n/config`, ou a env do
   compose / backup do volume. Reaplicá-la restaura todas de uma vez; recriar OAuth custa
   reautorização com o dono da conta.
2. Se sumiu: recriar na UI, ordenado por erros/dia × se o fluxo é produção.
3. **Varra o resto depois.** Cruze todas as credenciais contra as já vistas verdes — senão o
   incidente volta fatiado conforme cada fluxo ocioso receber tráfego.
4. Se houve fila de contenção, o drenador do backlog é entrega separada, só depois do conserto.

## Causa típica da troca de chave

Container recriado sem `N8N_ENCRYPTION_KEY` explícita no compose: o n8n gera uma nova
silenciosamente em `~/.n8n/config` e sobe normal. Nada falha até o primeiro fluxo executar — por
isso o intervalo entre o evento e a detecção costuma ser de meses.
