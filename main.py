from fastapi import FastAPI, Depends
from sqlalchemy import func
from starlette.middleware.cors import CORSMiddleware

from database import SessionLocal, engine, get_db
from sqlalchemy.orm import Session
from models import CaseBreakdown, SankeyFilter, Base
import models
import pandas as pd

app = FastAPI()
# Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/sankey-data/")
def get_sankey_data(filters: SankeyFilter, db: Session = Depends(get_db)):
    query = db.query(
        CaseBreakdown.source,
        CaseBreakdown.target,
        func.sum(CaseBreakdown.metric).label('total_metric')
    )

    if filters.County:
        query = query.filter(CaseBreakdown.County == filters.County)
    if filters.SubCounty:
        query = query.filter(CaseBreakdown.SubCounty == filters.SubCounty)
    if filters.Agency:
        query = query.filter(CaseBreakdown.Agency == filters.Agency)
    if filters.Partner:
        query = query.filter(CaseBreakdown.Partner == filters.Partner)
    if filters.CohortYearMonth:
        query = query.filter(CaseBreakdown.CohortYearMonth == filters.CohortYearMonth)

    query = query.group_by(CaseBreakdown.source, CaseBreakdown.target)
    data = query.all()

    df = pd.DataFrame([{
        'source': d.source,
        'target': d.target,
        'metric': d.total_metric
    } for d in data])

    print(df['source'].tolist().index(row['source']) for _, row in df.iterrows())
    # Transforming the data for Highcharts Sankey
    sankey_data = [
        {"from": record.source, "to": record.target, "weight": record.total_metric}
        for record in data
    ]

    return {"sankeyData": sankey_data}


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
