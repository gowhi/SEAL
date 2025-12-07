import json
import requests
from typing import Optional, List
from pyrit.models import Message
from pyrit.prompt_target import HTTPTarget, PromptChatTarget
from pyrit.interfaces import PromptTarget

# --------------------------------------------------------------------------
# 1. Definición del Tool Schema (CONSTANTE para el ataque)
# Lo definimos aquí para inyectarlo en el constructor de la clase.
# --------------------------------------------------------------------------
TOOL_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "file_writer",
            "description": "Writes content to a file at the specified path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "The full path of the file."},
                    "content": {"type": "string", "description": "The content to write to the file."}
                },
                "required": ["path", "content"]
            }
        }
    }
]

class OllamaToolTarget(PromptChatTarget):
    """Custom PromptTarget para Ollama, capaz de manejar Tool Calling y System Prompts."""
    
    def __init__(self, endpoint_url: str, model: str, system_prompt: str, **kwargs) -> None:
        """
        Inicializa el Target con la URL de Ollama, el modelo y el System Prompt.
        
        Args:
            endpoint_url: URL base del servidor Ollama (ej: http://localhost:11434).
            model: Nombre del modelo a usar (ej: llama3.2:latest).
            system_prompt: La instrucción de seguridad/rol (se inyecta en el contexto).
        """
        # Llamar al constructor de la clase padre (PromptChatTarget, que hereda de PromptTarget)
        # Esto permite que PyRIT maneje el historial y los System Prompts.
        super().__init__(**kwargs)
        
        self.endpoint_url = endpoint_url.rstrip('/') # Elimina barra final
        self.model = model
        self.default_system_prompt = system_prompt
        self.session = requests.Session()
        
    async def send_prompt_async(self, *, message: Message) -> Message:
        """
        Anula el método para construir la solicitud JSON específica de la API de Ollama (/api/chat).
        """
        
        # El mensaje de entrada contiene el Prompt mutado (del usuario)
        user_prompt = message.prompt_request.request_pieces[0].original_value
        
        # El historial de la conversación (messages) debe incluir el system prompt primero.
        messages = [
            {"role": "system", "content": self.default_system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Construir el cuerpo JSON EXACTO que probaste con curl
        payload = {
            "model": self.model,
            "messages": messages,
            "tools": TOOL_SCHEMA, # Inyectamos el Tool Schema aquí
            "stream": False # Desactivar streaming para PyRIT
        }
        
        url = f"{self.endpoint_url}/api/chat"
        headers = {"Content-Type": "application/json"}
        
        try:
            # Enviar la solicitud HTTP
            response = self.session.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status() # Lanza una excepción si la respuesta no es 200 OK
            
            # Ollama devuelve la respuesta en JSON
            response_json = response.json()
            
            # Extraer el contenido de la respuesta (el Tool Call o el texto de rechazo)
            assistant_message = response_json.get("message", {})
            
            # Aquí es donde PyRIT debe registrar el resultado (la respuesta bruta)
            # Retornamos un nuevo objeto Message con la respuesta para que PyRIT la guarde en la memoria.
            return Message(
                role="assistant",
                content=json.dumps(assistant_message), # Guardamos el JSON completo de la respuesta del LLM
                message_type="response",
            )

        except requests.exceptions.RequestException as e:
            # Manejar errores de conexión o API
            print(f"Error al enviar prompt a Ollama: {e}")
            return Message(role="assistant", content=f"ERROR: {str(e)}", message_type="response")

    # Los métodos abstractos de PromptTarget deben estar definidos
    def set_system_prompt(self, prompt: str) -> None:
        self.default_system_prompt = prompt
        
    def get_token_limit(self) -> int:
        return 4096 # Límite genérico para el contexto.