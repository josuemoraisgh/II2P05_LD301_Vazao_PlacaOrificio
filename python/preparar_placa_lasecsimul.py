"""Cria uma cópia LasecSimul com os dados de uma das placas da prática.

Exemplo: python python/preparar_placa_lasecsimul.py FE-02-AR
A cópia parte de lasecsimul/placa_orificio_ld301.lsproj, é gravada em
lasecsimul/ e altera somente as propriedades exportadas da instância da placa. O transmissor LD301 permanece com sua
parametrização original; LRV, URV, raiz, User Unit e display devem ser gravados
e relidos online pelo PACTware.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PASTA = ROOT / "lasecsimul"
SOURCE = PASTA / "placa_orificio_ld301.lsproj"
RHO_AR = 3.5808630809926583  # kg/m³: ar seco a 20 °C e 301,325 kPa abs (folhas de dados)
# placa: (D [mm], d [mm], Qmax nas condições de operação [m³/h] = Qn,max·ρn/ρ1)
VALUES = {
    "FE-02-AR": (15.8, 6.255, 5.413291324),
    "FE-09-AR": (15.8, 1.824, 0.541329132),
    "FE-01-AR": (20.93, 15.673, 10.826582648),
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("placa", choices=VALUES)
    parser.add_argument("--substituir-gerado", action="store_true", help="Atualiza um arquivo *_calculada.lsproj já gerado por este script")
    args = parser.parse_args()
    D, d, qmax = VALUES[args.placa]
    output = PASTA / f"placa_orificio_{args.placa.replace('-', '_')}_calculada.lsproj"
    if output.exists() and not args.substituir_gerado:
        parser.error(f"O destino já existe; preservado: {output.name}")
    project = json.loads(SOURCE.read_text(encoding="utf-8"))
    wrapper = next(c for c in project["components"] if "orifice_flow_dp" in c.get("typeId", ""))
    if wrapper.get("typeId") != "subsystem.local.orifice_flow_dp":
        parser.error(f"O projeto-base deve usar a definição local do subsistema; encontrado: {wrapper.get('typeId')}")
    local_definition = next(
        (item for item in project.get("subsystems", []) if item.get("typeId") == "subsystem.local.orifice_flow_dp"),
        None,
    )
    if local_definition is None or not local_definition.get("components"):
        parser.error("A definição local da placa não está incorporada em project['subsystems']")
    local_types = {component.get("typeId") for component in local_definition["components"]}
    required_new_blocks = {"sl.gain", "sl.fcn", "sl.mux", "sl.discrete_transfer_fcn"}
    missing = sorted(required_new_blocks - local_types)
    if missing:
        parser.error(f"A definição local não foi migrada para os blocos atuais: {', '.join(missing)}")
    legacy_wrappers = sorted(
        type_id for type_id in local_types
        if type_id and type_id.startswith("control.") and type_id != "control.constant"
    )
    if legacy_wrappers:
        parser.error(f"A definição local ainda contém blocos de controle antigos: {', '.join(legacy_wrappers)}")
    # A definição está incorporada no .lsproj. Não mantenha metadata que pareça uma
    # dependência de um arquivo .lssubcircuit externo que não acompanha os projetos didáticos.
    local_definition.pop("origin", None)
    properties = wrapper.setdefault("properties", {})
    for id_, value in {
        "c_D": D,
        "c_d": d,
        "c_tap": 3,
        "c_lup": 44,
        "c_ldn": 8,
        "c_pipe_mat": 1,
        "c_plate_mat": 2,
        "c_T": 20,
        "c_fluid": 1,
        "c_rho": RHO_AR,
        "c_mu": 0.0181,
        "c_kappa": 1.4,
        "c_p1": 200,
        "c_qmax": qmax,
        "c_inst": 0,
    }.items():
        # O LasecSimul persiste as propriedades exportadas na instância da placa.
        # Editar só as constantes do subcircuito embutido não atualiza este painel.
        properties[f"@{id_}.value"] = value
    output.write_text(json.dumps(project, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output.name)


if __name__ == "__main__":
    main()
