cat setup_execute_benchmark.py
import asyncio
import os
import pathlib
import sys
import yaml
import json
import logging
from dotenv import load_dotenv
from typing import List, Dict, Any, Union

# Configurar logger para suprimir errores de PyRIT/SQLAlchemy y mantener la ejecución estable
logger = logging.getLogger("pyrit")
logger.setLevel(logging.ERROR)

# Permitir import locales
sys.path.append(os.path.dirname(__file__))

# -----------------------
# PyRIT imports
# -----------------------
from pyrit.memory import CentralMemory, SQLiteMemory
from pyrit.models import SeedPrompt
from pyrit.executor.attack.single_turn import PromptSendingAttack
from pyrit.executor.attack.core import AttackExecutor, AttackConverterConfig
from pyrit.prompt_converter import ROT13Converter, CharSwapConverter, MaliciousQuestionGeneratorConverter, NoiseConverter, ToneConverter,
from pyrit.prompt_normalizer.prompt_converter_configuration import PromptConverterConfiguration

# -----------------------
# Custom imports
# -----------------------
from ollama_initializer import OllamaInitializer
from ollama_tool_target import OllamaToolTarget


async def run_attack_tanda(converters_list: List[Any], name: str, objectives: List[str], all_results: list):
    """Función auxiliar que ejecuta un AttackExecutor con una configuración específica y exporta los resultados."""
    
    # 1. Construir la configuración del conversor
    converters = PromptConverterConfiguration.from_converters(converters=converters_list)
    config = AttackConverterConfig(request_converters=converters)

    # 2. Configurar el ataque con el conversor actual
    attack = PromptSendingAttack(attack_converter_config=config)
    
    memory_labels = {
        "op_name": f"Estrategia_1_Tanda_{name}",
        "estrategia": name,
        "modelo": os.getenv("OLLAMA_ATTACK_MODEL"),
    }
    
    print(f"🚀 Ejecutando Tanda: {name}...")
    
    # 3. Ejecutar la tanda
    current_results = await AttackExecutor().execute_single_turn_attacks_async(
        attack=attack,
        objectives=objectives,
        seed_groups=CentralMemory.get_memory_instance().get_seed_groups(),
        memory_labels=memory_labels,
    )
    
    # 4. Procesar y exportar los resultados inmediatamente (JSONL)
    memory = CentralMemory.get_memory_instance()
    
    for result in current_results:
        
        final_score = None
        
        # --- BYPASS ROBUSTO para el SCORE (Evita el crash) ---
        score_attachment_id = getattr(result, 'last_score_id', None)
        
        if score_attachment_id:
            try:
                # Intentamos usar el método más robusto para recuperar scores por ID de MessagePiece
                final_score = memory.get_prompt_scores(prompt_ids=[score_attachment_id])
            except Exception:
                pass
        
        # --- RECUPERACIÓN ROBUSTA DE LA CONVERSACIÓN ---
        conversation_messages = []
        
        # Opción A: Intenta leer mensajes directamente del objeto AttackResult
        if hasattr(result, 'attack_target_output_messages') and result.attack_target_output_messages:
            conversation_messages = result.attack_target_output_messages
        else:
            # Opción B: Si falla la Opción A, intenta recuperarlos de la DB
            conversation_id = getattr(result, 'attack_target_conversation_id', result.conversation_id)
            conversation_messages = memory.get_message_pieces(conversation_id=conversation_id)

        # Extraer el contenido del LLM Target (ROL: TOOL o ASSISTANT)
        llm_target_response = "[EMPTY_RESPONSE]"
        for msg in conversation_messages:
            role = str(msg.role).lower()
            if role in ["assistant", "model", "tool_target", "tool"]:
                # Preferimos el valor original de la respuesta (el JSON de la llamada)
                llm_target_response = msg.original_value or msg.converted_value 
                break

        # --- EXPORTAR LÍNEA JSONL ---
        output_data = {
            "tanda": name,
            "objective": result.objective,
            "target_output": llm_target_response,
            "outcome": final_score[0].score_value if final_score and final_score[0].score_value else "UNDETERMINED",
            "rationale": final_score[0].score_rationale if final_score else "N/A"
        }
        
        # Imprimimos el objeto JSONL a stdout (capturado por la redirección >)
        print(json.dumps(output_data))

    all_results.extend(current_results)
    print(f"✅ Tanda {name} finalizada. {len(current_results)} resultados exportados.")


async def run_benchmark():

    load_dotenv()

    # --- 0. Setup memoria ---
    sqlite_instance = SQLiteMemory(db_path="./pyrit_results.sqlite")
    CentralMemory.set_memory_instance(sqlite_instance)
    
    # --- 1. Inicializar PyRIT con tu Initializer personalizado ---
    initializer = OllamaInitializer()
    initializer.initialize()

    # --- 2. Cargar YAML y Objetivos ---
    yaml_path = pathlib.Path("./2025_tfm_tool_injection_strategy1.yaml")
    
    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            yaml_data = yaml.safe_load(f)
    except FileNotFoundError:
        print("❌ ERROR: Archivo YAML no encontrado.")
        return

    seed_prompts_list = [SeedPrompt(added_by="ubuntu@ai-bench-01", **item) for item in yaml_data.get("seeds", [])]
    await CentralMemory.get_memory_instance().add_seeds_to_memory_async(seeds=seed_prompts_list)
    
    objectives_to_execute = [seed.value for seed in seed_prompts_list]

    # --- Configuración de CONVERSORES (Definimos las listas de instancias) ---
    no_converters = []
    rot13_converters = [ROT13Converter()]
    charswap_converters = [CharSwapConverter()]
    
    # --- 3. Orquestación y Ejecución de Tandas ---
    all_results = []
    
    # TANDA 1: Prompts Base (Control)
    await run_attack_tanda(no_converters, "BASE_SinConversion", objectives_to_execute, all_results)
    
    # TANDA 2: Ataque con ROT13
    await run_attack_tanda(rot13_converters, "ROT13_Cifrado", objectives_to_execute, all_results)
    
    # TANDA 3: Ataque con CharSwap
    await run_attack_tanda(charswap_converters, "CharSwap_Ofuscacion", objectives_to_execute, all_results)

    print(f"\n✔ Benchmark de {len(all_results)} ejecuciones completado.")


if __name__ == "__main__":
    try:
        # Ejecutamos en silencio, el output JSONL va a stdout
        asyncio.run(run_benchmark())
    except Exception as e:
        import traceback
        # Imprimimos el error a stderr para no contaminar stdout (el archivo JSONL)
        traceback.print_exc(file=sys.stderr)
        print(f"\n❌ Error fatal en el benchmark: {e}", file=sys.stderr)