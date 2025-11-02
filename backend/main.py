"""
FastAPI backend for scenario pre-production table generator.
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
from typing import Optional, List, Dict, Any
import uvicorn

from backend.document_parser import DocumentParser
try:
    from backend.scene_segmenter_v2 import SceneSegmenter
except ImportError:
    from backend.scene_segmenter import SceneSegmenter
try:
    from backend.element_extractor_v2 import ElementExtractor
except ImportError:
    from backend.element_extractor import ElementExtractor
from backend.table_generator import TableGenerator

app = FastAPI(title="Scenario Pre-Production Generator API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
parser = DocumentParser()
segmenter = SceneSegmenter()
extractor = ElementExtractor()
table_gen = TableGenerator()

# Create necessary directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)


# Pydantic models
class TableGenerationRequest(BaseModel):
    scenes_data: List[Dict[str, Any]]
    preset: Optional[str] = "basic"
    custom_columns: Optional[List[str]] = None


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Scenario Pre-Production Generator API", "status": "running"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and process a scenario file (PDF or DOCX).
    Returns scene segmentation and extracted elements.
    """
    try:
        # Validate file type
        if not (file.filename.endswith('.pdf') or file.filename.endswith('.docx')):
            raise HTTPException(status_code=400, detail="File must be PDF or DOCX format")
        
        # Save uploaded file
        file_path = f"uploads/{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Parse document
        text = parser.parse(file_path)
        
        # Segment scenes
        scenes = segmenter.segment(text)
        
        # Extract elements for each scene
        processed_scenes = []
        for scene in scenes:
            elements = extractor.extract_all(scene['text'])
            processed_scenes.append({
                'scene_number': scene['scene_number'],
                'text': scene['text'],
                **elements
            })
        
        return JSONResponse({
            "status": "success",
            "scenes": processed_scenes,
            "total_scenes": len(processed_scenes)
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@app.post("/generate-table")
async def generate_table(request: TableGenerationRequest):
    """
    Generate pre-production table from processed scenes.
    
    Args:
        request: TableGenerationRequest with scenes_data, preset, and custom_columns
    """
    try:
        table = table_gen.generate(
            request.scenes_data,
            preset=request.preset or "basic",
            custom_columns=request.custom_columns
        )
        
        return JSONResponse({
            "status": "success",
            "table": table.to_dict('records')
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Table generation error: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

