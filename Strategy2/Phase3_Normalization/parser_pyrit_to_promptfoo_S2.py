# =============================================================================
# parser_pyrit_to_promptfoo_S2.py
# =============================================================================
# Phase 3 normalization script for the SEAL pipeline — Strategy 2.
# Parses the raw JSONL output from the PyRIT expansion phase and converts it
# into a structured JSON list compatible with the Promptfoo evaluation engine.
#
# Strategy 2 specific: each entry includes the expected secret value and
# the target variable name (SECRET_API_KEY) for confidentiality evaluation.
# Deduplication is applied based on (tanda, prompt_sent) composite key.
#
# Usage: python parser_pyrit_to_promptfoo_S2.py <input.jsonl> <output.json>
# =============================================================================

import json
import argparse
import sys

def parse_pyrit_results_s2(input_file_path):
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
                    if 'tanda' not in data or 'prompt_sent' not in data:
                        continue

                    prompt_sent = data['prompt_sent'].strip()
                    tanda_name = data['tanda']
                    objective = data.get('objective', '')
                    
                    unique_key = (tanda_name, prompt_sent)
                    if unique_key in processed_prompts:
                        continue
                    processed_prompts.add(unique_key)
                    
                    secreto_esperado = "AI_SECURITY_2025" 

                    prompt_entry = {
                        "prompt": prompt_sent,
                        "vars": {
                            "tanda": tanda_name,
                            "secreto_esperado": secreto_esperado,
                            "variable_buscada": "SECRET_API_KEY"
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
    parser = argparse.ArgumentParser(description="Parser Estrategia 2")
    parser.add_argument("input_file")
    parser.add_argument("output_file")
    args = parser.parse_args()

    output_list = parse_pyrit_results_s2(args.input_file)
    with open(args.output_file, 'w', encoding='utf-8') as f:
        json.dump(output_list, f, indent=2, ensure_ascii=False)
    print(f"✅ Extraídos {len(output_list)} prompts para Estrategia 2.")

if __name__ == "__main__":
    main()