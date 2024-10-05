from typing import Final

MODELS : Final = {
    "Google": [
        {
            "id": "gemma-7b-it",
            "name": "Gemma 7B IT"
        },
        {
            "id": "gemma2-9b-it",
            "name": "Gemma 2 9B IT"
        }
    ],
    "Meta": [
        {
            "id": "llama3-8b-8192",
            "name": "LLaMA 3 8B 8192"
        },
        {
            "id": "llama-3.1-8b-instant",
            "name": "LLaMA 3.1 8B Instant"
        },
        {
            "id": "llama3-70b-8192",
            "name": "LLaMA 3 70B 8192"
        },
        {
            "id": "llama-guard-3-8b",
            "name": "LLaMA Guard 3 8B"
        },
        {
            "id": "llama-3.1-70b-versatile",
            "name": "LLaMA 3.1 70B Versatile"
        }
    ],
    "Groq": [
        {
            "id": "llama3-groq-70b-8192-tool-use-preview",
            "name": "LLaMA 3 Groq 70B 8192 Tool Use Preview"
        },
        {
            "id": "llama3-groq-8b-8192-tool-use-preview",
            "name": "LLaMA 3 Groq 8B 8192 Tool Use Preview"
        }
    ],
    "Mistral": [
        {
            "id": "mixtral-8x7b-32768",
            "name": "Mixtral 8x7B 32768"
        }
    ],
}


DEFAULT_MODEL_ID = 'llama3-70b-8192'
DEFAULT_TEMPARATURE = 0.3
