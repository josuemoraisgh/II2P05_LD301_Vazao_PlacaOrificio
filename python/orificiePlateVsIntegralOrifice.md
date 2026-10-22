## Introdução

Este documento visa descrever as principais diferenças entre o código original para cálculo de diâmetro de orifício e a versão adaptada para orifícios integrais. Além disso, ele apresenta um guia detalhado sobre como utilizar o código para calcular o diâmetro necessário para atingir uma vazão volumétrica desejada em sistemas de orifícios integrais.

## Principais Diferenças entre o Código Original e o Código para Orifício Integral

### Coeficiente de Descarga ($C$)

- **Orifício Convencional**: No caso de orifícios convencionais, o coeficiente de descarga ($C$) é tipicamente definido como $0.61$. Este valor é amplamente utilizado em sistemas de medição de vazão onde a precisão é crucial, mas a instalação pode variar.
  
- **Orifício Integral**: Para orifícios integrais, o coeficiente de descarga é ajustado para um valor ligeiramente maior, geralmente entre $0.62$ e $0.64$. Isso ocorre devido ao design otimizado das tomadas de pressão, que são integradas ao bloco do orifício, proporcionando uma melhor eficiência e menor perda de carga.

### Correção de Instalação e Tomadas

- **Orifício Integral**: Os orifícios integrais possuem um design otimizado que minimiza a necessidade de fatores de correção para instalação ($K_{\text{inst}}$). Como resultado, esses fatores tendem a ser próximos de $1.00$, o que significa que a instalação é menos crítica e menos propensa a erros. Em contraste, orifícios convencionais podem ter fatores de correção mais variáveis, dependendo da montagem e do posicionamento das tomadas de pressão.
  
- **Tomadas de Pressão**: As tomadas de pressão em orifícios integrais são parte integrante do próprio bloco, o que reduz significativamente as incertezas associadas à montagem e ao alinhamento das tomadas. Isso resulta em medições mais precisas e confiáveis.

### Removido o Tipo de Orifício

- **Orifício Integral**: Em orifícios integrais, o formato do orifício é sempre concêntrico e projetado como parte do conjunto. Como resultado, não há necessidade de correções para diferentes tipos de orifícios, simplificando o processo de cálculo e reduzindo a complexidade do sistema.

## Cálculo de Diâmetro de Orifício para Orifício Integral

Este documento descreve um código para calcular o diâmetro de um orifício em uma placa de orifício ou em um orifício integral, considerando o método convencional. Os principais ajustes incluem um coeficiente de descarga e fatores de correção específicos para orifícios integrais quando esta opção é escolhida.

## Código Adaptado para Orifício Integral

```python
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

```

## Diferenças entre Orifício Convencional e Integral

| Característica          | Orifício Convencional      | Orifício Integral |
|------------------------|--------------------------|-------------------|
| **Tomada de Pressão**  | Flange, parede ou canto  | Integrada no bloco |
| **Coeficiente de Descarga ($C$)** | 0.61 | 0.62 - 0.64 |
| **Facilidade de Instalação** | Requer montagem precisa | Compacto e mais fácil |
| **Fatores de Correção** | Variam com a instalação | Menos sensível |
| **Precisão** | Depende do posicionamento das tomadas | Menor variação |

## Conclusão

Este código permite calcular o diâmetro de um orifício em um orifício integral ou em uma placa de orifício. Para um sistema de orifício integral, ele otimiza os fatores de correção e o coeficiente de descarga, adequando-se para medições de vazão onde a instalação compacta e a menor variação de coeficientes de correção são desejáveis.

## Contribuições

Se você quiser contribuir com melhorias ou novas funcionalidades, sinta-se à vontade para abrir um pull request!

---

### Exemplo de Uso

Para usar o código acima, basta chamar a função `calculate_orifice_diameter()` com os parâmetros desejados. Por exemplo:

