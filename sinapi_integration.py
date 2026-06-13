def get_precos_equipamentos(uf="SP"):
    """Retorna preços médios de equipamentos por UF"""
    
    precos_equipamentos = {
        "VRF/VRV": {
            "condensadora_por_tr": {"SP": 3500, "RJ": 3800, "MG": 3400, "RS": 3600, "default": 3500},
            "evaporadora_cassete": {"SP": 4200, "RJ": 4500, "MG": 4100, "RS": 4300, "default": 4200},
            "evaporadora_duto": {"SP": 3800, "RJ": 4100, "MG": 3700, "RS": 3900, "default": 3800},
            "evaporadora_piso_teto": {"SP": 4500, "RJ": 4800, "MG": 4400, "RS": 4600, "default": 4500},
        },
        "Água Gelada": {
            "chiller_por_tr": {"SP": 2800, "RJ": 3100, "MG": 2700, "RS": 2900, "default": 2800},
            "fan_coil_cassete": {"SP": 2500, "RJ": 2700, "MG": 2400, "RS": 2600, "default": 2500},
            "fan_coil_duto": {"SP": 2200, "RJ": 2400, "MG": 2100, "RS": 2300, "default": 2200},
            "fan_coil_high_wall": {"SP": 2000, "RJ": 2200, "MG": 1900, "RS": 2100, "default": 2000},
            "torre_resfriamento_por_tr": {"SP": 800, "RJ": 880, "MG": 780, "RS": 820, "default": 800},
        },
        "Split": {
            "split_9000_btu": {"SP": 1800, "RJ": 2000, "MG": 1750, "RS": 1850, "default": 1800},
            "split_12000_btu": {"SP": 2200, "RJ": 2400, "MG": 2100, "RS": 2250, "default": 2200},
            "split_18000_btu": {"SP": 2800, "RJ": 3100, "MG": 2700, "RS": 2900, "default": 2800},
            "split_24000_btu": {"SP": 3500, "RJ": 3800, "MG": 3400, "RS": 3600, "default": 3500},
            "multisplit_evaporadora": {"SP": 1500, "RJ": 1650, "MG": 1450, "RS": 1550, "default": 1500},
        }
    }
    
    resultado = {}
    for sistema, equipamentos in precos_equipamentos.items():
        resultado[sistema] = {}
        for equipamento, precos_por_uf in equipamentos.items():
            valor = precos_por_uf.get(uf, precos_por_uf["default"])
            resultado[sistema][equipamento] = valor
    
    return resultado
