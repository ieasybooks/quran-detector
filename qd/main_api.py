from fastapi import FastAPI, HTTPException
from matcher import QuranMatcherAnnotator
from schemas import AnnotateRequest, AnnotateResponse, MatchResponse

app = FastAPI(title="Quran Matcher API")

matcher = QuranMatcherAnnotator(
    index_file="../dfiles/quran-index.xml",
    ayat_file="../dfiles/quran-simple.txt",
    stops_file="../dfiles/nonTerminals.txt",
)


@app.get("/ping")
async def ping():
    """
    Health check endpoint.
    """
    return {"message": "pong"}


@app.post("/annotate", response_model=AnnotateResponse)
async def annotate_text(request: AnnotateRequest):
    """
    Annotates the input text by calling the matcher's annotate_text method.
    """
    try:
        annotated = matcher.annotate_text(request.text)
        return AnnotateResponse(annotated_text=annotated)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/match", response_model=MatchResponse)
async def match_text(request: AnnotateRequest):
    """
    Returns match records by calling the matcher's match_all method.
    The returned records should be a list of dictionaries that conform
    to the MatchRecord model.
    """
    try:
        records = matcher.match_all(request.text)
        return MatchResponse(records=records)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
