import os
import logging
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from dotenv import load_dotenv
from google import genai


SYSTEM_PROMPT = """
Você é um professor avaliador de código Java.

Você receberá um código Java feito por um aluno.

Sua tarefa é:
1. Corrigir o código Java.
2. Avaliar o código original do aluno.
3. Dar uma nota final de 0 a 10.
4. Explicar brevemente os erros encontrados.

Critérios de avaliação:

1. Compilação e sintaxe. Peso: 30%.
Avalie se o código compila corretamente.
Considere erros de chaves, ponto e vírgula, nomes incorretos, imports ausentes e estrutura da classe.

2. Lógica e funcionamento. Peso: 30%.
Avalie se o código resolve corretamente o problema proposto.
Considere cálculos, condições, laços, entrada de dados e saída esperada.

3. Organização e clareza. Peso: 20%.
Avalie indentação, nomes de variáveis, clareza, organização dos métodos e facilidade de leitura.

4. Boas práticas em Java. Peso: 10%.
Avalie uso correto de classes, métodos, tipos, Scanner, modificadores e estruturas da linguagem.

5. Tratamento de entrada e erros. Peso: 10%.
Avalie se o código trata entradas inválidas, casos extremos ou possíveis erros de execução.

Formato obrigatório da resposta:

NOTA_FINAL: número de 0 a 10

METRICAS:
- Compilação e sintaxe: nota de 0 a 10
- Lógica e funcionamento: nota de 0 a 10
- Organização e clareza: nota de 0 a 10
- Boas práticas em Java: nota de 0 a 10
- Tratamento de entrada e erros: nota de 0 a 10

JUSTIFICATIVA:
Explique de forma breve os principais erros encontrados no código original.

CODIGO_CORRIGIDO:
Coloque aqui somente o código Java corrigido.
Não use markdown.
Não use ```java.
"""
def selecionar_arquivo_java() -> str:#certinha
    janela = tk.Tk()
    janela.withdraw()

    caminho = filedialog.askopenfilename(
        title="Selecione o código Java do aluno",
        filetypes=[
            ("Arquivos Java", "*.java"),
            ("Todos os arquivos", "*.*"),
        ],
    )

    if not caminho:
        raise ValueError("Nenhum arquivo foi selecionado")

    return caminho


def selecionar_local_saida() -> str:
    janela = tk.Tk()
    janela.withdraw()

    caminho = filedialog.asksaveasfilename(
        title="Salvar avaliação como",
        defaultextension=".txt",
        filetypes=[
            ("Arquivo de texto", "*.txt"),
            ("Todos os arquivos", "*.*"),
        ],
    )

    if not caminho:
        raise ValueError("Nenhum local de saída foi selecionado")

    return caminho


def corrigir_codigo_java(
    client: genai.Client,
    caminho_entrada: str,
    enunciado: str = "",
    instrucao_extra: str | None = None
) -> str:
    codigo = Path(caminho_entrada).read_text(encoding="utf-8")

    prompt = f"""
Corrija e avalie o seguinte código Java.

Enunciado da atividade:
{enunciado or "O enunciado não foi informado. Avalie a lógica aparente do código."}

Instrução extra do usuário:
{instrucao_extra or "Corrija os erros necessários e avalie o código do aluno com base nas métricas definidas."}

Código do aluno:
{codigo}
"""

    resposta = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            SYSTEM_PROMPT,
            prompt,
        ],
    )

    return resposta.text.strip()


def is_quota_error(err: Exception) -> bool:
    if err is None:
        return False

    msg = str(err)
    return "429" in msg or "TooManyRequests" in msg


def mock_gemini_response(input_text: str) -> str:
    return "\nResposta esperada: " + input_text


def main():
    if not load_dotenv():
        raise RuntimeError("Erro ao carregar o .env")

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY não definida")

    client = genai.Client(api_key=api_key)

    caminho_entrada = selecionar_arquivo_java()
    caminho_saida = selecionar_local_saida()

    enunciado = input("Digite o enunciado da atividade: ").strip()

    arquivo_entrada = Path(caminho_entrada)

    if not arquivo_entrada.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {arquivo_entrada}")

    if arquivo_entrada.suffix != ".java":
        raise ValueError("O arquivo de entrada precisa ser .java")

    try:
        resposta = corrigir_codigo_java(
            client=client,
            caminho_entrada=caminho_entrada,
            enunciado=enunciado,
        )

    except Exception as e:
        if is_quota_error(e):
            logging.warning("\nO máximo de quota foi excedido")
            resposta = mock_gemini_response("Não foi possível chamar a API agora.")
        else:
            raise RuntimeError(f"Erro na API: {e}") from e

    Path(caminho_saida).write_text(resposta, encoding="utf-8")

    print("\nAvaliação gerada com sucesso.")
    print(f"Arquivo analisado: {caminho_entrada}")
    print(f"Resultado salvo em: {caminho_saida}")


if __name__ == "__main__":
    main()
