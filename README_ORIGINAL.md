# Instrumentação Industrial II
## Aula Prática 05: Medição de Vazão com Placa de Orifício e Transmissor LD301

Esta prática apresenta a base teórica e a execução, no simulador **LasecSimul**, de uma medição de vazão por **placa de orifício** com o transmissor de pressão diferencial **Smar LD301 (HART)**, configurado pelo **PACTware**.

O material foi organizado para ligar, passo a passo, a física da medição ao que o transmissor faz, com foco em:

- princípio da medição de vazão por pressão diferencial;
- equação da placa de orifício e coeficiente de descarga `C` segundo a **ISO 5167-2**;
- influência do tipo de tomada, dos trechos retos, do material e da temperatura;
- relação quadrática entre `ΔP` e vazão e a função **raiz quadrada** do transmissor;
- configuração do LD301 pelo PACTware para **indicar e transmitir vazão**;
- verificação dos resultados com um script em Python.

---

## Índice

1. [Introdução](#1-introdução)
2. [Princípio da medição por pressão diferencial](#2-princípio-da-medição-por-pressão-diferencial)
3. [A placa de orifício segundo a ISO 5167-2](#3-a-placa-de-orifício-segundo-a-iso-5167-2)
4. [Instalação: tomadas, trechos retos e rugosidade](#4-instalação-tomadas-trechos-retos-e-rugosidade)
5. [A planta no LasecSimul](#5-a-planta-no-lasecsimul)
6. [O transmissor LD301 na medição de vazão](#6-o-transmissor-ld301-na-medição-de-vazão)
7. [Arquivos da prática](#7-arquivos-da-prática)
8. [Como executar](#8-como-executar)
9. [Conexão com o PACTware](#9-conexão-com-o-pactware)
10. [Configuração do LD301 para vazão](#10-configuração-do-ld301-para-vazão)
11. [Ferramenta de apoio em Python](#11-ferramenta-de-apoio-em-python)
12. [Sugestão de atividade experimental](#12-sugestão-de-atividade-experimental)
13. [Conclusão](#13-conclusão)
14. [Referências](#14-referências)
15. [Apêndice: lista de imagens](#15-apêndice-lista-de-imagens)

---

## 1. Introdução

A **placa de orifício** é o elemento primário de vazão mais usado na indústria. Trata-se de uma chapa fina com um furo calibrado, instalada entre dois flanges da tubulação. Ao passar pelo furo, o fluido acelera e sua pressão cai. Essa queda de pressão, medida antes e depois da placa, está relacionada à vazão.

Esse tipo de medição é amplamente utilizado em:

- linhas de água, vapor, óleo e gás;
- controle de vazão em malhas de processo;
- medição fiscal e de transferência de custódia (gás natural);
- sistemas de utilidades industriais.

As placas de orifício se destacam por apresentarem:

- construção simples e baixo custo;
- ausência de partes móveis;
- norma internacional completa (**ISO 5167**), que permite calcular a vazão sem calibração em laboratório;
- uso de transmissores de pressão diferencial padronizados, como o LD301.

Como desvantagens, apresentam perda de carga permanente e relação **quadrática** entre vazão e pressão diferencial, o que limita a rangeabilidade.

**Figura 1. Placa de orifício concêntrica**

![Figura 1](assets/fig01_placa_orificio.jpg)

> **Imagem a inserir:** foto de uma placa de orifício concêntrica real, de preferência segurada pela haste (aba de identificação), mostrando o furo central, a aresta viva do lado de montante e o chanfro (bisel) do lado de jusante. Se possível, uma segunda foto da placa montada entre dois flanges com as tomadas de pressão. As fotos `placa01.jpg` a `placa03.jpg` da pasta antiga da prática podem ser reaproveitadas.

---

## 2. Princípio da medição por pressão diferencial

### 2.1 Bernoulli e continuidade

Considere a seção 1, na tubulação (diâmetro `D`, velocidade `V_1`), e a seção 2, no orifício (diâmetro `d`, velocidade `V_2`). Para um fluido incompressível e sem perdas, a equação de **Bernoulli** entre as duas seções, na mesma altura, é:

$$
P_1 + \frac{1}{2}\rho V_1^2 = P_2 + \frac{1}{2}\rho V_2^2
$$

e a equação da **continuidade** é:

$$
V_1 \frac{\pi D^2}{4} = V_2 \frac{\pi d^2}{4}
\quad\Rightarrow\quad
V_1 = \beta^2 V_2
$$

onde a **razão de diâmetros** é:

$$
\beta = \frac{d}{D}
$$

Substituindo `V_1` em Bernoulli e chamando `ΔP = P_1 − P_2`:

$$
V_2 = \sqrt{\frac{2\,\Delta P}{\rho\,(1-\beta^4)}}
$$

### 2.2 Equação da vazão

Multiplicando pela área do orifício e corrigindo os efeitos reais (contração do jato, atrito, posição das tomadas) com o **coeficiente de descarga** `C`, e a compressibilidade com o **fator de expansibilidade** `ε`, chega-se à equação da placa de orifício:

$$
Q = C\,\varepsilon\,\frac{\pi d^2}{4}\sqrt{\frac{2\,\Delta P}{\rho\,(1-\beta^4)}}
$$

Onde:

- `Q` é a vazão volumétrica nas condições de operação (m³/s);
- `C` é o coeficiente de descarga (adimensional, em torno de 0,6);
- `ε` é o fator de expansibilidade (`ε = 1` para líquidos);
- `d` é o diâmetro do orifício (m);
- `ΔP` é a pressão diferencial entre as tomadas (Pa);
- `ρ` é a massa específica do fluido a montante (kg/m³).

Isolando `ΔP`, obtém-se a forma usada pelo simulador:

$$
\Delta P = \frac{8\,\rho\,(1-\beta^4)\,Q^2}{C^2\,\varepsilon^2\,\pi^2\,d^4}
$$

### 2.3 A relação quadrática

A equação mostra que **`ΔP` cresce com o quadrado da vazão**:

$$
\frac{\Delta P}{\Delta P_{max}} \approx \left(\frac{Q}{Q_{max}}\right)^2
$$

Assim, metade da vazão produz apenas um quarto da pressão diferencial, e 10 % da vazão produzem só 1 % do `ΔP`. Por isso o transmissor precisa **extrair a raiz quadrada** para que a corrente 4–20 mA seja proporcional à vazão (seção 6).

### 2.4 Perfil de pressão e perda permanente

Depois da placa, o jato continua se contraindo até a **vena contracta**, onde a pressão é mínima, e então se expande, recuperando parte da pressão. A parcela não recuperada é a **perda de carga permanente**:

$$
\Delta\omega = \frac{\sqrt{1-\beta^4(1-C^2)} - C\beta^2}{\sqrt{1-\beta^4(1-C^2)} + C\beta^2}\,\Delta P
$$

**Figura 2. Perfil de pressão ao longo da placa de orifício**

![Figura 2](assets/fig02_perfil_pressao.png)

> **Imagem a inserir:** desenho em corte de um trecho de tubulação com a placa de orifício e, logo abaixo, um gráfico da pressão estática ao longo do eixo da tubulação. O gráfico deve mostrar a pressão a montante `P_1`, a queda até o mínimo na vena contracta (um pouco depois da placa), a recuperação parcial a jusante e, indicadas com cotas, a pressão diferencial medida `ΔP` e a perda permanente `Δω`. Desenhe as linhas de corrente se contraindo no orifício e se expandindo depois.

---

## 3. A placa de orifício segundo a ISO 5167-2

### 3.1 Coeficiente de descarga de Reader-Harris/Gallagher

A ISO 5167-2 dá o coeficiente de descarga `C` de uma placa concêntrica de aresta viva pela equação de **Reader-Harris/Gallagher**:

$$
\begin{aligned}
C ={}& 0{,}5961 + 0{,}0261\beta^2 - 0{,}216\beta^8 + 0{,}000521\left(\frac{10^6\beta}{Re_D}\right)^{0{,}7} \\
&+ \left(0{,}0188 + 0{,}0063A\right)\beta^{3{,}5}\left(\frac{10^6}{Re_D}\right)^{0{,}3} \\
&+ \left(0{,}043 + 0{,}080e^{-10L_1} - 0{,}123e^{-7L_1}\right)\left(1 - 0{,}11A\right)\frac{\beta^4}{1-\beta^4} \\
&- 0{,}031\left(M_2' - 0{,}8M_2'^{\,1{,}1}\right)\beta^{1{,}3}
\end{aligned}
$$

com:

$$
A = \left(\frac{19000\,\beta}{Re_D}\right)^{0{,}8}
\qquad
M_2' = \frac{2L_2'}{1-\beta}
\qquad
Re_D = \frac{4\,\rho\,Q}{\pi\,\mu\,D}
$$

Quando `D < 71,12 mm`, soma-se ainda o termo de tubulação pequena:

$$
+\;0{,}011\,(0{,}75-\beta)\left(2{,}8 - \frac{D}{25{,}4}\right)
$$

Onde:

- `Re_D` é o número de Reynolds na tubulação;
- `μ` é a viscosidade dinâmica do fluido (Pa·s);
- `L_1` é a distância da tomada de alta à face de montante da placa, dividida por `D`;
- `L_2'` é a distância da tomada de baixa à face de jusante da placa, dividida por `D`.

Observe que **`C` depende de `Re_D`**, portanto da própria vazão. Ele não é uma constante: varia pouco, mas varia.

### 3.2 Fator de expansibilidade

Para gases, a queda de pressão no orifício expande o fluido. A ISO 5167-2 corrige isso com:

$$
\varepsilon = 1 - \left(0{,}351 + 0{,}256\beta^4 + 0{,}93\beta^8\right)\left[1 - \left(\frac{p_2}{p_1}\right)^{1/\kappa}\right]
$$

Onde `κ` é o expoente isentrópico do gás e `p_1`, `p_2` são as pressões absolutas nas tomadas. Para líquidos, `ε = 1`.

### 3.3 Faixa de validade

A equação só vale dentro dos limites da norma:

- `d ≥ 12,5 mm`;
- `50 mm ≤ D ≤ 1000 mm`;
- `0,1 ≤ β ≤ 0,75`;
- `Re_D ≥ 5000`; com tomadas de flange, também `Re_D ≥ 170\,β^2 D` (D em mm);
- com tomadas de canto ou D e D/2 e `β > 0,56`, `Re_D ≥ 16000\,β^2`;
- para gases, `p_2/p_1 ≥ 0,75`.

### 3.4 Correção de temperatura

`D` e `d` são medidos a 20 °C. Na temperatura de operação `T`, cada um dilata conforme o seu material:

$$
D_T = D_{20}\left[1 + \alpha_{tubo}\,(T-20)\right]
\qquad
d_T = d_{20}\left[1 + \alpha_{placa}\,(T-20)\right]
$$

---

## 4. Instalação: tomadas, trechos retos e rugosidade

### 4.1 Tipos de tomada

A ISO 5167-2 admite três posições para as tomadas de pressão. Cada uma entra na equação de `C` pelos valores de `L_1` e `L_2'`:

| Tomada | Posição | `L_1` | `L_2'` |
|---|---|---:|---:|
| Flange | 25,4 mm de cada face da placa, furadas nos flanges | `25,4/D` | `25,4/D` |
| D e D/2 (*radius taps*) | 1·D antes e 0,5·D depois da placa | 1 | 0,47 |
| Canto (*corner taps*) | rente às faces da placa | 0 | 0 |

**Figura 3. Posição das tomadas de flange, D e D/2 e de canto**

![Figura 3](assets/fig03_tipos_tomada.png)

> **Imagem a inserir:** desenho em corte de uma placa de orifício entre flanges, com as três alternativas de tomada lado a lado (ou sobrepostas em cores diferentes): tomadas de canto rentes à placa; tomadas de flange a 25,4 mm (1") de cada face, furadas nos próprios flanges; tomadas D e D/2 na tubulação, a uma distância `D` antes e `D/2` depois da placa. Cote as distâncias e identifique as tomadas de alta (+) e de baixa (−).

### 4.2 Trechos retos

Curvas, válvulas e reduções deformam o perfil de velocidade. Para que a equação de `C` seja válida, a placa precisa de **trechos retos** mínimos antes (montante) e depois (jusante). Para **uma curva de 90° a montante**, a Tabela 3 da ISO 5167-2 pede, em múltiplos de `D`:

| β | Montante sem incerteza adicional | Montante mínimo (+0,5 % de incerteza) | Jusante |
|---:|---:|---:|---:|
| ≤ 0,20 | 6 | 3 | 4 |
| 0,40 | 16 | 3 | 6 |
| 0,50 | 22 | 9 | 6 |
| 0,60 | 42 | 13 | 7 |
| 0,67 | 44 | 20 | 7 |
| 0,75 | 44 | 20 | 8 |

Para `β` intermediário, vale a linha do `β` maior seguinte.

**Figura 4. Trechos retos a montante e a jusante da placa**

![Figura 4](assets/fig04_trechos_retos.png)

> **Imagem a inserir:** desenho isométrico ou em planta de uma linha com a entrada por uma curva de 90°, o trecho reto a montante (cotado como `L montante = n·D`), a placa de orifício entre flanges, o trecho reto a jusante (cotado como `L jusante = n·D`) e, no fim, uma válvula de controle. Indique o sentido do escoamento com setas e mostre as tomadas descendo até o transmissor de pressão diferencial.

### 4.3 Rugosidade

A rugosidade interna da tubulação também altera `C`. A norma limita a razão `10^4·Ra/D` (Tabela 1 da ISO 5167-2). Para `β = 0,6`, o limite é cerca de 4,1. Tubos de ferro fundido ou galvanizados de pequeno diâmetro ultrapassam esse limite.

---

## 5. A planta no LasecSimul

O projeto [`placa_orificio_ld301.lsproj`](placa_orificio_ld301.lsproj) reproduz uma linha de água com uma placa de orifício, uma válvula de controle no fim do trecho a jusante e o transmissor LD301 ligado às tomadas. A planta vem **incorporada ao projeto**: não é preciso instalar nada além do LasecSimul (versão **0.0.83 ou mais nova**).

**Figura 5. Projeto completo no LasecSimul**

![Figura 5](assets/fig05_projeto_completo.png)

> **Imagem a inserir:** captura de tela do LasecSimul com o projeto `placa_orificio_ld301.lsproj` aberto e a simulação **rodando** (selo verde "Running"). Devem aparecer: o slider "Válvula de controle (%)" à esquerda, a planta da placa de orifício no centro, o LD301 à direita com a fonte de 24 V, o resistor de 250 Ω, o amperímetro, o modem HART e o osciloscópio. Use o botão de "ajustar tudo à tela".

### 5.1 O que a planta calcula

- a **válvula** (0–100 %, pelo slider) impõe a vazão `Q = Qmax·u/100`, com um atraso de primeira ordem de 1 s;
- `D` e `d` são corrigidos para a temperatura de operação;
- `C` vem da equação de Reader-Harris/Gallagher da seção 3, para a tomada escolhida;
- `ε` vem da equação da norma quando o fluido é gás;
- a tomada de **alta (HIGH)** recebe a pressão a montante `p_1`, e a de **baixa (LOW)** recebe `p_1 − ΔP`, ambas em mmH2O, que é a unidade do LD301.

### 5.2 Parâmetros (Propriedades exportadas)

Selecione a planta e abra o painel **Properties** → **Propriedades exportadas**. Os valores mudam com a simulação rodando:

| Parâmetro | Padrão |
|---|---|
| Diâmetro interno da tubulação D (a 20 °C) | 52,5 mm (2" sch 40) |
| Diâmetro do orifício d (a 20 °C) | 31,5 mm (β = 0,6) |
| Tipo de tomada de pressão | Flange |
| Trecho reto a montante (da curva até a placa) | 44 D |
| Trecho reto a jusante (da placa até a válvula) | 8 D |
| Material da tubulação | Aço carbono |
| Material da placa de orifício | Aço inox AISI 316 |
| Temperatura de operação | 20 °C |
| Fluido | Líquido |
| Massa específica na operação | 998,2 kg/m³ (água a 20 °C) |
| Viscosidade dinâmica | 1,002 cP |
| Expoente isentrópico κ (gás) | 1,4 |
| Pressão a montante (manométrica) | 200 kPa |
| Vazão máxima (válvula 100 %) | 15 m³/h |
| Desvio didático de instalação e rugosidade | Aplicar |

O **desvio didático** é um recurso de aula e não faz parte da norma. Quando a instalação foge da norma (trecho reto curto ou tubo rugoso), ele aumenta o `C` real em até 2 % para que a turma veja o erro de medição. Pode ser desligado.

**Figura 6. Detalhe da planta da placa de orifício**

![Figura 6](assets/fig06_planta.png)

> **Imagem a inserir:** captura ampliada só da planta, com a simulação rodando e a válvula em 100 %. Devem estar visíveis: a entrada pela curva de 90°, a tubulação com as setas de fluxo, a placa de orifício entre flanges (FE), a válvula de controle (FV) com o selo "100 %", as lâmpadas "Tipo de tomada" (Flange acesa) e "Conformidade com a ISO 5167-2" (todas verdes), os displays de medição (Vazão 15,00 m³/h, Reynolds 100668, C 0,6124, ΔP 3376 mmH2O) e os displays de parâmetros em amarelo. Use o botão "ajustar seleção" com a planta selecionada.

**Figura 7. Propriedades exportadas da planta**

![Figura 7](assets/fig07_propriedades_exportadas.png)

> **Imagem a inserir:** captura do painel **Properties** com a planta selecionada, rolado até "Propriedades exportadas", mostrando os campos numéricos (D, d, trechos retos, temperatura...) e as caixas de seleção (tipo de tomada aberta, mostrando Flange / D e D/2 / Canto).

### 5.3 Resultados com os valores padrão

| Válvula | Q (m³/h) | Re_D | C | ΔP (mmH2O) | ΔP (% da faixa) |
|---:|---:|---:|---:|---:|---:|
| 100 % | 15,00 | 100 668 | 0,6124 | 3376,3 | 100,0 |
| 75 % | 11,25 | 75 501 | 0,6135 | 1892,5 | 56,1 |
| 50 % | 7,50 | 50 334 | 0,6153 | 836,1 | 24,8 |
| 30 % | 4,50 | 30 200 | 0,6184 | 298,0 | 8,8 |
| 20 % | 3,00 | 20 134 | 0,6216 | 131,1 | 3,9 |

Note que, com metade da vazão, o `ΔP` não é exatamente 25 % porque o `C` aumenta quando o Reynolds diminui.

---

## 6. O transmissor LD301 na medição de vazão

O LD301 mede a diferença entre as pressões das tomadas **H** (alta) e **L** (baixa) e a converte em corrente de 4 a 20 mA. A comunicação **HART** é sobreposta à corrente e permite configurar o transmissor pelo PACTware.

### 6.1 Faixa de calibração

No LD301, os limites **inferior (LRV)** e **superior (URV)** da calibração são sempre de **pressão**. Para a placa padrão:

- LRV = 0 mmH2O (vazão zero, 4 mA);
- URV = ΔP na vazão máxima = 3376,3 mmH2O (15 m³/h, 20 mA).

A vazão **nunca** entra no LRV/URV. Ela entra pela função de transferência e pela unidade do usuário.

### 6.2 Função raiz quadrada

Com a função **linear**, a saída acompanha o `ΔP`:

$$
I = 4 + 16\cdot\frac{\Delta P - LRV}{URV - LRV}\quad[\text{mA}]
$$

Com a função **raiz quadrada (Sqrt)**, o LD301 calcula:

$$
X = \frac{\Delta P - LRV}{URV - LRV}\cdot 100\,\%
\qquad
\text{saída} = 10\sqrt{X}\;[\%]
\qquad
I = 4 + 16\cdot\frac{\text{saída}}{100}
$$

e a corrente fica proporcional à vazão.

O manual do LD301 define um **ponto de corte** (padrão 6 % da faixa de pressão). Abaixo dele:

- no modo **Abrupto (Hard)**, a saída vai a 0 %;
- no modo **Suave (Bumpless)**, a saída fica linear com o `ΔP`.

O corte evita o ganho muito alto da raiz perto de zero. Com 6 % de `ΔP`, o corte corresponde a `15·\sqrt{0,06} = 3,67` m³/h.

### 6.3 Unidade do Usuário e display

A **Unidade do Usuário (User Unit)** dá unidade e escala ao % da saída: 0 % corresponde a 0 m³/h e 100 % a 15 m³/h. O resultado é a **PV** do LD301, que o display pode mostrar com o ícone **PV**.

O display alterna até duas variáveis a cada 3 s (**First Var** e **Second Var**):

| Opção | Mostra |
|---|---|
| OUT | saída em mA |
| PV% | variável de processo em % |
| PV | variável de processo na unidade do usuário (a vazão) |
| PRES | pressão diferencial |
| TEMP | temperatura do sensor |
| None | só na 2ª variável: não alterna |

O LD301 do projeto vem com tag **FT100**, faixa 0…3376,3 mmH2O, função **linear** e display em PV% / TEMP. Configurá-lo para vazão é o objetivo da seção 10.

**Figura 8. Malha 4–20 mA do LD301 no simulador**

![Figura 8](assets/fig08_malha_4_20.png)

> **Imagem a inserir:** captura ampliada da região do LD301 no LasecSimul: o transmissor com o display, a fonte de 24 V, o resistor de 250 Ω, o amperímetro mostrando a corrente e o modem HART ligado sobre o resistor. Destaque com setas os fios HIGH (laranja) e LOW (amarelo) vindos da planta.

---

## 7. Arquivos da prática

Os arquivos desta pasta são:

- [`placa_orificio_ld301.lsproj`](placa_orificio_ld301.lsproj): projeto do LasecSimul com a planta incorporada e o LD301;
- [`placa_orificio_calculo.py`](placa_orificio_calculo.py): script para calcular a vazão com os mesmos ajustes da planta (seção 11);
- [`assets/`](assets): imagens deste roteiro.

---

## 8. Como executar

1. Instale ou atualize a extensão **LasecSimul** no VS Code (versão 0.0.83 ou mais nova).
2. Abra esta pasta no VS Code e dê dois cliques em `placa_orificio_ld301.lsproj`.
3. Clique em **Run** (▶). O selo no canto superior direito muda para "Running".
4. Selecione o slider **"Válvula de controle (%)"** e altere o **Valor do sinal** no painel Properties (ou arraste o slider).
5. Observe a vazão, o `ΔP`, a corrente no amperímetro e o display do LD301.
6. Para mudar os parâmetros da planta, selecione a planta e use **Propriedades exportadas**.

Observações importantes:

- a vazão responde à válvula com um atraso de cerca de 1 s; espere estabilizar antes de anotar;
- ao mudar `D`, `d` ou o fluido, o `ΔP` na vazão máxima muda e o **URV do LD301 precisa ser refeito**;
- as lâmpadas vermelhas indicam instalação fora da norma; com o desvio didático ligado, o `C` real muda.

---

## 9. Conexão com o PACTware

O **modem HART** do projeto está ligado sobre o resistor de 250 Ω e se comunica com o computador por uma porta serial virtual.

1. Selecione o **Modem HART** e confira em Properties: **Ligação com o PC** = Serial (COM / CNC) e **Porta serial** = `CNCB0`.
2. No **com0com**, crie (ou confira) o par de portas `CNCB0` ↔ `COM20`. O LasecSimul usa um lado; o PACTware usa o outro.
3. No PACTware, abra **Ver → Catálogo de instrumentos**, atualize o catálogo e adicione **HART Communication**.
4. Dê dois cliques no driver HART e selecione a porta **COM20**. Desmarque **Multimaster and Burst mode support**. Clique em **Apply** e **OK**.
5. Clique com o botão direito no driver → **Adicionar instrumento** → escolha o DTM do **LD301** (Smar).
6. Com a simulação rodando, clique com o botão direito no LD301 → **Conectar**. Os ícones ficam verdes e o tag **FT100** aparece.
7. Abra a **Parametrização online** do LD301.

**Figura 9. Par de portas virtuais no com0com**

![Figura 9](assets/fig09_com0com.png)

> **Imagem a inserir:** janela de configuração do com0com (*Setup for com0com*) mostrando o par com `CNCB0` de um lado e `COM20` do outro, com as opções padrão.

**Figura 10. LD301 conectado no PACTware**

![Figura 10](assets/fig10_pactware_conectado.png)

> **Imagem a inserir:** tela do PACTware com a árvore do projeto mostrando "HOST PC → HART Communication (COM20) → LD301" com os ícones verdes de conexão, e a janela do DTM aberta exibindo o tag FT100 e a variável primária em mmH2O.

---

## 10. Configuração do LD301 para vazão

Faça uma alteração por vez, aplique (**Write/Apply**) e confira o efeito no simulador antes da próxima.

### 10.1 Calibração (faixa de ΔP)

Em **Calibration**: unidade **mmH2O**, **Lower = 0**, **Upper = 3376,3** → aplicar.

**Figura 11. Tela de calibração do LD301**

![Figura 11](assets/fig11_dtm_calibration.png)

> **Imagem a inserir:** tela **Calibration** do DTM do LD301 com a unidade mmH2O, Lower Value 0 e Upper Value 3376,3 preenchidos, antes de aplicar.

Com a função ainda **linear**, a corrente acompanha o `ΔP`: válvula a 50 % → **7,96 mA**.

### 10.2 Função raiz quadrada

Em **Configuration → Function**: selecione **Sqrt**, ponto de corte **6 %** e modo **Hard** (abrupto) → aplicar.

**Figura 12. Função de transferência raiz quadrada**

![Figura 12](assets/fig12_dtm_function.png)

> **Imagem a inserir:** tela **Configuration** do DTM com a função de transferência **Sqrt** selecionada, o campo do ponto de corte com 6 % e a opção de modo do corte (Hard/Bumpless) visível.

Agora a corrente acompanha a vazão: válvula a 50 % → **11,96 mA**.

### 10.3 Unidade do Usuário

Em **User Unit**: **On**, unidade **m3/h**, **0 % = 0** e **100 % = 15** → aplicar.

**Figura 13. Unidade do Usuário em m³/h**

![Figura 13](assets/fig13_dtm_user_unit.png)

> **Imagem a inserir:** tela **User Unit** do DTM com a opção habilitada (On), a unidade m3/h selecionada na lista de vazão volumétrica e os valores 0 (0 %) e 15 (100 %).

### 10.4 Display

Em **Display (LCD Indicator)**: **First Var = PV** e **Second Var = OUT** (ou **None** para mostrar só a vazão) → aplicar.

**Figura 14. Configuração do display**

![Figura 14](assets/fig14_dtm_display.png)

> **Imagem a inserir:** tela de configuração do display do DTM com First Var = PV e Second Var = OUT.

**Figura 15. Display do LD301 indicando vazão**

![Figura 15](assets/fig15_lcd_vazao.png)

> **Imagem a inserir:** duas capturas ampliadas do display do LD301 no simulador, com a válvula em 100 %: uma com "15.00 m3/h" e o ícone PV aceso, e outra, 3 s depois, com "20.00 mA". Monte as duas lado a lado.

### 10.5 Conferência

Com a raiz, corte de 6 % (Hard) e Unidade do Usuário de 0 a 15 m³/h:

| Válvula | Vazão real (planta) | ΔP (% da faixa) | Corrente linear | Corrente com raiz | LCD (PV) |
|---:|---:|---:|---:|---:|---:|
| 100 % | 15,00 | 100,0 | 20,00 mA | 20,00 mA | 15,00 m3/h |
| 75 % | 11,25 | 56,1 | 12,97 mA | 15,98 mA | 11,23 m3/h |
| 50 % | 7,50 | 24,8 | 7,96 mA | 11,96 mA | 7,464 m3/h |
| 30 % | 4,50 | 8,8 | 5,41 mA | 8,75 mA | 4,457 m3/h |
| 20 % | 3,00 | 3,9 | 4,62 mA | 4,00 mA | 0,000 m3/h |

A 20 % de válvula o `ΔP` (3,9 %) fica abaixo do corte de 6 %, e a indicação vai a zero. No modo Bumpless, a mesma válvula daria 6,54 mA.

**Figura 16. Corrente em função da vazão: linear e raiz quadrada**

![Figura 16](assets/fig16_grafico_corrente_vazao.png)

> **Imagem a inserir:** gráfico com a vazão (0 a 15 m³/h) no eixo horizontal e a corrente (4 a 20 mA) no vertical, com duas curvas feitas com os valores medidos na tabela acima: a função linear (parábola, abaixo da reta) e a função raiz quadrada (praticamente uma reta). Marque a região abaixo do corte de 6 % (até 3,67 m³/h).

---

## 11. Ferramenta de apoio em Python

O script [`placa_orificio_calculo.py`](placa_orificio_calculo.py) usa as **mesmas equações** da planta. Ele serve para o aluno fazer as contas e depois conferir com a simulação. Só usa a biblioteca padrão do Python.

Copie para o bloco `CONFIGURACAO`, no início do arquivo, os valores de **Propriedades exportadas** e informe o que foi medido:

```text
python placa_orificio_calculo.py --dp 836.1                ΔP lido no LD301/PACTware (mmH2O)
python placa_orificio_calculo.py --corrente 7.96           corrente do laço, LD301 linear
python placa_orificio_calculo.py --corrente 11.96 --raiz   corrente do laço, LD301 com raiz
python placa_orificio_calculo.py --valvula 50              abertura -> vazão -> ΔP
python placa_orificio_calculo.py                           pergunta o que foi medido
```

Os ajustes também podem ir na linha de comando, por exemplo `--tomada 2 --L_montante 10 --T 80`.

A partir do `ΔP`, o script resolve a vazão por **iteração**, porque `C` depende de `Re_D`, que depende de `Q`, e mostra cada passo:

```text
Iteração (C depende de Re, que depende de Q):
   k      C (ISO)      C real     Q [m³/h]        Re_D
   1     0.600000    0.600000     7.313091       49079
   2     0.615471    0.615471     7.501660       50345
   3     0.615341    0.615341     7.500069       50334
   4     0.615342    0.615342     7.500082       50334
```

Com o chute inicial `C = 0,6`, a vazão converge em três ou quatro passos.

No final, ele imprime os mesmos valores dos displays da planta: geometria na temperatura, trechos exigidos, desvio, conformidade, `C`, `ε`, `ΔP` e perda permanente. Com `--autoteste`, o script se confere com os valores de referência da norma.

**Figura 17. Saída do script de cálculo**

![Figura 17](assets/fig17_script_python.png)

> **Imagem a inserir:** captura do terminal do VS Code com a execução de `python placa_orificio_calculo.py --dp 836.1`, mostrando a tabela de iterações e o relatório final com a vazão de 7,50 m³/h.

---

## 12. Sugestão de atividade experimental

### Parte A: linear × raiz quadrada

1. Configure o LD301 com a faixa de 0 a 3376,3 mmH2O e função **linear**.
2. Para as aberturas de válvula de 100, 75, 50, 30 e 20 %, aguarde estabilizar e registre a vazão real (display da planta), o `ΔP` (PACTware) e a corrente (amperímetro).
3. Mude a função para **raiz quadrada** e repita.
4. Configure a **Unidade do Usuário** e o **display** e registre a vazão indicada no LD301.
5. Calcule o erro entre a vazão indicada e a vazão real.

| Válvula | Q real (m³/h) | ΔP (mmH2O) | I linear (mA) | I raiz (mA) | Q indicada (m³/h) | Erro (%) |
|---:|---:|---:|---:|---:|---:|---:|
| 100 % | | | | | | |
| 75 % | | | | | | |
| 50 % | | | | | | |
| 30 % | | | | | | |
| 20 % | | | | | | |

### Parte B: coeficiente de descarga e número de Reynolds

1. Para cada abertura da Parte A, anote `Re_D` e `C (ISO 5167-2)` nos displays da planta.
2. Faça um gráfico de `C` em função de `Re_D`.
3. Explique por que a vazão indicada pelo LD301 a 50 % (7,46 m³/h) difere da real (7,50 m³/h).

### Parte C: tipo de tomada

Com a válvula em 100 %, troque o tipo de tomada e registre:

| Tomada | C | ΔP (mmH2O) | Q calculada pelo script (m³/h) |
|---|---:|---:|---:|
| Flange | | | |
| D e D/2 | | | |
| Canto | | | |

### Parte D: trechos retos

1. Com a válvula em 100 %, reduza o trecho reto a montante para 30, 20, 13, 10 e 5 D.
2. Registre o estado da lâmpada "Montante", o desvio didático, o `C` real, o `ΔP` e a vazão indicada pelo LD301.
3. A partir de qual comprimento a medição sai da norma? Qual o erro de vazão com 5 D?

### Parte E: material e temperatura

1. Troque o material da tubulação para ferro fundido e depois para aço galvanizado. Registre `10^4·Ra/D`, a lâmpada "Rugosidade" e o `ΔP`.
2. Volte para aço carbono e aumente a temperatura para 80 °C. Registre `D`, `d` e `ΔP` e explique a variação.

### Questões para o relatório

1. Por que o LRV/URV do LD301 é configurado em pressão e não em vazão?
2. Qual seria a corrente a 10 % de vazão com a função linear? E com a raiz? Discuta a rangeabilidade.
3. Para que serve o ponto de corte da raiz? Compare os modos Hard e Bumpless.
4. Se o fluido mudar de água para óleo (ρ = 870 kg/m³, μ = 30 cP), o que precisa ser reconfigurado no LD301?

Essa atividade conecta a norma, o comportamento físico do elemento primário e a configuração real de um transmissor HART.

---

## 13. Conclusão

A prática mostra, de forma aplicada, a cadeia completa de uma medição de vazão por pressão diferencial:

- a vazão acelera o fluido no orifício e cria uma queda de pressão;
- a norma ISO 5167-2 relaciona essa queda à vazão pelo coeficiente `C`;
- o LD301 mede a pressão diferencial entre as tomadas de alta e de baixa;
- a função raiz quadrada torna a corrente proporcional à vazão;
- a Unidade do Usuário e o display apresentam a vazão em engenharia;
- a instalação (tomadas, trechos retos, rugosidade) define se a medição é confiável.

Com isso, o roteiro serve tanto como material de estudo quanto como apoio para a aula prática de instrumentação.

---

## 14. Referências

- Apostila de Instrumentação Industrial II - UFU
- ISO 5167-1 e ISO 5167-2. *Measurement of fluid flow by means of pressure differential devices inserted in circular cross-section conduits running full — Part 1: General principles; Part 2: Orifice plates.*
- Reader-Harris, M. J.; Sattary, J. A. *The orifice plate discharge coefficient equation.* Flow Measurement and Instrumentation, 1990.
- Smar. *LD301 — Manual de Instruções, Operação e Manutenção* (seção 3: Função de Transferência, User Unit e LCD Indicator).
- Delmée, G. J. *Manual de Medição de Vazão.* Editora Blucher.
- Bell, C. *fluids: Fluid dynamics component of Chemical Engineering Design Library (ChEDL)* — biblioteca de referência usada para validar o simulador.
- [LasecSimul — LASEC/UFU](https://github.com/LASEC-UFU/LasecSimul)

---

## 15. Apêndice: lista de imagens

Todas as imagens ficam na pasta [`assets/`](assets), com os nomes exatos da tabela. Cada figura do texto já traz, no quadro "Imagem a inserir", o que ela precisa mostrar. Este apêndice reúne como produzir cada uma.

### 15.1 Como produzir as imagens

- **Capturas do LasecSimul:** VS Code maximizado (1920 × 1080), barra lateral fechada (`Ctrl+B`) e escala do Windows em 100 %. Rode a simulação e espere os valores estabilizarem antes de capturar. Use **Ajustar tudo** ou **Ajustar seleção** na barra do esquemático e a Ferramenta de Captura (`Win+Shift+S`), recortando só a área de interesse. Salve em PNG.
- **Capturas do PACTware:** janela maximizada, LD301 conectado (ícones verdes). Recorte a árvore do projeto e a área do DTM. Se uma tela for longa, capture só a parte com os campos citados no texto.
- **Fotos:** luz difusa, sem flash direto no display (evita reflexo), câmera paralela ao objeto. Salve em JPG.
- **Desenhos:** diagrams.net (draw.io), Inkscape ou PowerPoint, fundo branco, exportados em PNG com cerca de 1600 px de largura.
- **Anotações:** setas e números em vermelho, fonte sem serifa. Explique cada número na legenda ou no parágrafo da figura.
- **Cores das tomadas:** use as mesmas do LasecSimul em todos os desenhos: **alta (H) em laranja** e **baixa (L) em amarelo**.

### 15.2 Figuras

| Figura | Arquivo | Tipo | Como obter | O que destacar |
|---:|---|---|---|---|
| 1 | `fig01_placa_orificio.jpg` | Foto | Fotografe a placa do laboratório sobre fundo neutro em duas vistas: a face de montante e o perfil. Pode reaproveitar `placa01.jpg` a `placa03.jpg` da pasta antiga da prática. | Aresta viva (montante), chanfro a 45° (jusante) e haste com a gravação do diâmetro `d`, do material e do tag FE. |
| 2 | `fig02_perfil_pressao.png` | Desenho | Corte da tubulação com a placa e as linhas de corrente se contraindo. Embaixo, um gráfico da pressão ao longo do eixo: patamar `P_1`, queda até a vena contracta (cerca de 0,5 D depois da placa) e recuperação parcial até cerca de 6 D. | Cotas de `ΔP` (entre as tomadas) e de `Δω` (entre `P_1` e a pressão recuperada); posição da vena contracta. |
| 3 | `fig03_tipos_tomada.png` | Desenho | Corte da placa entre flanges com as três tomadas em cores diferentes: canto (rente à placa), flange (25,4 mm de cada face) e D e D/2 (na tubulação). | Cotas de 25,4 mm, `D` e `D/2`; sinais + e − de cada tomada. |
| 4 | `fig04_trechos_retos.png` | Desenho | Linha com a curva de 90°, o trecho reto a montante, a placa, o trecho a jusante e a válvula de controle, com as tomadas descendo até o LD301. | Cotas `L montante = n·D` e `L jusante = n·D`; setas de escoamento. |
| 5 | `fig05_projeto_completo.png` | Captura LasecSimul | Abra `placa_orificio_ld301.lsproj`, clique em **Run**, ponha a válvula em 50 %, espere 3 s e clique em **Ajustar tudo**. Capture o esquemático inteiro com o selo "Running". | Números de 1 a 8: slider, planta, LD301, fonte, resistor, amperímetro, modem HART e osciloscópio. |
| 6 | `fig06_planta.png` | Captura LasecSimul | Válvula em 100 %, espere 3 s. Selecione a planta, clique em **Ajustar seleção** e recolha o painel Properties (seta `›`). Capture só a planta. | Lâmpada Flange acesa, lâmpadas de conformidade verdes, displays de Vazão 15,00 m³/h, Reynolds, C e ΔP 3376 mmH2O. |
| 7 | `fig07_propriedades_exportadas.png` | Captura LasecSimul | Selecione a planta, abra o painel **Properties**, role até "Propriedades exportadas" e clique na caixa "Tipo de tomada" para abrir a lista antes de capturar. | A lista aberta (Flange, D e D/2, Canto) e os campos numéricos de D, d e trechos retos. |
| 8 | `fig08_malha_4_20.png` | Captura LasecSimul | Com a válvula em 100 %, aproxime a região do LD301 com `Ctrl` + roda do mouse e capture. | Fios HIGH (laranja) e LOW (amarelo), fonte de 24 V, resistor de 250 Ω, amperímetro com 20,00 mA e modem HART. |
| 9 | `fig09_com0com.png` | Captura Windows | Menu Iniciar → **com0com** → **Setup**. Capture a janela com o par de portas. | Os nomes `CNCB0` e `COM20` do mesmo par. |
| 10 | `fig10_pactware_conectado.png` | Captura PACTware | Com a simulação rodando, conecte o LD301 e abra a Parametrização online. Capture a janela inteira. | Ícones verdes na árvore, tag FT100 e PV em mmH2O. |
| 11 | `fig11_dtm_calibration.png` | Captura PACTware | Tela **Calibration** com os valores digitados, antes de aplicar. | Unidade mmH2O, Lower 0 e Upper 3376,3. |
| 12 | `fig12_dtm_function.png` | Captura PACTware | Tela **Configuration → Function** com a raiz selecionada. | Sqrt, ponto de corte 6 % e modo Hard. |
| 13 | `fig13_dtm_user_unit.png` | Captura PACTware | Tela **User Unit** com a lista de unidades aberta em m3/h. | On, m3/h, 0 (0 %) e 15 (100 %). |
| 14 | `fig14_dtm_display.png` | Captura PACTware | Tela de configuração do display. | First Var = PV e Second Var = OUT. |
| 15 | `fig15_lcd_vazao.png` | Captura LasecSimul (montagem) | Válvula em 100 %. Aproxime o display do LD301 (zoom de cerca de 300 %) e capture duas vezes com 3 s de intervalo, uma em cada página. Monte as duas lado a lado. | "15.00 m3/h" com o ícone PV aceso e "20.00 mA". |
| 16 | `fig16_grafico_corrente_vazao.png` | Gráfico | Planilha ou Python com os valores medidos na tabela da seção 10.5: vazão no eixo x e corrente no eixo y, uma série linear e uma com raiz. | Região sombreada abaixo do corte (até 3,67 m³/h); legenda das duas funções. |
| 17 | `fig17_script_python.png` | Captura terminal | No terminal do VS Code, nesta pasta, rode `python placa_orificio_calculo.py --dp 836.1` e capture a saída. | A tabela de iterações e a linha "Vazão 7.50 m³/h" do relatório. |
