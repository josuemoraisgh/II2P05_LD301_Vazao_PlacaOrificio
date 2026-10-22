from compute_corrections import compute_corrections
from find_beta import flow_rate_from_beta

d = 0.0127 # 
D = 0.0266 # float(input("Digite o diâmetro interno da tubulação D (m): "))
deltaP = 24750.74 # float(input("Digite a queda de pressão ΔP (Pa): "))
rho = 1000.0 # float(input("Digite a densidade do fluido ρ (kg/m³): "))
C = 0.61 # Valor típico do coeficiente de descarga para placa de orifício
# C = 0.64 # Valor típico do coeficiente de descarga para orifício integral 
epsilon = 1.0 # float(input("Digite o fator de expansibilidade ε (1.0 para líquidos): "))
L_upstream = 10*D # float(input("Digite a distância a montante da placa (m): "))
L_downstream = 5*D # float(input("Digite a distância a jusante da placa (m): "))
# print("\nMateriais de tubulação disponíveis: steel, cast iron, stainless steel, plastic, copper")
material = "steel" # input("Digite o material da tubulação: ").strip()
# print("\nTipos de tomadas disponíveis: flange, radius, vena, corner, pipe")
tap_type = "flange" # input("Digite o tipo de tomada utilizado: ").strip()
# print("\nTipos de orifício disponíveis: concentrico, excêntrico, segmental, conica, bordo")
orifice_type = "concentrico" # input("Digite o tipo de orifício da placa: ").strip()

# Calcula os fatores de correção
K_tap, K_inst, K_material, K_orifice = compute_corrections(D, L_upstream, L_downstream, material, tap_type, orifice_type)
C_eff = C * K_tap * K_inst * K_material * K_orifice
    
Q = flow_rate_from_beta(d/D, D, deltaP, rho, C_eff, epsilon)
print("Razão β (d/D): {:.4f} m".format(d/D))
print("Vazão Q: {:.4f} m³/s".format(Q))