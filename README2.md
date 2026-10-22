
# EININDII - Cálculo de placa de Orifício

## Sumário

- [1. Derivação da Equação de Velocidade a partir da Equação de Bernoulli](#1-derivação-da-equação-de-velocidade-a-partir-da-equação-de-bernoulli)
- [2. Equação para Vazão Real com Correções](#2-equação-para-vazão-real-com-correções)
- [3. Método Iterativo para Dimensionamento de Placa de Orifício](#3-método-iterativo-para-dimensionamento-de-placa-de-orifício)
- [4. Valores Genéricos Típicos para Referência](#4-valores-genéricos-típicos-para-referência)
- [5. Exemplo Prático](#5-exemplo-prático)
- [6. Dados das Placas de Orifício](#6-dados-das-placas-de-orifício)
- [7. Conclusão](#7-conclusão)

---

## 1. Derivação da Equação de Velocidade a partir da Equação de Bernoulli

Para obter a relação:

$$
V = \sqrt{\frac{2\Delta P}{\rho}}
$$

Partimos da equação de Bernoulli para um escoamento incompressível, estacionário e sem atrito. Em sua forma geral, para dois pontos (1 e 2) ao longo de uma linha de corrente, a equação de Bernoulli é dada por

$$
\frac{P_1}{\rho g} + \frac{V_1^2}{2g} + z_1 = \frac{P_2}{\rho g} + \frac{V_2^2}{2g} + z_2,
$$

onde:
>>> - $P$ é a pressão;
>>> - $\rho$ é a densidade do fluido;
>>> - $V$ é a velocidade do escoamento;
>>> - $g$ é a aceleração da gravidade;
>>> - $z$ é a elevação.

### Simplificações e Assunções

1. **Fluxo Horizontal:**  
   Se o tubo é horizontal, então $z_1 = z_2$. Isso elimina os termos de energia potencial:

$$
\frac{P_1}{\rho g} + \frac{V_1^2}{2g} = \frac{P_2}{\rho g} + \frac{V_2^2}{2g}.
$$

2. **Velocidade Inicial Desprezível:**  
   Escolhe-se o ponto 1 em uma seção ampla antes da placa, onde o fluido tem velocidade muito baixa em comparação com a velocidade na seção restrita (vena contracta). Assim, assumimos:

$$
V_1 \approx 0.
$$

   Aqui, $V_1$ é a velocidade real do fluido no ponto 1, não uma variação. A aproximação $V_1 \approx 0$ significa apenas que, nesse modelo ideal simplificado, a velocidade antes da restrição é considerada muito pequena quando comparada com $V_2$. Portanto, o termo cinético $\frac{V_1^2}{2g}$ é desprezado. Em uma tubulação real, porém, o fluido já possui velocidade antes da placa; esse efeito aparece depois na equação prática por meio do termo $(1-\beta^4)$.

3. **Ausência de Perdas Dissipativas:**  
   Nesta análise ideal, não consideramos perdas por atrito ou turbulência; estas serão incorporadas posteriormente via coeficiente de descarga.

### Derivação

Com as simplificações, a equação de Bernoulli entre o ponto 1 (antes da restrição) e o ponto 2 (na vena contracta) torna-se:

$$
\frac{P_1}{\rho g} = \frac{P_2}{\rho g} + \frac{V_2^2}{2g}.
$$

Multiplicando ambos os lados por $g$:

$$
\frac{P_1}{\rho} = \frac{P_2}{\rho} + \frac{V_2^2}{2}.
$$

Reorganizando:

$$
\frac{P_1 - P_2}{\rho} = \frac{V_2^2}{2}.
$$

Definindo a queda de pressão $\Delta P = P_1 - P_2$, temos:

$$
\frac{\Delta P}{\rho} = \frac{V_2^2}{2}.
$$

Multiplicando por 2 e isolando $V_2$:

$$
V_2 = \sqrt{\frac{2\Delta P}{\rho}}.
$$

Portanto, sob as condições:
- Fluxo horizontal: $z_1 = z_2$
- Velocidade inicial desprezível: $V_1 \approx 0$
- Sem perdas dissipativas

obtém-se a equação fundamental:

$$
V = \sqrt{\frac{2\Delta P}{\rho}}.
$$

---

## 2. Equação para Vazão Real com Correções

Na prática, o escoamento através de uma placa de orifício sofre efeitos de contração do jato (vena contracta) e outras perdas, o que faz com que a área efetiva de escoamento seja menor que a área física do orifício. Para levar isso em conta, aplicamos os seguintes ajustes:

1. **Área do Orifício:**  
   Se o diâmetro do orifício é $d$, a área física é

$$
A = \frac{\pi d^2}{4}.
$$

   Como o orifício é parte de uma tubulação com diâmetro $D$, define-se a razão

$$
\beta = \frac{d}{D}.
$$

   Logo:

$$
d = \beta D
$$

   e a área do orifício também pode ser escrita como:

$$
A = \frac{\pi (\beta D)^2}{4} = \frac{\pi \beta^2 D^2}{4}.
$$

2. **Correção pela Contração do Jato:**  
   Estudos experimentais indicam que a vazão teórica deve ser corrigida por fatores que dependem de $\beta$ e da geometria real do escoamento. O termo $(1-\beta^4)$, especificamente, vem do fato de que, em uma tubulação real, a velocidade antes da placa não é exatamente zero.

   Para mostrar de onde vem o termo $(1-\beta^4)$, considere Bernoulli sem diferença de altura e sem perdas:

$$
\frac{P_1}{\rho} + \frac{V_1^2}{2} = \frac{P_2}{\rho} + \frac{V_2^2}{2}.
$$

   Reorganizando:

$$
\Delta P = P_1 - P_2 = \frac{\rho}{2}(V_2^2 - V_1^2).
$$

   Pela continuidade, a vazão é a mesma antes da placa e no orifício:

$$
Q = A_1 V_1 = A_2 V_2.
$$

   Portanto:

$$
V_1 = \frac{Q}{A_1}
\quad\text{e}\quad
V_2 = \frac{Q}{A_2}.
$$

   Substituindo em Bernoulli:

$$
\Delta P = \frac{\rho}{2}Q^2\left(\frac{1}{A_2^2} - \frac{1}{A_1^2}\right).
$$

   Como:

$$
A_1 = \frac{\pi D^2}{4}
\quad\text{e}\quad
A_2 = \frac{\pi d^2}{4} = \beta^2 A_1,
$$

   então:

$$
\frac{A_2}{A_1} = \beta^2
\quad\Rightarrow\quad
\left(\frac{A_2}{A_1}\right)^2 = \beta^4.
$$

   Também pela continuidade:

$$
A_1V_1 = A_2V_2
\quad\Rightarrow\quad
V_1 = \frac{A_2}{A_1}V_2 = \beta^2V_2.
$$

   Substituindo isso em Bernoulli:

$$
\Delta P = \frac{\rho}{2}(V_2^2 - V_1^2)
         = \frac{\rho}{2}(V_2^2 - \beta^4V_2^2)
         = \frac{\rho}{2}V_2^2(1-\beta^4).
$$

   Isolando a velocidade no orifício, chega-se a:

$$
V_2 = \sqrt{\frac{2\Delta P}{\rho(1-\beta^4)}}.
$$

   Assim, o termo $(1-\beta^4)$ não significa uma perda por atrito. Ele aparece porque a velocidade a montante $V_1$ não foi desprezada. Quando se assume $V_1 \approx 0$, obtém-se a forma mais simples $V = \sqrt{\frac{2\Delta P}{\rho}}$; quando se usa a continuidade entre a tubulação e o orifício, aparece o fator $(1-\beta^4)$.

3. **Coeficiente de Descarga e Fator de Expansibilidade:**  
   Para compensar as perdas reais (devido à turbulência, efeitos de instalação, etc.), introduz-se o coeficiente de descarga $C_d$ (ou base $C$). Para fluidos compressíveis, aplica-se também o fator de expansibilidade $\varepsilon$ (que é 1 para líquidos e menor que 1 para gases).

Portanto, a vazão volumétrica real é dada por:

$$
Q = C \cdot \varepsilon \cdot A \cdot \sqrt{\frac{2\Delta P}{\rho (1-\beta^4)}}.
$$

Quando outros fatores de correção são considerados (como o tipo de tomadas, condições de instalação, material da tubulação e tipo de orifício), define-se:

$$
C_{\text{eff}} = C \cdot K_{\text{tap}} \cdot K_{\text{inst}} \cdot K_{\text{material}} \cdot K_{\text{orifice}}.
$$

Substituindo, obtemos a equação final:

$$
Q = C_{\text{eff}} \cdot \varepsilon \cdot A \cdot \sqrt{\frac{2\Delta P}{\rho (1-\beta^4)}}.
$$

---

## 3. Método Iterativo para Dimensionamento de Placa de Orifício

O objetivo prático é encontrar o diâmetro do orifício $d$ (ou a razão $\beta$) que atenda à vazão volumétrica desejada $Q_{\text{desired}}$. Para isso, definimos a função:

$$
f(\beta) = C_{\text{eff}} \cdot \varepsilon \cdot \frac{\pi (\beta D)^2}{4} \cdot \sqrt{\frac{2\Delta P}{\rho (1-\beta^4)}} - Q_{\text{desired}} = 0.
$$

Encontrar a raiz de $f(\beta)$ equivale a determinar o valor de $\beta$ que satisfaça a condição de vazão.

### Método da Bissecção

O método da bissecção é aplicado da seguinte forma:

>>> 1. **Definição do Intervalo:**  
Escolhe-se um intervalo $[\beta_{\text{min}}, \beta_{\text{max}}]$ onde a função $f(\beta)$ muda de sinal. Para placas de orifício, normalmente utiliza-se um intervalo de 0.25 a 0.72.

>>> 2. **Cálculo do Ponto Médio:**  
Calcula-se o ponto médio:

$$
\beta_{\text{mid}} = \frac{\beta_{\text{min}} + \beta_{\text{max}}}{2},
$$

e avalia-se $f(\beta_{\text{mid}})$.

>>> 3. **Critério de Parada:**  
Se $|f(\beta_{\text{mid}})|$ for menor que uma tolerância (por exemplo, $10^{-6}$), $\beta_{\text{mid}}$ é aceita como solução.

>>> 4. **Atualização do Intervalo:**  
Se $f(\beta_{\text{min}})$ e $f(\beta_{\text{mid}})$ tiverem sinais opostos, a raiz está entre $\beta_{\text{min}}$ e $\beta_{\text{mid}}$; caso contrário, está entre $\beta_{\text{mid}}$ e $\beta_{\text{max}}$.

>>> 5. **Iteração:**  
Repete-se o procedimento com o novo intervalo até atingir a precisão desejada.

Após determinar $\beta$, o diâmetro do orifício é calculado por:

$$
d = \beta \cdot D.
$$

---

## 4. Valores Genéricos Típicos para Referência

Para facilitar a aplicação prática, seguem valores típicos usados no dimensionamento de placas de orifício:

>>> - **Vazão Volumétrica Desejada ($Q_{\text{desired}}$):**  
>>>> - Gases: 0.01 a 0.1 Nm³/s  
>>>> - Líquidos: 0.001 a 0.1 m³/s  
>>>> - Vapores: 0.01 a 1.0 Nm³/s
>>>
>>> - **Diâmetro Interno da Tubulação ($D$):**  
>>>> - Pequenas tubulações: 0.025 a 0.15 m (1″ a 6″)  
>>>> - Médias: 0.15 a 0.6 m (6″ a 24″)
>>>
>>> - **Queda de Pressão ($\Delta P$):**  
>>>> - Geralmente entre 25 kPa e 100 kPa (0.25 a 1.0 bar)
>>>
>>> - **Densidade do Fluido ($\rho$):**  
>>>> - Gases: aproximadamente 1.0 a 1.2 kg/m³ (ar)  
>>>> - Líquidos: aproximadamente 1000 kg/m³ (água)  
>>>> - Vapores: cerca de 0.6 kg/m³ em condições de saturação
>>>
>>> - **Coeficiente de Descarga Base ($C$):**  
>>>> - Aproximadamente 0.61 para placas de orifício padrão
>>>
>>> - **Fator de Expansibilidade ($\varepsilon$):**  
>>>> - Líquidos: 1.0  
>>>> - Gases/Vapores: geralmente entre 0.90 e 0.98
>>>
>>> - **Distâncias a Montante e Jusante ($L_{\text{upstream}}$ e $L_{\text{downstream}}$):**  
>>>> - Recomenda-se pelo menos 10 diâmetros ($10D$) a montante e 5 diâmetros ($5D$) a jusante

---

## 5. Exemplo Prático

Considere os seguintes parâmetros para uma aplicação com líquido:
>>> - $Q_{\text{desired}} = 0.02\, \text{m}^3/\text{s}$
>>> - $D = 0.15\, \text{m}$
>>> - $\Delta P = 50\,000\, \text{Pa}$
>>> - $\rho = 1000\, \text{kg/m}^3$
>>> - $C = 0.61$
>>> - $\varepsilon = 1.0$
>>> - $L_{\text{upstream}} = 1.5\, \text{m}$ (aproximadamente $10D$)
>>> - $L_{\text{downstream}} = 0.75\, \text{m}$ (aproximadamente $5D$)
>>> - Tipo de tomadas: "flange"
>>> - Material: "steel"
>>> - Tipo de orifício: "concentrico"

A função a ser resolvida é:

$$
C_{\text{eff}} \cdot \varepsilon \cdot \frac{\pi (\beta D)^2}{4} \cdot \sqrt{\frac{2\Delta P}{\rho (1-\beta^4)}} - 0.02 = 0.
$$

Suponha que, após iterações via bissecção, encontre-se $\beta \approx 0.4271$. Assim, o diâmetro do orifício é:

$$
d = \beta \cdot D \approx 0.4271 \times 0.15\,\text{m} \approx 0.0641\,\text{m},
$$

ou seja, aproximadamente 64,1 mm.

---

## 6. Dados das Placas de Orifício

Os dados abaixo foram obtidos por leitura visual das plaquetas presentes nas imagens da pasta `imagens`. A imagem `placa01.jpg` possui reflexo sobre a tag; com ampliação, os números `20.93`, `0.7488` e `15.673` ficam legíveis, mas a tag não. A identificação `FE-01-AR` dessa placa foi informada pelo professor. **Correção de 22/10/2026:** a leitura anterior (`β ≈ 0,425`, `d ≈ 8,89 mm`) não corresponde à plaqueta e foi substituída.

Na plaqueta aparecem duas informações diferentes relacionadas ao diâmetro:

- **Bitola nominal da linha:** valor comercial da tubulação, como `1/2"` ou `3/4"`. Esse valor identifica a linha, mas não é necessariamente igual ao diâmetro interno real.
- **$D$ interno:** diâmetro interno usado no cálculo da placa de orifício. Esse valor já considera o espaço interno disponível para o escoamento, ou seja, é o diâmetro depois de descontada a espessura da parede da tubulação.

Se estivéssemos falando de uma medida direta em polegadas, `1/2"` seria:

$$
0.5 \times 25.4 = 12.7\,\text{mm}
$$

Mas em tubulação industrial, `1/2"` normalmente significa **NPS 1/2** ou **DN15**, que é uma bitola nominal/histórica, não uma medida direta do diâmetro interno. Uma tubulação NPS 1/2 tem diâmetro externo padronizado de aproximadamente `21.3 mm`; o diâmetro interno depende da espessura da parede. Para uma parede típica como Schedule 40, o diâmetro interno fica próximo de `15.8 mm`, que equivale a `0.622"` em polegada decimal.

Portanto, não há contradição: `12.7 mm` é a conversão direta de meia polegada, enquanto `15.8 mm` é o diâmetro interno real de uma tubulação nominal NPS 1/2 usada para o cálculo de vazão.

| Imagem | Tag / FE | Bitola nominal / Classe | $D$ interno (mm) | $D$ interno (pol decimal) | $\beta = d/D$ | $d$ do orifício | Material | Confiança |
|---|---:|---:|---:|---:|---:|---:|---|---|
| `placa01.jpg` | `FE-01-AR` (informada; tag ilegível na foto) | `3/4" - 150 LBS` | `20.93 mm` | `0.824"` | `0.7488` | `15.673 mm` | `AISI 316` | números legíveis com ampliação |
| `placa02.jpg` | `FE-09-AR` | `1/2" - 150 LBS` | `15.8 mm` | `0.622"` | `0.1154` | `1.824 mm` | `AISI 316` | alta |
| `placa03.jpg` | `FE-02-AR` | `1/2" - 150 LBS` | `15.8 mm` | `0.622"` | `0.395` | `6.255 mm` | `AISI 316` | alta |

A área do orifício foi calculada por:

$$
A = \frac{\pi d^2}{4}
$$

| Imagem | $d$ | Área do orifício |
|---|---:|---:|
| `placa01.jpg` | `15.673 mm` | `~192.93 mm²` |
| `placa02.jpg` | `1.824 mm` | `~2.61 mm²` |
| `placa03.jpg` | `6.255 mm` | `~30.73 mm²` |

### placa01.jpg

<img src="imagens/placa01.jpg" alt="Placa de orifício 01" width="420">

### placa02.jpg

<img src="imagens/placa02.jpg" alt="Placa de orifício 02" width="420">

### placa03.jpg

<img src="imagens/placa03.jpg" alt="Placa de orifício 03" width="420">

---

## 7. Conclusão

A abordagem apresentada combina a fundamentação teórica da equação de Bernoulli – com as simplificações necessárias para um fluxo horizontal e sem perdas – com a aplicação prática de fatores de correção empíricos. O método iterativo, utilizando a bissecção, permite encontrar o valor de $\beta$ que satisfaça a vazão desejada e, consequentemente, determinar o diâmetro do orifício. Esta metodologia é amplamente utilizada em aplicações industriais, onde a precisão da medição de vazão é crítica e as condições reais de operação (como o tipo de tomadas, instalação, material e geometria do orifício) devem ser levadas em conta para obter resultados confiáveis.
