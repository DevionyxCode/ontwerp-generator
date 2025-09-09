from fastapi import APIRouter, HTTPException
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# Importeer de DrawioUseCaseDiagramGenerator vanuit de juiste module
# Vervang 'jouw_module.drawio_generator' door het daadwerkelijke pad naar het bestand
from core.usecases.compiler import DrawioUseCaseDiagramGenerator
from core.usecases.userstorietousecase import userstories_to_usecase_json

router = APIRouter(tags=["USECASEDIAGRAM"])

class Actor(BaseModel):
    id: str
    name: str
    linked_actors: Optional[List[str]] = []

class UseCase(BaseModel):
    id: str
    name: str
    includes: Optional[List[str]] = []
    extend: Optional[List[str]] = []

class Relation(BaseModel):
    actor_id: str
    use_case_id: str

class UseCaseInput(BaseModel):
    system: str
    actors: List[Actor]
    use_cases: List[UseCase]
    relations: List[Relation]

@router.post("/generate", response_class=Response)
def generate_usecase_diagram(input_data: UseCaseInput):
    """
    Genereert een Draw.io XML-bestand voor een use-case diagram op basis van JSON-input.
    """
    try:
        usecase_generator = DrawioUseCaseDiagramGenerator()
        xml_output = usecase_generator.run(input_data.dict())

        return Response(
            content=xml_output,
            media_type="application/xml",
            headers={"Content-Disposition": "attachment; filename=use_case_diagram.drawio"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fout bij het genereren van het use-case diagram: {str(e)}")


class UserStoryInput(BaseModel):
    user_stories: List[Dict[str, Any]]
    system: str = "Schoolportaal"

@router.post("/compile_userstories")
def compile_userstories(input_data: UserStoryInput):
    """
    Zet een lijst van user stories om naar use-case JSON structuur.
    """
    try:
        result = userstories_to_usecase_json(input_data.user_stories, input_data.system)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fout bij compileren van user stories: {str(e)}")