from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import json
from fastapi.responses import Response
import io
import xlsxwriter

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define the 18 classes
CLASSES = [
    "Salle 2", "Salle 5", "Salle 6", "Salle 7", "Salle 8", "Salle 9", 
    "Salle 10", "Salle 11", "Salle 12", "Salle 13", "Salle 14", "Salle 16", "Salle 18",
    "Nuage", "Soleil", "Arc-en-ciel", "Lune", "Étoile"
]

# Absence Model
class Absence(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    classe: str
    date: str  # DD/MM/YYYY format
    nom: str
    prenom: str
    motif: str  # M, RDV, F, A
    justifie: str  # O, N
    remarques: Optional[str] = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AbsenceCreate(BaseModel):
    classe: str
    date: str
    nom: str
    prenom: str
    motif: str
    justifie: str
    remarques: Optional[str] = ""

class AbsenceStats(BaseModel):
    classe: str
    total_absences: int
    absences_non_justifiees: int
    absences_recentes: int  # last 7 days

# Helper function to validate date format DD/MM/YYYY
def validate_french_date(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, "%d/%m/%Y")
        return True
    except ValueError:
        return False

# Helper function to prepare data for MongoDB (convert datetime to ISO string)
def prepare_for_mongo(data):
    if isinstance(data.get('created_at'), datetime):
        data['created_at'] = data['created_at'].isoformat()
    return data

# Helper function to parse data from MongoDB (convert ISO string back to datetime)
def parse_from_mongo(item):
    if isinstance(item.get('created_at'), str):
        try:
            item['created_at'] = datetime.fromisoformat(item['created_at'])
        except:
            item['created_at'] = datetime.now(timezone.utc)
    return item

# Routes
@api_router.get("/")
async def root():
    return {"message": "API du Suivi des Absences Scolaires"}

@api_router.get("/classes")
async def get_classes():
    return {"classes": CLASSES}

@api_router.post("/absences", response_model=Absence)
async def create_absence(absence_data: AbsenceCreate):
    # Validate inputs
    if absence_data.classe not in CLASSES:
        raise HTTPException(status_code=400, detail="Classe non valide")
    
    if not validate_french_date(absence_data.date):
        raise HTTPException(status_code=400, detail="Format de date invalide. Utilisez DD/MM/YYYY")
    
    if absence_data.motif not in ["M", "RDV", "F", "A"]:
        raise HTTPException(status_code=400, detail="Motif invalide")
    
    if absence_data.justifie not in ["O", "N"]:
        raise HTTPException(status_code=400, detail="Valeur de justification invalide")
    
    # Create absence
    absence = Absence(**absence_data.dict())
    absence_dict = prepare_for_mongo(absence.dict())
    await db.absences.insert_one(absence_dict)
    
    return absence

@api_router.get("/absences", response_model=List[Absence])
async def get_absences(classe: Optional[str] = None):
    query = {}
    if classe and classe in CLASSES:
        query["classe"] = classe
    
    absences = await db.absences.find(query).sort("created_at", -1).to_list(1000)
    return [Absence(**parse_from_mongo(absence)) for absence in absences]

@api_router.delete("/absences/{absence_id}")
async def delete_absence(absence_id: str):
    result = await db.absences.delete_one({"id": absence_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Absence non trouvée")
    return {"message": "Absence supprimée avec succès"}

@api_router.get("/stats", response_model=List[AbsenceStats])
async def get_statistics():
    stats = []
    
    # Calculate date 7 days ago
    seven_days_ago = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    seven_days_ago = seven_days_ago.replace(day=seven_days_ago.day - 7)
    
    for classe in CLASSES:
        # Total absences for this class
        total = await db.absences.count_documents({"classe": classe})
        
        # Unjustified absences
        unjustified = await db.absences.count_documents({"classe": classe, "justifie": "N"})
        
        # Recent absences (last 7 days)
        recent = await db.absences.count_documents({
            "classe": classe,
            "created_at": {"$gte": seven_days_ago.isoformat()}
        })
        
        stats.append(AbsenceStats(
            classe=classe,
            total_absences=total,
            absences_non_justifiees=unjustified,
            absences_recentes=recent
        ))
    
    return stats

@api_router.get("/export/excel")
async def export_excel(classe: Optional[str] = None):
    # Create Excel file in memory
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    
    # Add formats
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#366092',
        'font_color': 'white',
        'border': 1
    })
    
    unjustified_format = workbook.add_format({
        'bg_color': '#ffcccc',
        'border': 1
    })
    
    normal_format = workbook.add_format({'border': 1})
    
    if classe and classe in CLASSES:
        # Export single class
        absences = await db.absences.find({"classe": classe}).sort("date", -1).to_list(1000)
        worksheet = workbook.add_worksheet(classe)
        
        # Headers
        headers = ['Date', 'Nom', 'Prénom', 'Motif', 'Justifié', 'Remarques']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # Data
        for row, absence in enumerate(absences, 1):
            format_to_use = unjustified_format if absence.get('justifie') == 'N' else normal_format
            worksheet.write(row, 0, absence.get('date', ''), format_to_use)
            worksheet.write(row, 1, absence.get('nom', ''), format_to_use)
            worksheet.write(row, 2, absence.get('prenom', ''), format_to_use)
            worksheet.write(row, 3, absence.get('motif', ''), format_to_use)
            worksheet.write(row, 4, absence.get('justifie', ''), format_to_use)
            worksheet.write(row, 5, absence.get('remarques', ''), format_to_use)
        
        worksheet.autofit()
        
    else:
        # Export all classes - create summary sheet first
        summary_sheet = workbook.add_worksheet('Résumé')
        summary_headers = ['Classe', 'Total Absences', 'Non Justifiées', 'Absences Récentes']
        for col, header in enumerate(summary_headers):
            summary_sheet.write(0, col, header, header_format)
        
        # Get stats for summary
        stats = await get_statistics()
        for row, stat in enumerate(stats, 1):
            summary_sheet.write(row, 0, stat.classe, normal_format)
            summary_sheet.write(row, 1, stat.total_absences, normal_format)
            summary_sheet.write(row, 2, stat.absences_non_justifiees, unjustified_format if stat.absences_non_justifiees > 0 else normal_format)
            summary_sheet.write(row, 3, stat.absences_recentes, normal_format)
        
        summary_sheet.autofit()
        
        # Create sheet for each class
        for classe_name in CLASSES:
            absences = await db.absences.find({"classe": classe_name}).sort("date", -1).to_list(1000)
            if absences:  # Only create sheet if there are absences
                worksheet = workbook.add_worksheet(classe_name)
                
                # Headers
                headers = ['Date', 'Nom', 'Prénom', 'Motif', 'Justifié', 'Remarques']
                for col, header in enumerate(headers):
                    worksheet.write(0, col, header, header_format)
                
                # Data
                for row, absence in enumerate(absences, 1):
                    format_to_use = unjustified_format if absence.get('justifie') == 'N' else normal_format
                    worksheet.write(row, 0, absence.get('date', ''), format_to_use)
                    worksheet.write(row, 1, absence.get('nom', ''), format_to_use)
                    worksheet.write(row, 2, absence.get('prenom', ''), format_to_use)
                    worksheet.write(row, 3, absence.get('motif', ''), format_to_use)
                    worksheet.write(row, 4, absence.get('justifie', ''), format_to_use)
                    worksheet.write(row, 5, absence.get('remarques', ''), format_to_use)
                
                worksheet.autofit()
    
    workbook.close()
    output.seek(0)
    
    filename = f"absences_{classe}.xlsx" if classe else "absences_toutes_classes.xlsx"
    
    return Response(
        content=output.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()