"""Cria uma cópia LasecSimul com os dados de uma das placas da prática.

Exemplo: python python/preparar_placa_lasecsimul.py FE-02-AR
A cópia parte de placa_orificio_ld301.lsproj e altera somente as propriedades
exportadas da instância da placa. O transmissor LD301 permanece com sua
parametrização original; LRV, URV, raiz, User Unit e display devem ser gravados
e relidos online pelo PACTware.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "placa_orificio_ld301.lsproj"
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
    output = ROOT / f"placa_orificio_{args.placa.replace('-', '_')}_calculada.lsproj"
    if output.exists() and not args.substituir_gerado:
        parser.error(f"O destino já existe; preservado: {output.name}")
    project = json.loads(SOURCE.read_text(encoding="utf-8"))
    wrapper = next(c for c in project["components"] if "orifice_flow_dp" in c.get("typeId", ""))
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
