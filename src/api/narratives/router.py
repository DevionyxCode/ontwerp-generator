from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict
from io import BytesIO
from core.narratives.compiler import UseCaseDocGenerator  # jouw class

router = APIRouter(tags=["Narratives DOCX"])


class NarrativeInput(BaseModel):
    data: Dict  # JSON structuur van de use case / narratives


@router.post("/generate", response_class=StreamingResponse)
def generate_narrative_doc(input_data: NarrativeInput):
    try:
        # Maak de generator aan met de JSON data
        generator = UseCaseDocGenerator(input_data.data)
        doc_bytes = generator.generate_docx_bytes()

        # Return als DOCX download
        return StreamingResponse(
            BytesIO(doc_bytes),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": "attachment; filename=narrative.docx"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
