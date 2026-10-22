import math
from compute_corrections import compute_corrections

def calculate_deltaP(Q, d, D, rho, C, epsilon, L_upstream, L_downstream, material, tap_type, orifice_type):
    """
    Calcula a queda de pressão diferencial (ΔP) para uma placa de orifício
    a partir da vazão volumétrica Q, diâmetro do orifício d, diâmetro do tubo D, 
    densidade do fluido rho, coeficiente de descarga base C, fator de expansibilidade epsilon,
    e os fatores de correção determinados pelo tipo de tomada, instalação, material e tipo de orifício.
    
    A equação utilizada é:
    
    ΔP = (8 * ρ * (1 - β^4) * Q^2) / (C_eff^2 * ε^2 * π^2 * d^4)
    
    onde:
      - β = d / D
      - C_eff = C * K_tap * K_inst * K_material * K_orifice
    """
    beta = d / D
    # Obter os fatores de correção
    K_tap, K_inst, K_material, K_orifice = compute_corrections(D, L_upstream, L_downstream, material, tap_type, orifice_type)
    
    # Calcular o coeficiente de descarga efetivo
    C_eff = C * K_tap * K_inst * K_material * K_orifice
    
    # Calcular ΔP com a equação derivada
    deltaP = (8 * rho * (1 - beta**4) * Q**2) / (C_eff**2 * epsilon**2 * math.pi**2 * d**4)
    return deltaP

def main():
    # Dados de entrada (exemplo)
    Q = 0.02           # Vazão volumétrica desejada em m³/s
    d = 0.0641         # Diâmetro do orifício em m (fornecido)
    D = 0.15           # Diâmetro interno da tubulação em m (fornecido)
    rho = 1000         # Densidade do fluido (kg/m³) – exemplo para água
    C = 0.61 # Valor típico do coeficiente de descarga para placa de orifício
    # C = 0.64 # Valor típico do coeficiente de descarga para orifício integral 
    epsilon = 1.0      # Fator de expansibilidade (1 para líquidos)
    L_upstream = 10*D       # Distância a montante em m
    L_downstream = 5*D      # Distância a jusante em m
    
    # Dados para fatores de correção
    material = "steel"         # Material da tubulação (ex.: "steel")    
    tap_type = "flange"        # Tipo de tomadas (ex.: "flange")
    orifice_type = "concentrico" # Tipo de orifício (ex.: "concentrico")
    
    # Calcular a queda de pressão diferencial
    deltaP = calculate_deltaP(Q, d, D, rho, C, epsilon, L_upstream, L_downstream, material, tap_type, orifice_type)
    print("Queda de pressão diferencial (ΔP): {:.2f} Pa".format(deltaP))

if __name__ == "__main__":
    main()
