from compute_corrections import compute_corrections
from find_beta import find_beta

def calculate_orifice_diameter(Q_desired, D, deltaP, rho, C, epsilon,
                               L_upstream, L_downstream, material, tap_type ="integral", orifice_type ="integral"):
    """
    Calcula o diâmetro do orifício (d) necessário para atingir a vazão volumétrica desejada.
    
    Parâmetros:
      Q_desired   : Vazão volumétrica desejada (m³/s)
      D           : Diâmetro interno da tubulação (m)
      deltaP      : Queda de pressão diferencial (Pa)
      rho         : Densidade do fluido (kg/m³)
      C           : Coeficiente de descarga base (ex.: 0.61)
      epsilon     : Fator de expansibilidade (1.0 para líquidos)
      L_upstream  : Distância a montante (m)
      L_downstream: Distância a jusante (m)
      material    : Material da tubulação (ex.: "steel", "cast iron", etc.)      
      tap_type    : Tipo de tomadas (ex.: "flange", "radius", etc.)
      orifice_type: Tipo de orifício (ex.: "concentrico", "excêntrico", "segmental", "conica", "bordo")
    
    Retorna:
      d_orifice   : Diâmetro do orifício (m)
      beta        : Razão (d_orifice / D)
      corrections : Dicionário com os fatores de correção e o coeficiente efetivo.
    """
    # Calcula os fatores de correção
    K_tap, K_inst, K_material, K_orifice = compute_corrections(D, L_upstream, L_downstream, material, tap_type, orifice_type)
    C_eff = C * K_tap * K_inst * K_material * K_orifice

    # Encontra o beta que satisfaz Q_desired
    beta = find_beta(Q_desired, D, deltaP, rho, C_eff, epsilon)
    d_orifice = beta * D

    corrections = {
        "K_tap": K_tap,
        "K_inst": K_inst,
        "K_material": K_material,
        "K_orifice": K_orifice,
        "C_eff": C_eff
    }

    return d_orifice, beta, corrections


print("Dimensionamento de Placa de Orifício a partir da Vazão Volumétrica Desejada")
print("-----------------------------------------------------------------------")

Q_desired = 0.02 # float(input("Digite a vazão volumétrica desejada Q (Nm³/s): "))
D = 0.15 # float(input("Digite o diâmetro interno da tubulação D (m): "))
deltaP = 50000 # float(input("Digite a queda de pressão ΔP (Pa): "))
rho = 1000.0 # float(input("Digite a densidade do fluido ρ (kg/m³): "))
C = 0.61 # Valor típico do coeficiente de descarga para placa de orifício
# C = 0.64 # Valor típico do coeficiente de descarga para orifício integral 
epsilon = 1.0 # float(input("Digite o fator de expansibilidade ε (1.0 para líquidos): "))
L_upstream = 10*D # float(input("Digite a distância a montante da placa (m): "))
L_downstream = 5*D # float(input("Digite a distância a jusante da placa (m): "))
# print("\nMateriais de tubulação disponíveis: steel, cast iron, stainless steel, plastic, copper")
material = "steel" # input("Digite o material da tubulação: ").strip()
# print("\nTipos de tomadas disponíveis: integral, flange, radius, vena, corner, pipe")
tap_type = "flange" # input("Digite o tipo de tomada utilizado: ").strip()
# print("\nTipos de orifício disponíveis: integral, concentrico, excêntrico, segmental, conica, bordo")
orifice_type = "concentrico" # input("Digite o tipo de orifício da placa: ").strip()
        
d_orifice, beta, corrections = calculate_orifice_diameter(
    Q_desired, D, deltaP, rho, C, epsilon,
    L_upstream, L_downstream, material, tap_type, orifice_type
)

print("\nResultados:")
print("Razão β (d/D): {:.4f}".format(beta))
print("Diâmetro do orifício d: {:.4f} m".format(d_orifice))
print("\nFatores de Correção Aplicados:")
print(" - K_tap (tipo de tomada): {:.3f}".format(corrections["K_tap"]))
print(" - K_inst (instalação): {:.3f}".format(corrections["K_inst"]))
print(" - K_material (material): {:.3f}".format(corrections["K_material"]))
print(" - K_orifice (tipo de orifício): {:.3f}".format(corrections["K_orifice"]))
print(" - Coeficiente de Descarga Efetivo (C_eff): {:.3f}".format(corrections["C_eff"]))
