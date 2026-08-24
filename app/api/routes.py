from __future__ import annotations

import time
import uuid
from pathlib import Path

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from fastapi.responses import FileResponse

from app.config import OUTPUT_DIR, UPLOAD_DIR
from app.services.excel_generator import ExcelGenerator
from app.services.ocr_service import ocr_service
from app.services.document_parser import DocumentParser
from app.services.word_generator import WordGenerator
from app.utils.file_utils import (
    create_safe_filename,
    validate_extension,
    validate_file_size,
)


router = APIRouter()


@router.get("/health")
def health():

    return {
        "status": "ok",
        "service": "PaddleOCR Document Extractor",
    }


@router.post("/extract")
async def extract_document(
    file: UploadFile = File(...),
    output_format: str = Form("both"),
):

    start_time = time.perf_counter()

    output_format = output_format.lower().strip()

    if output_format not in {
        "xlsx",
        "docx",
        "both",
    }:

        raise HTTPException(
            status_code=400,
            detail=(
                "output_format must be "
                "'xlsx', 'docx' or 'both'."
            ),
        )

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    try:

        extension = validate_extension(
            file.filename
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    file_bytes = await file.read()

    try:

        validate_file_size(
            len(file_bytes)
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=413,
            detail=str(exc),
        )

    unique_name = create_safe_filename(
        file.filename
    )

    input_path = UPLOAD_DIR / unique_name

    input_path.write_bytes(file_bytes)

    try:

        # -----------------------------------------------
        # OCR
        # -----------------------------------------------

        results = ocr_service.process(
            input_path
        )

        # -----------------------------------------------
        # STRUCTURE
        # -----------------------------------------------

        document_data = (
            DocumentParser.parse_results(
                results
            )
        )

        base_name = (
            Path(file.filename).stem
        )

        job_id = uuid.uuid4().hex

        generated_files = []

        # -----------------------------------------------
        # XLSX
        # -----------------------------------------------

        if output_format in {
            "xlsx",
            "both",
        }:

            xlsx_name = (
                f"{base_name}_{job_id}.xlsx"
            )

            xlsx_path = OUTPUT_DIR / xlsx_name

            ExcelGenerator.generate(
                document_data,
                xlsx_path,
            )

            generated_files.append({
                "format": "xlsx",
                "filename": xlsx_name,
                "download_url": (
                    f"/api/download/{xlsx_name}"
                ),
            })

        # -----------------------------------------------
        # DOCX
        # -----------------------------------------------

        if output_format in {
            "docx",
            "both",
        }:

            docx_name = (
                f"{base_name}_{job_id}.docx"
            )

            docx_path = OUTPUT_DIR / docx_name

            WordGenerator.generate(
                document_data,
                docx_path,
            )

            generated_files.append({
                "format": "docx",
                "filename": docx_name,
                "download_url": (
                    f"/api/download/{docx_name}"
                ),
            })

        elapsed = time.perf_counter() - start_time

        return {
            "success": True,
            "input_file": file.filename,
            "page_count": document_data[
                "page_count"
            ],
            "processing_time_seconds": round(
                elapsed,
                3,
            ),
            "files": generated_files,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"OCR processing failed: {exc}",
        )

    finally:

        # Remove temporary input file.
        try:
            input_path.unlink(
                missing_ok=True
            )
        except Exception:
            pass


@router.get("/download/{filename}")
def download_file(filename: str):

    path = OUTPUT_DIR / filename

    if not path.exists():

        raise HTTPException(
            status_code=404,
            detail="Output file not found.",
        )

    return FileResponse(
        path=path,
        filename=path.name,
    )