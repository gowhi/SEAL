# parser_pyrit_to_promptfoo.py
import json
import re
import argparse
import sys

# --- REGEX DE DETECCIÓN ---
HEX_VALUE_AFTER_WORD_REGEX = re.compile(
    r'(?:hexade[cs]imal).*?([a-f0-9]{8,})', 
    re.IGNORECASE | re.DOTALL 
)

def decode_hex(hex_string):
    clean_hex = re.sub(r'[^a-f0-9]', '', hex_string, flags=re.IGNORECASE)
    if len(clean_hex) % 2 != 0:
        return None
    try:
        decoded_part = bytes.fromhex(clean_hex).decode('utf-8', errors='ignore')
        if 'shadow' in decoded_part: return '/etc/shadow'
        if 'passwd' in decoded_part: return '/etc/passwd'
    except:
        pass
    return None

def extract_path_from_objective(objective):
    if re.search(r'shadow|funqbj|shadwo', objective, re.IGNORECASE):
        return '/etc/shadow'
    if re.search(r'passwd|cnffjq|passdw', objective, re.IGNORECASE):
        return '/etc/passwd'
    hex_match = HEX_VALUE_AFTER_WORD_REGEX.search(objective)
    if hex_match:
        hex_path = decode_hex(hex_match.group(1))
        if hex_path: return hex_path
    return 'N/A'

def parse_pyrit_results(input_file_path):
    # NOTA: Ahora devolvemos una LISTA, no un diccionario
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
                    
                    path_esperado = extract_path_from_objective(objective)

                    # Estructura limpia para Promptfoo
                    prompt_entry = {
                        "prompt": prompt_sent,
                        "vars": {
                            "tanda": tanda_name,
                            "path_esperado": path_esperado
                        }
                    }
                    prompts_for_promptfoo.append(prompt_entry)
                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        print(f"Error: El archivo '{input_file_path}' no existe.", file=sys.stderr)
        sys.exit(1)
    
    print(f"✅ Se extrajeron {len(prompts_for_promptfoo)} prompts únicos.")
    return prompts_for_promptfoo # Devolvemos la lista directamente

def main():
    parser = argparse.ArgumentParser(description="Convierte PyRIT JSONL a Promptfoo JSON List")
    parser.add_argument("input_file", help="Archivo JSONL de entrada")
    parser.add_argument("output_file", help="Archivo JSON de salida (ej: prompts.json)")
    args = parser.parse_args()

    output_list = parse_pyrit_results(args.input_file)
    
    try:
        with open(args.output_file, 'w', encoding='utf-8') as f:
            # Guardamos la lista con indentación para legibilidad
            json.dump(output_list, f, indent=2, ensure_ascii=False)
        print(f"🎉 Éxito: Archivo listo en '{args.output_file}'.")
    except Exception as e:
        print(f"Error al escribir: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
