"""Camada de aplicação entre a interface gráfica e as equações físicas.

Este módulo não conhece Tkinter. A interface fornece valores e recebe resultados
estruturados, o que permite reutilizar o serviço em outras interfaces.
"""
from __future__ import annotations

import math
from typing import Any, Dict, Tuple

from python import calculos


class ServicoCalculo:
    """Orquestra os cálculos sem depender de qualquer componente visual."""

    @staticmethod
    def configuracao_padrao() -> Dict[str, Any]:
        """Retorna uma cópia dos parâmetros padrão, evitando mutação global."""
        return calculos.CONFIGURACAO.copy()

    @staticmethod
    def calcular(configuracao: Dict[str, Any], modo: str, valor: float,
                 raiz_quadrada: bool = False) -> Tuple[Dict[str, Any], str]:
        """Calcula vazão/pressão conforme a grandeza informada.

        @param configuracao Parâmetros da placa e do transmissor.
        @param modo ``valvula``, ``dp`` ou ``corrente``.
        @param valor Abertura em %, pressão em mmH2O ou corrente em mA.
        @param raiz_quadrada True quando o LD301 estiver configurado com raiz.
        @return Tupla com resultado numérico e descrição da entrada convertida.
        @throws ValueError Para modo inválido ou parâmetros inconsistentes.
        """
        ServicoCalculo._validar_configuracao(configuracao)
        if not math.isfinite(valor):
            raise ValueError("O valor informado deve ser um número finito.")
        if modo == "valvula":
            if not 0 <= valor <= 100:
                raise ValueError("A abertura da válvula deve estar entre 0 e 100 %.")
            vazao = configuracao["Qmax"] * max(valor, 0.0) / 100.0
            return calculos.dp_da_vazao(configuracao, vazao), f"Abertura da válvula: {valor:g} %"
        if modo == "dp":
            if valor < 0:
                raise ValueError("O ΔP deve ser maior ou igual a zero.")
            return calculos.vazao_do_dp(configuracao, valor), f"ΔP informado: {valor:g} mmH₂O"
        if modo == "corrente":
            if not 4 <= valor <= 20:
                raise ValueError("A corrente do laço deve estar entre 4 e 20 mA.")
            if configuracao["URV"] <= configuracao["LRV"]:
                raise ValueError("Para converter corrente, URV deve ser maior que LRV.")
            corte = configuracao["corte_raiz"]
            if not 0 <= corte <= 100:
                raise ValueError("O corte de raiz deve estar entre 0 e 100 % da faixa de pressão.")
            if raiz_quadrada:
                saida_percentual = (valor - 4) / 16 * 100
                limite_saida = 10 * math.sqrt(corte)
                if saida_percentual < limite_saida:
                    limite_ma = 4 + 16 * limite_saida / 100
                    raise ValueError(
                        f"Com raiz e corte abrupto de {corte:g} %, a saída acima do corte "
                        f"começa em {limite_ma:.3f} mA. A 4 mA não é possível determinar "
                        "um ΔP único; valores intermediários abaixo desse limite não são "
                        "produzidos por esse modelo. Confira a função e o corte do LD301 "
                        "ou informe a pressão diferencial medida."
                    )
            dp, faixa = calculos.dp_da_corrente(configuracao, valor, raiz_quadrada)
            resultado = calculos.vazao_do_dp(configuracao, dp)
            tipo = "raiz quadrada" if raiz_quadrada else "linear"
            return resultado, f"Corrente: {valor:g} mA ({tipo}, {faixa:.3f} % da faixa; ΔP = {dp:.3f} mmH₂O)"
        raise ValueError(f"Modo de cálculo desconhecido: {modo}")

    @staticmethod
    def _validar_configuracao(configuracao: Dict[str, Any]) -> None:
        """Valida invariantes físicos e códigos antes de chamar as equações.

        @param configuracao Dicionário completo de parâmetros do modelo.
        @throws ValueError Quando um parâmetro viola o domínio aceito.
        """
        for chave in calculos.CONFIGURACAO:
            numero = configuracao[chave]
            if not isinstance(numero, (int, float)) or not math.isfinite(numero):
                raise ValueError(f"O campo {chave} deve conter um número finito.")
        if configuracao["D"] <= 0 or not 0 < configuracao["d"] < configuracao["D"]:
            raise ValueError("A geometria deve satisfazer 0 < d < D.")
        for chave, rotulo in (("rho", "Massa específica"), ("mu", "Viscosidade"), ("Qmax", "Vazão volumétrica de operação a 100 %")):
            if configuracao[chave] <= 0:
                raise ValueError(f"{rotulo} deve ser maior que zero.")
        if configuracao["kappa"] <= 0:
            raise ValueError("O expoente isentrópico deve ser maior que zero.")
        if configuracao["p1"] <= -calculos.P_ATM_KPA:
            raise ValueError("A pressão absoluta a montante deve ser maior que zero.")
        if configuracao["tomada"] not in calculos.TOMADAS:
            raise ValueError("Tomada deve ser 1, 2 ou 3.")
        if configuracao["material_tubo"] not in calculos.MATERIAIS or configuracao["material_placa"] not in calculos.MATERIAIS:
            raise ValueError("Os códigos dos materiais devem estar entre 1 e 6.")
        if configuracao["fluido"] not in (0, 1) or configuracao["desvio"] not in (0, 1):
            raise ValueError("Fluido e desvio devem usar os códigos 0 ou 1.")
        try:
            geometria = calculos.geometria(configuracao)
        except ZeroDivisionError as erro:
            raise ValueError("A temperatura informada produz um diâmetro de tubulação igual a zero.") from erro
        if not 0 < geometria["d_T"] < geometria["D_T"]:
            raise ValueError("Na temperatura informada, os diâmetros devem satisfazer 0 < d < D.")
