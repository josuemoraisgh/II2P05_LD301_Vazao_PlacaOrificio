# Relatório de validação da prática LD301

**Data:** 22/10/2026. **Máquina:** Windows Server 2025, sessão RDP, VS Code com LasecSimul 0.0.100, Python 3.12.5, PACTware 5.0 (DTM HART Communication 1.0.58, DTM SMAR LD301 3.03), com0com com par `COM20 ↔ CNCB0`.

Cada afirmação abaixo aponta para uma captura real em [`capturas/`](../capturas/). Valores calculados aparecem como [C]; valores lidos em tela, como [O].

## 1. Python

| Verificação | Resultado | Evidência |
|---|---|---|
| `python --version` e `--autoteste` | Python 3.12.5; 12 casos OK | [captura](../capturas/python_02_versao_autoteste.png) |
| FE-02-AR a 100 % | Q₁ 5,413 m³/h; Re 23973; C 0,6148; ε 0,9904; ΔP 11,2802 kPa = 1150,3 mmH₂O | [captura](../capturas/python_04_fe02_saida_valvula_100.png) |
| FE-02-AR a 50 % | 2,707 m³/h; Re 11986; C 0,6180; ε 0,9977; 280,5 mmH₂O | [captura](../capturas/python_05_fe02_saida_valvula_50.png) |
| FE-09-AR a 100 % | 0,541 m³/h; Re 2397; C 0,6196; ε 0,9867; 1617,5 mmH₂O | [captura](../capturas/python_06_fe09_saida.png) |
| FE-01-AR a 100 % (d corrigido) | 10,827 m³/h; Re 36194; C 0,6152; ε 0,9990; 80,5 mmH₂O | [captura](../capturas/python_07_fe01_saida.png) |
| Quadro das três placas | gerado por `python/gerar_folhas_dados.py` | [captura](../capturas/python_08_tres_placas_resumo.png) |
| Verificação independente | script separado, sem importar o código da prática, reproduziu ρₙ, ρ₁, Re, C, ε e ΔP das três placas | executado nesta revisão |

## 2. Correções feitas

1. **FE-01-AR:** a plaqueta (placa01.jpg ampliada) mostra `d/D = 0,7488` e `d = 15,673 mm`, e não `β ≈ 0,425` e `d ≈ 8,89 mm`. Com isso, URV passa de 1123,2 para **80,5 mmH₂O**. A folha e o `preparar_placa_lasecsimul.py` foram corrigidos. A tag da placa01 está coberta por reflexo; a identificação FE-01-AR foi informada pelo professor.
2. **Planta zerada no LasecSimul:** o pacote instalado da extensão 0.0.100 não tem `bundled/project/schema/block-library`. Sem esses arquivos, os blocos `sl.*` aparecem como "?" e a extensão não lê seus valores, embora o motor os execute (com URV 3376,3 e função linear, o LD301 marcava 5,329 mA ⇒ 280,4 mmH₂O a 50 %). Um projeto de teste com dois `sl.gain` novos, sem migração, apresentou o mesmo defeito. Com autorização do professor, os 13 arquivos da biblioteca do repositório-fonte (cujo conteúdo está todo embutido no executável `lasecsimul-core.exe` 0.0.100) foram copiados para a extensão instalada, e só a janela da prática foi recarregada. Depois disso a planta respondeu. [Antes](../capturas/lasecsimul_10_fe02_antes_mostradores_zerados_ld301_responde.png), [teste](../capturas/lasecsimul_11_teste_sl_gain_sem_biblioteca.png), [depois](../capturas/lasecsimul_15_modelo_interno_blocos_reconhecidos.png).
3. **`preparar_placa_lasecsimul.py`:** deixou de substituir o modelo da placa pelo modelo antigo do backup. Agora parte do projeto principal e grava só as Propriedades exportadas. As três cópias `_calculada` foram regeneradas.
4. **`placa_orificio_calculo.py`:** só mudou a saída (Q com 3 casas; ΔP em kPa com 4 casas, em mmH₂O e em mmH₂O@20 °C) e o cabeçalho. Nenhuma equação foi alterada; o autoteste continua passando.
5. **Folhas de dados:** origem de cada valor indicada como [P], [E], [C] ou [O]; Re, C e ε por ponto; páginas reais do DTM; verificação item a item dos limites da ISO 5167-2; nota sobre mmH₂O × mmH₂O@20 °C (0,18 %); ordem de conexão modem → canal → dispositivo.
6. **README:** a afirmação de que a User Unit inicial estava desligada estava errada (estava `On`, 243–800 mm). As referências ao manual passaram a citar página impressa e página do PDF.
7. **Organização do repositório:** pastas `folhas_de_dados/`, `lasecsimul/`, `pactware/`, `python/`, `docs/`, `imagens/` e `capturas/`. Arquivos legados (projetos intermediários, backups de migração, manual duplicado, scripts exploratórios e capturas não usadas) foram removidos e continuam no histórico do git.

## 3. LasecSimul (após a correção)

| Ensaio | Python [C] | Planta [O] | Evidência |
|---|---|---|---|
| FE-02 0 % | 0 | 0,00 m³/h; 0 mmH₂O | [captura](../capturas/lasecsimul_14_fe02_valvula_0.png) |
| FE-02 50 % | 2,707 m³/h; 280,5 mmH₂O; Re 11986; C 0,6180; ε 0,9977 | 2,71 m³/h; 280 mmH₂O; 11986; 0,6180; 0,9977 | [captura](../capturas/lasecsimul_16_fe02_valvula_50_detalhe.png) |
| FE-02 100 % | 5,413 m³/h; 1150,3 mmH₂O; Re 23973; C 0,6148; ε 0,9904 | 5,41 m³/h; 1150 mmH₂O; 23973; 0,6148; 0,9904 | [captura](../capturas/lasecsimul_13_fe02_valvula_100.png) |
| FE-09 50 % / 100 % | 390,0 / 1617,5 mmH₂O | 390 / 1617 mmH₂O | [50 %](../capturas/lasecsimul_35_fe09_valvula_50_verificacao.png), [100 %](../capturas/lasecsimul_34_fe09_valvula_100_verificacao.png) |
| FE-01 100 % | 80,5 mmH₂O | 81 mmH₂O | [captura](../capturas/lasecsimul_36_fe01_valvula_100_verificacao.png) |
| Caso-base com água 50 % | 7,50 m³/h; 836,1 mmH₂O; 7,96 mA (linear) | 7,50 m³/h; 836 mmH₂O; 7,961 mA | [captura](../capturas/lasecsimul_37_caso_base_agua_valvula_50_corrigido.png) |

**Conclusão:** a planta está validada nesta máquina. A mudança de abertura produz vazão e ΔP coerentes com o Python.

## 4. PACTware — execução contínua desde o projeto vazio (12:45–13:02)

1. PACTware aberto com apenas `HOST PC` → **Add device** → **HART Communication** → `COM0`. [início](../capturas/pw_n01_pactware_aberto_host_pc.png), [COM0](../capturas/pw_n04_com0_adicionado.png)
2. Dois cliques em `COM0` → Serial Interface **COM20** → Apply (árvore muda para COM20). [captura](../capturas/pw_n08_com20_aplicada_multimaster_marcado.png)
3. **Multimaster and Burst mode support** desmarcado em etapa própria, aplicado e conferido ao reabrir. [desmarcado](../capturas/pw_n09_multimaster_desmarcado.png), [conferido](../capturas/pw_n11_com20_reaberto_confirmado.png)
4. **Add device** em COM20 → LD301 (Smar, DTM 3.03) → árvore `HOST PC → COM20 → LD301`; projeto salvo como [`pactware/LD301_PACTware_FE02_Pratica.PW5`](../pactware/LD301_PACTware_FE02_Pratica.PW5). [árvore](../capturas/pw_n15_arvore_com20_ld301.png), [salvo](../capturas/pw_n17_projeto_salvo.png)
5. LasecSimul **Rodando**; modem **Abrir → Fechar**. [antes](../capturas/ls_n01_fe02_rodando_modem_abrir.png), [depois](../capturas/ls_n02_fe02_modem_aberto_fechar.png)
6. **Ordem errada registrada:** o Connect no COM20 foi feito com o modem ainda fechado e ficou parado em 67 %. Depois de abrir o modem, o canal não ficou verde e o DTM do LD301 mostrou Disconnected. **Desconectar e conectar só o LD301 não resolveu** nesta execução. Resolveu desconectar também o COM20 (fechamento forçado, "Disconnect failed → Yes") e refazer **Connect no modem COM20** (ícone verde) e depois **Connect no LD301**. [67 %](../capturas/pw_n19_connect_com20_modem_fechado_preso_67.png), [Disconnected](../capturas/pw_n30_dtm_aberto_antes_reconexao_disconnected.png), [forçar](../capturas/pw_n32_canal_preso_forcar_fechamento.png), [COM20 verde](../capturas/pw_n35_modem_com20_conectado_verde.png), [Connected FT100](../capturas/pw_n37_ld301_connected_ft100.png)
7. Online Parameterize, com cada página gravada e relida:
   - leitura inicial: Linear, URV 3376,3, PV(%)/Temp ([captura](../capturas/pw_n38_summary_online_antes.png));
   - URV 1150,3 ([releitura](../capturas/pw_n42_measurement_releitura_urv.png));
   - Function Sqrt ([releitura](../capturas/pw_n45_summary_releitura_sqrt.png));
   - User Unit On, 0–15, Volumetric Flow, **N m3/h**, PV 7,4068 ([releitura](../capturas/pw_n49_user_unit_releitura.png));
   - Display PV / Out(mA) ([releitura final](../capturas/pw_n52_summary_releitura_final.png)).
8. LCD do LD301 a 50 %: **7.407 Nm3/h** e **11.901 mA**; amperímetro 11,90 mA. [LCD vazão](../capturas/ls_n03z_lcd_7407_nm3h.png), [LCD mA](../capturas/ls_n04z_lcd_11901_ma.png)

## 5. Verificação em vários pontos (primeira execução, mesma configuração)

| Abertura | ΔP planta [O] | Corrente [C] / [O] | PV [C] / [O] (Nm³/h) |
|---:|---:|---:|---:|
| 100 % | 1150 mmH₂O | 20,000 / 20,00 mA | 14,9997 / 14,9997 |
| 75 % | 639 mmH₂O | 15,926 / 15,93 mA | 11,181 / LCD 11,180 |
| 50 % | 280 mmH₂O | 11,901 / 11,90 mA | 7,407 / 7,4068 |
| 26 % | 74 mmH₂O | 8,070 / 8,070 mA | 3,816 / não registrado |
| 25 % | 69 mmH₂O | 4,000 / 4,000 mA | 0 / 0,0000 (corte abrupto) |

Evidências na Oficina 05, Passo 07, do [README](../README.md#o05-p09).

## 6. Pendências reais

- **Ponto e modo de corte:** não foram encontrados nas páginas online do DTM 3.03 percorridas. O valor 6 % / Hard foi verificado só pelo comportamento (25 % → 4 mA; 26 % → 8,07 mA).
- **Persistência:** os parâmetros gravados por HART se perdem quando a simulação é reconstruída (edição do esquema ou reabertura do arquivo). Gravar o `.lsproj` com a configuração online não foi testado. [Evidência](../capturas/lasecsimul_26_reconstrucao_restaura_ld301_fecha_modem.png)
- **Outras máquinas:** a correção da biblioteca `block-library` foi feita só nesta máquina. Para as demais, é preciso copiar os arquivos ou publicar um pacote da extensão que os inclua.
- **FE-09-AR e FE-01-AR:** planta verificada; o LD301 dessas cópias não foi parametrizado, pois é tarefa do aluno.
- **Limites metrológicos:** as três placas têm `D < 50 mm` e estão fora do escopo da ISO 5167-2; os coeficientes são uso didático. As dimensões vêm de foto e devem ser medidas antes de uso físico.
- **Divergências manual × simulador:** o span mínimo da faixa 2 é 0,42 kPa no manual e ≈ 0,25 kPa no DTM; o código de pedido `M2` designa sensor manométrico, usado como diferencial no simulador.
