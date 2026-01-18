from google import genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.genai.errors import ClientError

class GeminiClient:
    """Handles interactions with the Google Gemini API using the new SDK."""

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API Key not provided.")
        
        self.client = genai.Client(api_key=api_key)
        # Reverting to the model we know works, and managing rate limits with retry
        self.model_name = "gemini-flash-latest"


    @retry(
        retry=retry_if_exception_type(ClientError),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        stop=stop_after_attempt(5),
        reraise=True
    )
    def generate_batch_questions(self, count: int = 20) -> list:
        """Generates a batch of quiz questions in JSON format."""
        prompt = (
            f"You are an Italian language tutor for a German speaker. "
            f"Generate {count} distinct quiz questions in german. "
            "Mix Translation questions and Multiple Choice Questions (A, B, C). "
            "Return a JSON LIST of objects. Each object must have this structure:\n"
            "{\n"
            '  "question": "The question text (including options if MCQ)",\n'
            '  "correct_answers": ["list", "of", "acceptable", "answers", "or", "A"/"B"/"C"],\n'
            '  "explanation": "Bilingual explanation (IT + DE) incase of error",\n'
            '  "keywords": ["key", "words", "related", "to", "topic"]\n'
            "}"
        )
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        import json
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            # Fallback or empty list on failure
            return []
