---
name: linux-app-management
description: "Use ao gerenciar apps e backups no Linux."
metadata:
  hermes:
    tags: [linux, fedora, desktop, packages, installation]
---

# Gerenciar aplicativos Linux

## Procedimento

1. **Respeite o escopo do verbo.** Baixar não autoriza instalar. Ao trocar aplicativos, remova somente o alvo pedido e preserve os demais. Distinga desinstalação, exclusão do instalador e exclusão de dados pessoais; não apague configurações ou projetos como efeito implícito da desinstalação.
2. **Confira sistema e arquitetura:** `uname -m`, leitura de `/etc/os-release` e `rpm -q <pacote>` em Fedora. Escolha artefato compatível com plataforma e arquitetura.
3. **Identifique o produto antes da release.** Confira função e repositório oficial. Uma organização pode publicar um app principal e uma família de ferramentas separadas. Não generalize a ausência de Linux em uma release para toda a família. Quando o usuário indicar que há versão Linux, investigue os produtos relacionados e downloads oficiais antes de propor Wine ou compilação.
4. **Enumere artefatos oficiais.** No GitHub, use `gh release view <tag> --repo <owner/repo> --json tagName,assets,url` ou `gh api repos/<owner>/<repo>/releases/latest`. Preserve a versão pedida; use a última somente se não houver versão fixada. Selecione por plataforma, arquitetura e extensão, não apenas nome parecido. `.app.tar.gz` pode conter aplicativo macOS; compactação não prova suporte a Linux.
5. **Baixe e valide antes de executar.** Use o diretório Downloads real do usuário. Grave em `.part`, confira tamanho contra `assets[].size` e SHA-256 contra `assets[].digest`; só então promova para o nome final. Se não houver digest publicado, declare a limitação. Não sobrescreva arquivo existente sem comparar ou confirmar. Confira o RPM com `rpm -qp --queryformat '%{NAME} %{VERSION} %{ARCH}\n' <arquivo>`.
6. **Instale pelo gerenciador da distribuição.** No Fedora com autenticação gráfica disponível, use `pkexec /usr/bin/dnf install -y <caminho-absoluto.rpm>`: o usuário autentica na janela do sistema, sem enviar senha ao chat. Pacotes independentes podem entrar na mesma transação. Falha de `sudo -n true` significa falta de autenticação não interativa, não impossibilidade de instalar. Se a autorização for cancelada, não reporte instalação; repita quando solicitado. Uma pergunta de escopo não substitui autorização de sistema.
7. **Verifique o estado real.** Execute `rpm -q <pacote>`, `rpm -V <pacote>` e examine `rpm -ql <pacote>`. Confira executáveis e arquivo `.desktop` em `/usr/share/applications/`. Para binários dinâmicos de origem confiável, use `ldd <binário>` e procure bibliotecas `not found`; interprete binários estáticos separadamente. Isso comprova instalação e integração, não funcionamento da interface: não diga que abriu sem exercitar o app.
8. **Remova com escopo exato.** Use `pkexec /usr/bin/dnf remove -y <pacote>` e confirme ausência com `rpm -q <pacote>`. Se também for pedido excluir o instalador, prefira `gio trash <caminho-exato>` e confira que saiu de Downloads. Preserve dados pessoais e confirme que aplicativos que devem permanecer continuam instalados.
9. **Relate curto:** nome e versão, baixado versus instalado, caminho se relevante e verificação feita. Informe bloqueios ou verificações pendentes. Não entregue instruções no lugar da execução autorizada disponível.

## Google Drive e arquivos sensíveis

Para Google Drive no KDE, backup de `.env` ou organização desses arquivos para transferência, carregue `references/google-drive-env-backups.md`.

- **Identifique a experiência pedida antes de substituir o produto:** cliente oficial, integração ao gerenciador de arquivos e site no navegador não são equivalentes. Consulte o suporte oficial da plataforma e explique a diferença antes de configurar uma alternativa; não apresente uma integração de terceiros como o aplicativo oficial.
- **Descubra o escopo completo antes de copiar credenciais:** se o pedido é todos os projetos de um diretório, inventarie esse diretório, incluindo `.env.*`, em vez de reutilizar apenas os arquivos conhecidos da conversa. Preserve caminhos por projeto e separe clones principais, testes/worktrees e arquivados.
- **Distinga entrega local de backup remoto:** ampliar uma pasta local não atualiza um ZIP já enviado. Informe o alcance exato de cada cópia, sem afirmar sincronização inexistente.

## Backup no Google Drive

Para configurar OAuth pelo terminal e provar transporte e restauração remotos, siga `references/restic-rclone-drive.md`.

- Para backup grande, confira o limite da ferramenta Composio antes de escolhê-la como transporte; acesso à API do Drive não configura uma rotina de backup local.
- Antes de configurar Rclone, leia `rclone help backend drive` e a seção “Making your own client_id” de https://rclone.org/drive/: use cliente OAuth próprio para rotina durável; o compartilhado tem aviso de desativação em 2026. Confirme autorização antes de criar projeto Cloud e não ative faturamento implicitamente.
- Se o usuário preferir fazer a configuração no navegador, entregue um roteiro numerado com links diretos, campos, valores, botões e pontos de parada; não insista em computer use. Separe essa etapa manual da configuração e dos testes que o agente executará pelo terminal. Para receber credencial OAuth Desktop, peça o caminho absoluto do JSON baixado, não seu conteúdo no chat.
- Configure Google Drive API e cliente OAuth do tipo Desktop; avalie `drive.file` para restringir acesso aos arquivos criados pelo aplicativo e valide criação, leitura e restauração antes de adotá-lo. Não copie escopos amplos do tutorial sem necessidade, nem apresente o escopo menor como já testado. Preserve o mesmo cliente OAuth no kit de recuperação, pois o acesso `drive.file` depende da identidade do aplicativo.
- Para rotina durável com público Externo, confira em Audience se o aplicativo está Em produção; o modo Testing pode limitar a autorização a uma semana. Se o usuário aceitar explicitamente uso temporário em Testing, registre a decisão, confirme a conta em Usuários de teste e prossiga sem impor publicação ou agendamento diário. Expiração da autorização exige reconexão, não apaga os arquivos já enviados. Publicar o aplicativo não torna os arquivos públicos. Se a publicação exigir homepage, política ou verificação, pare e resolva o requisito real: não invente URLs nem prometa dispensa universal de verificação.
- Valide em marcos separados: autenticação e conta exata; upload/download Rclone com comparação byte a byte; backup Restic no repositório remoto, `check --read-data` e restauração de prova. Leia o alvo remoto após escrever e registre ID, tamanho e evidência sem segredos. Rotule provas locais e sintéticas corretamente: nem transporte funcionando nem restauração de amostra comprovam backup integral ou boot.
- Confirme guarda da chave fora do notebook antes de certificar recuperabilidade. Quando o usuário confirmar que guardou senha e cliente OAuth, registre como confirmação do usuário e prossiga; não repita o mesmo gate nem exija inspecionar seu gerenciador. Essa confirmação não substitui ensaio de recuperação. Restic é backup de arquivos; recuperação integral exige tratar raiz, home, boot, EFI, metadados e consistência dos dados ativos, além de ensaio em destino seguro.
- Para captura integral Btrfs, aplique a sequência de inventário, preparação privilegiada e envio/verificação em fases de `references/restic-rclone-drive.md`. Snapshots somente leitura de raiz/home são sequenciais, não uma transação global; explicite a consistência dos aplicativos e não prometa imagem inicializável.
- Para cópia longa, mantenha processo rastreado com logs privados, progresso sanitizado e verificação condicionada ao sucesso do envio (`--backup <dir> && --verify <dir>` no mesmo comando privilegiado para não exigir nova janela `pkexec` ao mudar de fase). Prefira iniciar sem `heartbeat` periódico (`notify=true` apenas no encerramento), pois cada tick de heartbeat acorda o agente no turno e polui a conversa; só habilite `heartbeat` se precisar reagir no meio da execução, e nunca responda com linha de progresso a notificações internas de heartbeat: comunique apenas bloqueio, mudança de etapa ou conclusão verificada. Quando houver pedido de status do usuário, relate a última etapa observada e bytes processados, não bytes enviados: deduplicação e compressão tornam essas medidas diferentes. Não estime prazo a partir do percentual enquanto o inventário cresce. Separe preparado, envio em andamento, snapshot remoto confirmado e restauração validada; um heartbeat não conclui nenhuma dessas fases. Se o progresso parar de mudar, investigue processo, estado e logs antes de diagnosticar travamento; não reinicie a cópia nem remova locks com base apenas no percentual. Atividade TCP comprova transporte naquele intervalo, não persistência no Drive, snapshot concluído ou integridade: mantenha essas afirmações separadas no diagnóstico.

- Se o usuário pedir para deixar seguindo em segundo plano, mantenha a tentativa existente e cesse atualizações repetitivas de percentual; não transforme heartbeats em novas mensagens ou pedidos de autorização. Informe apenas uma vez as condições reais de continuidade e volte a comunicar falha que exige intervenção, mudança de fase ou conclusão verificada. Registre o handle e a fase localmente quando necessário, sem novo poll a cada heartbeat nem reescrita do relatório para cada incremento: telemetria rotineira fica nos logs, não na conversa ou no histórico de decisões.
- Se a rede cair ou a máquina reiniciar durante backup em background, preserve snapshots e dados remotos; não prometa retomada automática. Rclone/Restic podem esgotar tentativas e encerrar, e um reboot desmonta pontos em `/run` e deixa lock órfão no repositório. Após reconectar ou religar, confira `uptime -s`, árvore de processos, estado local e locks remotos (`restic list locks --no-lock` + `restic cat lock <id> --no-lock`) antes de remover lock morto com `restic unlock` e repetir a mesma captura; pacotes e índices já gravados em `data/` e `index/` são deduplicados rapidamente na retomada, mas só a confirmação do snapshot final comprova conclusão. Lembre que background não impede suspensão ou desligamento do notebook. Siga a reconciliação de tentativa e credenciais em `references/restic-rclone-drive.md` antes de retomar.

## Pitfalls

- Diferencie hash e assinatura: SHA-256 igual ao publicado comprova correspondência com o artefato da release, não autenticação independente do autor. Se DNF ignorar OpenPGP de pacote local, não afirme que validou assinatura.
- Leia o README e as limitações antes de recomendar alternativa profissional: menus e números de paridade não comprovam fluxos funcionando. Apresente software alpha como candidato a teste, não substituto profissional já validado.
- Descubra versões e artefatos em cada instalação; não transforme versões da sessão em padrões permanentes.

## Critério de conclusão

- Download: arquivo final existe, plataforma e identidade corretas, integridade validada ou limitação declarada.
- Instalação: gerenciador concluiu, consulta posterior confirma pacote e nenhuma falha de integridade foi ignorada.
- Remoção: consulta posterior confirma ausência; instalador e dados pessoais tratados somente conforme o escopo.
- Backup: só relate cópia concluída após exit 0 e leitura do snapshot remoto exato; só relate verificação concluída após conferir seus resultados e a restauração das amostras. Tamanho agregado do repositório, tráfego TCP, heartbeat ou processo ativo não substituem esses marcos. Declare separadamente o que falta para restauração integral e boot.
