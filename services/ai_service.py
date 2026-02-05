from google import genai

MODEL_NAME = "gemini-3-flash-preview"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "") # овој АПИ клуч го добиваме од гемини

def generate_text(prompt: str) -> str:
    # ова е функцијата којашто ќе ја користиме за да добиеме notes и description со помош на AI
    api_key = GEMINI_API_KEY

    if not api_key:
        return "GEMINI_API_KEY недостасува или е погрешен"

    client = genai.Client(api_key=api_key) # креираме гемини клиент којшто ни овозможува комуникација со нивното АПИ

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )  # генерираме контент, имаме два клучни аргументи - име на моделот, промпт
        return (response.text or "").strip() or "Нема резултат од AI (празен текст)."
    except Exception as e:
        return f"AI грешка: {e}"
