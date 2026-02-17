import streamlit as st
import requests
from streamlit_folium import st_folium
import folium

# ============= CONFIG =============

API_URL = "https://api-prediction-house.onrender.com"

# Centre de Toulouse par défaut
DEFAULT_LAT = 43.6047
DEFAULT_LON = 1.4442

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

        .info-box {
            background: #f0f4ff;
            border-left: 3px solid #3498db;
            padding: 0.75rem 1rem;
            border-radius: 4px;
            color: #2c3e50;
            font-size: 0.9rem;
            margin: 0.5rem 0 1rem 0;
        }

        #MainMenu, footer, header { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

# ============= FONCTIONS =============

def geocode_address(address: str):
    """Convertit une adresse en coordonnées GPS via Nominatim (OpenStreetMap, gratuit)."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": f"{address}, Toulouse, France",
        "format": "json",
        "limit": 1
    }
    headers = {"User-Agent": "ImmoToulouseApp/1.0"}
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        results = response.json()
        if results:
            return float(results[0]["lat"]), float(results[0]["lon"]), results[0]["display_name"]
        return None, None, None
    except Exception:
        return None, None, None


def create_map(lat, lon):
    """Crée une carte Folium centrée sur les coordonnées données."""
    m = folium.Map(
        location=[lat, lon],
        zoom_start=14,
        tiles="CartoDB positron"
    )
    folium.Marker(
        location=[lat, lon],
        popup="📍 Localisation du bien",
        icon=folium.Icon(color="black", icon="home", prefix="fa")
    ).add_to(m)
    return m


# ============= ÉTAT SESSION =============

if "lat" not in st.session_state:
    st.session_state.lat = DEFAULT_LAT
if "lon" not in st.session_state:
    st.session_state.lon = DEFAULT_LON
if "adresse_affichee" not in st.session_state:
    st.session_state.adresse_affichee = ""

# ============= HEADER =============

st.markdown("<h1>Estimer mon bien</h1>", unsafe_allow_html=True)
st.markdown('<p class="subtitle">Estimation instantanée basée sur les ventes à Toulouse</p>', unsafe_allow_html=True)
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ============= RECHERCHE ADRESSE =============

st.markdown("**📍 Localisation du bien**")

col_input, col_btn = st.columns([3, 1])

with col_input:
    adresse = st.text_input(
        "Adresse",
        placeholder="Ex : 12 rue Saint-Rome",
        label_visibility="collapsed"
    )

with col_btn:
    rechercher = st.button("Rechercher", use_container_width=True)

if rechercher and adresse:
    with st.spinner("Recherche de l'adresse..."):
        lat, lon, display_name = geocode_address(adresse)
    
    if lat and lon:
        st.session_state.lat = lat
        st.session_state.lon = lon
        st.session_state.adresse_affichee = display_name
        st.success(f"✅ {display_name}")
    else:
        st.markdown("""
            <div class="error-box">
                ❌ Adresse introuvable. Essayez avec plus de détails (numéro + rue).
            </div>
        """, unsafe_allow_html=True)

if st.session_state.adresse_affichee and not rechercher:
    st.success(f"✅ {st.session_state.adresse_affichee}")

# ============= CARTE =============

st.markdown('<div class="info-box">🖱️ Ou cliquez directement sur la carte pour placer le bien</div>', unsafe_allow_html=True)

m = create_map(st.session_state.lat, st.session_state.lon)
map_data = st_folium(m, height=350, width=None, returned_objects=["last_clicked"])

# Mettre à jour les coordonnées si l'utilisateur clique sur la carte
if map_data and map_data.get("last_clicked"):
    st.session_state.lat = map_data["last_clicked"]["lat"]
    st.session_state.lon = map_data["last_clicked"]["lng"]
    st.session_state.adresse_affichee = ""

st.caption(f"Coordonnées sélectionnées : {st.session_state.lat:.4f}, {st.session_state.lon:.4f}")

# ============= FORMULAIRE =============

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown("**🏠 Caractéristiques du bien**")

col1, col2 = st.columns(2)

with col1:
    surface = st.number_input(
        "Surface Carrez (m²)",
        min_value=5.0,
        max_value=500.0,
        value=60.0,
        step=1.0
    )

with col2:
    pieces = st.number_input(
        "Nombre de pièces",
        min_value=1,
        max_value=20,
        value=3,
        step=1
    )

has_terrain = st.toggle("Le bien dispose d'un terrain")

st.markdown("<br>", unsafe_allow_html=True)

# ============= BOUTON & APPEL API =============

if st.button("✦ Estimer le prix"):
    
    payload = {
        "lot1_surface_carrez": surface,
        "nombre_pieces_principales": pieces,
        "latitude": st.session_state.lat,
        "longitude": st.session_state.lon,
        "has_terrain": int(has_terrain)
    }
    
    with st.spinner("Calcul en cours..."):
        try:
            response = requests.post(f"{API_URL}/predict", json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                prix = data['prix_predit']
                prix_min = data['prix_min']
                prix_max = data['prix_max']
                details = data['details']
                
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