"""Interface gráfica Tkinter para o cálculo de vazão em placa de orifício.

A camada visual apenas coleta dados, chama ``ServicoCalculo`` e apresenta
resultados. Nenhuma equação de medição é implementada neste arquivo.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path
import math
import sys
from typing import Dict

# Permite executar tanto como módulo quanto diretamente pelo caminho do arquivo.
RAIZ_PROJETO = Path(__file__).resolve().parents[2]
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

from python.servicos.servico_calculo import ServicoCalculo
from python.servicos.servico_arquivos import ServicoArquivosProjeto
from python import calculos


class AplicacaoPlacaOrificio(tk.Tk):
    """Janela principal, responsável exclusivamente pela interação do usuário."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Vazão em placa de orifício — ISO 5167-2")
        self.geometry("900x760")
        self.minsize(760, 620)
        self.servico = ServicoCalculo()
        self.servico_arquivos = ServicoArquivosProjeto()
        self.config_vars: Dict[str, tk.StringVar] = {}
        self.preset = tk.StringVar(value="FE-02-AR")
        self._construir_tela()

    def _construir_tela(self) -> None:
        """Cria formulário de configuração, entrada de medição e painel de saída."""
        raiz = ttk.Frame(self, padding=12)
        raiz.pack(fill="both", expand=True)
        ttk.Label(raiz, text="Dimensionamento e conferência da placa de orifício",
                  font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 8))

        paginas = ttk.Notebook(raiz)
        paginas.pack(fill="both", expand=True)
        pagina_calculo = ttk.Frame(paginas, padding=8)
        pagina_arquivos = ttk.Frame(paginas, padding=12)
        paginas.add(pagina_calculo, text="Calculadora")
        paginas.add(pagina_arquivos, text="Arquivos da prática")
        self._construir_pagina_arquivos(pagina_arquivos)

        corpo = ttk.Panedwindow(pagina_calculo, orient="horizontal")
        corpo.pack(fill="both", expand=True)
        quadro_cfg = ttk.LabelFrame(corpo, text="Parâmetros do modelo", padding=8)
        quadro_calc = ttk.Frame(corpo, padding=(12, 0, 0, 0))
        corpo.add(quadro_cfg, weight=1)
        corpo.add(quadro_calc, weight=2)

        seletor = ttk.Frame(quadro_cfg)
        seletor.pack(fill="x", pady=(0, 8))
        ttk.Label(seletor, text="Configuração:").pack(anchor="w")
        lista_presets = ttk.Combobox(
            seletor,
            textvariable=self.preset,
            values=("Caso-base (água)", "FE-02-AR", "FE-09-AR", "FE-01-AR"),
            state="readonly",
        )
        lista_presets.pack(fill="x")
        lista_presets.bind("<<ComboboxSelected>>", self._carregar_preset)

        canvas = tk.Canvas(quadro_cfg, highlightthickness=0, width=320)
        barra = ttk.Scrollbar(quadro_cfg, orient="vertical", command=canvas.yview)
        campos = ttk.Frame(canvas)
        campos.bind("<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=campos, anchor="nw")
        canvas.configure(yscrollcommand=barra.set)
        canvas.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")

        descricoes = {
            "D": "Diâmetro interno D [mm]", "d": "Diâmetro do orifício d [mm]",
            "tomada": "Tomada (1 flange, 2 D/D2, 3 canto)", "L_montante": "Trecho reto montante [D]",
            "L_jusante": "Trecho reto jusante [D]", "material_tubo": "Material do tubo (1–6)",
            "material_placa": "Material da placa (1–6)", "T": "Temperatura [°C]",
            "fluido": "Fluido (0 líquido, 1 gás)", "rho": "Massa específica [kg/m³]",
            "mu": "Viscosidade [cP]", "kappa": "Expoente isentrópico κ",
            "p1": "Pressão manométrica p1 [kPa]", "Qmax": "Vazão volumétrica de operação a 100 % [m³/h]",
            "desvio": "Desvio didático (0/1)", "LRV": "Valor inferior da faixa de ΔP (LRV) [mmH₂O]",
            "URV": "Valor superior da faixa de ΔP (URV) [mmH₂O]", "corte_raiz": "Corte de raiz [% da faixa]",
        }
        for linha, (chave, valor) in enumerate(self.servico.configuracao_padrao().items()):
            ttk.Label(campos, text=descricoes.get(chave, chave), wraplength=190, justify="left").grid(row=linha, column=0, sticky="w", pady=3)
            variavel = tk.StringVar(value=str(valor))
            self.config_vars[chave] = variavel
            ttk.Entry(campos, textvariable=variavel, width=13).grid(row=linha, column=1, sticky="ew", padx=(6, 0), pady=3)
        self._carregar_preset()

        entrada = ttk.LabelFrame(quadro_calc, text="Grandeza medida", padding=10)
        entrada.pack(fill="x")
        self.modo = tk.StringVar(value="valvula")
        modos = (("Válvula (%)", "valvula"), ("ΔP (mmH₂O)", "dp"), ("Corrente (mA)", "corrente"))
        for texto, valor in modos:
            ttk.Radiobutton(entrada, text=texto, value=valor, variable=self.modo,
                            command=self._atualizar_unidade).pack(anchor="w")
        linha = ttk.Frame(entrada)
        linha.pack(fill="x", pady=(8, 0))
        ttk.Label(linha, text="Valor:").pack(side="left")
        self.valor = tk.StringVar(value="50")
        self.campo_valor = ttk.Entry(linha, textvariable=self.valor, width=16)
        self.campo_valor.pack(side="left", padx=6)
        self.raiz = tk.BooleanVar(value=False)
        self.opcao_raiz = ttk.Checkbutton(entrada, text="LD301 configurado com raiz quadrada", variable=self.raiz)
        self.opcao_raiz.pack(anchor="w", pady=(6, 0))
        ttk.Label(entrada, text="ΔP, LRV e URV usam mmH₂O convencional (9,80665 Pa).",
                  wraplength=440).pack(anchor="w", pady=(2, 0))
        ttk.Label(entrada, text="Na conversão com raiz, o corte considerado é abrupto (Hard).",
                  wraplength=440).pack(anchor="w", pady=(2, 0))
        ttk.Button(entrada, text="Calcular", command=self._calcular).pack(anchor="e", pady=(8, 0))

        self.entrada_info = ttk.Label(quadro_calc, text="Informe os parâmetros e pressione Calcular.", wraplength=500)
        self.entrada_info.pack(anchor="w", pady=(10, 4))
        quadro_saida = ttk.Frame(quadro_calc)
        quadro_saida.pack(fill="both", expand=True)
        self.saida = tk.Text(quadro_saida, height=24, wrap="word", state="disabled", font=("Consolas", 10))
        barra_saida = ttk.Scrollbar(quadro_saida, orient="vertical", command=self.saida.yview)
        self.saida.configure(yscrollcommand=barra_saida.set)
        self.saida.pack(side="left", fill="both", expand=True)
        barra_saida.pack(side="right", fill="y")
        ttk.Label(pagina_calculo, text="Resultados simulados; não substituem calibração nem dimensionamento certificado.",
                  foreground="#555").pack(anchor="w", pady=(8, 0))
        self._atualizar_unidade()
        # Ao editar entradas, o resultado anterior deixa de representar os dados atuais.
        for variavel in (*self.config_vars.values(), self.valor, self.raiz):
            variavel.trace_add("write", self._dados_modificados)

    def _dados_modificados(self, *_args) -> None:
        """Remove resultados antigos quando qualquer entrada é alterada."""
        self.entrada_info.configure(text="Dados alterados. Clique em Calcular para atualizar os resultados.")
        self.saida.configure(state="normal")
        self.saida.delete("1.0", "end")
        self.saida.configure(state="disabled")

    def _construir_pagina_arquivos(self, pagina: ttk.Frame) -> None:
        """Apresenta as operações de arquivos didáticos por botões e seletores."""
        ttk.Label(pagina, text="Geração dos arquivos didáticos",
                  font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(0, 8))
        ttk.Label(
            pagina,
            text=("As folhas de dados e os projetos LasecSimul são arquivos de apoio. "
                  "Você pode gerá-los ou atualizá-los aqui sem digitar comandos."),
            wraplength=680,
        ).pack(anchor="w", pady=(0, 12))

        quadro_folhas = ttk.LabelFrame(pagina, text="Folhas de dados", padding=10)
        quadro_folhas.pack(fill="x", pady=(0, 10))
        ttk.Label(quadro_folhas, text="Gera as três folhas com os dados fixos da prática; não usa as alterações do formulário.",
                  wraplength=680).pack(anchor="w")
        ttk.Button(quadro_folhas, text="Gerar / atualizar as três folhas",
                   command=self._gerar_folhas).pack(anchor="e", pady=(8, 0))

        quadro_projeto = ttk.LabelFrame(pagina, text="Cópia do projeto LasecSimul", padding=10)
        quadro_projeto.pack(fill="x", pady=(0, 10))
        ttk.Label(quadro_projeto, text="Gera uma cópia a partir do projeto-base e dos dados fixos da placa; não usa os campos editados na calculadora.",
                  wraplength=680).pack(anchor="w")
        linha = ttk.Frame(quadro_projeto)
        linha.pack(fill="x", pady=(8, 0))
        self.placa_arquivo = tk.StringVar(value="FE-02-AR")
        ttk.Combobox(linha, textvariable=self.placa_arquivo,
                     values=("FE-02-AR", "FE-09-AR", "FE-01-AR"),
                     state="readonly", width=14).pack(side="left")
        ttk.Button(linha, text="Preparar projeto", command=self._preparar_projeto).pack(side="right")

        self.status_arquivos = tk.Text(pagina, height=8, wrap="word", state="disabled")
        self.status_arquivos.pack(fill="both", expand=True, pady=(6, 0))

    def _registrar_arquivos(self, mensagem: str) -> None:
        """Mostra o resultado das operações de arquivo na própria janela."""
        self.status_arquivos.configure(state="normal")
        self.status_arquivos.delete("1.0", "end")
        self.status_arquivos.insert("1.0", mensagem)
        self.status_arquivos.configure(state="disabled")

    def _gerar_folhas(self) -> None:
        """Gera folhas após solicitar confirmação quando elas já existem."""
        caminhos = self.servico_arquivos.caminhos_folhas()
        existentes = [caminho.name for caminho in caminhos if caminho.exists()]
        if existentes and not messagebox.askyesno(
            "Atualizar folhas existentes?",
            "As folhas abaixo serão substituídas pelos valores recalculados:\n\n"
            + "\n".join(existentes)
            + "\n\nAnotações e observações adicionadas a esses arquivos serão perdidas. Deseja continuar?",
            parent=self,
        ):
            return
        try:
            gravados = self.servico_arquivos.gerar_folhas()
            self._registrar_arquivos("Folhas geradas com sucesso:\n" + "\n".join(str(p) for p in gravados))
            messagebox.showinfo("Geração concluída", f"{len(gravados)} folhas foram gravadas.", parent=self)
        except (OSError, ValueError, KeyError) as erro:
            messagebox.showerror("Falha ao gerar folhas", str(erro), parent=self)

    def _preparar_projeto(self) -> None:
        """Prepara o projeto selecionado e confirma antes de substituir cópia."""
        placa = self.placa_arquivo.get()
        destino = self.servico_arquivos.caminho_projeto(placa)
        substituir = False
        if destino.exists():
            substituir = messagebox.askyesno(
                "Atualizar projeto existente?",
                f"O arquivo {destino.name} já existe e será substituído por uma nova cópia do projeto-base. "
                "Alterações anteriores da planta e do LD301 salvas nesse arquivo serão perdidas. Deseja continuar?",
                parent=self,
            )
            if not substituir:
                return
        try:
            gravado = self.servico_arquivos.preparar_projeto(placa, substituir=substituir)
            self._registrar_arquivos(f"Projeto preparado com sucesso:\n{gravado}")
            messagebox.showinfo("Projeto preparado", f"Arquivo salvo em:\n{gravado}", parent=self)
        except (OSError, ValueError, KeyError, StopIteration) as erro:
            messagebox.showerror("Falha ao preparar projeto", str(erro), parent=self)

    def _carregar_preset(self, _evento=None) -> None:
        """Carrega visualmente os parâmetros de um caso documentado.

        A seleção apenas preenche os campos; o usuário continua livre para
        alterar qualquer valor antes de solicitar o cálculo.
        """
        configuracao = self.servico.configuracao_padrao()
        placas = {
            "FE-02-AR": (15.8, 6.255, 5.413291324, 1150.3),
            "FE-09-AR": (15.8, 1.824, 0.541329132, 1617.5),
            "FE-01-AR": (20.93, 15.673, 10.826582648, 80.5),
        }
        selecionado = self.preset.get()
        if selecionado in placas:
            diametro, furo, vazao_maxima, faixa_superior = placas[selecionado]
            configuracao.update(
                D=diametro, d=furo, tomada=3, L_montante=44.0, L_jusante=8.0,
                material_tubo=1, material_placa=2, T=20.0, fluido=1,
                rho=3.5808630809926583, mu=0.0181, kappa=1.4, p1=200.0,
                Qmax=vazao_maxima, desvio=0, LRV=0.0, URV=faixa_superior,
                corte_raiz=6.0,
            )
        for chave, valor in configuracao.items():
            variavel = self.config_vars.get(chave)
            if variavel is not None:
                variavel.set(str(valor))

    def _atualizar_unidade(self) -> None:
        """Habilita a opção de raiz somente para a entrada de corrente."""
        ativa = self.modo.get() == "corrente"
        self.opcao_raiz.configure(state="normal" if ativa else "disabled")
        self.valor.set({"valvula": "50", "dp": "836.1", "corrente": "11.96"}[self.modo.get()])

    def _ler_configuracao(self) -> dict:
        """Converte os campos para tipos nativos preservando tipos padrão."""
        padroes = self.servico.configuracao_padrao()
        configuracao = {}
        for chave, variavel in self.config_vars.items():
            texto = variavel.get().strip().replace(",", ".")
            tipo = type(padroes[chave])
            try:
                numero = float(texto)
            except ValueError as erro:
                raise ValueError(f"O campo {chave} deve conter um número válido.") from erro
            if not math.isfinite(numero):
                raise ValueError(f"O campo {chave} deve conter um número finito.")
            if tipo is int and not numero.is_integer():
                raise ValueError(f"O campo {chave} deve conter um código inteiro.")
            configuracao[chave] = int(numero) if tipo is int else numero
        return configuracao

    def _calcular(self) -> None:
        """Valida entradas, solicita o cálculo ao serviço e apresenta um relatório."""
        try:
            configuracao = self._ler_configuracao()
            valor = float(self.valor.get().strip().replace(",", "."))
            resultado, descricao = self.servico.calcular(configuracao, self.modo.get(), valor, self.raiz.get())
            self.entrada_info.configure(text=descricao)
            self._mostrar_resultado(configuracao, resultado)
        except (ValueError, KeyError, ZeroDivisionError) as erro:
            self._dados_modificados()
            messagebox.showerror("Não foi possível calcular", str(erro), parent=self)

    def _mostrar_resultado(self, cfg: dict, r: dict) -> None:
        """Formata somente a apresentação; todos os valores vêm do serviço."""
        linhas = [
            "RESULTADOS",
            f"Vazão volumétrica de operação {r['Q']:.4f} m³/h",
            f"Velocidade                    {r['v']:.4f} m/s",
            f"Número de Reynolds            {r['Re']:.0f}",
            f"Coeficiente C (ISO)           {r['C_iso']:.6f}",
            f"Coeficiente C real            {r['C_real']:.6f}",
            f"Fator de expansibilidade      {r['eps']:.6f}",
            f"ΔP                            {r['dp_pa']/1000:.4f} kPa",
            f"                              {r['dp_pa']/calculos.MMH2O_EM_PA:.2f} mmH₂O",
            f"                              {r['dp_pa']/calculos.MMH2O_20C_EM_PA:.2f} mmH₂O @ 20 °C",
            f"Perda permanente              {r['perda_kpa']:.4f} kPa",
            "", "CONFORMIDADE",
        ]
        linhas.extend(f"{nome:<24} {'OK' if ok else 'FORA'}" for nome, ok in r["ok"].items())
        linhas.extend(self._explicar_validacoes(cfg, r))
        linhas.extend(["", "GEOMETRIA NA TEMPERATURA DE OPERAÇÃO",
                       f"D = {r['geo']['D_T']:.4f} mm    d = {r['geo']['d_T']:.4f} mm    β = {r['geo']['beta']:.6f}",
                       f"Instalação: {calculos.TOMADAS[cfg['tomada']]}"])
        self.saida.configure(state="normal")
        self.saida.delete("1.0", "end")
        self.saida.insert("1.0", "\n".join(linhas))
        self.saida.configure(state="disabled")

    @staticmethod
    def _explicar_validacoes(cfg: dict, r: dict) -> list[str]:
        """Explica os critérios que sustentam os indicadores de conformidade.

        Os limites e comparações reproduzem os utilizados pelo núcleo de cálculo.
        A explicação deixa explícito que o resultado é uma verificação didática,
        não uma certificação da instalação ou do instrumento.
        """
        geo, dev = r["geo"], r["dev"]
        beta, diametro, furo, reynolds = geo["beta"], geo["D_T"], geo["d_T"], r["Re"]
        razao = calculos.razao_pressoes(cfg, r["dp_pa"])
        minimo_re_tomada = (
            170 * beta ** 2 * diametro if cfg["tomada"] == 1
            else (0.0 if beta < 0.56 else 16000 * beta ** 2)
        )
        condicoes = [
            ("Geometria β", 0.0999 < beta < 0.7501,
             f"0,10 < β < 0,75; calculado β = {beta:.5f}."),
            ("Diâmetro D", 49.999 < diametro < 1000.001,
             f"50 mm ≤ D ≤ 1000 mm; calculado D(T) = {diametro:.3f} mm."),
            ("Diâmetro do furo d", furo > 12.499,
             f"d ≥ 12,5 mm; calculado d(T) = {furo:.3f} mm."),
            ("Reynolds mínimo", reynolds > 5000,
             f"Re_D > 5000; calculado Re_D = {reynolds:.0f}."),
        ]
        if cfg["tomada"] == 1:
            condicoes.append(("Reynolds / tomada flange", reynolds > minimo_re_tomada,
                              f"Para flange: Re_D > 170·β²·D = {minimo_re_tomada:.0f}; calculado {reynolds:.0f}."))
        elif beta >= 0.56:
            condicoes.append(("Reynolds / tomada", reynolds > minimo_re_tomada,
                              f"Para β ≥ 0,56: Re_D > 16000·β² = {minimo_re_tomada:.0f}; calculado {reynolds:.0f}."))
        else:
            condicoes.append(("Reynolds / tomada", True,
                              f"Para esta tomada e β < 0,56, o modelo não aplica mínimo adicional; Re_D = {reynolds:.0f}."))
        if cfg["fluido"] == 1:
            condicoes.append(("Razão de pressões do gás", razao > 0.75,
                              f"p₂/p₁ > 0,75 para usar ε; calculado p₂/p₁ = {razao:.4f} (pressões absolutas)."))

        linhas = [
            "", "O QUE CADA VERIFICAÇÃO SIGNIFICA",
            f"[{ 'OK' if r['ok']['Montante'] else 'FORA' }] Montante: compara {cfg['L_montante']:.2f} D instalado com mínimo {dev['A']:.2f} D "
            "para a condição de instalação modelada (uma curva de 90° a montante).",
            f"[{ 'OK' if r['ok']['Jusante'] else 'FORA' }] Jusante: compara {cfg['L_jusante']:.2f} D instalado com mínimo {dev['A_jus']:.2f} D.",
            f"[{ 'OK' if r['ok']['Rugosidade'] else 'FORA' }] Rugosidade: compara 10⁴·Ra/D = {dev['rug_rel']:.3f} com limite aproximado {dev['rug_lim']:.3f}.",
            "Faixa ISO é um indicador agregado. Os critérios individuais usados pelo modelo são:",
        ]
        linhas.extend(f"  [{'OK' if ok else 'FORA'}] {nome}: {explicacao}" for nome, ok, explicacao in condicoes)
        falhas = [nome for nome, ok, _ in condicoes if not ok]
        linhas.append("Critérios dimensionais/de regime fora: " + (", ".join(falhas) if falhas else "nenhum"))
        linhas.extend([
            "Os comprimentos mínimos usam a tabela implementada para uma curva de 90° a montante.",
            "O ajuste de C por desvios de instalação e rugosidade é uma aproximação didática, não um cálculo normativo de incerteza.",
            "A tela verifica estes critérios selecionados; isso não certifica o conjunto nem substitui a avaliação completa da ISO 5167-2.",
        ])
        return linhas


def main() -> None:
    """Ponto de entrada da aplicação gráfica."""
    AplicacaoPlacaOrificio().mainloop()


if __name__ == "__main__":
    main()
