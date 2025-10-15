from google import genai
from django.conf import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

def generate_questions(text_content):

    prompt = f"""Generate 5 quiz questions with answers from this text:
    {text_content}

    Format each as:
    Q: [question]
    A: [answer]
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    # Parse response
    parts = response.text.split("Q: ")
    qa_pairs = []

    for part in parts:
        if "A: " in part:
            question_and_answer = part.split("A: ")
            question = question_and_answer[0].strip()
            answer = question_and_answer[1].strip()
            qa_pairs.append({'question': question, 'answer': answer})

    return qa_pairs
