## Observações

- **Leitura** - Recomenda-se abrir e ler esse arquivo em uma IDE (VSCode, PyCharm)
- **Execução** - Abre o VSCode e deixa executando. Ele será atualizado automaticamente.
- **Arquivo** - Não pode abrir o arquivo [erros_digitacao.xlsx](C:\Users\paulomatos\OneDrive - CENEGED - COMPANHIA ELETROMECANICA E GERENCIAMENTO DE DADOS\script erros\erros_digitacao.xlsx) enquanto o código estiver sendo executado, senão ele pode crashar, e tem que executar de novo manualmente.
  - Caso apenas você queira ver o arquivo, tem que ir pelo Excel Online [vindo por aqui](https://cenegedadm-my.sharepoint.com/:x:/g/personal/leitufortal02_cenegedadm_onmicrosoft_com/IQAk-TJyrR6SR4mfvFoy7gfTAVi3d5sWhZuI6Tf4JC1zFu0?e=TAToLH)
- **Correções** - Sempre atualizar nesse arquivo a cada modificação nova! (ir nas últimas linhas)
- **Uso de IA** - Antes de colar um código gerado por IA, leia e interprete antes de executar e testar, se possível, faça um debug do código para verificar se há erros.
- **Página painel de erros** - É aberto quando o _Ligar_Painel.bat_ é executado junto com o sistema (configurado pela TI).
  - Nela é exibido as seguintes colunas horizontais:
    - Data
    - Instalação
    - Endereço
    - Leiturista
    - Supervisor
    - Consumo Atual
    - Média

---

## CORRECOES

### Sempre atualizar a cada modificação nova!

> 26/08/2026
>
> > Seleção do layout /PAULO corrigida para buscar dinamicamente
> >
> > > Ir em comentário: O robô vai olhar linha por linha procurando o /PAULO
> > > Mostram colunas extraídas do SAP para facilitar ajustes futuros
> > > Ir em comentário: ADICIONE ESTE PRINT AQUI PARA DESCOBRIR OS NOMES ORIGINAIS:
> > > Pesquisa a data atual no SAP
> > > Ir em comentário: Data que será pesquisada no SAP
> > > Módulo de agendamento (schedule) adicionado para rodar a cada 30 minutos
> > > Ir em comentário: ESTE É O ÚNICO if **name** == "**main**": QUE SEU SCRIPT DEVE TER

> 27/08/2026
>
> > Salva a planilha de erros de digitação diretamente na pasta do OneDrive, mantendo os erros antigos e adicionando apenas os novos.
> >
> > > Ir em comentário: Caminho 1: Pasta local do projeto
> > > Personalização da planilha para a TV (renomeia colunas, reordena, etc.)
> > > Ir em comentário: 🎨 PERSONALIZAÇÃO DA PLANILHA PARA A TV

> 28/08/2026
>
> > Adição do arquivo .env para que seja utilizado outros logins caso a outra não esteja disponível
> >
> > > Ir em comentário: Carrega as senhas ocultas do arquivo .env (logo no começo)
> > > Logins alternativos caso o login principal esteja sendo usado
> > > Ir em comentário: Função principal para login e abertura da instalação
> > > Correção do arquivo local que não estava sendo atualizado
> > > Ir em comentário: # Caminho 1: Pasta local do projeto
> > > Correção do arquivo do Excel Online que não estava sendo atualizado
> > > Ir em comentário: # ☁️ FORÇAR SINCRONIZAÇÃO IMEDIATA DO ONEDRIVE

> 31/08/2026
>
> > Criação do arquivo _Ligar_Painel.bat_ ao ligar o pc do painel (falar com a TI para que o arquivo inicie o sistema com esse arquivo)
> >
> > > Ir na pasta de script erros
> > > O campo _Nota de leitura do leiturista_ foi retirado
> > > Ir em comentário: Estava dando erro de layout, então comentei a linha abaixo. Se quiser preencher o código, descomente e ajuste conforme necessário.
> > > O painel de erros não apresentava a data
> > > Ir em comentário: Garante que a página web continue carregando o JSON normalmente (Nota: Se não tiver o dados_tv.json, ele exibirá essa mensagem: Nenhum erro registrado hoje. 🎉)
