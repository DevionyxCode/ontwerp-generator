from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from google import genai
from typing import List

router = APIRouter()

# Pydantic model voor de input
class ERDInput(BaseModel):
    erd_json: List[dict]

@router.post("/erdtoclassdiagram")
async def erd_to_classdiagram(
    input_data: ERDInput,
    authorization: str = Header(..., description="Bearer API Key")
):
    try:
        # Haal de API Key uit de Authorization header
        if not authorization.lower().startswith("bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        api_key = authorization.split(" ")[1]

        # Initialiseer Gemini client met API Key
        client = genai.Client(api_key=api_key)

        # Prompt samenstellen
        prompt = f'''
Je taak is om een ERD om te zetten naar een volledig classediagram in het volgende JSON-formaat:

{{
  "classes": [
    {{"id": "C1", "name": "ClassNaam", "attributes": ["attribuut: type", "..."], "methods": ["methode()","..."]}},
    ...
  ],
  "relations": [
    {{"from": "C1", "to": "C2", "type": "relatietype"}},
    ...
  ]
}}

Regels voor de AI:
1. Gebruik **alle classes en relaties uit de ERD** om een volledig classediagram te maken.
2. Mogelijke relatie-types zijn:
   - association
   - aggregation
   - composition
   - Inheritance
   - implementation
   - dependency
3. Kies het relatietype correct op basis van de ERD-relaties.
4. Output moet correct JSON-formaat zijn zoals hierboven, zodat het direct in een Word-document geplakt kan worden.

Hier is de ERD input die gebruikt moet worden:
{input_data.erd_json}
'''

        # Vraag aan Gemini
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return {"class_diagram": response.text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
