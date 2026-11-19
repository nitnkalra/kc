"""Map free-text Excel categories to the 5 landing-page categories.

Matching order (case / punctuation insensitive):
  1. Exact canonical name or alias   e.g. "DevOps" -> Software Engineering & QA
  2. Keyword contained in the label  e.g. "Intro to Data Engineering" -> Data Engineering
  3. No match -> None (logged as warning, not counted on site)

To support a new label, add it to CATEGORY_ALIASES (or KEYWORDS).
"""

import re
from typing import Optional

DS_AI = "Data Science & AI"
DATA_ENG = "Data Engineering"
CLOUD = "Cloud & Low-Code"
SOFTWARE = "Software Engineering & QA"
BUSINESS = "Business & Communication"

SITE_CATEGORIES = [DS_AI, DATA_ENG, CLOUD, SOFTWARE, BUSINESS]

# Full-label aliases (exact match after normalisation)
CATEGORY_ALIASES = {
    DS_AI: [
        "Data Science", "DS", "AI", "Artificial Intelligence", "ML",
        "Machine Learning", "Deep Learning", "AI/ML", "GenAI", "Gen AI",
        "Generative AI", "LLM", "LLMs", "NLP", "Computer Vision", "CV",
        "RAG", "AI Agents", "Agentic AI", "Prompt Engineering", "MLOps",
        "Analytics", "Data Analytics", "Statistics",
    ],
    DATA_ENG: [
        "DE", "Data Eng", "Big Data", "ETL", "ELT", "Databricks", "Spark",
        "PySpark", "Delta Lake", "Lakehouse", "Data Warehouse",
        "Data Warehousing", "Data Governance", "Data Pipelines", "SQL",
        "Fabric", "Microsoft Fabric", "Azure Data Factory", "ADF",
        "Data Platform", "Streaming",
    ],
    CLOUD: [
        "Cloud", "Cloud Computing", "Azure", "AWS", "GCP", "Low Code",
        "No Code", "Power Platform", "Power Apps", "Power Automate",
        "Power BI", "Dynamics", "Dynamics 365", "Logic Apps", "CRM", "ERP",
        "SharePoint",
    ],
    SOFTWARE: [
        "Software Engineering", "Software Development", "Full Stack",
        "Full Stack Development", "Fullstack", "Frontend", "Front End",
        "Backend", "Back End", "Web Development", "Mobile Development",
        "App Development", "Flutter", "DevOps", "CI/CD", "CICD", "QA",
        "Testing", "Quality Assurance", "Automation Testing", "UI/UX", "UI",
        "UX", "Security", "Cyber Security", "Cybersecurity", "Networking",
        "API", "APIs", "Programming", "Python", "Coding",
    ],
    BUSINESS: [
        "Business", "Communication", "Soft Skills", "Leadership",
        "Management", "Project Management", "Product Management",
        "Supply Chain", "Demand Planning", "Finance", "KPI", "KPIs",
        "Presentation Skills", "Domain", "Consulting",
    ],
}

# Fallback: first keyword found inside the label wins (checked in order)
KEYWORDS = [
    ("data eng", DATA_ENG),
    ("data sci", DS_AI),
    ("machine learn", DS_AI),
    ("genai", DS_AI),
    ("gen ai", DS_AI),
    ("llm", DS_AI),
    ("devops", SOFTWARE),
    ("full stack", SOFTWARE),
    ("software", SOFTWARE),
    ("test", SOFTWARE),
    ("cloud", CLOUD),
    ("low code", CLOUD),
    ("power ", CLOUD),
    ("business", BUSINESS),
    ("communicat", BUSINESS),
]


def _normalise(label: str) -> str:
    """'CI/CD' -> 'ci cd', 'Data Science & AI' -> 'data science and ai'."""
    text = label.lower().replace("&", " and ")
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


_LOOKUP = {_normalise(c): c for c in SITE_CATEGORIES}
for _canonical, _aliases in CATEGORY_ALIASES.items():
    _LOOKUP.update({_normalise(a): _canonical for a in _aliases})


def map_category(label: str) -> Optional[str]:
    """Return one of SITE_CATEGORIES for a free-text label, or None."""
    key = _normalise(label)
    if not key:
        return None
    if key in _LOOKUP:
        return _LOOKUP[key]
    padded = f" {key} "
    for keyword, category in KEYWORDS:
        if keyword in padded:
            return category
    return None
