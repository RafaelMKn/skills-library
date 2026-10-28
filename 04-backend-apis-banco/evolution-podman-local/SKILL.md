---
name: evolution-podman-local
description: "Use when installing local Evolution API with Podman."
---

# Evolution API local com Podman rootless

- Confirme tags reais no Docker Hub e release estável GitHub antes do pull; tag estável API pode ter prefixo v enquanto release não tem. Fixe RepoDigests após pull.
- Restrinja todos os nomes a um prefixo novo, API/Manager a127.0.0.1 e não publique PostgreSQL/Redis. Não toque volumes/containers de outros projetos.
- Use PostgreSQL15 e Redis7 com volumes nomeados; secrets aleatórios em env0600 dentro de diretório0700. Nunca imprima secrets nem respostas de create/connect que incluam tokens/QR.
- Manager2.3.5 possui `gzip_proxied ... must-revalidate`, inválido em nginx. Substitua por configuração nginx válida via bind mount somente leitura com SELinux :Z; preserve SPA try_files e root /usr/share/nginx/html.
- CORS restrito da API2.3.7 pode rejeitar requisição SEM Origin com500. Teste root/fetchInstances/create/connect com Origin permitido do Manager em vez de abrir CORS *.
- Frontend Manager2.3.5 guarda apiUrl, token, version e clientName em localStorage. Confirme esses nomes no bundle antes de automatizar login; não exponha API key em URL/chat/stdout.
- Teste containers running, API200 com versão, Manager200, fetchInstances autenticado e persistência após stop/start. Criar instância pessoal sem enviar mensagens, readMessages/readStatus/alwaysOnline/syncFullHistory false. QR deve ser escaneado só pelo usuário.
- Restart policy rootless não equivale a inicialização automática no login; registre a limitação e forneça start/stop por nomes explícitos. Manager shell pode exigir SIGKILL no stop; não conclua falha do backend por esse aviso.
