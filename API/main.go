package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"strings"

	"github.com/joho/godotenv"
	"google.golang.org/genai"
)

func main() {
	if err := godotenv.Load(); err != nil {
		log.Fatal("Erro ao carregar o .env")
	}

	apiKey := os.Getenv("GEMINI_API_KEY")
	if apiKey == "" {
		log.Fatal("GEMINI_API_KEY não definida")
	}

	ctx := context.Background()

	client, err := genai.NewClient(ctx, &genai.ClientConfig{
		APIKey: apiKey,
	})
	if err != nil {
		log.Fatal(err)
	}

	prompt := "Faça uma breve apresentação"

	resposta, err := CallGeminiOrMock(ctx, client, prompt)
	if err != nil {
		log.Fatal(err)
	}

	fmt.Println("\nResposta:", resposta)
}

func CallGeminiOrMock(ctx context.Context, client *genai.Client, prompt string) (string, error) {
	resp, err := client.Models.GenerateContent(ctx, "gemini-2.0-flash", genai.Text(prompt), nil)

	if err != nil {
		if isQuotaError(err) {
			log.Println("\nN° maximo de Quota excedida")
			return MockGeminiResponse(prompt), nil
		}
		return "", fmt.Errorf("erro na API: %w", err)
	}

	if len(resp.Candidates) == 0 {
		return "", fmt.Errorf("a API retornou com sucesso entretanto nenhum conteúdo retornado")
	}

	return resp.Text(), nil
}

func MockGeminiResponse(input string) string {
	return "Resposta esperada: " + input
}

func isQuotaError(err error) bool {
	if err == nil {
		return false
	}
	return strings.Contains(err.Error(), "429") || strings.Contains(err.Error(), "TooManyRequests")
}
