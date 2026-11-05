"""CLI do projeto; importa o núcleo de cálculo sem duplicar suas equações."""
import argparse
import math
from pathlib import Path
import sys

# Garante imports do pacote ao executar este arquivo diretamente pela raiz.
RAIZ_PROJETO = Path(__file__).resolve().parents[1]
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

from python.calculos import *  # noqa: F401,F403 - compatibilidade para a CLI
# =====================================================================================
# Relatório (mesmos valores dos displays da planta)
# =====================================================================================
def relatorio(cfg, r):
    geo, dev = r["geo"], r["dev"]
    print("\nAjustes")
    print(f"  D = {cfg['D']} mm, d = {cfg['d']} mm (a 20 °C); tomada: {TOMADAS[cfg['tomada']]}")
    print(f"  Tubulação: {MATERIAIS[cfg['material_tubo']][0]}; placa: {MATERIAIS[cfg['material_placa']][0]}; T = {cfg['T']} °C")
    print(f"  Fluido: {'gás' if cfg['fluido'] == 1 else 'líquido'}; ρ = {cfg['rho']} kg/m³; μ = {cfg['mu']} cP; p1 = {cfg['p1']} kPa")
    print("\nGeometria na temperatura de operação")
    print(f"  D = {cfg['D']}·(1 + {geo['alfa_tubo']}e-6·({cfg['T']} − 20)) = {geo['D_T']:.2f} mm")
    print(f"  d = {cfg['d']}·(1 + {geo['alfa_placa']}e-6·({cfg['T']} − 20)) = {geo['d_T']:.3f} mm")
    print(f"  β = d/D = {geo['beta']:.4f}")
    print("\nInstalação (ISO 5167-2, Tabela 3 -- uma curva de 90°)")
    print(f"  Montante: instalado {cfg['L_montante']} D, exigido {dev['A']} D (mínimo com +0,5 %: {dev['B']} D)")
    print(f"  Jusante:  instalado {cfg['L_jusante']} D, exigido {dev['A_jus']} D")
    print(f"  10⁴·Ra/D = {dev['rug_rel']:.2f} (limite {dev['rug_lim']:.2f})")
    print(f"  Desvio didático de C: montante {dev['montante']:.3f} % + jusante {dev['jusante']:.3f} % "
          f"+ rugosidade {dev['rugosidade']:.3f} % = {dev['total']:.2f} %{'' if cfg['desvio'] == 1 else ' (desligado)'}")
    print("  Conformidade: " + ", ".join(f"{nome} {'OK' if ok else 'FORA'}" for nome, ok in r["ok"].items()))
    print("\nResultado (compare com os displays da planta)")
    print(f"  Vazão               {r['Q']:.3f} m³/h (nas condições de operação)")
    print(f"  Velocidade          {r['v']:.2f} m/s")
    print(f"  Reynolds Re_D       {r['Re']:.0f}")
    print(f"  C (ISO 5167-2)      {r['C_iso']:.4f}")
    print(f"  C real (com desvio) {r['C_real']:.4f}")
    print(f"  ε (expansibilidade) {r['eps']:.4f}")
    print(f"  ΔP na placa         {r['dp_pa'] / 1000:.4f} kPa = {r['dp_pa'] / MMH2O_EM_PA:.1f} mmH2O "
          f"(= {r['dp_pa'] / MMH2O_20C_EM_PA:.1f} mmH2O@20°C)")
    print(f"  Perda permanente    {r['perda_kpa']:.2f} kPa")
    print(f"  HIGH / LOW          {KPA_EM_MMH2O * cfg['p1']:.0f} / {KPA_EM_MMH2O * cfg['p1'] - r['dp_pa'] / MMH2O_EM_PA:.0f} mmH2O")


# =====================================================================================
# Autoteste: valores da biblioteca fluids (ISO 5167-2), os mesmos dos testes do simulador
# =====================================================================================
def autoteste():
    def confere(nome, obtido, esperado, tolerancia):
        ok = abs(obtido - esperado) <= tolerancia * abs(esperado)
        print(f"  {'OK   ' if ok else 'FALHA'} {nome}: {obtido:.9g} (esperado {esperado:.9g})")
        return ok

    base = dict(CONFIGURACAO, D=52.5, d=31.5, tomada=1, L_montante=44, L_jusante=8, material_tubo=1, material_placa=2,
                T=20.0, fluido=0, rho=998.2, mu=1.002, kappa=1.4, p1=200.0, Qmax=15.0, desvio=1, LRV=0.0, URV=3376.3)
    ok = True
    r = dp_da_vazao(base, 15)
    ok &= confere("C a 15 m³/h (flange)", r["C_iso"], 0.612422441827, 1e-8)
    ok &= confere("ΔP a 15 m³/h [mmH2O]", r["dp_pa"] / MMH2O_EM_PA, 3376.285174987, 1e-6)
    ok &= confere("perda permanente [kPa]", r["perda_kpa"], 20.728212903, 1e-6)
    ok &= confere("ΔP a 7,5 m³/h [mmH2O]", dp_da_vazao(base, 7.5)["dp_pa"] / MMH2O_EM_PA, 836.081491565, 1e-6)
    ok &= confere("C tomada D e D/2", dp_da_vazao(dict(base, tomada=2), 15)["C_iso"], 0.612965722556, 1e-8)
    ok &= confere("C tomada de canto", dp_da_vazao(dict(base, tomada=3), 15)["C_iso"], 0.611526303754, 1e-8)
    ok &= confere("ΔP com montante 10 D [mmH2O]", dp_da_vazao(dict(base, L_montante=10), 15)["dp_pa"] / MMH2O_EM_PA, 3319.865147240, 1e-6)
    gas = dict(base, fluido=1, rho=3.57, mu=0.0181, Qmax=150.0)
    r = dp_da_vazao(gas, 150)
    ok &= confere("ε do gás", r["eps"], 0.988368449177, 1e-6)
    ok &= confere("ΔP do gás [mmH2O]", r["dp_pa"] / MMH2O_EM_PA, 1244.199774964, 1e-6)
    ok &= confere("vazão do ΔP 836,08 mmH2O [m³/h]", vazao_do_dp(base, 836.081491565)["Q"], 7.5, 1e-7)
    ok &= confere("vazão do gás pelo ΔP [m³/h]", vazao_do_dp(gas, 1244.199774964)["Q"], 150.0, 1e-6)
    dp_mm, _ = dp_da_corrente(base, 4 + 0.16 * 10 * math.sqrt(100 * 836.081491565 / 3376.3), raiz=True)
    ok &= confere("vazão da corrente com raiz [m³/h]", vazao_do_dp(base, dp_mm)["Q"], 7.5, 1e-7)
    print("Autoteste:", "tudo certo" if ok else "FALHOU")
    return ok


# =====================================================================================
def ler_argumentos():
    p = argparse.ArgumentParser(description="Vazão em placa de orifício (ISO 5167-2), igual à planta do LasecSimul.")
    medido = p.add_mutually_exclusive_group()
    medido.add_argument("--dp", type=float, help="ΔP medido [mmH2O] -> calcula a vazão")
    medido.add_argument("--corrente", type=float, help="corrente do laço do LD301 [mA] -> ΔP -> vazão")
    medido.add_argument("--valvula", type=float, help="abertura da válvula [%%] -> vazão -> ΔP")
    medido.add_argument("--autoteste", action="store_true", help="confere o script com os valores de referência")
    p.add_argument("--raiz", action="store_true", help="LD301 com função raiz quadrada (para --corrente)")
    for chave, valor in CONFIGURACAO.items():
        p.add_argument(f"--{chave}", type=type(valor), default=valor, help=f"padrão: {valor}")
    return p.parse_args()


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # Δ, β, ε no console do Windows
    except (AttributeError, ValueError):
        pass
    args = ler_argumentos()
    if args.autoteste:
        sys.exit(0 if autoteste() else 1)
    cfg = {chave: getattr(args, chave) for chave in CONFIGURACAO}
    if cfg["tomada"] not in TOMADAS or cfg["material_tubo"] not in MATERIAIS or cfg["material_placa"] not in MATERIAIS:
        sys.exit("tomada deve ser 1, 2 ou 3 e os materiais de 1 a 6")

    if args.dp is None and args.corrente is None and args.valvula is None:
        print("O que você mediu?  1) ΔP no LD301 (mmH2O)   2) corrente do laço (mA)   3) abertura da válvula (%)")
        opcao = input("Opção: ").strip()
        valor = float(input("Valor: ").replace(",", "."))
        if opcao == "1":
            args.dp = valor
        elif opcao == "2":
            args.corrente = valor
            args.raiz = input("O LD301 está com raiz quadrada? (s/n): ").strip().lower().startswith("s")
        else:
            args.valvula = valor

    if args.valvula is not None:
        Q = cfg["Qmax"] * max(args.valvula, 0) / 100
        print(f"Vazão imposta pela válvula: Q = Qmax·u/100 = {cfg['Qmax']}·{args.valvula}/100 = {Q:.4f} m³/h")
        relatorio(cfg, dp_da_vazao(cfg, Q))
        return
    if args.corrente is not None:
        saida_percentual = (args.corrente - 4) / 16 * 100
        corte_saida = 10 * math.sqrt(cfg["corte_raiz"])
        if args.raiz and saida_percentual < corte_saida:
            print(f"Aviso: saída {saida_percentual:.2f} % abaixo do corte da raiz "
                  f"({cfg['corte_raiz']} % da faixa = {corte_saida:.2f} % da saída); "
                  "abaixo do corte a saída não segue a raiz.")
        dp_mm, entrada = dp_da_corrente(cfg, args.corrente, args.raiz)
        print(f"Corrente {args.corrente} mA -> {entrada:.3f} % da faixa ({'raiz quadrada' if args.raiz else 'linear'}) "
              f"-> ΔP = {cfg['LRV']} + {entrada:.3f} % · ({cfg['URV']} − {cfg['LRV']}) = {dp_mm:.1f} mmH2O")
        args.dp = dp_mm
    relatorio(cfg, vazao_do_dp(cfg, args.dp))


if __name__ == "__main__":
    main()
