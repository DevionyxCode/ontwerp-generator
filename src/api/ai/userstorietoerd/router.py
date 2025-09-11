from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from google import genai
from typing import List

router = APIRouter()

# Pydantic model voor de input
class StoryDetail(BaseModel):
    as_a: str
    i_want: str
    so_that: str

class UserStory(BaseModel):
    id: str
    title: str
    user_story: StoryDetail
    description: str
    acceptance_criteria: List[str]

class UserStoryInput(BaseModel):
    user_stories: List[UserStory]


@router.post("/userstorytoerd")
async def userstory_to_erd(
    input_data: UserStoryInput,
    authorization: str = Header(..., description="Bearer API Key")
):
    try:
        print("🔹 Endpoint /userstorytoerd aangeroepen")
        print(f"Ontvangen authorization header: {authorization}")
        print(f"Ontvangen user stories: {input_data.user_stories}")

        # Haal de API Key uit de Authorization header
        if not authorization.lower().startswith("bearer "):
            print("❌ Ongeldige authorization header")
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        api_key = authorization.split(" ")[1]
        print(f"✅ API key succesvol opgehaald: {api_key[:5]}***")

        # Initialiseer Gemini client met API Key
        print("🔹 Initialiseren van Gemini client...")
        client = genai.Client(api_key=api_key)
        print("✅ Gemini client geïnitialiseerd")

        # Prompt samenstellen
        prompt = f'''
        Je taak is om een lijst van user stories om te zetten naar een ERD in **zuiver JSON-formaat**.  
        ⚠️ Output moet **enkel JSON** zijn, zonder uitleg, zonder markdown, zonder ```json blokken.  

        Het formaat moet exact zo zijn:
        [
          {{
            "title": "TabelNaam",
            "fields": [
              {{"type": "PK", "name": "ID", "datatype": "INT", "not_null": true, "unique": true, "auto_increment": true}},
              {{"type": "FK", "name": "AndereTabelID", "datatype": "INT", "not_null": true, "unique": false, "references": {{"table": "AndereTabel", "field": "ID"}}}},
              {{"type": "", "name": "VeldNaam", "datatype": "VARCHAR(100)", "not_null": true}}
            ]
          }}
        ]

        Regels voor de AI:
        1. Gebruik **alle user stories** om de tabellen en relaties te bepalen.
        2. Zet PK en FK correct en beschrijf de referenties.
        3. Kies datatypes logisch op basis van het veld (string → VARCHAR, boolean → BOOLEAN, datum → DATE, enz.).
        4. Output moet altijd **een JSON-array** zijn, direct bruikbaar in code, zonder extra tekst.

        Hier zijn de user stories:
        {input_data.user_stories}
        '''

        print("🔹 Prompt samengesteld:")
        print(prompt)

        # Vraag aan Gemini
        print("🔹 Request sturen naar Gemini...")
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        print("✅ Response ontvangen van Gemini")
        print(f"Response tekst: {response.text}")

        return {"erd": response.text}

    except Exception as e:
        print(f"❌ Er trad een fout op: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
