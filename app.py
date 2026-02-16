from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import joblib
import pandas as pd
import numpy as np
from typing import Optional
from math import radians, sin, cos, asin, sqrt
import uvicorn

# ============= CONSTANTES =============

STATIONS_TOULOUSE = {
    # Ligne A
    "Balma-Gramont": (43.62971164231746, 1.4831444388334585),
    "Argoulets": (43.62439184264503, 1.4768072274086192), 
    "Roseraie": (43.619870148945814, 1.4693228826532732),
    "Jolimont": (43.61538472316486, 1.4636057521703651),
    "Marengo – SNCF": (43.61072986498919, 1.4550073139327766),
    "Jean Jaurès": (43.60585995727777, 1.4491864712489415),
    "Capitole": (43.60419516166457, 1.4449659097167153),
    "Esquirol": (43.60030772301489, 1.4441848939899071),  
    "Saint-Cyprien – République": (43.597832326764525, 1.4317676052962165),
    "Patte d'Oie": (43.59630560148399, 1.4233691391055898),
    "Arènes": (43.59336285730645, 1.418306789899077),  
    "Fontaine-Lestang": (43.58751549085796, 1.4183833603785048),
    "Mermoz": (43.58345482990229, 1.4153180750828234),  
    "Bagatelle": (43.579898082395694, 1.4119812195216574),
    "Mirail – Université": (43.574814562246765, 1.402110554498417),
    "Reynerie": (43.57071434748996, 1.4019491169204168),  
    "Bellefontaine": (43.56609357794097, 1.398335491324841),
    "Basso Cambo": (43.57002423377021, 1.3922718601581425),
    # Ligne B
    "Borderouge": (43.64097358525123, 1.452298505170243),
    "Trois Cocus": (43.6382946007621, 1.4440672462982207),
    "La Vache": (43.633626034149714, 1.4349464413809196),
    "Barrière de Paris": (43.62661607705671, 1.4337725625189777),
    "Minimes": (43.62057375762567, 1.4358736943998551),
    "Canal du Midi": (43.61535261294454, 1.4337298761297568),
    "Compans-Caffarelli": (43.61067018931617, 1.4357931429011612),
    "Jeanne d'Arc": (43.608577144508914, 1.4457416228090167),
    "François Verdier": (43.6004629288437, 1.452297507755522),
    "Carmes": (43.597852135960615, 1.4454169016576714),
    "Palais de Justice": (43.59220811162977, 1.444592987028543),
    "Saint-Michel Marcel-Langer": (43.58604790672622, 1.4471783419698658),
    "Empalot": (43.57991639870424, 1.442075253939026),
    "Saint-Agne SNCF": (43.57970775512508, 1.450212702539849),
    "Saouzelong": (43.579494535801096, 1.4593810546013988),
    "Rangueil": (43.57481310670238, 1.4619417649912032),
    "Faculté de Pharmacie": (43.56803581915576, 1.4645477034498953),
    "Université-Paul-Sabatier": (43.56074285864322, 1.4624382220957395),
    "Ramonville": (43.55571867873419, 1.4757832659295467)
}

# ============= FONCTIONS MÉTRO =============

def haversine(lat1, lon1, lat2, lon2):
    """Calcule la distance en kilomètres entre deux coordonnées GPS."""
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # rayon de la Terre en km
    return c * r

def get_nearest_metro(lat, lon):
    """Trouve la station de métro la plus proche et sa distance."""
    min_dist = np.inf
    nearest_name = None
    for name, coords in STATIONS_TOULOUSE.items():
        d = haversine(lat, lon, coords[0], coords[1])
        if d < min_dist:
            min_dist = d
            nearest_name = name
    return min_dist, nearest_name

# ============= INITIALISATION =============

app = FastAPI(
    title="API Prédiction Prix Immobilier Toulouse",
    description="Prédiction de prix basée sur XGBoost",
    version="1.0.0"
)

# Charger le modèle
try:
    model = joblib.load('model.pkl')
    metadata = joblib.load('metadata.pkl')
    print("✅ Modèle chargé avec succès")
except Exception as e:
    print(f"❌ Erreur chargement modèle: {e}")
    model = None
    metadata = None

# ============= SCHÉMAS =============

class BienImmobilier(BaseModel):
    """Données d'entrée pour la prédiction"""
    lot1_surface_carrez: float = Field(..., gt=0, description="Surface Carrez en m²")
    nombre_pieces_principales: int = Field(..., ge=1, description="Nombre de pièces principales")
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")
    has_terrain: int = Field(0, ge=0, le=1, description="Présence d'un terrain (0 ou 1)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "lot1_surface_carrez": 75.0,
                "nombre_pieces_principales": 3,
                "latitude": 43.6047,
                "longitude": 1.4442,
                "has_terrain": 0
            }
        }

class PredictionResponse(BaseModel):
    """Réponse de prédiction"""
    prix_predit: float
    prix_min: float
    prix_max: float
    details: dict

# ============= ROUTES =============

@app.get("/")
def root():
    """Page d'accueil de l'API"""
    return {
        "message": "🏠 API Prédiction Prix Immobilier Toulouse",
        "status": "online",
        "model_type": metadata.get('model_type') if metadata else "unknown",
        "endpoints": {
            "predict": "/predict",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
def health_check():
    """Vérification santé de l'API"""
    if model is None or metadata is None:
        raise HTTPException(status_code=503, detail="Modèle non chargé")
    
    return {
        "status": "healthy",
        "model_loaded": True,
        "model_type": metadata.get('model_type'),
        "test_mae": metadata.get('test_mae'),
        "test_r2": metadata.get('test_r2')
    }

@app.post("/predict", response_model=PredictionResponse)
def predict_price(bien: BienImmobilier):
    """
    Prédire le prix d'un bien immobilier
    
    Calcule automatiquement la distance au métro le plus proche
    """
    if model is None or metadata is None:
        raise HTTPException(status_code=503, detail="Modèle non disponible")
    
    try:
        # 1️⃣ CALCULER LES FEATURES CUSTOM (métro)
        nearest_distance, nearest_name = get_nearest_metro(
            bien.latitude, 
            bien.longitude
        )
        
        # 2️⃣ CRÉER LE DATAFRAME AVEC TOUTES LES FEATURES
        input_data = pd.DataFrame([{
            'lot1_surface_carrez': bien.lot1_surface_carrez,
            'nombre_pieces_principales': bien.nombre_pieces_principales,
            'latitude': bien.latitude,
            'longitude': bien.longitude,
            'has_terrain': bien.has_terrain,
            'nearest_metro_distance_km': nearest_distance,
            'nearest_metro_name': nearest_name
        }])
        
        # 3️⃣ PRÉDICTION (le pipeline applique StandardScaler + OneHotEncoder + XGBoost)
        prediction = model.predict(input_data)[0]
        
        # 4️⃣ INTERVALLE DE CONFIANCE
        mae = metadata.get('test_mae', 35590)
        prix_min = max(0, prediction - mae)
        prix_max = prediction + mae
        
        return PredictionResponse(
            prix_predit=round(prediction, 2),
            prix_min=round(prix_min, 2),
            prix_max=round(prix_max, 2),
            details={
                "surface": bien.lot1_surface_carrez,
                "pieces": bien.nombre_pieces_principales,
                "metro_proche": nearest_name,
                "distance_metro_km": round(nearest_distance, 2),
                "has_terrain": bool(bien.has_terrain)
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur de prédiction: {str(e)}"
        )

@app.post("/predict_batch")
def predict_batch(biens: list[BienImmobilier]):
    """Prédire plusieurs biens (max 100)"""
    if len(biens) > 100:
        raise HTTPException(status_code=400, detail="Max 100 biens par requête")
    
    results = []
    for bien in biens:
        try:
            prediction = predict_price(bien)
            results.append({
                "input": bien.dict(),
                "prediction": prediction.dict()
            })
        except Exception as e:
            results.append({
                "input": bien.dict(),
                "error": str(e)
            })
    
    return {"results": results, "count": len(results)}

# ============= RUN LOCAL =============

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)