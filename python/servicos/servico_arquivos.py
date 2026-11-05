"""Casos de uso para gerar os arquivos didáticos do projeto.

Este serviço concentra operações de arquivos fora da interface Tkinter. As
confirmações de sobrescrita ficam na camada visual; este módulo recebe essa
decisão explicitamente e executa a operação solicitada.
"""
from __future__ import annotations

from pathlib import Path
from typing import List

from python import gerar_folhas_dados, preparar_placa_lasecsimul


class ServicoArquivosProjeto:
    """Orquestra a geração de folhas de dados e projetos de simulação."""

    @staticmethod
    def caminhos_folhas() -> List[Path]:
        """Lista as folhas que serão atualizadas pelo gerador."""
        raiz = Path(__file__).resolve().parents[2]
        return [raiz / "folhas_de_dados" / f"FOLHA_DADOS_{placa['tag'].replace('-', '_')}.md"
                for placa in gerar_folhas_dados.PLACAS]

    @staticmethod
    def gerar_folhas() -> List[Path]:
        """Gera e devolve os caminhos das folhas didáticas."""
        return gerar_folhas_dados.gerar_folhas()

    @staticmethod
    def caminho_projeto(placa: str) -> Path:
        """Devolve o caminho de saída esperado para a placa selecionada."""
        if placa not in preparar_placa_lasecsimul.VALUES:
            raise ValueError(f"Placa desconhecida: {placa}")
        raiz = Path(__file__).resolve().parents[2]
        nome = placa.replace("-", "_")
        return raiz / "lasecsimul" / f"placa_orificio_{nome}_calculada.lsproj"

    @staticmethod
    def preparar_projeto(placa: str, substituir: bool = False) -> Path:
        """Prepara a cópia LasecSimul e devolve seu caminho final."""
        return preparar_placa_lasecsimul.preparar_placa(placa, substituir)
