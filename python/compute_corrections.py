def compute_corrections(D, L_upstream, L_downstream, material, tap_type, orifice_type):
    # Fator de correção para o tipo de tomadas (taps)
    tap_correction = {
        "integral" : 1.00,
        "flange": 1.00,
        "radius": 0.98,
        "vena": 0.95,
        "corner": 0.97,
        "pipe": 0.96
    }
    K_tap = tap_correction.get(tap_type.lower(), 1.00)
    
    # Correção para instalação: recomenda-se L_upstream >= 10*D e L_downstream >= 5*D.
    K_up = 1.0 if L_upstream >= 10 * D else L_upstream / (10 * D)
    K_down = 1.0 if L_downstream >= 5 * D else L_downstream / (5 * D)
    K_inst = K_up * K_down

    # Fator de correção para material da tubulação
    material_correction = {
        "steel": 1.00,
        "cast iron": 0.98,
        "stainless steel": 1.02,
        "plastic": 1.00,
        "copper": 1.00
    }
    K_material = material_correction.get(material.lower(), 1.00)

    # Fator de correção para o tipo de orifício
    orifice_correction = {
        "integral" : 1.00,
        "concentrico": 1.00,
        "excêntrico": 0.98,
        "segmental": 0.96,
        "conica": 1.01,
        "bordo": 1.00
    }
    K_orifice = orifice_correction.get(orifice_type.lower(), 1.00)

    # Produto final dos fatores de correção
    return K_tap, K_inst, K_material, K_orifice
