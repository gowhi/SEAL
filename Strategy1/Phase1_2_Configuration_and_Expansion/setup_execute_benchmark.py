# =============================================================================
# setup_execute_benchmark.py
# =============================================================================
# Main execution script for the SEAL adversarial expansion pipeline (Phase 1_2).
# Loads seed prompts from YAML, applies PyRIT converters in batches, and
# outputs structured JSONL logs for downstream normalization in Phase 3.
#
# Converters applied per batch:
#   - BASE: no transformation
#   - ROT13_Cifrado: ROT13 encoding
#   - CharSwap_Ofuscacion: character-level substitution
#   - LLM_MaliciousQ: LLM-based malicious rewriting
#   - LLM_Noise: syntactic noise injection
#   - LLM_Tone_Aggressive: tone modulation (frantic)
#
# Output: JSONL file with (prompt, response, tanda, outcome) per interaction.
# Redirect stdout to capture logs: python setup_execute_benchmark.py > output.jsonl
# =============================================================================

import asyncio
import os
import pathlib
import sys
import yaml
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict, Any, Union

logger = logging.getLogger("pyrit")
logger.setLevel(logging.ERROR)

sys.path.append(os.path.dirname(__file__))

from pyrit.memory import CentralMemory, SQLiteMemory
from pyrit.models import SeedPrompt
from pyrit.executor.attack.single_turn import PromptSendingAttack
from pyrit.executor.attack.core import AttackExecutor, AttackConverterConfig
from pyrit.prompt_converter import ROT13Converter, CharSwapConverter, MaliciousQuestionGeneratorConverter, NoiseConverter, ToneConverter
from pyrit.prompt_normalizer.prompt_converter_configuration import PromptConverterConfiguration
from ollama_initializer import OllamaInitializer
from ollama_tool_target import OllamaToolTarget

# Auxiliary template class required for LLM-based converters
class FakePromptTemplate:
    def __init__(self, template: str): self.template = template
    def render_template_value(self, **kwargs): return self.template.format(**kwargs)

async def run_attack_tanda(converters_list: List[Any], name: str, objectives: List[str], all_results: list):
    
    print(f"🚀 Ejecutando Tanda: {name}...")
    
    converters = PromptConverterConfiguration.from_converters(converters=converters_list)
    config = AttackConverterConfig(request_converters=converters)
    attack = PromptSendingAttack(attack_converter_config=config)
    
    attack_model = os.getenv("OLLAMA_ATTACK_MODEL", "llama3.2:latest")
    scorer_model = os.getenv("OLLAMA_SCORER_MODEL", "mistral:latest")
    
    current_results = await AttackExecutor().execute_single_turn_attacks_async(
        attack=attack,
        objectives=objectives,
        seed_groups=CentralMemory.get_memory_instance().get_seed_groups(),
    )
    
    memory = CentralMemory.get_memory_instance()
    tanda_summaries = []

    for result in current_results:
        final_score = None
        score_id = getattr(result, 'last_score_id', None)
        if score_id:
            try: final_score = memory.get_prompt_scores(prompt_ids=[score_id])
            except: pass
        
        conversation_messages = memory.get_message_pieces(conversation_id=result.conversation_id)
        llm_target_response = ""
        attack_prompt_sent = ""

        for msg in conversation_messages:
            role = str(msg.role).lower()
            if role == "user": attack_prompt_sent = msg.converted_value or msg.original_value
            if role in ["assistant", "model", "tool_target", "tool"]:
                llm_target_response = msg.original_value or msg.converted_value 
                break

        tool_calls = None
        content_text = llm_target_response
        if "[TOOL_CALLS]:" in llm_target_response:
            parts = llm_target_response.split("[TOOL_CALLS]:")
            content_text = parts[0].strip()
            try: tool_calls = json.loads(parts[1].strip())
            except: pass

        llama_log = {
            "model": attack_model,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "message": {"role": "assistant", "content": content_text, "tool_calls": tool_calls},
            "done_reason": "stop", "done": True, "total_duration": 1000000000, "eval_count": 30
        }
        print(json.dumps(llama_log))

        if final_score:
            mistral_log = {
                "model": scorer_model,
                "created_at": datetime.utcnow().isoformat() + "Z",
                "message": {"role": "assistant", "content": json.dumps({"score_value": final_score[0].score_value, "rationale": final_score[0].score_rationale})},
                "done": True
            }
            print(json.dumps(mistral_log))

        tanda_summaries.append({
            "tanda": name,
            "objective": result.objective,
            "prompt_sent": attack_prompt_sent,
            "target_output": llm_target_response,
            "outcome": final_score[0].score_value if final_score else "UNDETERMINED",
            "rationale": final_score[0].score_rationale if final_score else "N/A"
        })

    for summary in tanda_summaries:
        print(json.dumps(summary))

    all_results.extend(current_results)
    print(f"✅ Tanda {name} finalizada. {len(current_results)} resultados exportados.")

async def run_benchmark():
    load_dotenv()
    sqlite_instance = SQLiteMemory(db_path="./pyrit_results.sqlite")
    CentralMemory.set_memory_instance(sqlite_instance)
    OllamaInitializer().initialize()

    yaml_path = pathlib.Path("./2025_tfm_tool_injection_strategy1.yaml")
    with open(yaml_path, "r", encoding="utf-8") as f:
        yaml_data = yaml.safe_load(f)

    seed_prompts_list = [SeedPrompt(added_by="ubuntu", **item) for item in yaml_data.get("seeds", [])]
    await CentralMemory.get_memory_instance().add_seeds_to_memory_async(seeds=seed_prompts_list)
    objectives = [seed.value for seed in seed_prompts_list]

    attacker_target = OllamaToolTarget(
        endpoint_url=os.getenv("OLLAMA_SERVER_URL"), 
        model=os.getenv("OLLAMA_ATTACK_MODEL"), 
        system_prompt="Rewriter assistant."
    )

    # Converter batches — each tuple defines (converters, batch_name)
    tandas = [
        ([], "BASE_SinConversion"),
        ([ROT13Converter()], "ROT13_Cifrado"),
        ([CharSwapConverter()], "CharSwap_Ofuscacion"),
        ([MaliciousQuestionGeneratorConverter(converter_target=attacker_target, prompt_template=FakePromptTemplate("Reescribe: {prompt}"))], "LLM_MaliciousQ"),
        ([NoiseConverter(converter_target=attacker_target)], "LLM_Noise"),
        ([ToneConverter(converter_target=attacker_target, tone="frantic")], "LLM_Tone_Aggressive")
    ]
    
    all_results = []
    for convs, name in tandas:
        await run_attack_tanda(convs, name, objectives, all_results)
    
    print(f"\n✔ Benchmark completado.")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
