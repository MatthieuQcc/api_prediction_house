import streamlit as st
import requests

# ============= CONFIG =============

API_URL = "https://api-prediction-house.onrender.com"

st.set_page_config(
    page_title="Estimation Immobilier Toulouse",
    page_icon="🏠",
    layout="centered"
)

# ============= STYLE =============

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500&display=swap');

        html, body, [class*="css"] {
            font-family: 'DM Sans', sans-serif;
        }
        
        .main {
            background-color: #FAFAF8;
        }

        h1 {
            font-family: 'DM Serif Display', serif;
            font-size: 2.4rem !important;
            color: #1a1a1a;
            margin-bottom: 0.2rem !important;
        }
        
        .subtitle {
            color: #888;
            font-size: 1rem;
            margin-bottom: 2rem;
            font-weight: 300;
        }

        .divider {
            height: 2px;
            background: linear-gradient(to right, #1a1a1a, transparent);
            margin: 1.5rem 0;
        }

        .result-box {
            background: #1a1a1a;
            color: white;
            border-radius: 12px;
            padding: 2rem;
            text-align: center;
            margin-top: 1.5rem;
        }

        .result-label {
            font-size: 0.85rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: #999;
            margin-bottom: 0.5rem;
        }

        .result-price {
            font-family: 'DM Serif Display', serif;
            font-size: 3rem;
            color: white;
            letter-spacing: -1px;
        }

        .result-range {
            font-size: 0.85rem;
            color: #aaa;
            margin-top: 0.5rem;
        }

        .detail-pill {
            display: inline-block;
            background: #2d2d2d;
            color: #ccc;
            border-radius: 20px;
            padding: 4px 14px;
            font-size: 0.8rem;
            margin: 3px;
        }

        .stButton > button {
            background-color: #1a1a1a;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.75rem 2rem;
            font-family: 'DM Sans', sans-serif;
            font-size: 1rem;
            font-weight: 500;
            width: 100%;
            cursor: pointer;
            transition: background 0.2s;
        }

        .stButton > button:hover {
            background-color: #333;
        }

        .error-box {
            background: #fff0f0;
            border-left: 3px solid #e74c3c;
            padding: 1rem;
            border-radius: 4px;
            color: #c0392b;
            margin-top: 1rem;
        }

        /* Cacher le header Streamlit */
        #MainMenu, footer, header { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

# ============= HEADER =============

st.markdown("<h1>Estimer mon bien</h1>", unsafe_allow_html=True)
st.markdown('<p class="subtitle">Estimation instantanée basée sur les ventes à Toulouse</p>', unsafe_allow_html=True)
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ============= FORMULAIRE =============

col1, col2 = st.columns(2)

with col1:
    surface = st.number_input(
        "Surface Carrez (m²)",
        min_value=5.0,
        max_value=500.0,
        value=60.0,
        step=1.0
    )
    latitude = st.number_input(
        "Latitude",
        min_value=43.50,
        max_value=43.75,
        value=43.6047,
        step=0.0001,
        format="%.4f"
    )

with col2:
    pieces = st.number_input(
        "Nombre de pièces",
        min_value=1,
        max_value=20,
        value=3,
        step=1
    )
    longitude = st.number_input(
        "Longitude",
        min_value=1.25,
        max_value=1.65,
        value=1.4442,
        step=0.0001,
        format="%.4f"
    )

has_terrain = st.toggle("Le bien dispose d'un terrain")

st.markdown("<br>", unsafe_allow_html=True)

# ============= BOUTON & APPEL API =============

if st.button("Estimer le prix"):
    
    payload = {
        "lot1_surface_carrez": surface,
        "nombre_pieces_principales": pieces,
        "latitude": latitude,
        "longitude": longitude,
        "has_terrain": int(has_terrain)
    }
    
    with st.spinner("Calcul en cours..."):
        try:
            response = requests.post(f"{API_URL}/predict", json=payload, timeout=30)
            
            # HTTP response status code 200 means success
            if response.status_code == 200:
                data = response.json()
                
                prix = data['prix_predit']
                prix_min = data['prix_min']
                prix_max = data['prix_max']
                details = data['details']
                
                # Affichage du résultat
                st.markdown(f"""
                    <div class="result-box">
                        <div class="result-label">Estimation</div>
                        <div class="result-price">{prix:,.0f} €</div>
                        <div class="result-range">
                            Fourchette : {prix_min:,.0f} € — {prix_max:,.0f} €
                        </div>
                        <br>
                        <div>
                            <span class="detail-pill">📍 {details['metro_proche']}</span>
                            <span class="detail-pill">🚇 {details['distance_metro_km']} km du métro</span>
                            <span class="detail-pill">📐 {details['surface']} m²</span>
                            <span class="detail-pill">🚪 {details['pieces']} pièces</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            else:
                st.markdown(f"""
                    <div class="error-box">
                        ❌ Erreur serveur ({response.status_code}) : {response.text}
                    </div>
                """, unsafe_allow_html=True)
        
        except requests.exceptions.Timeout:
            st.markdown("""
                <div class="error-box">
                    ⏳ L'API met du temps à répondre (première requête après inactivité).<br>
                    Patientez 30 secondes et réessayez.
                </div>
            """, unsafe_allow_html=True)
        
        except requests.exceptions.ConnectionError:
            st.markdown("""
                <div class="error-box">
                    🔌 Impossible de joindre l'API. Vérifiez que l'URL Render est correcte.
                </div>
            """, unsafe_allow_html=True)

# ============= FOOTER =============

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<p class="subtitle" style="font-size:0.75rem; text-align:center;">Données DVF · Toulouse · Modèle XGBoost</p>', unsafe_allow_html=True)