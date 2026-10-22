"""Gera as três folhas didáticas de dimensionamento das placas fotografadas.

Usa as mesmas equações do script principal da prática (placa_orificio_calculo.py) e
imprime no terminal um quadro-resumo das três placas. Os resultados são de
simulação e não substituem calibração nem dimensionamento certificado.

Uso (na raiz do repositório):  python python/gerar_folhas_dados.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import placa_orificio_calculo as calc  # noqa: E402


R_AR = 287.05  # J/(kg K), valor de projeto para ar seco
P_N = 101325.0  # Pa abs
T_N = 273.15  # K
P1_G = 200.0  # kPa manométricos
P1_ABS = (P1_G + 101.325) * 1000  # Pa abs
T1 = 293.15  # K
MU_CP = 0.0181  # cP
KAPPA = 1.4
RHO_N = P_N / (R_AR * T_N)
RHO_1 = P1_ABS / (R_AR * T1)
Q_RATIO = RHO_N / RHO_1
CORTE = 6.0  # % da faixa de pressão (padrão do LD301, manual §3)

PLACAS = [
    dict(tag="FE-02-AR", foto="placa03.jpg", D=15.8, d=6.255, beta_gravado="0,395", qn=15.0, linha="1/2", principal=True,
         identificacao="FE-02-AR, gravado e legível na plaqueta", origem_id="P",
         conferencia="leitura nítida. O β gravado (0,395) é d/D truncado; d/D = 0,395886 arredonda para 0,396. "
                     "Os cálculos usam D e d gravados."),
    dict(tag="FE-09-AR", foto="placa02.jpg", D=15.8, d=1.824, beta_gravado="0,1154", qn=1.5, linha="1/2", principal=False,
         identificacao="FE-09-AR, gravado e legível na plaqueta", origem_id="P",
         conferencia="leitura nítida; d/D gravado (0,1154) confere com 1,824/15,8 = 0,115443."),
    dict(tag="FE-01-AR", foto="placa01.jpg", D=20.93, d=15.673, beta_gravado="0,7488", qn=30.0, linha="3/4", principal=False,
         identificacao="tag **não legível** na foto (reflexo); a identificação FE-01-AR para placa01.jpg foi informada pelo professor",
         origem_id="professor",
         conferencia="D = 20,93, d/D = 0,7488 e d = 15,673 são legíveis com ampliação; 15,673/20,93 = 0,748829, "
                     "coerente com o d/D gravado. **Correção de 22/10/2026:** a revisão anterior havia lido "
                     "d ≈ 8,89 mm e β ≈ 0,425, valores que não constam da plaqueta."),
]


def numero(valor: float, casas: int = 3) -> str:
    return f"{valor:.{casas}f}".replace(".", ",")


def configuracao(placa: dict) -> dict:
    cfg = calc.CONFIGURACAO.copy()
    cfg.update(D=placa["D"], d=placa["d"], tomada=3, L_montante=44.0,
               L_jusante=8.0, material_tubo=1, material_placa=2, T=20.0,
               fluido=1, rho=RHO_1, mu=MU_CP, kappa=KAPPA, p1=P1_G,
               Qmax=placa["qn"] * Q_RATIO, desvio=0)
    return cfg


def resultados(placa: dict) -> dict:
    cfg = configuracao(placa)
    full = calc.dp_da_vazao(cfg, cfg["Qmax"])
    urv = round(full["dp_pa"] / calc.MMH2O_EM_PA, 1)
    return dict(cfg=cfg, full=full, urv=urv)


def linha_tabela(placa: dict, res: dict, abertura: int) -> str:
    cfg, urv = res["cfg"], res["urv"]
    qn = placa["qn"] * abertura / 100
    if abertura == 0:
        return (f"| 0% | 0,000 | 0,000 | — | — | — | 0,000 | 0,0 | 0,00% | 0,00% | 4,000 | 0,000 |")
    r = calc.dp_da_vazao(cfg, cfg["Qmax"] * abertura / 100)
    dp_mm = r["dp_pa"] / calc.MMH2O_EM_PA
    dp_pct = 100 * dp_mm / urv
    saida = 10 * math.sqrt(dp_pct) if dp_pct >= CORTE else 0.0  # raiz 10·√x com corte abrupto
    corrente = 4 + 16 * saida / 100
    indicacao = placa["qn"] * saida / 100
    return (f"| {abertura}% | {numero(qn, 3)} | {numero(r['Q'], 3)} | {numero(r['Re'], 0)} | {numero(r['C_iso'], 4)} | "
            f"{numero(r['eps'], 4)} | {numero(r['dp_pa'] / 1000, 3)} | {numero(dp_mm, 1)} | {numero(dp_pct, 2)}% | "
            f"{numero(saida, 2)}% | {numero(corrente, 3)} | {numero(indicacao, 3)} |")


def limites(placa: dict, res: dict) -> str:
    full = res["full"]
    beta, re_ = full["geo"]["beta"], full["Re"]
    re_min = 5000 if beta <= 0.56 else max(5000, 16000 * beta ** 2)
    razao = calc.razao_pressoes(res["cfg"], full["dp_pa"])
    itens = [
        f"`D = {numero(placa['D'], 2)} mm` — {'dentro' if 50 <= placa['D'] <= 1000 else '**fora**'} de 50 mm ≤ D ≤ 1000 mm;",
        f"`d = {numero(placa['d'], 3)} mm` — {'dentro' if placa['d'] >= 12.5 else '**fora**'} de d ≥ 12,5 mm;",
        f"`β = {numero(beta, 4)}` — {'dentro' if 0.1 <= beta <= 0.75 else '**fora**'} de 0,10 ≤ β ≤ 0,75;",
        f"`Re_D = {numero(re_, 0)}` na vazão máxima — {'dentro' if re_ >= re_min else '**fora**'} de Re_D ≥ {numero(re_min, 0)} "
        f"(tomadas de canto);",
        f"`p₂/p₁ = {numero(razao, 4)}` — {'dentro' if razao >= 0.75 else '**fora**'} de p₂/p₁ ≥ 0,75 exigido para ε.",
    ]
    return "\n".join(f"- {item}" for item in itens)


def folha(placa: dict) -> str:
    res = resultados(placa)
    cfg, full, urv = res["cfg"], res["full"], res["urv"]
    dp_kpa = full["dp_pa"] / 1000
    dp_mm = full["dp_pa"] / calc.MMH2O_EM_PA
    dp_mm20 = full["dp_pa"] / calc.MMH2O_20C_EM_PA
    beta = placa["d"] / placa["D"]
    area = math.pi * placa["d"] ** 2 / 4
    tipo = "exemplo resolvido" if placa["principal"] else "exercício do aluno, com valores de conferência"
    slug = placa["tag"].replace("-", "_")
    rows = "\n".join(linha_tabela(placa, res, abertura) for abertura in (0, 20, 25, 50, 75, 100))
    corte_mm = CORTE / 100 * urv

    if placa["principal"]:
        observado = (
            "Os valores **observados** na execução real (LasecSimul rodando e LD301 lido pelo PACTware) estão no "
            "[README, Oficina 05](README.md#oficina-05), com as capturas de cada ponto. Esta folha contém apenas "
            "dados lidos na plaqueta, dados estipulados e valores calculados.")
    else:
        observado = (
            "Preencha durante a aula. Use somente valores lidos nas telas reais; não copie a coluna calculada.\n\n"
            "| Válvula | ΔP no LasecSimul (mmH₂O) | PV lida no PACTware | Corrente no amperímetro (mA) | LCD do LD301 | Captura |\n"
            "|---:|---:|---:|---:|---:|---|\n"
            "| 0% |  |  |  |  |  |\n| 25% |  |  |  |  |  |\n| 50% |  |  |  |  |  |\n| 100% |  |  |  |  |  |")

    extra = ""
    if not placa["principal"]:
        perguntas = {
            "FE-09-AR": ("Na vazão máxima estipulada, Re_D ≈ 2397 fica abaixo de 5000. O que isso significa para o C calculado "
                         "pela equação de Reader–Harris/Gallagher?"),
            "FE-01-AR": ("Com β = 0,7488, o ΔP máximo é só 0,79 kPa (≈ 80,5 mmH₂O), cerca de 1,6% do limite de 50 kPa do "
                         "sensor M2/D2 do LD301. Qual faixa de sensor do manual (D1, D2…) você escolheria? Que Qₙ,max "
                         "daria ≈ 1000 mmH₂O com esta mesma placa?"),
        }[placa["tag"]]
        extra = f"""
## 9. Atividade do aluno

1. Abra a foto [imagens/{placa['foto']}](imagens/{placa['foto']}) e confira cada valor da seção 1. Anote o que é lido e o que é calculado.
2. Sem olhar as seções 3 e 6, calcule ρₙ, ρ₁, Q₁,max, β, área do furo, Re_D, C, ε, ΔPmax e URV.
3. Execute o comando da seção 3 no terminal e compare a saída com o seu cálculo. Faça uma captura do terminal.
4. Gere a cópia do projeto com `python python/preparar_placa_lasecsimul.py {placa['tag']} --substituir-gerado` (ou edite as **Propriedades exportadas** à mão, conforme a seção 4) e confira o painel de propriedades antes de rodar.
5. Abra `placa_orificio_{slug}_calculada.lsproj` e rode a simulação. Clique **Abrir** no modem do LasecSimul. No PACTware, faça **Connect no modem COM20** (ícone verde) e só depois **Connect no LD301** (aba com `#` e **Connected**).
6. Parametrize o LD301 online conforme a seção 5, gravando e relendo cada página. Não use **Offline Parameterize** como prova de gravação.
7. Preencha a tabela da seção 7 em 0%, 25%, 50% e 100% de abertura e explique o corte abrupto em 20% e 25%.
8. Responda: {perguntas}
"""

    return f"""# Folha de dados — {placa['tag']}

**Tipo:** {tipo}. **Revisão:** 22/10/2026. **Serviço estipulado para a prática:** medição de vazão de ar seco em bancada simulada. **Foto de identificação:** [imagens/{placa['foto']}](imagens/{placa['foto']}).

![Plaqueta da placa {placa['tag']}](imagens/{placa['foto']})

**Como ler a origem de cada valor:** **[P]** lido na plaqueta fotografada; **[E]** dado de processo estipulado para a prática, conforme pedido do professor; **[C]** calculado a partir de [P] e [E]; **[O]** observado na tela de uma ferramenta durante a execução.

## 1. Dados da placa

| Campo | Valor | Origem |
|---|---:|:---:|
| Identificação | {placa['identificacao']} | {placa['origem_id']} |
| Linha nominal e classe | {placa['linha']}", 150 LBS | P |
| Fabricante gravado | DIGITROL | P |
| Diâmetro interno da tubulação, D | {numero(placa['D'], 3)} mm | P |
| d/D gravado | {placa['beta_gravado']} | P |
| Diâmetro do orifício, d | {numero(placa['d'], 3)} mm | P |
| Material da placa | AISI 316 | P |
| β = d/D | {numero(beta, 6)} | C |
| Área do orifício = πd²/4 | {numero(area, 3)} mm² | C |

**Conferência da leitura:** {placa['conferencia']} A classe 150 LBS refere-se à conexão flangeada, não à faixa de pressão diferencial do LD301.

## 2. Dados de processo estipulados para a prática [E]

A plaqueta não informa fluido, pressão, temperatura nem vazão. Os valores abaixo foram **estipulados para a prática** e são comuns às três folhas, exceto a vazão máxima.

| Campo | Valor |
|---|---:|
| Fluido | ar seco, escoamento em um sentido |
| Temperatura de operação T₁ | 20 °C = 293,15 K |
| Pressão de operação a montante p₁ | 200,000 kPa manométricos = 301,325 kPa absolutos |
| Condição de referência de Qₙ | 0 °C = 273,15 K; 101,325 kPa absolutos |
| Constante específica do ar, R | 287,05 J/(kg·K) |
| Viscosidade dinâmica μ a 20 °C | 0,0181 cP = 1,81×10⁻⁵ Pa·s |
| Expoente isentrópico κ | 1,40 |
| Tomadas no modelo | canto, código 3 |
| Tubulação / placa no modelo | aço carbono, código 1 / AISI 316, código 2 |
| Trechos retos na simulação | 44D a montante e 8D a jusante |
| Desvio didático de C | 0 = desligado |
| **Vazão máxima de referência Qₙ,max** | **{numero(placa['qn'], 3)} Nm³/h** |

**Convenção:** Nm³/h é volume de ar seco referido a 0 °C e 101,325 kPa absolutos. O LasecSimul recebe e mostra a vazão volumétrica **nas condições de operação** (m³/h a 20 °C e 301,325 kPa abs). Como p₁ e T₁ são constantes nesta prática, Qₙ = Q₁·ρ₁/ρₙ é proporcional a Q₁.

## 3. Cálculo reproduzível [C]

1. **Densidades (gás ideal):** ρₙ = pₙ/(R·Tₙ) = {numero(RHO_N, 6)} kg/m³; ρ₁ = p₁,abs/(R·T₁) = {numero(RHO_1, 6)} kg/m³.
2. **Vazão máxima nas condições de operação:** Q₁ = Qₙ·ρₙ/ρ₁ = {numero(placa['qn'], 3)} × {numero(Q_RATIO, 6)} = **{numero(cfg['Qmax'], 6)} m³/h**. É o valor do parâmetro `Qmax` do LasecSimul.
3. **Geometria:** β = {numero(placa['d'], 3)}/{numero(placa['D'], 3)} = {numero(beta, 6)}; A₀ = {numero(area, 3)} mm². A 20 °C não há correção térmica de D e d.
4. **Velocidade e Reynolds na vazão máxima:** v = {numero(full['v'], 3)} m/s; Re_D = 4ρ₁Q₁/(πμD) = **{numero(full['Re'], 0)}**.
5. **Coeficiente de descarga:** Reader–Harris/Gallagher com tomadas de canto e termo de tubo pequeno (D < 71,12 mm): **C = {numero(full['C_iso'], 6)}**.
6. **Expansibilidade e ΔP (iterados):** ε = {numero(full['eps'], 6)}; p₂/p₁ = {numero(calc.razao_pressoes(cfg, full['dp_pa']), 6)}; ΔP = 8ρ₁(1−β⁴)Q₁²/(C²ε²π²d⁴) = **{numero(dp_kpa, 4)} kPa = {numero(dp_mm, 2)} mmH₂O**.
7. **Faixa do LD301:** LRV = **0,0 mmH₂O**; URV = **{numero(urv, 1)} mmH₂O**. O URV é a pressão diferencial na vazão máxima, não a vazão. A perda permanente estimada ({numero(full['perda_kpa'], 3)} kPa) não é o URV.

**Unidade mmH₂O.** O script e a planta do LasecSimul convertem Pa em mmH₂O com 9,80665 Pa/mmH₂O (mmH₂O convencional). O LD301 rotula a unidade como `mmH2O@20C` (código HART 4, manual Tabela 3.1: 1 mmH₂O@20 °C = 248,642/25,4 = 9,7891 Pa). No simulador, o LD301 recebe HIGH − LOW sem converter unidade, logo o URV que coincide com a planta é **{numero(urv, 1)}**. Num transmissor real, o mesmo ΔP vale {numero(dp_mm20, 1)} mmH₂O@20 °C (diferença de 0,18%); para evitar a ambiguidade, configure-o em kPa: URV = {numero(dp_kpa, 3)} kPa.

### Comando do cálculo independente

```powershell
python placa_orificio_calculo.py --D {placa['D']} --d {placa['d']} --tomada 3 --L_montante 44 --L_jusante 8 --material_tubo 1 --material_placa 2 --T 20 --fluido 1 --rho {RHO_1:.9f} --mu 0.0181 --kappa 1.4 --p1 200 --Qmax {cfg['Qmax']:.9f} --desvio 0 --LRV 0 --URV {urv:.1f} --valvula 100
```

Para outro ponto, troque `--valvula 100` pela abertura desejada. O quadro das três placas sai de `python python/gerar_folhas_dados.py`.

## 4. Ajustes no LasecSimul (aplicar na cópia do projeto)

Use `placa_orificio_{slug}_calculada.lsproj`, gerado por `python python/preparar_placa_lasecsimul.py {placa['tag']}`, ou edite as **Propriedades exportadas** da placa numa cópia do projeto:

| Propriedade | Valor | Propriedade | Valor |
|---|---:|---|---:|
| D | {numero(placa['D'], 3)} mm | Fluido | 1 = gás |
| d | {numero(placa['d'], 3)} mm | ρ | {numero(RHO_1, 6)} kg/m³ |
| Tomada | 3 = canto | μ | 0,0181 cP |
| Montante / jusante | 44D / 8D | κ | 1,4 |
| Material tubo / placa | 1 / 2 | p₁ | 200 kPa manométricos |
| Temperatura | 20 °C | Qmax | {numero(cfg['Qmax'], 6)} m³/h |
| Desvio didático | 0 | | |

## 5. Parametrização do LD301 no PACTware (aplicar online)

Antes: LasecSimul **Rodando**, **Abrir** no modem, **Connect no modem COM20** (ícone verde) e **Connect no LD301** (aba `LD301 # Parameter`, barra **Connected**). Caminho no DTM SMAR LD301 (versão 3.03): **Online Parameterize → Blocks**. Grave cada página com **Write** e releia antes de passar à seguinte.

| Página do DTM | Parâmetro | Valor a gravar |
|---|---|---|
| Configuration → Measurement | Primary Variable Unit | mmH2O@20°C |
| Configuration → Measurement | LRV / URV | 0,0000 / {numero(urv, 1)} |
| Summary | Function | Sqrt |
| — | Ponto de corte / modo | não aparece nas páginas online do DTM 3.03; o transmissor simulado mantém {numero(CORTE, 0)}% / Hard (abrupto). Verifique pelo comportamento: abaixo de {numero(corte_mm, 1)} mmH₂O a corrente deve ficar em 4,000 mA |
| Configuration → User Unit | Mode / Eng. Unit (0%) / Eng. Unit (100%) | On / 0 / {numero(placa['qn'], 2)} |
| Configuration → User Unit | Unit Family / Unit Description | Volumetric Flow / N m3/h |
| Configuration → Display | Display 1st / 2nd variable | PV / Out(mA) |

Pela raiz ideal, o corte de {numero(CORTE, 0)}% da faixa de pressão equivale a {numero(placa['qn'] * math.sqrt(CORTE / 100), 3)} Nm³/h (24,49% da vazão máxima). O DTM oferece `N m3/h` na família Volumetric Flow; a alternativa `m3/h` com 100% → {numero(cfg['Qmax'], 3)} indicaria a vazão nas condições de operação.

## 6. Resultados para conferência [C]

| Válvula | Qₙ (Nm³/h) | Q₁ (m³/h) | Re_D | C | ε | ΔP (kPa) | ΔP (mmH₂O) | ΔP/faixa | Saída raiz | Corrente (mA) | Indicação esperada (Nm³/h) |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
{rows}

Saída raiz = 10·√(ΔP/faixa em %) com corte abrupto em {numero(CORTE, 0)}%; indicação = Qₙ,max × saída. A indicação difere um pouco de Qₙ porque C e ε variam com a vazão e o LD301 só extrai a raiz. Em 0% não há escoamento, e Re, C e ε não se aplicam. **Estes números são previsões calculadas, não leituras de tela.**

## 7. Valores observados na aplicação [O]

{observado}

## 8. Limites de validade

Faixa de aplicação da ISO 5167-2 para placa com tomadas de canto, comparada com esta placa:

{limites(placa, res)}

**Conclusão:** esta placa está fora do escopo da ISO 5167-2 em pelo menos um requisito. O C usado pelo Python e pelo LasecSimul é uma **extrapolação didática**; a folha não declara conformidade normativa nem exatidão certificada. Antes de usar a placa física, confirme dimensões, posição das tomadas, condições de processo e a faixa do sensor do LD301 por método adequado a tubos pequenos.
{extra}
## Fontes

- [Foto da placa no projeto](imagens/{placa['foto']}).
- ISO 5167-2:2022 — [escopo oficial](https://www.iso.org/standard/79180.html) e [prévia do texto, §§ 5.1.8 e 5.3.1](https://cdn.standards.iteh.ai/samples/79180/1029711dc5e5474f8c079fffcf5b6b3b/ISO-5167-2-2022.pdf).
- [NIST — condições de referência de gás](https://www.nist.gov/pml/owm/metric-si/unit-conversion/pressure-and-gas-flow-unit-conversions).
- SMAR, manual do LD301, cópia local [MANUAL_LD301.pdf](MANUAL_LD301.pdf): Tabela 3.1 (unidades), Unidade do Usuário, função RAIZ e ponto de corte, display; tabela de faixas do sensor.
- [Código de cálculo usado nesta folha](placa_orificio_calculo.py) e [gerador desta folha](python/gerar_folhas_dados.py).
"""


def resumo() -> None:
    print(f"Ar seco: ρn = {RHO_N:.6f} kg/m³ (0 °C; 101,325 kPa abs)   ρ1 = {RHO_1:.6f} kg/m³ (20 °C; 301,325 kPa abs)"
          f"   Q1/Qn = {Q_RATIO:.6f}")
    print(f"{'Placa':9s} {'D mm':>6s} {'d mm':>7s} {'β':>7s} {'Qn Nm³/h':>9s} {'Q1 m³/h':>9s} {'Re_D':>7s} {'C':>8s} "
          f"{'ε':>8s} {'ΔP kPa':>8s} {'ΔP mmH2O':>9s} {'URV':>7s}")
    for placa in PLACAS:
        res = resultados(placa)
        full = res["full"]
        print(f"{placa['tag']:9s} {placa['D']:6.2f} {placa['d']:7.3f} {full['geo']['beta']:7.4f} {placa['qn']:9.3f} "
              f"{res['cfg']['Qmax']:9.4f} {full['Re']:7.0f} {full['C_iso']:8.5f} {full['eps']:8.5f} "
              f"{full['dp_pa'] / 1000:8.4f} {full['dp_pa'] / calc.MMH2O_EM_PA:9.2f} {res['urv']:7.1f}")


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    resumo()
    for placa in PLACAS:
        destino = ROOT / f"FOLHA_DADOS_{placa['tag'].replace('-', '_')}.md"
        # Os links da folha são relativos à raiz do projeto.
        destino.write_text(folha(placa), encoding="utf-8")
        print("Gravada:", destino.name)


if __name__ == "__main__":
    main()
