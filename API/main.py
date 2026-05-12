import os
from dotenv import load_dotenv
from google import genai


def mock_gemini_response(user_input):
    return f"\nResposta esperada: {user_input}"


def is_quota_error(error):
    error_str = str(error)
    return "429" in error_str or "TooManyRequests" in error_str


def call_gemini_or_mock(client, prompt):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        if not response.text:
            raise Exception(
                "A API retornou com sucesso, entretanto nenhum conteúdo foi retornado"
            )

        return response.text

    except Exception as error:
        if is_quota_error(error):
            print("Quota máxima excedida")
            return mock_gemini_response(prompt)

        raise Exception(f"Erro na API: {error}")


def main():
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise Exception("GEMINI_API_KEY não definida")

    client = genai.Client(api_key=api_key)

    prompt = "Hoje é que dia?"

    resposta = call_gemini_or_mock(client, prompt)

    print("\nResposta:\n")
    print(resposta)


if __name__ == "__main__":
    main()