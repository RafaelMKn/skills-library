# Facebook/Meta — permissões e isolamento no GHL

## Procedimento de investigação

1. Identifique a superfície: Settings → Integrations/Lead Ads, Social Planner ou Ad Manager. Pergunte em qual tela aparecem os ativos e com qual login; visão da agência não comprova visão do cliente.
2. Separe três camadas: autorização do perfil Meta ao aplicativo; páginas efetivamente conectadas à subconta; permissões do usuário GHL para visualizar, selecionar e alterar esses ativos. Ver nomes não comprova poder operar, e selecionar uma página não comprova isolamento dos demais módulos.
3. Releia os artigos oficiais abaixo. Use trechos do corpo da página, não só snippets. Se a extração terminar antes da seção relevante apesar de não indicar truncamento, busque HTML direto ou navegador antes de concluir que a seção não existe.
4. Relate precisamente o alcance da fonte. Os artigos de Lead Ads restringem seleção ao usuário que integrou, mas não enumeram todas as combinações de perfil Admin e visualização de páginas já conectadas. O artigo de Social Planner distingue autorização global de conexão local; não o use como garantia de isolamento em todo o produto.
5. Para comprovar a configuração real, teste com login separado de cliente, na subconta autorizada. Registre perfil, permissões, módulo, ativos visíveis, ativos selecionáveis e ações permitidas. Inclua Integrações, Ad Manager e Social Planner quando liberados. Não use o login da agência como substituto.
6. Antes de alterar produção, confirme alvo e escopo e preserve a configuração. Não desmarque páginas de outros clientes durante reautorização: a seleção mais recente do mesmo perfil/aplicativo pode revogar conexões usadas por outras subcontas.

## Fontes oficiais e limites

- Lead Ads multipágina: https://help.gohighlevel.com/support/solutions/articles/155000004537 — seção de integração afirma que somente o usuário que integrou pode selecionar as páginas, exigindo acesso completo no Facebook. Há seleção de páginas e gerenciamento posterior por subconta.
- Seletor de páginas: https://help.gohighlevel.com/support/solutions/articles/48001234487-facebook-pages-missing-in-manage-pages-during-integration- — descreve restrição do dropdown ao usuário que integrou e alerta para não desmarcar páginas usadas por outras subcontas.
- Autorização de contas sociais: https://help.gohighlevel.com/support/solutions/articles/155000008432-why-you-should-grant-access-to-all-pages-when-connecting-a-social-account — autorizar todas as páginas não conecta todas a todas as locations; reautorizar o mesmo perfil com conjunto reduzido pode interromper conexões anteriores. O contexto do artigo é Social Planner.
- Ad Manager: https://help.gohighlevel.com/support/solutions/articles/155000002434-setting-up-of-facebook-account-for-ad-manager-default-ad-manager — conexão de perfil, conta de anúncios e página; permite adicionar páginas em Platform settings. Não transportar regras de Lead Ads para esse seletor sem confirmação.
- Permissões de usuário: https://help.gohighlevel.com/support/solutions/articles/155000002544-user-roles-permissions-and-assigned-data-subaccount — Admin está sujeito às permissões granulares suportadas; User segue permissões configuradas. Copy Permissions copia configurações entre usuários, mas não comprova uma política global obrigatória para usuários futuros.

## Automação de públicos

Ao investigar CRM → público de anúncios, diferencie Custom Audience de Lookalike: adicionar contatos ao público personalizado não equivale a criar ou atualizar um semelhante. Confirme ações, conexão e elegibilidade na conta. Planilha pode ser registro auxiliar, não necessariamente ponte obrigatória. Restrição de acesso à implementação não substitui autorização para o uso de dados; mantenha bases segregadas por cliente e finalidade explícita.

Feche as regras nesta ordem:
1. Defina sinais comerciais distintos; não trate visita realizada, proposta enviada e venda fechada automaticamente como um único MQL. Valide se alimentarão públicos separados ou agregados.
2. Separe novas qualificações de carga histórica; autorização para automatizar eventos futuros não aprova exportação retroativa.
3. Defina repetição, múltiplas oportunidades e correção sem duplicação. Distinga perda comercial de marcação incorreta: um marco realmente ocorrido pode continuar válido mesmo após perda; permanência depende da finalidade e da regra aprovada, não apenas da etapa atual.
4. Especifique remoção por erro ou retirada de autorização e tratamento de falhas com responsável. Confirme que as ações disponíveis suportam a regra antes de prometer execução nativa completa.
5. No aceite, diferencie execução da ação, recebimento pela Meta e correspondência do contato no público. Não prometa correspondência de todos, tamanho mínimo ou desempenho de anúncios; registre qual evidência o provedor realmente disponibiliza.

Fontes de capacidades a reler: ações de workflow em https://help.gohighlevel.com/support/solutions/articles/155000002294 e Google Sheets em https://help.gohighlevel.com/support/solutions/articles/48001238162. Confira custos e habilitação na conta antes de incluir Sheets como etapa obrigatória.

## Entrega

Comece com a conclusão e seu grau de comprovação. Em seguida apresente evidência literal curta, o que ela sustenta, o que não sustenta e o teste faltante. Não transforme ausência de teste em garantia de isolamento nem relato do usuário em vazamento confirmado.
