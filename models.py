from typing import Optional

from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, PrimaryKeyConstraint
from database import Base


class CaseBreakdown(Base):
    __tablename__ = "CSAggregateSentinelSankey"

    source = Column(String, unique=False)
    target = Column(String, unique=False)
    metric = Column(Integer, unique=False)
    ord = Column(Integer, unique=False)
    County = Column(String, unique=False)
    SubCounty = Column(String, unique=False)
    Gender = Column(String, unique=False)
    AgencyName = Column(String, unique=False)
    PartnerName = Column(String, unique=False)
    CohortYearMonth = Column(String, unique=False)

    __table_args__ = (
        PrimaryKeyConstraint(
            'source', 'target', 'County', 'SubCounty', 'AgencyName', 'PartnerName', 'CohortYearMonth', 'Gender'
        ),
    )


class SankeyFilter(BaseModel):
    County: Optional[list] = None
    SubCounty: Optional[list] = None
    Agency: Optional[list] = None
    Partner: Optional[list] = None
    CohortYearMonthStart: Optional[str] = None
    CohortYearMonthEnd: Optional[str] = None
    Gender: Optional[list] = None


class SankeyBreakdown(BaseModel):
    node: str
    CohortYearMonthStart: Optional[str] = None
    CohortYearMonthEnd: Optional[str] = None
    County: Optional[list] = None
    SubCounty: Optional[list] = None
    Agency: Optional[list] = None
    Partner: Optional[list] = None
    Gender: Optional[list] = None
