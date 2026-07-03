# =============================================================================
# blind_sample_parser.py — Genera muestras "ciegas" para validacion manual
# =============================================================================
# Proposito: extraer todas las interacciones de un eval.json de Promptfoo
# (cualquier estrategia S1/S2/S3) SIN los campos que provienen del evaluador
# determinista (score, pass, gradingResult, assert, error...), para que un
# humano pueda etiquetar cada interaccion sin sesgo y luego comparar acuerdo
# con el evaluador (Comment 2 del reviewer).
#
# Generico: funciona con cualquier eval.json que siga el esquema estandar
# de Promptfoo (head/body/outputs), independientemente de la estrategia.
#
# Uso:
#   python blind_sample_parser.py <eval.json> <strategy_label> [output.json] [--exclude-vars k1,k2]
#
# Ejemplo:
#   python blind_sample_parser.py eval-S3-locals.json S3 blind_S3.json --exclude-vars marcador_exito
# =============================================================================

import json
import sys
import argparse


# Heuristica: nombres de variables que tipicamente son "respuesta correcta"
# usada por el evaluador (no deben mostrarse al etiquetador humano para
# mantener el etiquetado ciego). Se puede ampliar con --exclude-vars.
DEFAULT_EXCLUDE_VAR_KEYS = {
    "marcador_exito",     # S3: flag interna de exito de inyeccion
    "secret_value",       # S2 (si existiera): valor secreto esperado
    "valor_secreto",
    "expected_output",
    "ground_truth",
}


def extract_prompt_parts(prompt_field):
    """Normaliza el campo 'prompt' de un output (puede ser lista de mensajes
    role/content, un dict con 'raw', o un STRING que contiene ese JSON
    serializado -- este ultimo es el caso mas comun en los eval.json de
    Promptfoo). Devuelve (system_prompt, user_prompt)."""
    system_prompt, user_prompt = None, None

    # Promptfoo suele serializar 'prompt' como string JSON, no como objeto.
    # Intentamos parsearlo antes de decidir el formato.
    if isinstance(prompt_field, str):
        try:
            parsed = json.loads(prompt_field)
            prompt_field = parsed
        except (json.JSONDecodeError, TypeError):
            pass  # se queda como string plano (formato antiguo o distinto)

    if isinstance(prompt_field, list):
        user_parts = []
        for msg in prompt_field:
            if not isinstance(msg, dict):
                continue
            role = msg.get("role")
            content = msg.get("content")
            if role == "system":
                system_prompt = content
            elif role == "user":
                if isinstance(content, str):
                    user_parts.append(content)
                else:
                    user_parts.append(json.dumps(content, ensure_ascii=False))
        if user_parts:
            user_prompt = "\n".join(user_parts)
    elif isinstance(prompt_field, dict):
        # formato alternativo: {"raw": "..."}
        system_prompt = prompt_field.get("raw")
    elif isinstance(prompt_field, str):
        system_prompt = prompt_field

    return system_prompt, user_prompt


def extract_model_output_text(out):
    """Prioriza 'text' (salida cruda del modelo); si no existe, cae a 'response'.
    Se deja tal cual (aunque sea un string que serializa una tool call) para
    que el etiquetador humano vea exactamente lo mismo que evaluo el scorer,
    sin introducir diferencias por reformateo."""
    if out.get("text") is not None:
        return out["text"]
    resp = out.get("response")
    if isinstance(resp, dict):
        return resp.get("output", resp)
    return resp


def extract_samples(data, strategy_label, exclude_var_keys):
    samples = []
    excluded_keys_found = set()

    body = data.get("body", [])
    for row in body:
        test = row.get("test", {}) or {}
        vars_raw = test.get("vars", {}) or {}
        description = test.get("description")
        test_idx = row.get("testIdx")

        # filtra variables "respuesta correcta" para mantener el etiquetado ciego
        context_vars = {}
        for k, v in vars_raw.items():
            if k in exclude_var_keys:
                excluded_keys_found.add(k)
                continue
            context_vars[k] = v

        for out in row.get("outputs", []):
            if out is None:
                continue

            system_prompt, user_prompt = extract_prompt_parts(out.get("prompt"))
            model_output = extract_model_output_text(out)

            sample = {
                "sample_id": f"{strategy_label}_{test_idx}_{out.get('promptIdx')}_{(out.get('id') or '')[:8]}",
                "strategy": strategy_label,
                "model": out.get("provider"),
                "test_description": description,
                "system_prompt": system_prompt,
                "context_vars": context_vars,   # contexto del ataque, sin flags de "respuesta correcta"
                "user_prompt": user_prompt,
                "model_output": model_output,
                "latency_ms": out.get("latencyMs"),
                # --- campos NO incluidos deliberadamente (vienen del evaluador): ---
                # score, pass, gradingResult, error, failureReason, namedScores,
                # test.assert (codigo del scorer)
                "human_label": None,   # <- campo vacio a rellenar por el etiquetador
                "human_notes": None,
            }
            samples.append(sample)

    return samples, excluded_keys_found


def main():
    parser = argparse.ArgumentParser(description="Genera muestras ciegas para validacion manual del evaluador.")
    parser.add_argument("eval_json", help="Ruta al archivo eval-*.json de Promptfoo")
    parser.add_argument("strategy_label", help="Etiqueta de estrategia, p.ej. S1, S2, S3")
    parser.add_argument("output_json", nargs="?", default=None, help="Ruta de salida (por defecto: blind_<strategy>.json)")
    parser.add_argument("--exclude-vars", default="", help="Claves adicionales de vars a excluir, separadas por coma")
    args = parser.parse_args()

    extra_exclude = {k.strip() for k in args.exclude_vars.split(",") if k.strip()}
    exclude_var_keys = DEFAULT_EXCLUDE_VAR_KEYS | extra_exclude

    with open(args.eval_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    samples, excluded_found = extract_samples(data, args.strategy_label, exclude_var_keys)

    output_path = args.output_json or f"blind_{args.strategy_label}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(samples, f, ensure_ascii=False, indent=2)

    print(f"[OK] {len(samples)} muestras extraidas de {args.eval_json}")
    print(f"[OK] Guardado en: {output_path}")
    if excluded_found:
        print(f"[INFO] Claves de 'vars' excluidas por ser respuesta-del-evaluador: {sorted(excluded_found)}")
    else:
        print("[INFO] No se encontraron claves de vars en la lista de exclusion (revisa si tu esquema usa otros nombres).")


if __name__ == "__main__":
    main()