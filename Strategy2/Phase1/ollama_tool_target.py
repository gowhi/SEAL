import json
import requests
import os
from typing import Optional, List, Any
from pyrit.models import Message, MessagePiece
from pyrit.prompt_target import PromptChatTarget
from dotenv import load_dotenv

load_dotenv()

# Esquema de la herramienta para el ataque
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
    def __init__(self, endpoint_url: str, model: str, system_prompt: Optional[str] = None, is_scorer: bool = False, **kwargs) -> None:
        super().__init__(**kwargs)
        self.endpoint_url = endpoint_url.rstrip('/')
        self.model = model
        self.is_scorer = is_scorer
        self.default_system_prompt = os.getenv("PROMPT") or system_prompt or "You are a helpful assistant."
        self.session = requests.Session()
        
    async def send_prompt_async(self, *, message: Message) -> Message:
        user_prompt = ""
        pieces = getattr(message, 'message_pieces', None) or getattr(message, 'request_pieces', [])
        
        if not pieces and hasattr(message, 'prompt_request'):
            pieces = getattr(message.prompt_request, 'request_pieces', [])
            
        if pieces:
            user_prompt = pieces[0].converted_value or pieces[0].original_value
        else:
            user_prompt = str(message)

        api_messages = [
            {"role": "system", "content": self.default_system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        payload = {
            "model": self.model,
            "messages": api_messages,
            "stream": False
        }

        if not self.is_scorer:
            payload["tools"] = TOOL_SCHEMA
        
        try:
            response = self.session.post(f"{self.endpoint_url}/api/chat", json=payload, timeout=60)
            response.raise_for_status()
            
            resp_data = response.json().get("message", {})
            content_text = resp_data.get("content", "")
            
            if "tool_calls" in resp_data:
                tools_json = json.dumps(resp_data["tool_calls"])
                full_output = f"{content_text} [TOOL_CALLS]: {tools_json}".strip()
            else:
                full_output = content_text

            new_piece = MessagePiece(role="assistant", original_value=full_output)
            return Message([new_piece]) 

        except Exception as e:
            error_piece = MessagePiece(role="assistant", original_value=f"ERROR: {str(e)}")
            return Message([error_piece])

    def _validate_request(self, *, prompt_request: Any) -> None:
        pass 

    def is_json_response_supported(self) -> bool:
        return True

    def set_system_prompt(self, system_prompt: str, **kwargs) -> None:
        """Establece el prompt del sistema. Definido para ser compatible con llamadas de PyRIT."""
        self.default_system_prompt = system_prompt
        
    def get_token_limit(self) -> int:
        return 4096
