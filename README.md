## Observações
+ **Leitura** - Recomenda-se abrir e ler o arquivo .md no Obsidian, e o código em uma IDE (VSCode, PyCharm).
+ **Execução** - Execute o *Ligar_Painel.bat* e deixa executando. Ele será atualizado automaticamente a cada 30 minutos, incluindo o código ao iniciar junto com o sistema.
+ **Conexão com a VPN**  
	+ Antes de executar o *Ligar_Painel.bat*, verifique a conexão com o Global na barra de tarefas, no canto inferior esquerdo. 
	+ Tem que aparecer um ícone de um globo cinza, se não aparecer clique na setinha e clica nesse globo. 
	+ Coloque o endereço de portal e clica em Connect. 
	+ Faça o login colocando o e-mail, senha e o código que será recebido pelo celular através do SMS ou do Microsoft Authenticator. 
	+ Após confirmar a conexão execute o *Ligar_Painel.bat*. 
+ **Arquivo** - Não pode abrir o arquivo [erros_digitacao.xlsx](C:\Users\paulomatos\OneDrive - CENEGED - COMPANHIA ELETROMECANICA E GERENCIAMENTO DE DADOS\script erros\erros_digitacao.xlsx) localmente enquanto o código estiver sendo executado, senão ele pode travar, e só vai executar de novo no tempo programado. 
    - Caso apenas você queira ver o arquivo, tem que ir pelo Excel Online, [vindo por aqui](https://cenegedadm-my.sharepoint.com/:x:/g/personal/leitufortal02_cenegedadm_onmicrosoft_com/IQAk-TJyrR6SR4mfvFoy7gfTAVi3d5sWhZuI6Tf4JC1zFu0?e=TAToLH)
+ **Correções** - Sempre atualizar nesse arquivo a cada modificação nova! (ir na página CORRECOES)
+ **Uso de IA** - Antes de colar um código gerado por IA, leia e interprete antes de executar e testar, se possível, faça um debug do código para verificar se há erros.
+ **Página painel de erros** - É aberto quando o *Ligar_Painel.bat* é executado junto com o sistema (configurado pela TI). 
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

>26/08/2026
>>Seleção do layout /PAULO corrigida para buscar dinamicamente
>>>Ir em comentário: O robô vai olhar linha por linha procurando o /PAULO
>>Mostram colunas extraídas do SAP para facilitar ajustes futuros
>>>Ir em comentário: ADICIONE ESTE PRINT AQUI PARA DESCOBRIR OS NOMES ORIGINAIS:
>>Pesquisa a data atual no SAP
>>>Ir em comentário: Data que será pesquisada no SAP
>>Módulo de agendamento (schedule) adicionado para rodar a cada 30 minutos
>>>Ir em comentário: ESTE É O ÚNICO if __name__ == "__main__": QUE SEU SCRIPT DEVE TER

>27/08/2026
>>Salva a planilha de erros de digitação diretamente na pasta do OneDrive, mantendo os erros antigos e adicionando apenas os novos.
>>>Ir em comentário: Caminho 1: Pasta local do projeto
>>Personalização da planilha para a TV (renomeia colunas, reordena, etc.)
>>Ir em comentário: 🎨 PERSONALIZAÇÃO DA PLANILHA PARA A TV

>28/08/2026
>>Adição do arquivo .env para que seja utilizado outros logins caso a outra não esteja disponível
>>>Ir em comentário: Carrega as senhas ocultas do arquivo .env (logo no começo)
>>Logins alternativos caso o login principal esteja sendo usado
>>>Ir em comentário: Função principal para login e abertura da instalação
>>Correção do arquivo local que não estava sendo atualizado
>>>Ir em comentário: # Caminho 1: Pasta local do projeto
>>Correção do arquivo do Excel Online que não estava sendo atualizado
>>>Ir em comentário: # ☁️ FORÇAR SINCRONIZAÇÃO IMEDIATA DO ONEDRIVE

>31/08/2026
>>Criação do arquivo *Ligar_Painel.bat* ao ligar o pc do painel (falar com a TI para que o arquivo inicie o sistema com esse arquivo)
>>>Ir na pasta de script erros
>>O campo *Nota de leitura do leiturista* foi retirado
>>>Ir em comentário: Estava dando erro de layout, então comentei a linha abaixo. Se quiser preencher o código, descomente e ajuste conforme necessário.
>>O painel de erros não apresentava a data
>>>Ir em comentário: Garante que a página web continue carregando o JSON normalmente (Nota: Se não tiver o *dados_tv.json*, ele exibirá essa mensagem: Nenhum erro registrado hoje. 🎉)

> 02/09/2026
>>Adicionado ao repositório de Paulo-cesar-Matos
>>>Ir em: https://github.com/Paulo-cesar-Matos/script-leituras-ceneged.git
>>>(Recomendação de segurança: Mover o repositório caso o colaborador seja desligado, recomendável realizar o upload do repositório em uma conta do GitHub onde a empresa tenha controle!)
>>O script *Ligar_Painel.bat* baixa e salva a pasta do repositório na área de trabalho, e baixa e instala o Git para atualização dos scripts.
>>>Nota: O arquivo **.env** (arquivos de logins do SAP e do postgres) não foi upado no repositório por segurança, para isso, adicione o arquivo manualmente fisicamente em:
>>>**C:\Users\{usuario-logado}\Desktop\Painel_Erros_SAP** 
>>Adicionado o arquivo README.md para documentação de correções e observações!

>08/09/2026
>>Adicionado a opção "Baixar Excel"
>>>Ir em comentário: Opção de baixar o arquivo Excel