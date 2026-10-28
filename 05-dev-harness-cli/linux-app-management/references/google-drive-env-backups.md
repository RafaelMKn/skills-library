# Google Drive e transferência de arquivos de ambiente

## 1. Definir cliente, plataforma e escopo

1. Confira o sistema real e consulte a documentação oficial de suporte do Google Drive antes de escolher instalador ou alternativa: https://support.google.com/drive/answer/2375082 . Se a plataforma não for suportada pela versão para computador, diga isso de início; ofereça Drive web ou cliente de terceiros explicitamente identificado. Não confunda site, integração Dolphin e sincronizador de pastas.
2. No Fedora KDE, descubra o que já existe com `rpm -q kio-gdrive kaccounts-providers` e valide o pacote com `rpm -V kio-gdrive`. KIO GDrive permite acesso pelo Dolphin (`dolphin gdrive:/`); não equivale ao cliente oficial nem comprova sincronização contínua.
3. Teste `kioclient --noninteractive ls gdrive:/`, extraia o identificador da conta retornado e só então liste `gdrive:/<conta>/`. Redescubra esse identificador depois de remover/adicionar uma conta: ele pode mudar. Caixa Drive marcada e conta habilitada não comprovam autorização para listar arquivos.
4. Não transforme novas tentativas de autenticação em uma sequência interminável: depois de uma tentativa, teste a operação real. Se falhar, declare o limite observado e use a alternativa independente autorizada, sem apresentar a tentativa como correção comprovada.

## 2. Inventariar `.env` por projeto sem revelar valores

1. Resolva as pastas reais, por exemplo `xdg-user-dir DESKTOP`; não presuma que se chamam Desktop ou Área de Trabalho. Confirme a raiz de projetos indicada pelo usuário.
2. Faça uma varredura recursiva com `os.walk(..., followlinks=False)` para nomes `.env` e `.env.*`. Exclua dependências e artefatos como `.git`, `node_modules`, `.venv`, `venv`, `__pycache__`, `.next`, `.nuxt`, `dist`, `build`, `.cache`, `.turbo` e `vendor`. Não siga arquivos ou diretórios simbólicos para fora da raiz.
3. Classifique os resultados antes da cópia: configuração (`.env`, `.env.local`, `.env.production` etc.); modelos (`example`, `exemplo`, `sample`, `template`, sem distinguir caixa); backups (`.bak`, `.backup`, `.old`); clones principais; QA/worktrees; arquivados. Não chame um arquivo de credencial válida só pelo nome ou tamanho.
4. Grave o inventário com caminhos, categoria e projeto, sem valores. Use Python para contar e agregar; leia esse arquivo para executar e conferir o lote, em vez de manter a lista mentalmente.
5. Para uma transferência dos ambientes reais, omita modelos e backups antigos por padrão. Preserve configurações de QA e arquivados em categorias separadas quando o usuário pedir abrangência; nunca misture um `.env` de teste ou clone antigo com o principal.

## 3. Entregar uma pasta local quando solicitado

1. Crie um destino separado com `umask 077`, diretórios 0700 e arquivos 0600. Preserve as fontes. Se o destino existir, compare antes: aceite cópia idêntica; não sobrescreva divergência silenciosamente.
2. Preserve o caminho relativo completo sob cada projeto. Um monorepo pode precisar simultaneamente de `apps/extension/.env.local`, `apps/painel/.env.local` e `supabase/functions/.env`; achatá-los como `projeto/.env` perde a associação e pode sobrescrever configurações.
3. Organize, por exemplo, `Projetos dev/<projeto>/<caminho>`, `Testes e worktrees/<clone>/<caminho>` e `Arquivados/<clone>/<caminho>`. Não interprete preservar um arquivo arquivado como autorização para usar aquele clone no trabalho atual.
4. Confira cada cópia byte a byte ou por hash e compare a quantidade com o inventário. Se houver cópias anteriores duplicadas, distinga arquivos únicos de cópias físicas na contagem.
5. Inclua manifesto sem valores com origem/destino e um LEIA-ME: conteúdo sensível em texto puro, restauração no caminho correspondente, não commitar nem compartilhar publicamente. No Dolphin, `Alt+.` mostra arquivos ocultos. Não renomeie `.env` só para torná-lo visível.
6. Informe exatamente o que foi copiado e o que ficou fora. Uma pasta local ampliada NÃO altera um backup remoto anterior; deixe essa diferença explícita. Não inicie upload em texto puro só porque o usuário pretende usar o Drive web depois.

## 4. Criar e verificar backup criptografado no Drive

1. Para upload pontual, carregue `composio-apps`, use a conexão existente e confira a identidade com GOOGLEDRIVE_GET_ABOUT. A autenticação Composio é independente da conta KDE; não imponha a configuração do Dolphin como pré-requisito quando o acesso de upload já está disponível.
2. Não envie `.env` em texto puro para staging de terceiros. Criptografe localmente primeiro. ZIP WinZip AES-256 com pyzipper em venv isolado é legível pelo 7-Zip atualizado no Windows; evite ZipCrypto. Use senha aleatória forte, arquivo de chave separado com 0600 em diretório 0700 fora de Git/Drive, e não imprima nem envie a senha ao chat. Alternativamente peça a senha via UI local segura, nunca pelo chat.
3. Preserve fontes, limite arquivos ao inventário autorizado e inclua manifesto de caminhos e hashes dentro do arquivo criptografado. Compare cada entrada extraída em memória com a fonte e teste rejeição de senha incorreta.
4. Crie pasta privada na raiz e leia permissões antes do envio. Para arquivo local, `composio execute GOOGLEDRIVE_UPLOAD_FILE --account <word_id> --file <arquivo-criptografado> -d '{"folder_to_upload_to":"<id>"}'` prepara FileUploadable automaticamente; não publique URL nem envie base64 manualmente.
5. Leia o arquivo remoto com id/name/size/parents/md5Checksum/sha256Checksum/permissions/owners/trashed/webViewLink. Confira hashes e tamanho contra o arquivo criptografado local e acesso somente do proprietário; não crie permissões públicas.
6. Entregue link, escopo dos arquivos, caminho da chave sem valor e instrução de extração no Windows. Avise que a chave precisa estar em gerenciador de senhas ou ser transferida por canal seguro antes de perder acesso ao notebook. Não coloque a chave junto do backup no Drive por conveniência.
7. Distinga backup pontual de sincronização e liste recuperação no Windows ou autenticação do cliente como pendências quando não exercitadas. Um upload verificado não prova restauração no outro sistema.
