import os
import time
import sys
import subprocess
from typing import Optional, Iterable
import win32com.client
import pyperclip
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from psycopg2.extras import execute_values
from datetime import datetime
from pathlib import Path
import schedule
from dotenv import load_dotenv

# Carrega as senhas ocultas do arquivo .env
load_dotenv()

# ========= CONFIG =========
CONNECTION_NAME = "SISTEMA DE LEITURAS"
USERNAME = os.getenv("SAP_USER_1")
PASSWORD = os.getenv("SAP_PASSWORD_1")
SESSION_INDEX = 0
TARGET_NODE_ID = "F00009"

SAP_LOGON_PATH = r"C:\Program Files (x86)\SAP\FrontEnd\SAPgui\saplogon.exe"

INSTALL_FIELD_ID = "wnd[0]/usr/ctxtEANLD-ANLAGE"
TREE_PATH = "wnd[0]/usr/cntlIMAGE_CONTAINER/shellcont/shell/shellcont[0]/shell"
# ==========================

# ========= CONFIG  BD =========
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
# ==========================


def encerrar_sap():
    try:
        print("🧹 Encerrando SAP...")
        subprocess.run(
            ["taskkill", "/F", "/IM", "saplogon.exe"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        subprocess.run(
            ["taskkill", "/F", "/IM", "sapgui.exe"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print("✅ SAP encerrado.")
    except Exception as e:
        print(f"⚠️ Falha ao encerrar SAP: {e}")


def abrir_sap_logon():
    print("🚀 AI - Análise de Erros iniciada...")
    subprocess.Popen(SAP_LOGON_PATH)
    time.sleep(1)


def _children(obj) -> Iterable:
    try:
        return [obj.Children(i) for i in range(obj.Children.Count)]
    except Exception:
        try:
            return list(obj.Children)
        except Exception:
            return []


def _children_count(obj) -> int:
    try:
        return obj.Children.Count
    except Exception:
        try:
            return len(obj.Children)
        except Exception:
            return 0


def _child(obj, idx: int):
    try:
        return obj.Children(idx)
    except Exception:
        return obj.Children.Item(idx)


def _safe_attr(obj, name, default=None):
    try:
        return getattr(obj, name)
    except Exception:
        return default


def get_application():
    sap_gui_auto = win32com.client.GetObject("SAPGUI")
    try:
        app = sap_gui_auto.GetScriptingEngine
        if app:
            return app
    except Exception:
        pass
    try:
        app = sap_gui_auto.GetScriptingEngine()
        if app:
            return app
    except Exception:
        pass
    ctrl = win32com.client.gencache.EnsureDispatch("Sapgui.ScriptingCtrl.1")
    return _safe_attr(ctrl, "Application", ctrl)


def open_connection_by_name(app, name: str):
    try:
        return app.OpenConnection(name, True)
    except Exception:
        return app.OpenConnectionByConnectionString(name, True)


def get_session_after_open(conn) -> object:
    for _ in range(30):
        if _children_count(conn) > 0:
            return _child(conn, SESSION_INDEX)
        time.sleep(0.5)
    raise RuntimeError("A sessão não ficou disponível após abrir a conexão.")


# Função principal para login e abertura da instalação
def login_and_open_instalacao(user: str, pwd: str):
    abrir_sap_logon()

    app = get_application()

    if not app:
        raise RuntimeError("SAP GUI Application não encontrada (habilite Scripting).")

    connection = open_connection_by_name(app, CONNECTION_NAME)
    session = get_session_after_open(connection)

    session.findById("wnd[0]").maximize()

    session.findById("wnd[0]/usr/txtRSYST-BNAME").text = user

    pwd_field = session.findById("wnd[0]/usr/pwdRSYST-BCODE")
    pwd_field.text = pwd
    pwd_field.setFocus()

    session.findById("wnd[0]").sendVKey(0)
    time.sleep(1.5)

    # ---> VERIFICA SE DEU ERRO OU SE ABRIR A TELA DE LOGON MÚLTIPLO <---
    # Se o SAP abrir uma janela adicional (wnd[1]), significa que o logon foi barrado
    if session.Children.Count > 1:
        print(f"⚠️ Conta {user} em uso (Logon Múltiplo). Cancelando...")
        return None

    # Verifica se apareceu mensagem de erro na barra inferior (ex: senha incorreta)
    status_bar = session.findById("wnd[0]/sbar", False)
    if status_bar and status_bar.messageType == "E":
        print(f"⚠️ Erro ao tentar {user}: {status_bar.text}")
        return None

    return session


def abrir_relatorio_leituras(session):
    tree = session.findById(
        "wnd[0]/usr/cntlIMAGE_CONTAINER/" "shellcont/shell/shellcont[0]/shell"
    )

    tree.selectedNode = "F00006"
    tree.doubleClickNode("F00006")

    session.findById("wnd[0]/usr/ctxtP_REPORT").text = "AQA0SYSTQV000009LEITURAS======"

    session.findById("wnd[0]/tbar[1]/btn[8]").press()

    # ⏱️ PAUSA ADICIONADA AQUI: Dá tempo para o SAP desenhar a tela antes da extração
    time.sleep(3)


EXEC_KEYWORDS = ["execut", "execute", "ausführen", "pesquis", "search", "run"]


def extrair_leituras_sap(session, data_leitura):
    try:
        # Preenche a data da leitura
        session.findById("wnd[0]/usr/ctxtSP$00002-LOW").text = data_leitura

        # Estava dando erro de layout, então comentei a linha abaixo. Se quiser preencher o código, descomente e ajuste conforme necessário.
        # Preenche o código
        # session.findById(
        #    "wnd[0]/usr/ctxtSP$00003-LOW"
        # ).text = "000"

        # Executa o relatório
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        time.sleep(3)

        # Localiza a tabela de resultados
        tabela = session.findById("wnd[0]/usr/cntlCONTAINER/shellcont/shell")

        # Abre a seleção de variantes
        tabela.pressToolbarButton("&MB_VARIANT")

        # Seleciona a tabela de variantes
        variante = session.findById(
            "wnd[1]/usr/ssubD0500_SUBSCREEN:"
            "SAPLSLVC_DIALOG:0501/"
            "cntlG51_CONTAINER/shellcont/shell"
        )

        # Conta quantas opções de layout existem na janelinha
        total_linhas = variante.RowCount
        layout_encontrado = False

        # O robô vai olhar linha por linha procurando o /PAULO
        for i in range(total_linhas):
            # A coluna técnica que guarda o nome do layout no SAP se chama "VARIANT"
            nome_layout = variante.GetCellValue(i, "VARIANT")

            if nome_layout == "/PAULO":
                variante.currentCellRow = i
                variante.selectedRows = str(i)
                variante.clickCurrentCell()
                layout_encontrado = True
                break  # Encontrou, pode parar de procurar!

        # Trava de segurança: se alguém deletar o layout /PAULO do SAP
        if not layout_encontrado:
            print(
                "⚠️ AVISO: O layout '/PAULO' não foi encontrado! O script vai falhar se as colunas estiverem erradas."
            )
            # Se não achar, clica na linha 0 só para tentar seguir ou avise o erro
            variante.currentCellRow = 0
            variante.selectedRows = "0"
            variante.clickCurrentCell()

        # Abre o menu de exportação
        tabela.pressToolbarContextButton("&MB_EXPORT")

        # Seleciona a opção Clipboard
        tabela.selectContextMenuItem("&PC")

        # Seleciona a opção de Clipboard
        opcao_clipboard = session.findById(
            "wnd[1]/usr/subSUBSCREEN_STEPLOOP:"
            "SAPLSPO5:0150/sub:"
            "SAPLSPO5:0150/"
            "radSPOPLI-SELFLAG[4,0]"
        )

        opcao_clipboard.select()
        opcao_clipboard.setFocus()

        # Confirma a exportação
        session.findById("wnd[1]/tbar[0]/btn[0]").press()

        time.sleep(2)

        # Lê o conteúdo do Clipboard
        texto = pyperclip.paste()

        return texto

    except Exception as e:
        print(f"❌ Erro ao extrair dados do SAP: {e}")
        return None


def converter_texto_sap_para_dataframe(texto):
    linhas = texto.splitlines()

    linhas = [linha.strip() for linha in linhas if linha.strip()]

    indice_cabecalho = None

    for i, linha in enumerate(linhas):
        if "Instalação" in linha and "Dt.leitura" in linha:
            indice_cabecalho = i
            break

    if indice_cabecalho is None:
        raise ValueError("Cabeçalho da tabela não encontrado.")

    cabecalho = linhas[indice_cabecalho]

    colunas = [coluna.strip() for coluna in cabecalho.split("|") if coluna.strip()]

    dados = []

    for linha in linhas[indice_cabecalho + 1 :]:

        if set(linha) <= {"-", " "}:
            continue

        if "|" not in linha:
            continue

        valores = [valor.strip() for valor in linha.split("|") if valor.strip()]

        if len(valores) == len(colunas):
            dados.append(valores)

    df = pd.DataFrame(dados, columns=colunas)

    # 🔴 ADICIONE ESTE PRINT AQUI PARA DESCOBRIR OS NOMES ORIGINAIS:
    print("\n🧐 Colunas extraídas do SAP:", df.columns.tolist())

    # Renomeia as colunas
    df = df.rename(
        columns={
            "Instalação": "instalacao",
            "Dt.leitura": "data_leitura",
            "ML": "ml",
            "NtLei": "ntlei",
            "Unid.leit.": "unid_leit",
            "Consumo atual": "consumo_atual",
            "SL": "sl",
            "TL": "tl",
            "Modif.por": "br",
            "Reg.": "reg",
            "CasaAntVírg.": "leitura",
            "Equipamento": "medidor",
        }
    )

    df["instalacao"] = df["instalacao"].astype(int)

    df["data_leitura"] = pd.to_datetime(df["data_leitura"], format="%d.%m.%Y").dt.date

    df["consumo_atual"] = (
        df["consumo_atual"]
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )

    df["leitura"] = (
        df["leitura"]
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )

    return df


def criar_tabela_consumo_diario():
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="postgres",
        user="postgres",
        password="root",
    )

    cursor = conn.cursor()

    cursor.execute("""
        CREATE SCHEMA IF NOT EXISTS "CENEGED";
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS "CENEGED"."tb_consumo_diario" (

            instalacao BIGINT,

            data_leitura DATE,

            ml VARCHAR(10),

            ntlei VARCHAR(10),

            unid_leit VARCHAR(30),

            consumo_atual NUMERIC(20, 6),

            sl VARCHAR(10),

            tl VARCHAR(10),

            br VARCHAR(30),

            reg VARCHAR(10),

            leitura float8,

            medidor VARCHAR(30)

        );
    """)

    conn.commit()

    cursor.close()
    conn.close()

    print("✅ Tabela CENEGED.tb_consumo_diario criada/verificada.")


def inserir_consumo_diario(df):

    if df.empty:
        print("⚠️ Nenhum dado novo para inserir.")
        return

    # Remove todas as instalações que possuem
    # mais de um registro na mesma data
    qtd_registros = (
        df.groupby(["instalacao", "data_leitura"]).size().reset_index(name="qtd")
    )

    registros_duplicados = qtd_registros[qtd_registros["qtd"] > 1]

    df = df.merge(
        registros_duplicados[["instalacao", "data_leitura"]],
        on=["instalacao", "data_leitura"],
        how="left",
        indicator=True,
    )

    # Mantém apenas instalações que aparecem
    # uma única vez na data
    df = df[df["_merge"] == "left_only"].drop(columns=["_merge"])

    if df.empty:
        print(
            "⚠️ Nenhum registro válido após remover "
            "instalações com múltiplas leituras."
        )
        return

    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )

    cursor = conn.cursor()

    colunas = [
        "instalacao",
        "data_leitura",
        "ml",
        "ntlei",
        "unid_leit",
        "consumo_atual",
        "sl",
        "tl",
        "br",
        "reg",
        "leitura",
        "medidor",
    ]

    valores = [tuple(row) for row in df[colunas].itertuples(index=False, name=None)]

    query = """
        INSERT INTO "CENEGED"."tb_consumo_diario" (
            instalacao,
            data_leitura,
            ml,
            ntlei,
            unid_leit,
            consumo_atual,
            sl,
            tl,
            br,
            reg,
            leitura,
            medidor
        )
        VALUES %s

        ON CONFLICT (
            instalacao,
            data_leitura,
            reg
        )

        DO NOTHING;
    """

    execute_values(cursor, query, valores)

    conn.commit()

    print(f"✅ {cursor.rowcount} novos registros inseridos.")

    cursor.close()
    conn.close()


def obter_siglas_cat():
    engine = create_engine(
        f"postgresql+psycopg2://"
        f"{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    query = """
        SELECT DISTINCT sigla
        FROM "CENEGED"."TB-CAT"
        WHERE sigla IS NOT NULL
    """

    df_cat = pd.read_sql(query, engine)

    engine.dispose()

    # Padroniza as siglas
    siglas = df_cat["sigla"].astype(str).str.strip().str.upper().tolist()

    return siglas


def filtrar_leituras_por_sigla(df):
    siglas_validas = obter_siglas_cat()

    # Pega os dois primeiros caracteres da unidade de leitura
    df["sigla"] = df["unid_leit"].astype(str).str[:2].str.upper()

    # Mantém apenas siglas que existem na TB-CAT
    df = df[df["sigla"].isin(siglas_validas)].copy()

    # Remove a coluna auxiliar
    df = df.drop(columns=["sigla"])

    return df


def filtrar_consumo(df):

    df = df[df["consumo_atual"] <= 10000].copy()

    return df


def limpar_dados_antigos(data_leitura):

    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )

    cursor = conn.cursor()

    query = """
        DELETE FROM "CENEGED"."tb_consumo_diario"
        WHERE data_leitura <> %s;
    """

    cursor.execute(query, (data_leitura,))

    registros_excluidos = cursor.rowcount

    conn.commit()

    cursor.close()
    conn.close()

    print(f"🧹 {registros_excluidos} registros antigos removidos.")


def identificar_consumos_fora_do_limite():

    engine = create_engine(
        f"postgresql+psycopg2://"
        f"{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    query = """
    SELECT
        c.data_leitura,
        c.instalacao,
        c.medidor,
        m.media_consumo,
        c.consumo_atual,
        c.leitura,
        c.br,
        a.leiturista,
        a.supervisor,
        m.latitude,
        m.longitude
    FROM "CENEGED"."tb_consumo_diario" c
    INNER JOIN "CENEGED"."tb_media_consumo" m
        ON c.instalacao = m.instalacao
    LEFT JOIN "CENEGED"."TB-AGENTES" a
        ON c.br = a.br
    WHERE
        c.consumo_atual > m.consumo_maximo_esperado
        AND c.consumo_atual <> c.leitura
        AND c.sl <> '2'
        AND c.consumo_atual > m.media_consumo * 1.50
        AND c.consumo_atual >= 100
        AND ABS(c.consumo_atual - m.media_consumo) < 1000
        AND m.media_consumo < 500
        AND m.media_consumo > 10
        AND m.coeficiente_variacao <= 0.50
        AND m.coeficiente_variacao > 0;
"""
    df_anomalias = pd.read_sql(query, engine)

    engine.dispose()

    return df_anomalias


def identificar_erros_digitacao(df_anomalias, tolerancia=0.15):

    import math

    vizinhos = {
        "0": [],
        "1": [],
        "2": ["1", "0"],
        "3": ["2"],
        "4": ["1"],
        "5": ["4", "2"],
        "6": ["5", "3"],
        "7": ["4"],
        "8": ["7", "5"],
        "9": ["8", "6"],
    }

    df = df_anomalias.copy()

    df["possivel_erro_digitacao"] = False
    df["consumo_simulado"] = None
    df["digito_testado"] = None

    for idx, row in df.iterrows():

        leitura = int(row["leitura"])
        consumo = int(row["consumo_atual"])
        media = float(row["media_consumo"])

        leitura_anterior = leitura - consumo

        diferenca = consumo - media

        if diferenca <= 100:
            continue

        # Descobre a casa (1,10,100,1000...)
        casa = 10 ** int(math.log10(diferenca))

        leitura_str = str(leitura)

        # posição do dígito a partir da direita
        pos = len(leitura_str) - len(str(casa))

        if pos < 0:
            continue

        digito = leitura_str[pos]

        if digito not in vizinhos:
            continue

        encontrou = False

        for novo_digito in vizinhos[digito]:

            nova_leitura = list(leitura_str)
            nova_leitura[pos] = novo_digito
            nova_leitura = int("".join(nova_leitura))

            novo_consumo = nova_leitura - leitura_anterior

            if abs(novo_consumo - media) <= media * tolerancia:

                df.at[idx, "possivel_erro_digitacao"] = True
                df.at[idx, "consumo_simulado"] = novo_consumo
                df.at[idx, "digito_testado"] = f"{digito}->{novo_digito}"

                encontrou = True
                break

        if not encontrou:
            df.at[idx, "possivel_erro_digitacao"] = False

    return df


def busca_endereco(session, df_novos):

    enderecos = []

    primeira_consulta = True

    total = len(df_novos)

    print(f"\n🏠 Buscando endereços de {total} clientes...")

    session.findById("wnd[0]").maximize()

    for i, (_, row) in enumerate(df_novos.iterrows(), start=1):

        print(f"📍 [{i}/{total}] Instalação: {row['instalacao']}")

        if primeira_consulta:

            session.findById("wnd[0]").sendVKey(12)
            session.findById("wnd[0]").sendVKey(12)
            session.findById("wnd[0]").sendVKey(12)

            shell = session.findById(
                "wnd[0]/usr/cntlIMAGE_CONTAINER/shellcont/shell/shellcont[0]/shell"
            )

            shell.selectedNode = "F00002"
            shell.doubleClickNode("F00002")

            primeira_consulta = False

        else:

            # Volta para a tela de pesquisa
            session.findById("wnd[0]").sendVKey(12)

        campo = session.findById("wnd[0]/usr/ctxtEANLD-ANLAGE")

        campo.text = str(row["instalacao"])

        session.findById("wnd[0]").sendVKey(0)

        endereco = session.findById("wnd[0]/usr/txtEANLD-LINE1").text

        enderecos.append(endereco)

    df_novos["endereco"] = enderecos

    print("✅ Busca de endereços concluída.")

    return df_novos


# Função de logins alt SAP
def main(argv: Optional[list] = None):

    # Data que será pesquisada no SAP
    data_sap = datetime.now().strftime("%d.%m.%Y")
    data_leitura = datetime.strptime(data_sap, "%d.%m.%Y").date()

    print("🔐 Iniciando logins SAP...")

    session = None
    usuario_conectado = None

    # Tenta até 5 contas diferentes configuradas no .env
    for i in range(1, 6):
        user = os.getenv(f"SAP_USER_{i}")
        pwd = os.getenv(f"SAP_PASSWORD_{i}")

        if not user or not pwd:
            continue  # Se a conta não existir no .env, pula para o próximo número

        print(f"\n🔄 Tentativa {i} - Testando login com: {user}")

        try:
            session = login_and_open_instalacao(user, pwd)

            if session:
                print(f"✅ Sucesso! Logado com a conta {user}.")
                usuario_conectado = user
                break  # Encontrou uma conta livre! Sai do loop e vai trabalhar.

        except Exception as e:
            print(f"⚠️ Falha inesperada com {user}: {e}")

        # Se chegou aqui, é porque a conta falhou (logon múltiplo ou erro).
        # Encerra o processo do SAP para abrir limpo na próxima tentativa.
        encerrar_sap()
        time.sleep(2)

    # Trava de segurança: Se esgotou todas as 5 contas e nenhuma deu certo
    if not session:
        print(
            "\n❌ Todas as contas cadastradas estão bloqueadas ou em uso. Abortando esta extração."
        )
        return  # Interrompe a execução e o schedule tentará novamente daqui a 30 minutos

    print("🚀 Abrindo relatório de leituras...")

    abrir_relatorio_leituras(session)

    print("📊 Iniciando extração...")

    texto = extrair_leituras_sap(session, data_sap)

    if texto:

        print("\n📋 Conteúdo extraído do Clipboard:\n")

        with open("clipboard_sap.txt", "w", encoding="utf-8") as arquivo:

            arquivo.write(texto)

        print("✅ Conteúdo salvo em clipboard_sap.txt")

        # Converte o texto do SAP para DataFrame
        df = converter_texto_sap_para_dataframe(texto)

        print(f"📊 Total de leituras extraídas: " f"{len(df)}")

        # Filtra apenas as siglas existentes na TB-CAT
        df = filtrar_leituras_por_sigla(df)

        print(f"✅ Leituras após filtro de CAT: " f"{len(df)}")

        # Remove consumos acima de 1000
        df = filtrar_consumo(df)

        print(f"✅ Leituras com consumo até 1000: " f"{len(df)}")

        # Cria a tabela caso ainda não exista
        criar_tabela_consumo_diario()

        # Remove registros de datas diferentes
        limpar_dados_antigos(data_leitura)

        # Insere os dados do dia
        # Duplicidades são ignoradas através de:
        # instalacao + data_leitura + reg
        inserir_consumo_diario(df)

        print("✅ Dados inseridos no PostgreSQL.")

        # Identifica consumos fora dos limites esperados
        df_anomalias = identificar_consumos_fora_do_limite()

        print("\n⚠️ Consumos fora dos limites esperados:")

        df_anomalias = identificar_erros_digitacao(df_anomalias)

        arquivo_historico = "historico_processado.txt"

        # Caminho 1: Pasta local do projeto
        arquivo_excel = "erros_digitacao.xlsx"

        # Caminho 2: Sua pasta do OneDrive (com o 'r' na frente para aceitar as barras)
        arquivo_onedrive = r"C:\Users\paulomatos\OneDrive - CENEGED - COMPANHIA ELETROMECANICA E GERENCIAMENTO DE DADOS\script erros\erros_digitacao.xlsx"
        arquivo_excel = arquivo_onedrive

        # Apenas possíveis erros de digitação
        df_novos = df_anomalias[df_anomalias["possivel_erro_digitacao"]].copy()

        # Chave única
        df_novos["chave"] = (
            df_novos["instalacao"].astype(str) + "_" + df_novos["br"].astype(str)
        )

        # Lê histórico
        if Path(arquivo_historico).exists():

            with open(arquivo_historico, "r", encoding="utf-8") as f:

                historico = set(linha.strip() for linha in f)

        else:

            historico = set()

        # Apenas registros inéditos
        df_novos = df_novos[~df_novos["chave"].isin(historico)]

        # Recria a planilha somente com os novos
        if not df_novos.empty:
            print(f"🏠 Buscando endereços de {len(df_novos)} clientes...")
            df_novos = busca_endereco(session, df_novos)

            # Salva no arquivo de histórico para não repetir no próximo ciclo
            with open(arquivo_historico, "a", encoding="utf-8") as f:
                for chave in df_novos["chave"]:
                    f.write(chave + "\n")

            # ==========================================================
            # 🎨 PERSONALIZAÇÃO DA PLANILHA PARA A TV
            # ==========================================================
            df_para_planilha = df_novos.drop(columns=["chave"]).copy()

            # 1. Renomeia os cabeçalhos para português amigável
            df_para_planilha = df_para_planilha.rename(
                columns={
                    "instalacao": "Instalação",
                    "medidor": "Medidor",
                    "media_consumo": "Média Consumo",
                    "consumo_atual": "Consumo Atual",
                    "leitura": "Leitura",
                    "br": "Matrícula (BR)",
                    "leiturista": "Leiturista",
                    "supervisor": "Supervisor",
                    "endereco": "Endereço",
                    "possivel_erro_digitacao": "Possível Erro",
                    "consumo_simulado": "Consumo Simulado",
                    "digito_testado": "Dígito Testado",
                }
            )

            # 2. Deixa as colunas mais importantes na frente (opcional)
            colunas_desejadas = [
                "Instalação",
                "Endereço",
                "Leiturista",
                "Supervisor",
                "Consumo Atual",
                "Média Consumo",
                "Leitura",
                "Medidor",
            ]
            colunas_finais = [
                c for c in colunas_desejadas if c in df_para_planilha.columns
            ] + [c for c in df_para_planilha.columns if c not in colunas_desejadas]

            df_para_planilha = df_para_planilha[colunas_finais]
            # ==========================================================

            # ---> SE TIVER ERRO NOVO: Acumula os dados na planilha <---
            # Verifica se o arquivo já existe no OneDrive para somar os novos erros aos antigos
            if Path(arquivo_excel).exists():
                df_antigo = pd.read_excel(arquivo_excel)
                # Junta o que já estava lá com os novos erros já formatados
                df_total = pd.concat([df_antigo, df_para_planilha], ignore_index=True)
                # Remove eventuais duplicadas se houver (usando o nome novo da coluna "Instalação")
                df_total = df_total.drop_duplicates(
                    subset=["Instalação", "Matrícula (BR)"], keep="last"
                )
            else:
                df_total = df_para_planilha

            # Salva o arquivo atualizado direto na pasta do OneDrive
            df_total.to_excel(arquivo_excel, index=False)
            df_total.to_json("dados_tv.json", orient="records", force_ascii=False)

            # ==========================================================
            # ☁️ FORÇAR SINCRONIZAÇÃO IMEDIATA DO ONEDRIVE
            # ==========================================================
            try:
                # Abre o Excel em segundo plano (invisível)
                excel = win32com.client.DispatchEx("Excel.Application")
                excel.Visible = False
                excel.DisplayAlerts = False

                # Abre, salva e fecha a planilha rapidamente para acionar a nuvem
                wb = excel.Workbooks.Open(arquivo_excel)
                wb.Save()
                wb.Close()
                excel.Quit()
                print("☁️ Sincronização com o Excel Online forçada com sucesso!")
            except Exception as e:
                print(f"⚠️ Aviso ao forçar sincronização do Excel: {e}")
            # ==========================================================
            print(
                f"✅ Planilha do OneDrive atualizada com {len(df_novos)} novos erros!"
            )
        else:
            print("✅ Nenhum erro novo nesta rodada.")

            # Garante que a página web continue carregando o JSON normalmente
            if Path(arquivo_excel).exists():
                pd.read_excel(arquivo_excel).to_json(
                    "dados_tv.json", orient="records", force_ascii=False
                )
            else:
                # SE DELETARAM OS ARQUIVOS E NÃO HÁ ERROS: Cria um JSON vazio para a TV não travar
                with open("dados_tv.json", "w", encoding="utf-8") as f:
                    f.write("[]")


# Agenda de novas extrações a cada 30 minutos
def rotina_de_extracao():
    print("\n🔄 Iniciando remessa de extração...")
    try:
        main(sys.argv)
    except Exception as e:
        print(f"\n❌ Erro durante a extração: {e}")
    finally:
        # Garante que o SAP fecha ao final do processo (com sucesso ou erro)
        encerrar_sap()
        print("\n⏳ Extração concluída! Agendamento reativado.")


# ESTE É O ÚNICO if __name__ == "__main__": QUE SEU SCRIPT DEVE TER
if __name__ == "__main__":
    try:
        print("▶️ Executando a primeira vez imediatamente...")
        rotina_de_extracao()

        # Define a regra do agendamento (a cada 30 minutos)
        schedule.every(30).minutes.do(rotina_de_extracao)

        print("\n⏰ Agendador iniciado. (Pressione Ctrl+C para sair)")

        # Loop infinito bem mais leve, focado apenas em checar o relógio
        while True:
            # Roda as tarefas que estão no horário
            schedule.run_pending()

            # --- Lógica do Timer Visual ---
            proxima_execucao = schedule.next_run()
            if proxima_execucao:
                # Calcula os segundos entre agora e a próxima execução
                tempo_restante = (proxima_execucao - datetime.now()).total_seconds()

                if tempo_restante > 0:
                    minutos, segundos = divmod(int(tempo_restante), 60)
                    # Adicionei espaços extras no final do print para limpar sujeiras na linha
                    print(
                        f"Próxima extração em: {minutos:02d}:{segundos:02d}          ",
                        end="\r",
                    )

            time.sleep(1)  # Aguarda 1 segundo antes de atualizar a tela

    except KeyboardInterrupt:
        print("\n\n🛑 Execução encerrada manualmente pelo usuário (Ctrl+C).")
        encerrar_sap()  # Fecha o SAP caso você cancele no meio da extração
