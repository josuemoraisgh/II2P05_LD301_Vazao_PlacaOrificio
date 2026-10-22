# Guia de Configuração do Transmissor SMAR LD301D2 no PACTware (Protocolo HART)

Este documento fornece um guia passo a passo para configurar o transmissor SMAR LD301D2 usando o software PACTware via protocolo HART, de forma que o dispositivo exiba a vazão em Nm³/h no display e transmita essa vazão na saída analógica (4–20 mA).

---

## Sumário

- [1. Configuração do Display](#1-configuração-do-display)
- [2. Configuração da Saída Analógica](#2-configuração-da-saída-analógica)
- [3. Ajustes de Compensação](#3-ajustes-de-compensação)
- [4. Verificação e Validação dos Dados](#4-verificação-e-validação-dos-dados)
- [5. Considerações Finais](#5-considerações-finais)

---

## 1. Configuração do Display

1. **Conexão e Identificação:**  
   - Conecte o transmissor SMAR LD301D2 ao PACTware via modem HART.
   - Localize o dispositivo na árvore de projetos e abra a DTM (Device Type Manager) de configuração.

2. **Seleção da Variável de Exibição:**  
   - No menu de configurações, acesse a seção **“Display”** ou **“Visor”**.
   - Selecione a variável a ser exibida como a **PV (Process Variable)**.

3. **Configuração da Unidade de Engenharia:**  
   - Ajuste a unidade de engenharia para **Nm³/h**.
   - Se a unidade não estiver listada, ative a opção **“Unidade do Usuário”** e configure:
     - 0% = 0 Nm³/h 
     - 100% = Vazão máxima desejada (consistente com a faixa de medição de ΔP).

4. **Confirmação:**  
   - Verifique no display do transmissor que a leitura aparece em Nm³/h.
   - Caso o transmissor possua alternância de telas, desative ou ajuste a segunda variável para mostrar somente a vazão.

---

## 2. Configuração da Saída Analógica

1. **Acesso à Configuração Básica:**  
   - No DTM, navegue até a seção de **“Setup”** ou **“Calibration”**.

2. **Definição da Faixa de Medição:**  
   - Configure o **Valor Inferior (LRV)** para corresponder à vazão mínima (0 Nm³/h = 4 mA).
   - Configure o **Valor Superior (URV)** para a vazão máxima (valor definido = 20 mA).  
     - Estes valores devem ser coerentes com a pressão diferencial correspondente à vazão máxima calculada.

3. **Função de Transferência:**  
   - Selecione a função **“Raiz Quadrada (SQRT)”** para que o transmissor aplique a extração de raiz na relação entre ΔP e vazão.
   - Configure o ponto de corte (cut-off) da raiz quadrada se o menu permitir, geralmente em torno de 6% da faixa.  
     > **Por que configurar o cut-off?**  
     > Esta configuração é importante porque a função raiz quadrada é altamente sensível a pequenos valores de ΔP. Em condições de baixa pressão diferencial, o sinal pode ser afetado pelo ruído do sensor, resultando em variações instáveis na leitura. Ao definir um cut-off (por exemplo, 6% da faixa), o transmissor ignora flutuações abaixo desse limiar, evitando a amplificação do ruído e garantindo uma medição mais estável e precisa.

4. **Salvar e Confirmar:**  
   - Salve as configurações e certifique-se que a saída analógica 4–20 mA esteja corretamente configurada para representar a faixa total de vazão.

---

## 3. Ajustes de Compensação

1. **Compensação de Zero (Trim):**  
   - Com o transmissor instalado, abra a válvula de equalização para zerar a pressão diferencial.
   - Use o comando “Trim de Zero” para calibrar o ponto de 4 mA (vazão zero).

2. **Compensação de Temperatura:**  
   - Verifique se o sensor de temperatura interno está ativo para compensar variações térmicas.
   - Se necessário, insira manualmente o valor médio de temperatura do processo.

3. **Fator de Expansibilidade:**  
   - Para medições de gás, insira o fator de expansibilidade (normalmente entre 0,90 e 0,98).
   - Para líquidos, deixe o valor em 1,0.

4. **Outros Ajustes:**  
   - Ajuste o **damping (amortecimento)** do sinal conforme necessário para estabilizar a leitura sem causar atrasos excessivos.
   - Caso o transmissor esteja montado em posição que gere um offset devido à pressão estática (ex.: instalação abaixo ou acima do orifício), utilize a função de compensação de elevação/supressão, se disponível.

---

## 4. Verificação e Validação dos Dados

1. **Sessão de Monitoramento:**  
   - Inicie uma sessão online no PACTware para monitorar os valores transmitidos pelo LD301D2.

2. **Teste de Zero:**  
   - Com o fluxo nulo (válvula de equalização aberta), confirme que o display indica aproximadamente **0 Nm³/h** e a saída está em **4 mA**.

3. **Teste com Pressão Diferencial Aplicada:**  
   - Aplique uma pressão diferencial conhecida correspondente a 50% da faixa (por exemplo, que gere aproximadamente 50% da vazão máxima).  
   - Verifique se o display indica cerca de 50% da vazão máxima (em Nm³/h) e a saída analógica aproximadamente **12 mA**.
   - Em seguida, aplique o ΔP máximo e confirme a leitura de **20 mA** e o valor de vazão esperado.

4. **Verificação do Sentido da Medição:**  
   - Certifique-se de que a pressão no lado **High (H)** está corretamente conectada para que a leitura de vazão seja positiva.
   - Caso a leitura esteja invertida (negativa), ajuste a configuração de “invert PV” no software.

5. **Documentação:**  
   - Registre todos os parâmetros configurados (LRV/URV, unidade Nm³/h, damping, etc.) e salve um backup da configuração através do PACTware.

---

## 5. Considerações Finais

Após concluir a configuração e validação, o transmissor SMAR LD301D2 deverá:
- Exibir a vazão em Nm³/h no display.
- Transmitir a vazão proporcionalmente via sinal analógico 4–20 mA.
- Estar ajustado para compensar variações de temperatura e compressibilidade (para gás), garantindo medições precisas e confiáveis.

*Nota:* Sempre consulte o manual do SMAR LD301D2 e a documentação do PACTware para detalhes específicos e possíveis variações na interface do usuário, pois as opções podem variar conforme a versão do firmware ou o modelo específico.
