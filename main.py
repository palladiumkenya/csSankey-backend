from pathlib import Path
from typing import Union
from sqlalchemy.sql import text
from fastapi import FastAPI, Depends, Request
from sqlalchemy import func
from starlette.middleware.cors import CORSMiddleware

from database import get_db
from sqlalchemy.orm import Session
from models import CaseBreakdown, SankeyFilter, SankeyBreakdown

import pandas as pd
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
# Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# app.mount("/{rest_of_path: path}/{rest_of_path2: path}", StaticFiles(directory="build", html=True), name="static")

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

    query = query.filter(CaseBreakdown.CohortYearMonth >= '2023-01-01')
    query = query.filter(CaseBreakdown.CohortYearMonth < '2024-01-01')

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


@app.post("/sankey-data/breakdown")
def sankey_data_breakdown(node: SankeyBreakdown, db: Session = Depends(get_db)):
    result = []  # List to hold multiple tables

    if node.node in ['Total Cases Reported', 'Linked', 'Not Linked']:
        # Table 1: Gender and LinkedToART
        query1 = 'SELECT Gender, SUM(LinkedToART) as number FROM CsSentinelEvents GROUP BY Gender;'
        data1 = db.execute(text(query1)).fetchall()

        result.append({
            "tableTitle": f"Gender Distribution for {node.node}",
            "columns": [
                {"field": "gender", "headerName": "Gender", "flex": 1, "minWidth": 100},
                {"field": "number", "headerName": "Number", "flex": 1, "minWidth": 100}
            ],
            "rows": [{"gender": row.Gender, "number": row.number} for row in data1]
        })
        print("here")
        # Table 2: Gender and Not Linked
        query2 = 'SELECT Gender, SUM(CASE WHEN LinkedToART = 0 THEN 1 ELSE 0 END) as number FROM CsSentinelEvents GROUP BY Gender;'
        data2 = db.execute(text(query2)).fetchall()
        result.append({
            "tableTitle": "Non-Linked Cases by Gender",
            "columns": [
                {"field": "gender", "headerName": "Gender", "flex": 1, "minWidth": 100},
                {"field": "number", "headerName": "Number", "flex": 1, "minWidth": 100}
            ],
            "rows": [{"gender": row.Gender, "number": row.number} for row in data2]
        })

        # Table 3: Patient Retention
        query3 = """
        SELECT 
            IIF(PatientRetained = 0, 'No', 'Yes') as patient_retained, 
            SUM(LinkedToART) as number 
        FROM CsSentinelEvents 
        GROUP BY PatientRetained;
        """
        data3 = db.execute(text(query3)).fetchall()
        result.append({
            "tableTitle": f"Patient Retention for {node.node}",
            "columns": [
                {"field": "patient_retained", "headerName": "Patient Retained", "flex": 1, "minWidth": 100},
                {"field": "number", "headerName": "Number", "flex": 1, "minWidth": 100}
            ],
            "rows": [{"patient_retained": row.patient_retained, "number": row.number} for row in data3]
        })

    elif node.node in ["Initial CD4 Not Done", "Initial CD4 Done", 'With AHD', 'Without AHD', 'Not Staged']:
        # Table 1: Patient Retained and Baseline CD4
        query1 = """
        SELECT 
            IIF(PatientRetained = 0, 'No', 'Yes') as patient_retained, 
            IIF(WithBaselineCD4 = 0, 'No', 'Yes') as with_baseline_cd4, 
            COUNT(WithBaselineCD4) as number 
        FROM CsSentinelEvents 
        GROUP BY PatientRetained, WithBaselineCD4;
        """
        data1 = db.execute(text(query1)).fetchall()
        result.append({
            "tableTitle": f"Patient Retention and Baseline CD4 for {node.node}",
            "columns": [
                {"field": "patient_retained", "headerName": "Patient Retained", "flex": 1, "minWidth": 100},
                {"field": "with_baseline_cd4", "headerName": "With Baseline CD4", "flex": 1, "minWidth": 100},
                {"field": "number", "headerName": "Number", "flex": 1, "minWidth": 100}
            ],
            "rows": [
                {
                    "patient_retained": row.patient_retained,
                    "with_baseline_cd4": row.with_baseline_cd4,
                    "number": row.number
                }
                for row in data1
            ]
        })

        # Table 2: WHO Stage and Gender
        query2 = """
        SELECT 
            WHOStageATART, 
            Gender, 
            SUM(LinkedToART) as number 
        FROM CsSentinelEvents 
        WHERE WHOStageATART > 0 
        GROUP BY WHOStageATART, Gender 
        ORDER BY WHOStageATART;
        """
        data2 = db.execute(text(query2)).fetchall()
        result.append({
            "tableTitle": f"WHO Stage Distribution by Gender for {node.node}",
            "columns": [
                { "field": "who_stage", "headerName": "WHO Stage", "flex": 1, "minWidth": 100 },
                { "field": "gender", "headerName": "Gender", "flex": 1, "minWidth": 100 },
                { "field": "number", "headerName": "Number", "flex": 1, "minWidth": 100 }
            ],
            "rows": [
                {
                    "who_stage": row.WHOStageATART,
                    "gender": row.Gender,
                    "number": row.number
                }
                for row in data2
            ]
        })

    return result



@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
