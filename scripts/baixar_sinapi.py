import requests
import pandas as pd
import json
import os
import zipfile
import io
from datetime import datetime
import re

# Lista de UFs disponíveis na SINAPI
UFS_DISPONIVEIS = {
    "SP": "https://www.caixa.gov.br/Downloads/sinapi/SINAPI_precos_referencia_SP.zip",
    "RJ": "https://www.caixa.gov.br/Downloads/sinapi/SINAPI_precos_referencia_RJ.zip",
    "MG": "https://www.caixa.gov.br/Downloads/sinapi/SINAPI_precos_referencia_MG.zip",
    "RS": "https://www.caixa.gov.br/Downloads/sinapi/SINAPI_precos_referencia_RS.zip",
    "BA": "https://www.caixa.gov.br/Downloads/sinapi/SINAPI_precos_referencia_BA.zip",
    "PR": "https://www.caixa.gov.br/Downloads/sinapi/SINAPI_precos_referencia_PR.zip",
    "SC": "https://www.caixa.gov.br/Downloads/sinapi/SINAPI_precos_referencia_SC.zip",
    "GO": "https://www.caixa.gov.br/Downloads/sinapi/SINAPI_precos_referencia_GO.zip",
    "PE": "https://www.caixa.gov.br/Downloads/sinapi/SINAPI_precos_referencia_PE.zip",
    "CE": "https://www.caixa.gov.br/Downloads/sinapi/SINAPI_precos_referencia_CE.zip",
    "DF": "https://www.caixa.gov.br/Downloads/sinapi/SINAPI_precos_referencia_DF.zip",
    "BR": "https://www.caixa.gov.br/Downloads/sinapi/SINAPI_precos_referencia_Brasil.zip"
}

def baixar_sinapi_por_uf(uf="SP"):
    """
    Baixa os dados da SINAPI para uma UF específica
    """
    print(f"🔄 Baixando SINAPI para {uf} - {datetime.now()}")
    
    url = UFS_DISPONIVEIS.get(uf.upper(), UFS_DISPONIVEIS["SP"])
    
    # Mapeamento de insumos para busca
    insumos_procurados = {
        "cobre_1_4": ["COBRE", "1/4", "TUBO"],
        "cobre_3_8": ["COBRE", "3/8", "TUBO"],
        "cobre_1_2": ["COBRE", "1/2", "TUBO"],
        "cobre_5_8": ["COBRE", "5/8", "TUBO"],
        "cobre_7_8": ["COBRE", "7/8", "TUBO"],
        "isolante_9mm": ["ISOLANTE", "ELASTOMERICO", "9mm"],
        "isolante_12mm": ["ISOLANTE", "ELASTOMERICO", "12mm"],
        "isolante_19mm": ["ISOLANTE", "ELASTOMERICO", "19mm"],
        "eletroduto_25": ["ELETRODUTO", "CORRUGADO", "25mm"],
        "eletroduto_32": ["ELETRODUTO", "CORRUGADO", "32mm"],
        "eletroduto_40": ["ELETRODUTO", "CORRUGADO", "40mm"],
        "fio_2_5mm": ["FIO", "COBRE", "2,5mm"],
        "fio_4mm": ["FIO", "COBRE", "4mm"],
        "fio_6mm": ["FIO", "COBRE", "6mm"],
        "gas_r410a": ["GAS", "R-410A", "REFRIGERANTE"],
        "solda_prata": ["SOLDA", "PRATA", "FOSFORO"],
        "dreno_25mm": ["TUBO", "PVC", "DRENO", "25mm"],
        "dreno_32mm": ["TUBO", "PVC", "DRENO", "32mm"],
    }
    
    precos = {
        "data_atualizacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "uf": uf.upper(),
        "insumos": {},
        "mao_de_obra": {},
        "referencias": {}
    }
    
    try:
        print(f"📥 Baixando dados da SINAPI para {uf.upper()}...")
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                arquivos_encontrados = []
                for file_name in z.namelist():
                    if file_name.endswith('.csv') or file_name.endswith('.xls') or file_name.endswith('.xlsx'):
                        arquivos_encontrados.append(file_name)
                        print(f"📄 Processando arquivo: {file_name}")
                        
                        if file_name.endswith('.csv'):
                            df = pd.read_csv(z.open(file_name), encoding='latin-1', on_bad_lines='skip')
                        else:
                            df = pd.read_excel(z.open(file_name))
                        
                        for insumo, palavras_chave in insumos_procurados.items():
                            if insumo not in precos["insumos"]:
                                valor = buscar_insumo_no_dataframe(df, palavras_chave)
                                if valor:
                                    precos["insumos"][insumo] = {
                                        "valor": valor,
                                        "unidade": "m",
                                        "codigo_sinapi": buscar_codigo_sinapi(df, palavras_chave)
                                    }
            
            completar_valores_padrao(precos)
            
            # Salvar dados da UF específica
            os.makedirs("data", exist_ok=True)
            filename = f"data/precos_sinapi_{uf.upper()}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(precos, f, indent=2, ensure_ascii=False)
            
            # Salvar também como geral
            salvar_arquivo_geral(precos)
            
            print(f"✅ Preços SINAPI para {uf.upper()} atualizados!")
            return True
        else:
            print(f"❌ Erro ao baixar: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no download: {e}")
        return False

def buscar_insumo_no_dataframe(df, palavras_chave):
    """Busca um insumo no DataFrame usando palavras-chave"""
    try:
        for col in df.columns:
            for idx, row in df.iterrows():
                texto = str(row[col]).upper()
                if all(palavra.upper() in texto for palavra in palavras_chave):
                    for col_preco in df.columns:
                        nome_col = str(col_preco).upper()
                        if any(p in nome_col for p in ["PRECO", "VALOR", "CUSTO", "R$", "UNITARIO"]):
                            valor = row[col_preco]
                            if isinstance(valor, (int, float)):
                                return round(float(valor), 2)
        return None
    except:
        return None

def buscar_codigo_sinapi(df, palavras_chave):
    """Busca o código SINAPI do insumo"""
    try:
        for col in df.columns:
            for idx, row in df.iterrows():
                texto = str(row[col]).upper()
                if all(palavra.upper() in texto for palavra in palavras_chave):
                    for col_codigo in df.columns:
                        if "CODIGO" in str(col_codigo).upper():
                            return str(row[col_codigo])
        return None
    except:
        return None

def completar_valores_padrao(precos):
    """Completa valores padrão para insumos não encontrados"""
    valores_padrao = {
        "cobre_1_4": {"valor": 32.50, "unidade": "m"},
        "cobre_3_8": {"valor": 38.00, "unidade": "m"},
        "cobre_1_2": {"valor": 45.00, "unidade": "m"},
        "cobre_5_8": {"valor": 52.00, "unidade": "m"},
        "cobre_7_8": {"valor": 68.00, "unidade": "m"},
        "isolante_9mm": {"valor": 18.00, "unidade": "m"},
        "isolante_12mm": {"valor": 22.00, "unidade": "m"},
        "isolante_19mm": {"valor": 32.00, "unidade": "m"},
        "eletroduto_25": {"valor": 4.80, "unidade": "m"},
        "eletroduto_32": {"valor": 6.50, "unidade": "m"},
        "eletroduto_40": {"valor": 8.90, "unidade": "m"},
        "fio_2_5mm": {"valor": 3.50, "unidade": "m"},
        "fio_4mm": {"valor": 5.20, "unidade": "m"},
        "fio_6mm": {"valor": 7.80, "unidade": "m"},
        "gas_r410a": {"valor": 85.00, "unidade": "kg"},
        "solda_prata": {"valor": 450.00, "unidade": "kg"},
        "dreno_25mm": {"valor": 8.50, "unidade": "m"},
        "dreno_32mm": {"valor": 12.00, "unidade": "m"},
    }
    
    for insumo, dados in valores_padrao.items():
        if insumo not in precos["insumos"]:
            precos["insumos"][insumo] = dados
    
    precos["mao_de_obra"] = {
        "tecnico_mes": {"valor": 2800.00, "unidade": "mês"},
        "ajudante_mes": {"valor": 1800.00, "unidade": "mês"},
        "engenheiro_hora": {"valor": 85.00, "unidade": "hora"},
        "encarregado_mes": {"valor": 3500.00, "unidade": "mês"},
    }
    
    precos["referencias"] = {
        "fonte": "SINAPI - CAIXA",
        "uf": precos["uf"],
        "competencia": datetime.now().strftime("%B/%Y"),
        "observacao": "Valores de referência - ajustar conforme necessidade"
    }

def salvar_arquivo_geral(precos_atual):
    """Salva um arquivo geral com a última UF selecionada"""
    arquivo_geral = "data/precos_sinapi.json"
    try:
        if os.path.exists(arquivo_geral):
            with open(arquivo_geral, "r", encoding="utf-8") as f:
                dados_gerais = json.load(f)
        else:
            dados_gerais = {}
        
        dados_gerais[precos_atual["uf"]] = precos_atual
        dados_gerais["ultima_atualizacao"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(arquivo_geral, "w", encoding="utf-8") as f:
            json.dump(dados_gerais, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar arquivo geral: {e}")

def listar_ufs_disponiveis():
    """Retorna lista de UFs disponíveis"""
    return list(UFS_DISPONIVEIS.keys())

def atualizar_todas_uFs():
    """Atualiza todas as UFs disponíveis"""
    resultados = {}
    for uf in UFS_DISPONIVEIS:
        print(f"\n{'='*50}")
        sucesso = baixar_sinapi_por_uf(uf)
        resultados[uf] = "OK" if sucesso else "FALHA"
    
    print(f"\n{'='*50}")
    print("RESUMO DA ATUALIZAÇÃO:")
    for uf, status in resultados.items():
        print(f"  {uf}: {status}")
    
    return resultados

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "todas":
            atualizar_todas_uFs()
        else:
            baixar_sinapi_por_uf(sys.argv[1])
    else:
        baixar_sinapi_por_uf("SP")
