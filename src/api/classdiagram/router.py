from fastapi import APIRouter, HTTPException
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel
from core.classdiagram.compiler import DrawioClassDiagramGenerator
from core.classdiagram.userstorietoclassdiagram import userstories_to_classdiagram
from typing import List, Dict

router = APIRouter(tags=["CLASSDIAGRAM"])

class UserStoryInput(BaseModel):
    data: List[Dict]  # JSON user stories


class classInput(BaseModel):
    data: Dict  # Verwacht nu een dict met 'classes' en 'relations'


@router.post("/generate", response_class=Response)
def generate_class(input_data: classInput):
    try:
        class_generator = DrawioClassDiagramGenerator()
        # De generator verwacht waarschijnlijk een JSON string
        xml_output = class_generator.run(json_data=input_data.data)

        return Response(
            content=xml_output,
            media_type="application/xml",
            headers={"Content-Disposition": "attachment; filename=class.drawio"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/userstorietoclassdiagram")
def compile_userstories(input_data: UserStoryInput):
    """
    Zet een lijst van user stories om naar use-case JSON structuur.
    """
    try:
        result = userstories_to_classdiagram(input_data.data)
        print(result)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fout bij compileren van user stories: {str(e)}")