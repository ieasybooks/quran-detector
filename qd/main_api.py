from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from qd.matcher import QuranMatcherAnnotator
from qd.schemas import AnnotateRequest, AnnotateResponse, MatchResponse

# Initialize FastAPI application
app = FastAPI(title="Quran Matcher API with Web Interface")

# Set up Jinja2 templates (templates are stored in the "templates" directory)
templates = Jinja2Templates(directory="templates")

# Mount static files (e.g., CSS) from the "static" directory
app.mount("/static", StaticFiles(directory="qd/static"), name="static")

# Initialize your matcher with the appropriate file paths
matcher = QuranMatcherAnnotator(
    index_file="dfiles/quran-index.xml",
    ayat_file="dfiles/quran-simple.txt",
    stops_file="dfiles/nonTerminals.txt",
)

# ---------------------------------------------
# API Endpoints
# ---------------------------------------------


@app.get("/ping")
async def ping():
    """Health-check endpoint."""
    return {"message": "pong"}


@app.post("/annotate", response_model=AnnotateResponse)
async def annotate_api(request_data: AnnotateRequest):
    """
    Annotates the input text by calling the matcher logic.
    Expects a JSON body with a "text" field.
    """
    try:
        annotated = matcher.annotate_text(request_data.text)
        return AnnotateResponse(annotated_text=annotated)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/match", response_model=MatchResponse)
async def match_api(request_data: AnnotateRequest):
    """
    Returns match records by calling the matcher logic.
    Expects a JSON body with a "text" field.
    """
    try:
        records = matcher.match_all(request_data.text)
        return MatchResponse(records=records)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------
# Web Interface Endpoints
# ---------------------------------------------


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serves the main HTML page with the form.
    The template (index.html) will display the form and any result.
    """
    return templates.TemplateResponse(
        "index.html", {"request": request, "result": None}
    )


@app.post("/web/annotate", response_class=HTMLResponse)
async def web_annotate(
    request: Request, text: str = Form(...), action: str = Form(...)
):
    """
    Handles form submissions from the web interface.
    Depending on the action ("annotate" or "match"), it calls the appropriate matcher method.
    """
    try:
        if action == "annotate":
            result = matcher.annotate_text(text)
        elif action == "match":
            records = matcher.match_all(text)
            # For display purposes, we convert the match records to a string.
            result = str(records)
        else:
            result = "Unknown action"
    except Exception as e:
        result = f"Error: {e}"
    return templates.TemplateResponse(
        "index.html", {"request": request, "result": result}
    )
