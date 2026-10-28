# Implantação de mudanças de voz no Desktop

## Procedimento

1. Confirme o launcher e o pacote usados pelo processo aberto antes de modificar o Desktop. Preserve a sessão do usuário; não reinicie o gateway para carregar uma mudança apenas de Electron.
2. Reaproveite `wake.detected` para restaurar/mostrar/focar a janela que recebeu o evento. Resolva a janela pelo `event.sender` do IPC, não por uma referência global à janela principal: múltiplas janelas podem pertencer a perfis diferentes. Não ligue foco a eventos gerais. No Wayland, trate foco negado com pedido de atenção, sem prometer foco obrigatório.
3. Execute testes específicos de janela minimizada, oculta, visível, inexistente e isolamento entre janelas. Separe resultado desses testes do teste real com microfone. Não classifique falhas da suíte completa como preexistentes sem baseline.
4. Gere o build no diretório `apps/desktop` e empacote em saída separada do aplicativo aberto:
   ```bash
   npm run build
   npm run builder -- --dir --publish never --config.directories.output=<diretorio-de-staging-absoluto>
   ```
   Use staging apropriado à instalação; scratch serve para validação temporária, não para autostart permanente.
5. Confira o conteúdo do pacote via API ASAR, não procurando strings no arquivo bruto: arquivos podem estar em `app.asar.unpacked`, e um resultado negativo na busca binária não prova ausência do código.
   ```javascript
   const asar = require('@electron/asar')
   for (const file of ['dist/electron-main.mjs', 'dist/electron-preload.js']) {
     const content = asar.extractFile('/caminho/resources/app.asar', file)
     console.log(file, content.includes(Buffer.from('hermes:window:raise-for-wake')))
   }
   ```
   Adapte o marcador ao recurso realmente implementado. Verifique também o renderer quando a mudança envolver sua lógica.
6. Solicite autorização para fechar/reabrir o Desktop se houver sessão ativa. Para troca de provider Python, instale o extra declarado com `hermes pm install --extra <extra>` e releia a configuração após `hermes config set`; reabra o backend do Desktop quando ele já tiver importado o módulo antigo. Não reconstrua Electron para uma mudança exclusivamente Python.
7. Antes de encerrar, registre a árvore de processos do Desktop e os PIDs do gateway e das pontes que devem permanecer. Identifique o processo principal efetivo do Electron, não apenas o primeiro processo com nome Hermes: encerrar um launcher/zygote pode deixar a janela e o backend antigos vivos. Após encerrar somente o alvo autorizado, confirme que o backend antigo saiu antes de relançar.
8. Reabra com `hermes desktop --skip-build` quando o pacote existente for o alvo verificado. Se o terminal não herdar o ambiente gráfico, obtenha `DISPLAY`, `WAYLAND_DISPLAY`, `XDG_RUNTIME_DIR` e `DBUS_SESSION_BUS_ADDRESS` da sessão gráfica do usuário; não adivinhe seus valores. Passe os valores observados ao launcher e confira o log do processo lançado, pois obter um PID não prova que Electron abriu.
9. Exija `HERMES_BACKEND_READY` e `wake.start(gui): listening for '<frase>' (<provider>)` no novo processo, e confirme que gateway e pontes mantiveram seus PIDs. Só depois solicite a chamada real: palavra de ativação, pausa, comando curto. Confira detecção → gravação → transcrição → resposta → TTS; depois repita com janela minimizada. Relate separadamente: configurado, testado offline, carregado, escutando e validado com voz real.

## Autostart e conversa

- Crie uma entrada `.desktop` de nome fixo em `~/.config/autostart`, com `Exec` absoluto, depois de conferir entradas existentes e o mecanismo de instância única. Valide com `desktop-file-validate`; isso não prova o login real.
- Não prometa início minimizado sem flag ou comportamento verificado. Autostart cobre o próximo login, não mantém o detector vivo após encerrar totalmente o Desktop.
- Configure `voice.auto_tts` e palavras de encerramento em PT-BR preservando as existentes. Confira no código se o encerramento exige frase inteira para evitar tratar um pedido contendo a palavra como comando de parar.
- Faça backup dos valores alterados e registre rollback de configuração, volume e autostart separadamente do rollback do pacote.
