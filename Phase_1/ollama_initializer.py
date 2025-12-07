import json
from typing import Optional, List
import httpx # Para peticiones asíncronas

from pyrit.models import Message, MessagePiece
from pyrit.prompt_target import PromptChatTarget

# --- Definición de la herramienta ---
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
    """PromptTarget para Ollama usando httpx y compatible con PyRIT."""
    
    def __init__(self, endpoint_url: str, model: str, system_prompt: str, is_scorer: bool = False, **kwargs) -> None:
        super().__init__(**kwargs)
        self.endpoint_url = endpoint_url.rstrip('/')
        self.model = model
        self.default_system_prompt = system_prompt
        self.is_scorer = is_scorer
        # La memoria se gestiona de forma externa/automática por el AttackExecutor

    async def send_prompt_async(self, *, message: Message) -> Message:
        # Extraer el prompt convertido del usuario
        user_prompt = message.message_pieces[0].converted_value

        messages = [
            {"role": "system", "content": self.default_system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }

        # Añadir las herramientas solo si no estamos usando el modelo como scorer (evaluador JSON)
        if self.is_scorer:
            payload["response_format"] = {"type": "json"}
        else:
            payload["tools"] = TOOL_SCHEMA

        url = f"{self.endpoint_url}/api/chat"

        async with httpx.AsyncClient(timeout=90) as client:
            try:
                # Realizar la petición a la API de chat de Ollama
                response = await client.post(url, json=payload, headers={"Content-Type": "application/json"})
                response.raise_for_status()
                response_json = response.json()
                
                # 🛑 ACCIÓN CLAVE: IMPRIMIR JSON PURO A STDOUT PARA REDIRECCIÓN 🛑
                # Esto garantiza que el JSON de la respuesta (TOOL o SCORE) sea capturado
                print(json.dumps(response_json))
                # -----------------------------------------------------------------

                assistant_message = response_json.get("message", {})

                # --- Lógica de Extracción para PyRIT ---
                tool_calls = assistant_message.get("tool_calls")
                
                if tool_calls:
                    response_content = json.dumps(tool_calls, indent=2)
                    response_role = "tool"
                else:
                    response_content = assistant_message.get("content", "")
                    response_role = "assistant"
                
                response_piece = MessagePiece(
                    role=response_role,
                    original_value=response_content
                )

                # Devolver el mensaje para que AttackExecutor se encargue de guardarlo en la memoria.
                return Message(message_pieces=[response_piece])

            except Exception as e:
                # Captura errores de conexión o HTTP y los propaga.
                raise RuntimeError(f"OllamaToolTarget send_prompt_async error: {e}") from e

    # PyRIT requiere este método
    def get_identifier(self) -> str:
        return f"ollama:{self.model}"

    def _validate_request(self, message: Message) -> None:
        if len(message.message_pieces) != 1:
            raise ValueError("OllamaToolTarget solo soporta solicitudes con una única pieza de mensaje.")
        if message.message_pieces[0].converted_value is None:
            raise ValueError("El valor convertido del mensaje no puede ser None.")

    @property
    def is_json_response_supported(self) -> bool:
        return True

    def set_system_prompt(self, system_prompt: str, **kwargs) -> None:
        self.default_system_prompt = system_prompt

    def get_token_limit(self) -> int:
        return 4096
