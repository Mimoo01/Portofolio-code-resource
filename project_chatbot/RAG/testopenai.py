from openai import OpenAI

client = OpenAI(
    api_key= "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"
)

response = client.responses.create(
    model="gpt-5",
    input="Halo"
)

print(response.output_text)


