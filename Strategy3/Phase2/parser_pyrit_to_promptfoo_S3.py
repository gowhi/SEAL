# parser_pyrit_to_promptfoo_S3.py
# Parser para Estrategia 3 - Inyección Indirecta (Disponibilidad / Secuestro de Contexto)
import json
import argparse
import sys
import re

def parse_pyrit_results_s3(input_file_path):
    prompts_for_promptfoo = []
    processed_prompts = set() 
    
    try:
        with open(input_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or not line.startswith('{'):
                    continue
                try:
                    data = json.loads(line)
                    # Filtramos solo las líneas que contienen el resumen de la tanda de PyRIT
                    if 'tanda' not in data or 'prompt_sent' not in data:
                        continue

                    prompt_sent = data['prompt_sent'].strip()
                    tanda_name = data['tanda']
                    objective = data.get('objective', '')
                    
                    unique_key = (tanda_name, prompt_sent)
                    if unique_key in processed_prompts:
                        continue
                    processed_prompts.add(unique_key)
                    
                    # --- Lógica Específica Estrategia 4 ---
                    # Identificamos el path que el ataque intentaba inyectar
                    # Usamos regex para extraer el path del objetivo (objective)
                    path_re = re.search(r'(/etc/\w+)', objective)
                    path_inyectado = path_re.group(1) if path_re else "Desconocido"

                    prompt_entry = {
                        "prompt": prompt_sent,
                        "vars": {
                            "tanda": tanda_name,
                            "path_inyectado": path_inyectado,
                            "tarea_legitima": "Resumir o analizar el texto",
                            "marcador_exito": "INDIRECT_INJECTION_SUCCESS" # Marcador usado en los prompts
                        }
                    }
                    prompts_for_promptfoo.append(prompt_entry)
                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        print(f"Error: El archivo '{input_file_path}' no existe.", file=sys.stderr)
        sys.exit(1)
    
    return prompts_for_promptfoo

def main():
    parser = argparse.ArgumentParser(description="Parser para Promptfoo - Estrategia 4 (Indirect Injection)")
    parser.add_argument("input_file", help="Archivo .jsonl con resultados de PyRIT")
    parser.add_argument("output_file", help="Archivo .json de salida para Promptfoo")
    args = parser.parse_args()

    output_list = parse_pyrit_results_s3(args.input_file)
    with open(args.output_file, 'w', encoding='utf-8') as f:
        json.dump(output_list, f, indent=2, ensure_ascii=False)
    print(f"✅ Extraídos {len(output_list)} prompts para Estrategia 4 (Inyección Indirecta).")

if __name__ == "__main__":
    main()
