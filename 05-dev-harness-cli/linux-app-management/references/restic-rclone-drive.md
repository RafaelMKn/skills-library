# Restic + Rclone no Google Drive

Receita para configurar cliente OAuth próprio e provar o percurso remoto sem exibir segredos. Não substitui desenho de recuperação integral.

## 1. Descoberta e guarda da credencial

1. Leia o estado documentado do projeto e execute `rclone listremotes`, `rclone version`, `restic version` e `rclone authorize --help`. Preserve remotes existentes; não sobrescreva configuração por suposição.
2. Descubra Downloads com `xdg-user-dir DOWNLOAD`; enumere candidatos JSON, sem imprimir conteúdo. Em código local, valide que o arquivo tem objeto `installed` com `client_id`, `client_secret`, `auth_uri` e `token_uri`: objeto `web` não equivale a cliente Desktop.
3. Se a movimentação foi autorizada, use diretório privado `.secrets/` do projeto (0700), arquivo 0600 e destino sem sobrescrita. Compare SHA-256 antes/depois e confira origem ausente. Inclua `.secrets/` no `.gitignore` sem apagar regras existentes. Informe caminho, não conteúdo.
4. Preserve a mesma identidade OAuth para recuperação com `drive.file`. Peça guarda do JSON fora do notebook junto à senha Restic; um projeto local com arquivo ignorado pelo Git não constitui kit externo.

## 2. Consentimento manual, configuração pelo terminal

Use o navegador somente para o usuário escolher conta e consentir. Não automatize a interface se ele preferir fazê-la manualmente.

Padrão exercitado: carregue o JSON em um processo Python, monte ambiente apenas para o subprocesso e execute:

    rclone authorize drive --auth-no-open-browser

Passe ao subprocesso:

    RCLONE_DRIVE_CLIENT_ID=<valor lido do JSON>
    RCLONE_DRIVE_CLIENT_SECRET=<valor lido do JSON>
    RCLONE_DRIVE_SCOPE=drive.file

Não coloque segredo em argumentos da linha de comando. Capture stdout em memória privada: `rclone authorize` devolve o token ali. Encaminhe stderr a log privado 0600 e extraia apenas a URL local de autorização para apresentar ao usuário. Não publique o log inteiro ou a resposta OAuth. Confira as flags da versão instalada antes de aplicar a receita.

Mantenha o processo em background rastreado enquanto aguarda consentimento. Informe o prazo real definido pelo wrapper; se expirar, reinicie o fluxo em vez de reutilizar URL antiga. Conclusão normal do processo ainda exige leitura da configuração e teste autenticado.

Após sucesso, extraia e valide o JSON de token: exija `access_token` e `refresh_token`. Grave uma seção nova no arquivo de configuração Rclone preservando as demais, com escrita atômica e 0600:

    [nome-do-remote]
    type = drive
    client_id = <lido do JSON>
    client_secret = <lido do JSON>
    scope = drive.file
    token = <JSON OAuth recebido>
    use_trash = true
    team_drive =

Use parser sem interpolação para ler/gravar valores e não imprima a seção. Não grave remote parcialmente autorizado nem prossiga se o nome já existir sem reconciliar o estado.

## 3. Verificar identidade e transporte

1. Leia de volta seção, escopo e permissões sem exibir token.
2. Faça uma consulta autenticada a `https://www.googleapis.com/drive/v3/about?fields=user(emailAddress),storageQuota`, com Bearer em memória. Compare o e-mail com a conta aprovada; conta divergente bloqueia upload.
3. Gere arquivo aleatório pequeno sem dados pessoais no scratch autorizado. Use destino exclusivo por prova, sem sobrescrever arquivo remoto existente.
4. Execute `rclone copyto ORIGINAL REMOTE:PASTA/ARQUIVO`, baixe para outro arquivo e compare bytes e SHA-256. Leia `rclone lsjson REMOTE:PASTA/ARQUIVO --stat`; confira tamanho e registre o ID retornado.
5. Grave evidência sanitizada: destino, ID, tamanho, hash, comparação e caminhos locais. Não remova a prova ou faça limpeza abrangente sem escopo explícito.

A consulta de identidade e o upload foram exercitados com `drive.file`; isso não garante acesso a arquivos antigos criados por outro aplicativo.

## 4. Repositório criptografado e prova Restic remota

1. Gere senha aleatória forte em arquivo 0600 com criação exclusiva, sem stdout. Não confunda senha de prova descartável com chave do repositório que receberá dados reais.
2. Use `RESTIC_PASSWORD_FILE` apontando para esse arquivo; não passe a senha no comando. Defina:

    RESTIC_REPOSITORY=rclone:NOME_DO_REMOTE:PASTA/restic

3. Para destino novo confirmado, execute `restic init --repository-version 2`. Se já houver repositório, valide-o com a chave correta; não reinicialize nem troque a chave implicitamente.
4. Faça `restic backup DIRETORIO_DE_PROVA --tag prova-remota --json`; obtenha o snapshot pelo registro de resumo, não por texto presumido.
5. Execute `restic check --read-data` e `restic restore ID --target DESTINO_VAZIO`. Compare bytes e modo do arquivo restaurado; releia `restic snapshots --json ID` para confirmar o snapshot remoto.
6. Registre IDs e resultados. Uma prova sintética remota valida criptografia/transporte/restauração daquela amostra, não a cópia do notebook nem todos os metadados possíveis.

## 5. Gates para dados reais e recuperação integral

- Confirme a guarda da senha e do cliente OAuth em gerenciador acessível fora do notebook antes de depender da cópia real. Não peça os valores no chat; peça confirmação de guarda. A única senha dentro do próprio backup não permite recuperá-lo.
- Gere procedimento sem segredos com conta, identidade do cliente a preservar, remote/repositório, forma de reautorizar e comandos de listar/verificar/restaurar em destino seguro. Não chame um documento apenas local de kit externo já disponível.
- Inventarie `findmnt`, `lsblk`, raiz/home/subvolumes, boot/EFI, serviços e volumes antes da captura integral. Trate consistência de filesystem e de aplicativos como requisitos distintos; não pare bancos ou serviços implicitamente.
- Interprete falha de `sudo -n true` somente como ausência de autenticação não interativa; ofereça o caminho administrativo apropriado com autorização do sistema, sem pedir senha pelo chat.
- Não confunda `du` com `df` em Btrfs: compressão, reflinks e permissões podem produzir números diferentes ou parciais. Não apresente tamanho parcial como total a enviar.
- Separe snapshot de prova, primeiro backup real, restauração de amostra e ensaio integral/boot no relatório. Não habilite timer, `forget` ou `prune` por padrão, especialmente quando o usuário aceitou apenas uma cópia temporária.

## 6. Captura integral Btrfs: preparar antes de enviar

Este desenho teve preparação privilegiada real e início de envio exercitados; não o trate como recuperação integral ou boot já validados. Os testes locais de Restic não substituem a validação real de Btrfs, mount ou Drive.

1. Descubra os alvos com `findmnt --json -o TARGET,SOURCE,FSTYPE,OPTIONS,UUID`, `lsblk --json -o PATH,PKNAME` e, com autorização administrativa, `btrfs subvolume list /` e `btrfs subvolume show /` e `/home`. Valide todos os subvolumes antes de capturar: um snapshot não inclui recursivamente outros subvolumes. Interrompa diante de layout inesperado em vez de omitir dados. Confira parsers contra saída real: `lsblk PKNAME` pode retornar só o nome, sem `/dev/`.
2. Reutilize um executor revisado com fases `prepare`, `backup` e `verify`, manifesto e estado privados. Antes de root, rode testes de exclusões, recusas, exit codes e restauração local real. Não considere mocks prova dos comandos privilegiados. Use caminhos absolutos e `workdir` explícito nos comandos de retomada; um diretório temporário removido não pode ser pré-requisito da próxima execução.
3. Em `prepare`, adquira lock exclusivo e valide credenciais/repositório existente sem reinicializar. Use staging root 0700, arquivos 0600 e ID exclusivo. Preserve inventário de partições (`sfdisk --dump`, somente leitura), `lsblk`, UEFI (`efibootmgr -v`), mounts, pacotes e subvolumes. Isso documenta a reconstrução; não torna o backup inicializável.
4. Capture `/boot` e EFI separadamente, com `tar --acls --xattrs --selinux --numeric-owner`; ao arquivar boot, exclua o mount EFI e arquive-o em outra saída. Qualquer exit não zero impede declarar preparação concluída. Preserve dados ativos com mecanismo apropriado ao aplicativo. Para Akonadi/MariaDB local identificado, foi exercitado `mariadb-dump --socket=SOCKET_CONFIRMADO -u USUARIO_CONFIRMADO --single-transaction --skip-lock-tables --databases akonadi`, executado como seu usuário; não generalize esse dump para outros bancos ou motores não transacionais. Nunca imprima o dump.
5. Monte o top-level Btrfs (`subvolid=5`) num mountpoint privado e exclusivo. Crie snapshots `btrfs subvolume snapshot -r` como irmãos dos subvolumes de origem, não dentro deles. Registre ID, UUID, origem e flags; releia `btrfs property get CAMINHO ro`. Desmonte somente o mount criado pela execução, inclusive em falha. Preserve os snapshots até decisão explícita de limpeza; nunca remova subvolume apenas para liberar uma tentativa.
6. Prepare manifesto com hashes dos artefatos e amostras, modos e donos. Calcule os valores esperados das amostras diretamente nos snapshots somente leitura, depois de criados; compare a restauração com esses valores, não com a árvore ativa que o usuário continuou alterando. Para boot/EFI e dumps, use os artefatos privados efetivamente enviados. Leia estado e manifesto de volta antes de iniciar upload. Snapshots raiz/home não são atômicos entre si; aplicativos abertos continuam sujeitos a recuperação de falha, mesmo com filesystem congelado no tempo. Não pare serviços nem use `fsfreeze` sem autorização específica.

## 7. Envio integral, retomada e conclusão

1. Execute Restic com prioridade baixa (`nice -n 19`, `ionice -c2 -n7`), lock de concorrência e ambiente explícito para `RCLONE_CONFIG`, `RESTIC_PASSWORD_FILE`, cache e temporários privados. Se rodar como root usando configuração Rclone do usuário, preserve e confira dono/modo ao terminar: a renovação OAuth pode substituir o arquivo e mudar seu dono. Não exponha tokens em logs.
2. Ao enviar snapshots via caminhos relativos `rootfs homefs` com cwd no pai exclusivo, use `--one-file-system` e exclua explicitamente o staging interno e a senha Restic. Não exclua caches, jogos ou pastas pessoais silenciosamente de um pedido integral. Teste com Restic real como os caminhos aparecem no snapshot e como as exclusões são resolvidas; o diretório de recuperação passado por caminho absoluto pode aparecer numa árvore diferente de `/rootfs` e `/homefs`.
3. Trate exit 3 como cópia incompleta, nunca sucesso. Só aceite exit 0 após extrair `snapshot_id` do resumo JSON, ler `restic snapshots --json ID` e auditar exclusões com `restic ls --json ID`. Preserve logs por tentativa. Se houver snapshot com a tag da execução que o estado local não conhece, reconcilie antes de repetir; não use `unlock --remove-all`, `prune` ou `forget` para contornar a divergência.
4. Para operação longa, encadeie `backup && verify` no processo rastreado, de modo que a verificação não rode após envio falho. Ignore percentuais iniciais como previsão: o scanner pode descobrir mais arquivos e aumentar o total. Diferencie os campos do resumo JSON: `total_bytes_processed` representa dados lógicos examinados e `data_added` representa dados adicionados ao repositório; não chame o primeiro de volume transmitido. `du`, uso Btrfs, total lógico do scanner e tamanho remoto não são intercambiáveis por causa de compressão, reflinks, deduplicação e metadados. Relate a etapa observada sem inventar tamanho final ou ETA. Consuma heartbeats como telemetria interna, sem resposta automática ou novo poll redundante; avise sobre bloqueio, mudança de fase ou conclusão, e responda a pedidos explícitos de status. Não prometa notificação em canal ausente.
### Progresso estável: diagnóstico sem interromper a cópia

- Compare os horários dos registros, não só a chegada do heartbeat: a notificação pode carregar a última linha antiga, sem novo progresso.
- Se bytes e arquivos permanecerem iguais, confira o processo rastreado e seus subprocessos, a fase no estado privado, a atualização do JSONL e o stderr da tentativa. Faça leitura direcionada e devolva apenas estado, horários e contagem de erros; os logs podem conter caminhos pessoais. Um stderr vazio não comprova saúde, assim como PID vivo não comprova avanço.
- Diferencie varredura, processamento de arquivo grande, espera pelo transporte e verificação antes de agir. Sem evidência suficiente, registre “sem avanço observado”, não “travado” nem “funcionando normalmente”.
- Se houver espera pelo transporte, meça atividade do subprocesso Rclone correto antes de declarar paralisação. Identifique seu PID na árvore da execução; obtenha duas amostras de `ss -tinp state established`, separadas por intervalo curto observado, e filtre as conexões pelo campo `pid=PID_CONFIRMADO,`. Extraia `bytes_acked`, `bytes_sent` e `bytes_retrans` das linhas TCP seguintes, sem publicar endpoints ou caminhos pessoais. O incremento de `bytes_acked` demonstra dados reconhecidos pelo par TCP no intervalo; não demonstra gravação do objeto no Drive, progresso lógico do Restic ou conclusão do backup. Compare conexões equivalentes: abertura/fechamento de sockets invalida subtrair cegamente os totais agregados. Registre intervalo e contadores, sem converter uma amostra curta em ETA do backup.
- Não interprete `%CPU` acumulado do `ps` como atividade instantânea nem conexão estabelecida como upload avançando. Correlacione estado, contadores de I/O/rede e progresso em mais de um instante. Se o JSONL parecer vazio enquanto há progresso no processo, considere buffering do wrapper; em executores próprios, faça flush explícito dos registros de status/erro para permitir inspeção durante a execução, sem reiniciar um envio ativo só para aplicar essa melhoria.
- Em executores Python novos, abra o JSONL de progresso com `open(caminho, 'a', buffering=1)` e grave cada registro completo com newline, ou execute `flush()` após cada registro. Faça o mesmo para erros que precisem de inspeção imediata; mantenha escrita atômica para os marcos de estado. Teste com um subprocesso ainda em execução: o teste deve conseguir ler um registro antes de o produtor terminar. Conferir o arquivo apenas após exit não detecta buffering que impede diagnóstico durante um envio de horas.
- Para medir presença remota durante envio ativo, use `rclone size REMOTE:PASTA --json` apenas como leitura pontual: registre bytes e count observados, sem tratá-los como snapshot confirmado ou dados íntegros. Nomeie o escopo consultado: o tamanho do repositório inteiro inclui provas anteriores, snapshots existentes, metadados e objetos da tentativa em andamento; não o atribua integralmente ao backup atual. Ao comparar esse total com os bytes lógicos do scanner, explique que as métricas não são equivalentes, sem atribuir a diferença observada a compressão, deduplicação ou trânsito sem medir cada contribuição. Se o comando do usuário falhar ao abrir `rclone.conf` durante execução root, confira dono/modo: renovação OAuth pode ter substituído o arquivo como root. Faça a consulta administrativa com `RCLONE_CONFIG` explícito, sem imprimir segredos nem ampliar permissões para contornar o erro; confira a restauração do dono/modo original ao encerrar o executor.
- Preserve processo, snapshots e locks durante o diagnóstico. Não crie uma segunda tentativa concorrente, não remova locks e não reinicie o envio apenas para ver se volta a andar. Retomada exige confirmar o fim da tentativa anterior e reconciliar o snapshot remoto com o estado local.
- Monitore espaço livre do filesystem que contém os snapshots durante envios longos, não apenas antes de prepará-los: alterações nos subvolumes ativos mantêm blocos antigos referenciados pelos snapshots e podem consumir espaço mesmo sem arquivos novos no staging. Registre a tendência com `df` e, quando necessário, `btrfs filesystem usage`; não some tamanhos de `du` para estimar blocos físicos nem apague snapshots automaticamente ao detectar pressão de espaço.

### Queda de rede, reinício e retorno à execução

1. Antes de perder conectividade, registre localmente apenas o handle do processo, RUN_DIR, identidades dos snapshots, fase e destino remoto sem segredos. Preserve a captura original: reconectar ou religar a máquina não autoriza novos snapshots, limpeza, timer ou alteração de política.
2. Ao voltar, consulte primeiro `uptime -s`, o processo rastreado e o estado local. Se ainda estiver ativo, acompanhe a mesma tentativa; não execute outro `backup` em paralelo. Se o handle não estiver disponível, confira a árvore de processos e o lock antes de concluir que a execução terminou.
3. Se terminou por falha ou reboot, confirme que não há subprocessos remanescentes. Se o mount top-level Btrfs ficava em `/run`, o reboot o terá desmontado enquanto os subvolumes readonly persistem no disco: garanta que o executor de retomada remonte `subvolid=5` e revalide os UUIDs dos snapshots contra o manifesto antes de chamar o Restic. Confira dono/modo de `rclone.conf` e a leitura pelo usuário original: um encerramento abrupto pode impedir o bloco final de restaurar permissões. Corrija somente após confirmar ausência de escritor ativo, preservando configuração e tokens; não torne o arquivo público.
4. Revalide acesso ao mesmo repositório e snapshots locais preservados. Se o token expirou, reautorize o mesmo cliente OAuth e conta; indisponibilidade de rede não justifica trocar a identidade do aplicativo. Reconcilie snapshots remotos com a tag da execução antes de decidir repetir, pois a confirmação local pode ter falhado depois da gravação remota.
5. Se a interrupção deixou lock órfão no repositório, inspecione-o com `restic list locks --no-lock` e `restic cat lock <ID> --no-lock` para comprovar que o PID e o timestamp pertencem à tentativa morta antes de executar `restic unlock` (sem `--remove-all`). Só remova lock após confirmar que não há processo `restic` ou `rclone` ativo.
6. Se não houver snapshot final confirmado e a captura continuar válida, retome pelo comando de backup da mesma execução (`--backup <RUN_DIR>`), preservando logs e `--cache-dir` anteriores. Pacotes e índices já gravados em `data/` e `index/` são reaproveitados pelo Restic na retomada (confira presença com `rclone size REMOTE:PASTA/restic/index --json` e `data --json`), deduplicando rapidamente o trecho já processado sem reenviar os blocos, mas arquivos parciais não equivalem a snapshot restaurável. Faça a leitura remota do ID final e a verificação somente após sucesso; não execute `init`, `forget` ou `prune` como solução de interrupção.

Este é um procedimento de retomada condicionada à inspeção, não garantia de que um processo desconectado sobreviverá ou de que houve retomada automática.

### Verificação e recuperação

5. Após confirmação do snapshot, execute `check --read-data` e restaure amostras de raiz/home e os artefatos boot/EFI num destino isolado. Compare conteúdo, modo e dono; teste ACL/xattrs explicitamente se forem critério de aceitação. Baixar arquivos tar de boot não testa sua extração, instalação do bootloader ou capacidade de inicialização. O check completo relê o repositório remoto e pode ser tão demorado quanto o envio; uma amostragem deve ser rotulada como tal.
6. Atualize o procedimento de recuperação com o layout observado e os caminhos reais no snapshot. Distinga o documento capturado daquele atualizado durante o envio: alterações na árvore ativa após a criação dos snapshots não entram na captura existente. Após confirmar o snapshot remoto, registre seu ID e os resultados da verificação num procedimento sem segredos e providencie sua disponibilidade fora do notebook; não afirme que a documentação mais recente está no backup sem ler a versão armazenada. Use paths estáveis ou estratégia explícita de parent se transformar a cópia única em rotina: incluir um RUN-ID nos paths impede seleção automática do snapshot pai. Só declare recuperabilidade integral depois de reconstrução e boot em destino seguro.

Referências oficiais: https://rclone.org/drive/ e https://restic.readthedocs.io/en/stable/030_preparing_a_new_repo.html . Revalide interfaces e políticas OAuth antes de orientar o usuário.
