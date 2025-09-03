from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List, Dict, Any

# Importeer de DrawioUseCaseDiagramGenerator vanuit de juiste module
# Vervang 'jouw_module.drawio_generator' door het daadwerkelijke pad naar het bestand
from jouw_module.drawio_generator import DrawioUseCaseDiagramGenerator

router = APIRouter(tags=["USECASEDIAGRAM"])

class UseCaseInput(BaseModel):
    system: str
    actors: List[Dict[str, str]]
    use_cases: List[Dict[str, Any]]
    relations: List[Dict[str, str]]

@router.post("/usecase-diagram/generate", response_class=Response)
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