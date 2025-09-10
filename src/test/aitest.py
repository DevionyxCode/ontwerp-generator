from google import genai

client = genai.Client(
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Hoe werkt AI?"
)
print(response.text)
