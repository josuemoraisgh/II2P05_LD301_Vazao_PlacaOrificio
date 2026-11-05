"""@file calculos.py
@brief Equações e regras de domínio para medição por placa de orifício.

Este módulo não acessa interface gráfica, terminal, arquivos ou rede. Suas
funções recebem parâmetros e devolvem resultados para serem usados por serviços,
interfaces ou ferramentas de linha de comando.
"""
import math

# =====================================================================================
# CONFIGURAÇÃO -- os mesmos ajustes de "Propriedades exportadas" da planta na simulação
# =====================================================================================
CONFIGURACAO = {
    "D": 52.5,            # Diâmetro interno da tubulação D, a 20 °C [mm]
    "d": 31.5,            # Diâmetro do orifício d, a 20 °C [mm]
    "tomada": 1,          # Tipo de tomada: 1 = Flange, 2 = D e D/2 (radius taps), 3 = Canto (corner taps)
    "L_montante": 44.0,   # Trecho reto a montante, da curva de 90° até a placa [múltiplos de D]
    "L_jusante": 8.0,     # Trecho reto a jusante, da placa até a válvula [múltiplos de D]
    "material_tubo": 1,   # Material da tubulação (código da tabela MATERIAIS abaixo)
    "material_placa": 2,  # Material da placa de orifício (código da tabela MATERIAIS)
    "T": 20.0,            # Temperatura de operação [°C]
    "fluido": 0,          # 0 = Líquido (ε = 1), 1 = Gás (ε pela ISO 5167-2)
    "rho": 998.2,         # Massa específica do fluido na operação, a montante [kg/m³]
    "mu": 1.002,          # Viscosidade dinâmica [cP]
    "kappa": 1.4,         # Expoente isentrópico κ (só para gás)
    "p1": 200.0,          # Pressão a montante, manométrica [kPa]
    "Qmax": 15.0,         # Vazão volumétrica de operação a 100 % da válvula [m³/h]; chave interna histórica
    "desvio": 1,          # Desvio didático de instalação e rugosidade: 1 = aplicar, 0 = não aplicar
    # LD301 (só para converter a corrente do laço em ΔP)
    "LRV": 0.0,           # Limite inferior da faixa [mmH2O]
    "URV": 3376.3,        # Limite superior da faixa [mmH2O]
    "corte_raiz": 6.0,    # Ponto de corte da raiz quadrada [% da faixa]
}

# código: (nome, coeficiente de dilatação α [1e-6/K], rugosidade Ra [mm])
MATERIAIS = {
    1: ("Aço carbono", 11.2, 0.015),
    2: ("Aço inox AISI 316", 16.0, 0.005),
    3: ("Ferro fundido", 10.4, 0.08),
    4: ("Aço galvanizado", 11.2, 0.05),
    5: ("Cobre", 16.8, 0.0005),
    6: ("PVC", 54.0, 0.0005),
}
TOMADAS = {1: "Flange (25,4 mm da placa)", 2: "D e D/2 (radius taps)", 3: "Canto (corner taps)"}

MMH2O_EM_PA = 9.80665          # 1 mmH2O convencional = 9,80665 Pa (o mesmo fator do bloco dp_mm da planta)
KPA_EM_MMH2O = 101.97162       # 1 kPa = 101,97162 mmH2O
# O LD301 real usa mmH2O a 20 °C (código HART 4): 1 inH2O@20 °C = 248,642 Pa (manual, Tabela 3.1).
MMH2O_20C_EM_PA = 248.642 / 25.4
P_ATM_KPA = 101.325            # pressão atmosférica [kPa]


# =====================================================================================
# Equações (as mesmas dos blocos da planta)
# =====================================================================================
def geometria(cfg):
    """@brief Calcula a geometria corrigida pela temperatura.
    @param cfg Dicionário com D, d, T e códigos dos materiais.
    @return Coeficientes de dilatação, rugosidade, D_T, d_T e beta.
    """
    _, alfa_tubo, ra_tubo = MATERIAIS[cfg["material_tubo"]]
    _, alfa_placa, _ = MATERIAIS[cfg["material_placa"]]
    D_T = cfg["D"] * (1 + alfa_tubo * 1e-6 * (cfg["T"] - 20))
    d_T = cfg["d"] * (1 + alfa_placa * 1e-6 * (cfg["T"] - 20))
    return {"alfa_tubo": alfa_tubo, "alfa_placa": alfa_placa, "Ra": ra_tubo, "D_T": D_T, "d_T": d_T, "beta": d_T / D_T}


def distancias_tomada(tomada, D_mm):
    """L1 (tomada de alta) e L'2 (tomada de baixa), em múltiplos de D -- ISO 5167-2, 5.3.2.1."""
    if tomada == 1:
        return 25.4 / D_mm, 25.4 / D_mm   # flange: 25,4 mm de cada face da placa
    if tomada == 2:
        return 1.0, 0.47                  # D e D/2
    return 0.0, 0.0                       # canto


def coeficiente_iso(beta, Re, tomada, D_mm):
    """@brief Calcula C pela equação de Reader-Harris/Gallagher.
    @param beta Razão entre diâmetro do orifício e tubulação.
    @param Re Número de Reynolds baseado em D.
    @param tomada Código do tipo de tomada de pressão.
    @param D_mm Diâmetro interno da tubulação em milímetros.
    @return Coeficiente de descarga ISO 5167-2.
    """
    Re = Re + (1 if Re < 1 else 0)  # vazão zero: evita divisão por zero (C não é usado nesse caso)
    L1, L2 = distancias_tomada(tomada, D_mm)
    A = (19000 * beta / Re) ** 0.8
    M2 = 2 * L2 / (1 - beta)
    C = (0.5961 + 0.0261 * beta ** 2 - 0.216 * beta ** 8
         + 0.000521 * (1e6 * beta / Re) ** 0.7
         + (0.0188 + 0.0063 * A) * beta ** 3.5 * (1e6 / Re) ** 0.3
         + (0.043 + 0.080 * math.exp(-10 * L1) - 0.123 * math.exp(-7 * L1)) * (1 - 0.11 * A) * beta ** 4 / (1 - beta ** 4)
         - 0.031 * (M2 - 0.8 * M2 ** 1.1) * beta ** 1.3)
    if D_mm < 71.12:  # termo de tubulação pequena
        C += 0.011 * (0.75 - beta) * (2.8 - D_mm / 25.4)
    return C


def trechos_exigidos(beta):
    """Tabela 3 da ISO 5167-2 (uma curva de 90° a montante), em múltiplos de D.
    β intermediário usa a linha do β maior seguinte. Devolve (montante A, montante B, jusante)."""
    if beta < 0.2001:
        return 6, 3, 4
    if beta < 0.4001:
        return 16, 3, 6
    if beta < 0.5001:
        return 22, 9, 6
    if beta < 0.6001:
        return 42, 13, 7
    if beta < 0.6701:
        return 44, 20, 7
    return 44, 20, 8


def limite_rugosidade(beta):
    """Limite de 10⁴·Ra/D (aproximação da Tabela 1 da ISO 5167-2)."""
    return 25.0 if beta < 0.3 else 4 + 21 * math.exp(-19.1 * (beta - 0.3))


def desvio_didatico(cfg, geo):
    """Desvio do C quando a instalação foge da norma (recurso didático, não é da ISO). Em %."""
    A, B, A_jus = trechos_exigidos(geo["beta"])
    L, L_jus = cfg["L_montante"], cfg["L_jusante"]
    montante = 0.0
    if B < L < A:
        montante = 0.5 * (A - L) / (A - B)          # +0,5 % no comprimento B
    elif L < B + 1e-6:
        montante = 0.5 + 1.5 * (B - L) / B          # até +2 % sem trecho reto
    jusante = 0.0
    if A_jus / 2 < L_jus < A_jus:
        jusante = 0.25 * (A_jus - L_jus) / (A_jus / 2)
    elif L_jus < A_jus / 2 + 1e-6:
        jusante = 0.25 + 0.25 * (A_jus / 2 - L_jus) / (A_jus / 2)
    r = 1e4 * geo["Ra"] / geo["D_T"]
    lim = limite_rugosidade(geo["beta"])
    rugosidade = 0.0
    if r > lim:
        rugosidade = 0.5 * (r / lim - 1) if r / lim < 5 else 2.0
    total = (montante + jusante + rugosidade) if cfg["desvio"] == 1 else 0.0
    return {"A": A, "B": B, "A_jus": A_jus, "montante": montante, "jusante": jusante, "rugosidade": rugosidade,
            "total": total, "rug_rel": r, "rug_lim": lim}


def razao_pressoes(cfg, dp_pa):
    """p2/p1 em pressão absoluta (limitada a 0,01, como na planta)."""
    p1_abs = cfg["p1"] + P_ATM_KPA
    return max((p1_abs - dp_pa / 1000) / p1_abs, 0.01)


def expansibilidade(cfg, beta, dp_pa):
    """ε pela ISO 5167-2 para gás; 1 para líquido."""
    if cfg["fluido"] != 1:
        return 1.0
    return 1 - (0.351 + 0.256 * beta ** 4 + 0.93 * beta ** 8) * (1 - razao_pressoes(cfg, dp_pa) ** (1 / cfg["kappa"]))


def reynolds(cfg, Q_m3h, D_mm):
    """Re_D = 4·ρ·Q / (π·μ·D)."""
    return 4 * cfg["rho"] * (Q_m3h / 3600) / (math.pi * cfg["mu"] * 1e-3 * D_mm * 1e-3)


def perda_permanente(beta, C, dp):
    raiz = math.sqrt(1 - beta ** 4 * (1 - C ** 2))
    return (raiz - C * beta ** 2) / (raiz + C * beta ** 2) * dp


def conformidade(cfg, geo, dev, Re, dp_pa):
    """As lâmpadas de conformidade da planta."""
    b, D, d, t = geo["beta"], geo["D_T"], geo["d_T"], cfg["tomada"]
    faixa_re = Re > 170 * b ** 2 * D if t == 1 else (b < 0.56 or Re > 16000 * b ** 2)
    faixa_iso = (0.0999 < b < 0.7501 and 49.999 < D < 1000.001 and d > 12.499 and Re > 5000 and faixa_re
                 and (cfg["fluido"] != 1 or razao_pressoes(cfg, dp_pa) > 0.75))
    return {"Montante": cfg["L_montante"] > dev["A"] - 1e-4, "Jusante": cfg["L_jusante"] > dev["A_jus"] - 1e-4,
            "Rugosidade": dev["rug_rel"] < dev["rug_lim"], "Faixa ISO": faixa_iso}


def resultado_completo(cfg, Q_m3h, dp_pa, C_iso, C_real, eps, geo, dev):
    Re = reynolds(cfg, Q_m3h, geo["D_T"])
    return {
        "Q": Q_m3h, "v": Q_m3h / 3600 / (math.pi / 4 * (geo["D_T"] / 1000) ** 2), "Re": Re,
        "C_iso": C_iso, "C_real": C_real, "eps": eps, "dp_pa": dp_pa,
        "perda_kpa": perda_permanente(geo["beta"], C_real, dp_pa) / 1000,
        "geo": geo, "dev": dev, "ok": conformidade(cfg, geo, dev, Re, dp_pa),
    }


def dp_da_vazao(cfg, Q_m3h):
    """@brief Resolve o caminho direto vazão → C → ε → ΔP.
    @param cfg Configuração completa do instrumento e da instalação.
    @param Q_m3h Vazão nas condições de operação, em m³/h.
    @return Dicionário estruturado com propriedades e resultados calculados.
    """
    geo = geometria(cfg)
    dev = desvio_didatico(cfg, geo)
    b, d = geo["beta"], geo["d_T"] / 1000
    C_iso = coeficiente_iso(b, reynolds(cfg, Q_m3h, geo["D_T"]), cfg["tomada"], geo["D_T"])
    C_real = C_iso * (1 + dev["total"] / 100)
    dp0 = 8 * cfg["rho"] * (1 - b ** 4) * (Q_m3h / 3600) ** 2 / (C_real ** 2 * math.pi ** 2 * d ** 4)
    dp, eps = dp0, 1.0
    for _ in range(50):  # ε depende de ΔP e ΔP depende de ε
        eps = expansibilidade(cfg, b, dp)
        dp = dp0 / eps ** 2
    return resultado_completo(cfg, Q_m3h, dp, C_iso, C_real, eps, geo, dev)


def vazao_do_dp(cfg, dp_mmh2o):
    """@brief Resolve o caminho inverso ΔP → vazão por iteração de C e Reynolds.
    @param cfg Configuração completa do instrumento e da instalação.
    @param dp_mmh2o Pressão diferencial medida em mmH2O convencional.
    @return Dicionário estruturado com propriedades e resultados calculados.

    Q = C·ε·(π/4)·d²·√(2·ΔP / (ρ·(1 − β⁴)))."""
    geo = geometria(cfg)
    dev = desvio_didatico(cfg, geo)
    b, d = geo["beta"], geo["d_T"] / 1000
    dp = dp_mmh2o * MMH2O_EM_PA
    if dp <= 0:
        return resultado_completo(cfg, 0.0, 0.0, coeficiente_iso(b, 0, cfg["tomada"], geo["D_T"]), 0.0, 1.0, geo, dev)
    eps = expansibilidade(cfg, b, dp)  # com o ΔP conhecido, ε sai direto
    raiz = math.sqrt(2 * dp / (cfg["rho"] * (1 - b ** 4)))
    C_iso = 0.6  # chute inicial
    Q = 0.0
    for _ in range(1, 51):
        C_real = C_iso * (1 + dev["total"] / 100)
        Q = C_real * eps * math.pi / 4 * d ** 2 * raiz * 3600
        Re = reynolds(cfg, Q, geo["D_T"])
        novo = coeficiente_iso(b, Re, cfg["tomada"], geo["D_T"])
        if abs(novo - C_iso) < 1e-12:
            break
        C_iso = novo
    return resultado_completo(cfg, Q, dp, C_iso, C_iso * (1 + dev["total"] / 100), eps, geo, dev)


def dp_da_corrente(cfg, miliamperes, raiz):
    """@brief Converte corrente do laço em pressão diferencial.
    @param cfg Configuração do transmissor, incluindo LRV, URV e corte.
    @param miliamperes Corrente do laço entre 4 e 20 mA.
    @param raiz Seleciona a transferência inversa de raiz quadrada.
    @return Tupla (ΔP em mmH2O, percentual de entrada da faixa).
    """
    saida = (miliamperes - 4) / 16 * 100  # % da saída
    if raiz:
        limite = 10 * math.sqrt(cfg["corte_raiz"])  # saída no ponto de corte
        entrada = (max(saida, 0) / 10) ** 2   # inverso de saída = 10·√entrada
    else:
        entrada = saida
    return cfg["LRV"] + entrada / 100 * (cfg["URV"] - cfg["LRV"]), entrada


