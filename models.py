from typing import Optional

from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, PrimaryKeyConstraint
from database import Base


class CaseBreakdown(Base):
    __tablename__ = "sentinel"

    source = Column(String, unique=False)
    target = Column(String, unique=False)
    metric = Column(Integer, unique=False)
    ord = Column(Integer, unique=False)
    County = Column(String, unique=False)
    SubCounty = Column(String, unique=False)
    Agency = Column(String, unique=False)
    Partner = Column(String, unique=False)
    CohortYearMonth = Column(String, unique=False)

    __table_args__ = (
        PrimaryKeyConstraint('source', 'target', 'County', 'SubCounty', 'Agency', 'Partner', 'CohortYearMonth'),
    )


class SankeyFilter(BaseModel):
    County: Optional[str] = None
    SubCounty: Optional[str] = None
    Agency: Optional[str] = None
    Partner: Optional[str] = None
    CohortYearMonthStart: Optional[str] = None
    CohortYearMonthEnd: Optional[str] = None


class SankeyBreakdown(BaseModel):
    node: str
    CohortYearMonthStart: Optional[str] = None
    CohortYearMonthEnd: Optional[str] = None
