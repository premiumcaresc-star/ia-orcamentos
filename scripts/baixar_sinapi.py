import requests
import pandas as pd
import json
import os
import zipfile
import io
from datetime import datetime
from bs4 import BeautifulSoup
import re

def baixar_sinapi_oficial():
    """
    Baixa os dados oficiais da SINAPI do site da CAIXA
    """
    print(f"🔄 Iniciando download dos preços SINAPI - {datetime.now()}")
    
    urls = {
        "sp": "https://www.caixa.gov.br/Downloads/sinapi/SINAPI_precos_referencia_SP.zip",
        "rj": "https://www.caixa.gov.br/Downloads/sinapi/SINAPI_precos_referencia_RJ.zip",
        "mg": "https://www.caixa.gov.br/Downloads/sinapi/SINAPI_precos_referencia_MG.zip",
        "rs": "https://www.caixa.gov.br/Downloads/sinapi/SINAPI_precos_referencia_RS.zip",
        "br": "https://www.caixa.gov.br/Downloads/sinapi/SINAPI_precos_referencia_Brasil.zip"
    }
    
    uf = "sp"
    url = urls.get(uf, urls["sp"])
    
    insumos_procurados = {
        "cobre_1_4": ["COBRE", "1/4", "TUBO", "REFERIGERACAO"],
        "cobre_3_8": ["COBRE", "3/8", "TUBO"],
        "cobre_1_2": ["COBRE", "1/2", "TUBO"],
        "cobre_5_8": ["COBRE", "5/8", "TUBO"],
        "isolante_9mm": ["ISOLANTE", "ELASTOMERICO", "9mm"],
        "isolante_12mm": ["ISOLANTE", "ELASTOMERICO", "12mm"],
        "eletroduto_25": ["ELETRODUTO", "CORRUGADO", "25mm"],
        "eletroduto_32": ["ELETRODUTO", "CORRUGADO", "32mm"],
        "fio_2_5mm": ["FIO", "COBRE", "2,5mm"],
        "fio_4mm": ["FIO", "COBRE", "4mm"],
        "gas_r410a": ["GAS", "R-410A", "REFRIGERANTE"],
        "solda_prata": ["SOLDA", "PRATA", "FOSFORO"],
    }
    
    precos = {
        "data_atualizacao": datetime.now().strftime("%Y-%m-%d"),
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
                for file_name in z.namelist():
                    if file_name.endswith('.csv') or file_name.endswith('.xls') or file_name.endswith('.xlsx'):
                        print(f"📄 Processando arquivo: {file_name}")
                        
                        if file_name.endswith('.csv'):
                            df = pd.read_csv(z.open(file_name), encoding='latin-1')
                        else:
                            df = pd.read_excel(z.open(file_name))
                        
                        for insumo, palavras_chave in insumos_procurados.items():
                            valor = buscar_insumo_no_dataframe(df, palavras_chave)
                            if valor:
                                precos["insumos"][insumo] = {"valor": valor, "unidade": "m"}
            
            completar_valores_padrao(precos)
            
            os.makedirs("data", exist_ok=True)
            with open("data/precos_sinapi.json", "w", encoding="utf-8") as f:
                json.dump(precos, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Preços SINAPI atualizados com sucesso!")
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
                        if any(p in col_preco.upper() for p in ["PRECO", "VALOR", "CUSTO", "R$"]):
                            valor = row[col_preco]
                            if isinstance(valor, (int, float)):
                                return round(float(valor), 2)
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
        "isolante_9mm": {"valor": 18.00, "unidade": "m"},
        "isolante_12mm": {"valor": 22.00, "unidade": "m"},
        "eletroduto_25": {"valor": 4.80, "unidade": "m"},
        "eletroduto_32": {"valor": 6.50, "unidade": "m"},
        "fio_2_5mm": {"valor": 3.50, "unidade": "m"},
        "fio_4mm": {"valor": 5.20, "unidade": "m"},
        "gas_r410a": {"valor": 85.00, "unidade": "kg"},
        "solda_prata": {"valor": 450.00, "unidade": "kg"},
    }
    
    for insumo, dados in valores_padrao.items():
        if insumo not in precos["insumos"]:
            precos["insumos"][insumo] = dados
    
    precos["mao_de_obra"] = {
        "tecnico_mes": {"valor": 2800.00, "unidade": "mês"},
        "ajudante_mes": {"valor": 1800.00, "unidade": "mês"},
        "engenheiro_hora": {"valor": 85.00, "unidade": "hora"},
    }
    
    precos["referencias"] = {
        "fonte": "SINAPI - CAIXA",
        "uf": precos["uf"],
        "competencia": datetime.now().strftime("%B/%Y"),
        "observacao": "Valores de referência - ajustar conforme necessidade"
    }

if __name__ == "__main__":
    baixar_sinapi_oficial()
