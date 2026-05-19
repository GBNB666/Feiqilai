from pathlib import Path
from app.config import settings
from app.services.ai_analyzer import analyze_paper_structure
from app.services.docx_processor import apply_formatting as format_docx
from app.services.pdf_processor import apply_formatting as format_pdf
from app.models.job import FormatJob, JobStatus


def run_formatting(job: FormatJob, custom_settings=None, enabled_settings=None) -> str:
    if not job.ai_analysis:
        structure = analyze_paper_structure(job.file_path, job.file_type)
        job.ai_analysis = str(structure)
    else:
        import ast
        try:
            data = ast.literal_eval(job.ai_analysis)
            if isinstance(data, dict) and "structure" in data:
                structure = data["structure"]
            else:
                structure = data
        except (ValueError, SyntaxError):
            import json
            try:
                data = json.loads(job.ai_analysis)
                if isinstance(data, dict) and "structure" in data:
                    structure = data["structure"]
                else:
                    structure = data
            except json.JSONDecodeError:
                structure = {}

    if job.format_mode == "manual" and job.user_annotations:
        import ast
        try:
            user_structure = ast.literal_eval(job.user_annotations)
            if "sections" in user_structure:
                structure = _merge_annotations(structure, user_structure)
        except (ValueError, SyntaxError):
            pass

    output_filename = f"formatted_{job.id}.{job.file_type}"
    output_path = str(Path(settings.output_dir) / output_filename)

    if job.file_type == "docx":
        format_docx(job.file_path, output_path, structure, custom_settings, enabled_settings)
    else:
        format_pdf(job.file_path, output_path, structure)

    job.output_path = output_path
    job.status = JobStatus.COMPLETED.value
    return output_path


def _merge_annotations(ai_structure: dict, user_structure: dict) -> dict:
    merged = ai_structure.copy()
    if "sections" in user_structure:
        merged["sections"] = user_structure["sections"]
    if "title" in user_structure and user_structure["title"]:
        merged["title"] = user_structure["title"]
    return merged
