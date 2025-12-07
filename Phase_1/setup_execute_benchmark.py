import asyncio
import os
import pathlib
import sys
from dotenv import load_dotenv # Necesario para cargar el archivo .env

# Aseguramos que los módulos personalizados sean accesibles
sys.path.append(os.path.dirname(__file__))

# Importar las clases de PyRIT
from pyrit.common.path import DATASETS_PATH
from pyrit.memory import CentralMemory
from pyrit.datasets import SeedDataset
from pyrit.setup import initialize_pyrit, SQLITE
from pyrit.executor.attack import (
    AttackConverterConfig,
    AttackExecutor,
    ConsoleAttackResultPrinter,
    PromptSendingAttack,
)

# Importar tu Initializer customizado y Converters algorítmicos
from ollama_initializer import OllamaInitializer
from ollama_tool_target import OllamaToolTarget # Importamos el Target que creaste
from pyrit.prompt_converter import ROT13Converter, CharSwapConverter 
from pyrit.prompt_normalizer.prompt_converter_configuration import PromptConverterConfiguration


async def run_benchmark():
    # --- 0. Configuración Inicial y Carga de Entorno ---
    load_dotenv()
    
    # 0.1. Inicializar PyRIT: Configura la DB (SQLite) y aplica defaults (OllamaInitializer)
    # NOTA: Pasamos el inicializador customizado para aplicar los defaults de OllamaToolTarget.
    initialize_pyrit(memory_db_type=SQLITE, initializers=[OllamaInitializer()])
    
    memory = CentralMemory.get_memory_instance()
    
    # --- 1. Fase de Recolección (Cargar SeedPrompts) ---
    
    # 1.1. Ruta a tu archivo YAML de SeedPrompts
    yaml_filepath = pathlib.Path("./2025_tfm_tool_injection_strategy1.yaml")

    print(f"Cargando Seed Prompts desde: {yaml_filepath}")
    
    try:
        seed_prompts_dataset = SeedDataset.from_yaml_file(yaml_filepath)
    except FileNotFoundError:
        print("\nERROR: ¡Archivo YAML de prompts no encontrado! Asegúrate de que '2025_tfm_tool_injection_strategy1.yaml' existe.")
        return

    # 1.2. Etiquetas para la memoria (clave para el filtrado)
    memory_labels = {"op_name": "Estrategia_1_Inyeccion", "estrategia": "Inyeccion_Argumentos", "modelo": os.getenv("OLLAMA_ATTACK_MODEL")}
    
    # 1.3. Guardar los prompts en la DB
    await memory.add_seeds_to_memory_async(
        seeds=seed_prompts_dataset.prompts, 
        memory_labels=memory_labels
    )
    
    print(f"✅ Cargados {len(seed_prompts_dataset.prompts)} prompts base en la DB.")

    # --- 2. Fase de Configuración del Ataque (Converters y Pipeline) ---
    
    # 2.1. Definir los Converters (Mutadores) que queremos usar
    # Los converters se apilan: el output de uno es el input del siguiente.
    # Usaremos 3 mutaciones algorítmicas que aumentan el espacio de búsqueda de evasión:
    
    converters_list = [
        ROT13Converter(), 
        CharSwapConverter(),
    ]
    # NOTA: Si PyRIT tuviera un Base64Converter() nativo, también lo incluirías aquí.

    # 2.2. Configuración de los Converters para el ataque
    converters = PromptConverterConfiguration.from_converters(converters=converters_list)
    converter_config = AttackConverterConfig(request_converters=converters)
    
    # 2.3. Configurar la Estrategia de Ataque (PromptSendingAttack)
    # NOTA: objective_target y attack_scoring_config ya se cargaron por defecto 
    #       gracias a OllamaInitializer.
    
    attack = PromptSendingAttack(
        # Usamos los defaults, pero especificamos la configuración del converter
        attack_converter_config=converter_config,
        max_retries=2, # Resiliencia: reintentar si hay un error de conexión
    )

    # 2.4. Ejecutar el ataque con los objetivos y seeds cargados
    # PyRIT recuperará los prompts mutados de la DB y los enviará al Target Adversarial
    
    print(f"\n🚀 Ejecutando ataque contra {os.getenv('OLLAMA_ATTACK_MODEL')}...")
    
    # Recuperamos la lista de prompts a ejecutar desde la DB
    objectives_to_execute = [seed.value for seed in seed_prompts_dataset.prompts]
    
    results = await AttackExecutor().execute_single_turn_attacks_async(
        attack=attack,
        objectives=objectives_to_execute,
        seed_groups=memory.get_seed_groups(dataset_name=seed_prompts_dataset.name),
        memory_labels=memory_labels,
    )
    
    print("\n✅ Ejecución finalizada. Resultados almacenados en la DB SQLite.")
    
    # --- 3. Fase de Análisis Inicial (Opcional, para verificación inmediata) ---
    
    print("\n--- Resultados de la prueba piloto (Primeros 5 ataques) ---")
    
    # Puedes usar la función de PyRIT para ver los resultados brutos inmediatamente
    for i, result in enumerate(results[:5]):
        print(f"\n[ATAQUE {i+1}] Objetivo: {result.objective}")
        # La respuesta bruta contiene el JSON de OllamaToolTarget
        # Usamos el resultado de la conversación de PyRIT
        if result.prompt_responses and result.prompt_responses[0].response_text:
            print(f"Respuesta (LLM Output): {result.prompt_responses[0].response_text}")
        
    print("\nContinúe con el script de exportación para el análisis completo en Promptfoo.")


if __name__ == "__main__":
    # Necesitas que el script principal sea asíncrono
    try:
        asyncio.run(run_benchmark())
    except Exception as e:
        print(f"\n❌ Error fatal en el benchmark: {e}")