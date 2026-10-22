# Folha de dados — FE-01-AR

**Tipo:** exercício do aluno, com valores de conferência. **Revisão:** 22/10/2026. **Serviço estipulado para a prática:** medição de vazão de ar seco em bancada simulada. **Foto de identificação:** [imagens/placa01.jpg](imagens/placa01.jpg).

![Plaqueta da placa FE-01-AR](imagens/placa01.jpg)

**Como ler a origem de cada valor:** **[P]** lido na plaqueta fotografada; **[E]** dado de processo estipulado para a prática, conforme pedido do professor; **[C]** calculado a partir de [P] e [E]; **[O]** observado na tela de uma ferramenta durante a execução.

## 1. Dados da placa

| Campo | Valor | Origem |
|---|---:|:---:|
| Identificação | tag **não legível** na foto (reflexo); a identificação FE-01-AR para placa01.jpg foi informada pelo professor | professor |
| Linha nominal e classe | 3/4", 150 LBS | P |
| Fabricante gravado | DIGITROL | P |
| Diâmetro interno da tubulação, D | 20,930 mm | P |
| d/D gravado | 0,7488 | P |
| Diâmetro do orifício, d | 15,673 mm | P |
| Material da placa | AISI 316 | P |
| β = d/D | 0,748829 | C |
| Área do orifício = πd²/4 | 192,928 mm² | C |

**Conferência da leitura:** D = 20,93, d/D = 0,7488 e d = 15,673 são legíveis com ampliação; 15,673/20,93 = 0,748829, coerente com o d/D gravado. **Correção de 22/10/2026:** a revisão anterior havia lido d ≈ 8,89 mm e β ≈ 0,425, valores que não constam da plaqueta. A classe 150 LBS refere-se à conexão flangeada, não à faixa de pressão diferencial do LD301.

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
| **Vazão máxima de referência Qₙ,max** | **30,000 Nm³/h** |

**Convenção:** Nm³/h é volume de ar seco referido a 0 °C e 101,325 kPa absolutos. O LasecSimul recebe e mostra a vazão volumétrica **nas condições de operação** (m³/h a 20 °C e 301,325 kPa abs). Como p₁ e T₁ são constantes nesta prática, Qₙ = Q₁·ρ₁/ρₙ é proporcional a Q₁.

## 3. Cálculo reproduzível [C]

1. **Densidades (gás ideal):** ρₙ = pₙ/(R·Tₙ) = 1,292284 kg/m³; ρ₁ = p₁,abs/(R·T₁) = 3,580863 kg/m³.
2. **Vazão máxima nas condições de operação:** Q₁ = Qₙ·ρₙ/ρ₁ = 30,000 × 0,360886 = **10,826583 m³/h**. É o valor do parâmetro `Qmax` do LasecSimul.
3. **Geometria:** β = 15,673/20,930 = 0,748829; A₀ = 192,928 mm². A 20 °C não há correção térmica de D e d.
4. **Velocidade e Reynolds na vazão máxima:** v = 8,741 m/s; Re_D = 4ρ₁Q₁/(πμD) = **36194**.
5. **Coeficiente de descarga:** Reader–Harris/Gallagher com tomadas de canto e termo de tubo pequeno (D < 71,12 mm): **C = 0,615173**.
6. **Expansibilidade e ΔP (iterados):** ε = 0,999020; p₂/p₁ = 0,997379; ΔP = 8ρ₁(1−β⁴)Q₁²/(C²ε²π²d⁴) = **0,7897 kPa = 80,53 mmH₂O**.
7. **Faixa do LD301:** LRV = **0,0 mmH₂O**; URV = **80,5 mmH₂O**. O URV é a pressão diferencial na vazão máxima, não a vazão. A perda permanente estimada (0,351 kPa) não é o URV.

**Unidade mmH₂O.** O script e a planta do LasecSimul convertem Pa em mmH₂O com 9,80665 Pa/mmH₂O (mmH₂O convencional). O LD301 rotula a unidade como `mmH2O@20C` (código HART 4, manual Tabela 3.1: 1 mmH₂O@20 °C = 248,642/25,4 = 9,7891 Pa). No simulador, o LD301 recebe HIGH − LOW sem converter unidade, logo o URV que coincide com a planta é **80,5**. Num transmissor real, o mesmo ΔP vale 80,7 mmH₂O@20 °C (diferença de 0,18%); para evitar a ambiguidade, configure-o em kPa: URV = 0,790 kPa.

### Comando do cálculo independente

```powershell
python placa_orificio_calculo.py --D 20.93 --d 15.673 --tomada 3 --L_montante 44 --L_jusante 8 --material_tubo 1 --material_placa 2 --T 20 --fluido 1 --rho 3.580863081 --mu 0.0181 --kappa 1.4 --p1 200 --Qmax 10.826582648 --desvio 0 --LRV 0 --URV 80.5 --valvula 100
```

Para outro ponto, troque `--valvula 100` pela abertura desejada. O quadro das três placas sai de `python python/gerar_folhas_dados.py`.

## 4. Ajustes no LasecSimul (aplicar na cópia do projeto)

Use `placa_orificio_FE_01_AR_calculada.lsproj`, gerado por `python python/preparar_placa_lasecsimul.py FE-01-AR`, ou edite as **Propriedades exportadas** da placa numa cópia do projeto:

| Propriedade | Valor | Propriedade | Valor |
|---|---:|---|---:|
| D | 20,930 mm | Fluido | 1 = gás |
| d | 15,673 mm | ρ | 3,580863 kg/m³ |
| Tomada | 3 = canto | μ | 0,0181 cP |
| Montante / jusante | 44D / 8D | κ | 1,4 |
| Material tubo / placa | 1 / 2 | p₁ | 200 kPa manométricos |
| Temperatura | 20 °C | Qmax | 10,826583 m³/h |
| Desvio didático | 0 | | |

## 5. Parametrização do LD301 no PACTware (aplicar online)

Antes: LasecSimul **Rodando**, **Abrir** no modem, **Connect no modem COM20** (ícone verde) e **Connect no LD301** (aba `LD301 # Parameter`, barra **Connected**). Caminho no DTM SMAR LD301 (versão 3.03): **Online Parameterize → Blocks**. Grave cada página com **Write** e releia antes de passar à seguinte.

| Página do DTM | Parâmetro | Valor a gravar |
|---|---|---|
| Configuration → Measurement | Primary Variable Unit | mmH2O@20°C |
| Configuration → Measurement | LRV / URV | 0,0000 / 80,5 |
| Summary | Function | Sqrt |
| — | Ponto de corte / modo | não aparece nas páginas online do DTM 3.03; o transmissor simulado mantém 6% / Hard (abrupto). Verifique pelo comportamento: abaixo de 4,8 mmH₂O a corrente deve ficar em 4,000 mA |
| Configuration → User Unit | Mode / Eng. Unit (0%) / Eng. Unit (100%) | On / 0 / 30,00 |
| Configuration → User Unit | Unit Family / Unit Description | Volumetric Flow / N m3/h |
| Configuration → Display | Display 1st / 2nd variable | PV / Out(mA) |

Pela raiz ideal, o corte de 6% da faixa de pressão equivale a 7,348 Nm³/h (24,49% da vazão máxima). O DTM oferece `N m3/h` na família Volumetric Flow; a alternativa `m3/h` com 100% → 10,827 indicaria a vazão nas condições de operação.

## 6. Resultados para conferência [C]

| Válvula | Qₙ (Nm³/h) | Q₁ (m³/h) | Re_D | C | ε | ΔP (kPa) | ΔP (mmH₂O) | ΔP/faixa | Saída raiz | Corrente (mA) | Indicação esperada (Nm³/h) |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0% | 0,000 | 0,000 | — | — | — | 0,000 | 0,0 | 0,00% | 0,00% | 4,000 | 0,000 |
| 20% | 6,000 | 2,165 | 7239 | 0,6500 | 1,0000 | 0,028 | 2,9 | 3,58% | 0,00% | 4,000 | 0,000 |
| 25% | 7,500 | 2,707 | 9049 | 0,6424 | 0,9999 | 0,045 | 4,6 | 5,72% | 0,00% | 4,000 | 0,000 |
| 50% | 15,000 | 5,413 | 18097 | 0,6255 | 0,9998 | 0,191 | 19,4 | 24,15% | 49,14% | 11,863 | 14,743 |
| 75% | 22,500 | 8,120 | 27146 | 0,6189 | 0,9995 | 0,438 | 44,7 | 55,54% | 74,53% | 15,924 | 22,358 |
| 100% | 30,000 | 10,827 | 36194 | 0,6152 | 0,9990 | 0,790 | 80,5 | 100,03% | 100,02% | 20,003 | 30,005 |

Saída raiz = 10·√(ΔP/faixa em %) com corte abrupto em 6%; indicação = Qₙ,max × saída. A indicação difere um pouco de Qₙ porque C e ε variam com a vazão e o LD301 só extrai a raiz. Em 0% não há escoamento, e Re, C e ε não se aplicam. **Estes números são previsões calculadas, não leituras de tela.**

## 7. Valores observados na aplicação [O]

Preencha durante a aula. Use somente valores lidos nas telas reais; não copie a coluna calculada.

| Válvula | ΔP no LasecSimul (mmH₂O) | PV lida no PACTware | Corrente no amperímetro (mA) | LCD do LD301 | Captura |
|---:|---:|---:|---:|---:|---|
| 0% |  |  |  |  |  |
| 25% |  |  |  |  |  |
| 50% |  |  |  |  |  |
| 100% |  |  |  |  |  |

## 8. Limites de validade

Faixa de aplicação da ISO 5167-2 para placa com tomadas de canto, comparada com esta placa:

- `D = 20,93 mm` — **fora** de 50 mm ≤ D ≤ 1000 mm;
- `d = 15,673 mm` — dentro de d ≥ 12,5 mm;
- `β = 0,7488` — dentro de 0,10 ≤ β ≤ 0,75;
- `Re_D = 36194` na vazão máxima — dentro de Re_D ≥ 8972 (tomadas de canto);
- `p₂/p₁ = 0,9974` — dentro de p₂/p₁ ≥ 0,75 exigido para ε.

**Conclusão:** esta placa está fora do escopo da ISO 5167-2 em pelo menos um requisito. O C usado pelo Python e pelo LasecSimul é uma **extrapolação didática**; a folha não declara conformidade normativa nem exatidão certificada. Antes de usar a placa física, confirme dimensões, posição das tomadas, condições de processo e a faixa do sensor do LD301 por método adequado a tubos pequenos.

## 9. Atividade do aluno

1. Abra a foto [imagens/placa01.jpg](imagens/placa01.jpg) e confira cada valor da seção 1. Anote o que é lido e o que é calculado.
2. Sem olhar as seções 3 e 6, calcule ρₙ, ρ₁, Q₁,max, β, área do furo, Re_D, C, ε, ΔPmax e URV.
3. Execute o comando da seção 3 no terminal e compare a saída com o seu cálculo. Faça uma captura do terminal.
4. Gere a cópia do projeto com `python python/preparar_placa_lasecsimul.py FE-01-AR --substituir-gerado` (ou edite as **Propriedades exportadas** à mão, conforme a seção 4) e confira o painel de propriedades antes de rodar.
5. Abra `placa_orificio_FE_01_AR_calculada.lsproj` e rode a simulação. Clique **Abrir** no modem do LasecSimul. No PACTware, faça **Connect no modem COM20** (ícone verde) e só depois **Connect no LD301** (aba com `#` e **Connected**).
6. Parametrize o LD301 online conforme a seção 5, gravando e relendo cada página. Não use **Offline Parameterize** como prova de gravação.
7. Preencha a tabela da seção 7 em 0%, 25%, 50% e 100% de abertura e explique o corte abrupto em 20% e 25%.
8. Responda: Com β = 0,7488, o ΔP máximo é só 0,79 kPa (≈ 80,5 mmH₂O), cerca de 1,6% do limite de 50 kPa do sensor M2/D2 do LD301. Qual faixa de sensor do manual (D1, D2…) você escolheria? Que Qₙ,max daria ≈ 1000 mmH₂O com esta mesma placa?

## Fontes

- [Foto da placa no projeto](imagens/placa01.jpg).
- ISO 5167-2:2022 — [escopo oficial](https://www.iso.org/standard/79180.html) e [prévia do texto, §§ 5.1.8 e 5.3.1](https://cdn.standards.iteh.ai/samples/79180/1029711dc5e5474f8c079fffcf5b6b3b/ISO-5167-2-2022.pdf).
- [NIST — condições de referência de gás](https://www.nist.gov/pml/owm/metric-si/unit-conversion/pressure-and-gas-flow-unit-conversions).
- SMAR, manual do LD301, cópia local [MANUAL_LD301.pdf](MANUAL_LD301.pdf): Tabela 3.1 (unidades), Unidade do Usuário, função RAIZ e ponto de corte, display; tabela de faixas do sensor.
- [Código de cálculo usado nesta folha](placa_orificio_calculo.py) e [gerador desta folha](python/gerar_folhas_dados.py).
