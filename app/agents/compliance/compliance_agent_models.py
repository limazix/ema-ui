from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# Input Schema for Compliance Agent
class ComplianceReportInput(BaseModel):
    fileName: str = Field(..., description="Name of the analyzed data file.")
    powerQualityDataSummary: str = Field(..., description="Summary of the power quality data.")
    identifiedRegulations: List[str] = Field(..., description="List of identified ANEEL regulations.")
    languageCode: str = Field("pt-BR", description="Language code for the report.")

# Output Schemas for Compliance Report
class ReportMetadata(BaseModel):
    title: str
    subtitle: Optional[str] = None
    author: str
    generatedDate: str  # YYYY-MM-DD

class BibliographyItem(BaseModel):
    text: str
    link: Optional[str] = None

class ReportSection(BaseModel):
    title: str
    content: str
    insights: List[str]
    relevantNormsCited: List[str]
    chartOrImageSuggestion: Optional[str] = None
    chartUrl: Optional[str] = None

class AnalyzeComplianceReportOutput(BaseModel):
    reportMetadata: ReportMetadata
    tableOfContents: List[str]
    introduction: Dict[str, str] # Could be more structured, but keeping it simple for now
    analysisSections: List[ReportSection]
    finalConsiderations: str
    bibliography: List[BibliographyItem]