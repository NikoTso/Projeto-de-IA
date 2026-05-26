import os
import logging
from dotenv import load_dotenv
from google import genai
from google.genai import types

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def main():
    if not load_dotenv():
        raise RuntimeError("Erro ao carregar o .env")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY não definida")

    client = genai.Client(api_key=api_key)

    prompt = input("")

    resposta = call_gemini_or_mock(client, prompt)
    print("\nResposta:\n", resposta)


def call_gemini_or_mock(client: genai.Client, prompt: str) -> str:
    if not prompt or not prompt.strip():
        raise ValueError("O prompt não pode estar vazio")

    try:
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        if not resp.candidates:
            raise RuntimeError("A API retornou com sucesso, entretanto nenhum conteúdo foi retornado")

        return resp.text

    except Exception as e:
        if is_quota_error(e):
            log.warning("\nN° máximo de Quota excedida")
            return mock_gemini_response(prompt)
        raise RuntimeError(f"Erro na API: {e}") from e


def mock_gemini_response(input_text: str) -> str:
    return "\nResposta esperada: " + input_text


def is_quota_error(err: Exception) -> bool:
    if err is None:
        return False
    msg = str(err)
    return "429" in msg or "TooManyRequests" in msg


if __name__ == "__main__":
    main()
