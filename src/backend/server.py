from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime
from pathlib import Path
import pandas as pd
import geopandas as gpd
import numpy as np
import joblib
import traceback
import logging
from sklearn.preprocessing import MinMaxScaler

# ============================
# CONFIGURAÇÕES E LOGS
# ============================
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

src_path = Path(__file__).parent.parent
model_path = src_path / "model" / "modelo_risco_viario2.pkl"

app = FastAPI(
    title="API de Risco Viário",
    description="API para previsão de risco de acidentes de trânsito com base em coordenadas geográficas.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ou ['http://localhost:8080'] para ser mais seguro
    allow_credentials=True,
    allow_methods=["*"],  # inclui OPTIONS, GET, POST etc
    allow_headers=["*"],
)

# ============================
# CARREGAMENTO DO MODELO
# ============================
try:
    model = joblib.load(model_path)

    model_features = []  # valor padrão

    # Se o modelo for um pipeline, tenta acessar o estimador final (ex: XGBClassifier)
    if hasattr(model, "named_steps"):
        for name, step in model.named_steps.items():
            if hasattr(step, "get_booster"):
                booster = step.get_booster()
                model_features = booster.feature_names or []
                break

        logging.info(f"Modelo carregado (Pipeline, {len(model_features)} features detectadas).")

    # Se for um XGBoost puro
    elif hasattr(model, "get_booster"):
        booster = model.get_booster()
        model_features = booster.feature_names or []
        logging.info(f"Modelo XGBoost carregado ({len(model_features)} features).")

    else:
        logging.info("Modelo carregado (outro tipo, sem feature_names).")

except Exception as e:
    logging.error(f"Falha ao carregar modelo: {e}")
    model = None
    model_features = []



# ============================
# SCHEMA DE ENTRADA
# ============================
class InputFeatures(BaseModel):
    latitude: str = Field(..., description="Latitude (pode conter vírgula)")
    longitude: str = Field(..., description="Longitude (pode conter vírgula)")
    data: str = Field(..., description="Data no formato YYYY-MM-DD")
    hora: int = Field(..., ge=0, le=23)
    chuva: int = Field(..., ge=0, le=1)
    tipo_via_num: int = Field(..., ge=0)
    tp_veiculo_bicicleta: int = Field(..., ge=0)
    tp_veiculo_caminhao: int = Field(..., ge=0)
    tp_veiculo_motocicleta: int = Field(..., ge=0)
    tp_veiculo_nao_disponivel: int = Field(..., ge=0)
    tp_veiculo_onibus: int = Field(..., ge=0)
    tp_veiculo_outros: int = Field(..., ge=0)
    tp_veiculo_automovel: int = Field(..., ge=0)

# ============================
# FUNÇÃO DE PRÉ-PROCESSAMENTO
# ============================
def preprocess_input(df: pd.DataFrame) -> pd.DataFrame:
    try:
        # Substitui vírgula por ponto e tenta converter para float
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].str.replace(',', '.', regex=False)
                try:
                    df[col] = df[col].astype(float)
                except:
                    pass

        # Remove coordenadas inválidas
        df.loc[df['latitude'] <= -90, 'latitude'] = np.nan
        df.loc[df['longitude'] <= -180, 'longitude'] = np.nan
        df = df[df['latitude'].notna() & df['longitude'].notna()]

        # Cria GeoDataFrame e projeta para UTM (Bauru — zona 23S)
        gdf = gpd.GeoDataFrame(
            df,
            geometry=gpd.points_from_xy(df.longitude, df.latitude),
            crs="EPSG:4326"
        ).to_crs("EPSG:32723")

        # Extrai coordenadas X/Y em metros
        df['x_coord'] = gdf.geometry.x
        df['y_coord'] = gdf.geometry.y

        # Normaliza com MinMaxScaler
        scaler = MinMaxScaler()
        df[['x_coord', 'y_coord']] = scaler.fit_transform(df[['x_coord', 'y_coord']])

        return df

    except Exception as e:
        logging.error(f"Erro no pré-processamento: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Erro durante o pré-processamento dos dados.")

# ============================
# ENDPOINT PRINCIPAL
# ============================
@app.post("/calcular_risco")
async def calcular_risco(features: InputFeatures):
    if model is None:
        raise HTTPException(status_code=500, detail="Modelo não disponível no servidor.")

    try:
        # Conversão e enriquecimento temporal
        data = datetime.strptime(features.data, "%Y-%m-%d")
        dia_semana = data.weekday()
        mes = data.month
        is_weekend = 1 if dia_semana >= 5 else 0

        # Criação do DataFrame inicial
        df_input = pd.DataFrame([{
            "latitude": features.latitude,
            "longitude": features.longitude,
            "data": features.data,
            "dia_semana": dia_semana,
            "mes": mes,
            "is_weekend": is_weekend,
            "hora": features.hora,
            "Chuva": features.chuva,
            "tipo_via_num": features.tipo_via_num,
            "tp_veiculo_bicicleta": features.tp_veiculo_bicicleta,
            "tp_veiculo_caminhao": features.tp_veiculo_caminhao,
            "tp_veiculo_motocicleta": features.tp_veiculo_motocicleta,
            "tp_veiculo_nao_disponivel": features.tp_veiculo_nao_disponivel,
            "tp_veiculo_onibus": features.tp_veiculo_onibus,
            "tp_veiculo_outros": features.tp_veiculo_outros,
            "tp_veiculo_automovel": features.tp_veiculo_automovel
        }])

        # Aplica o mesmo pré-processamento do modelo
        df_processed = preprocess_input(df_input)

        # Ajusta as colunas para o modelo
        if model_features:
            df_processed = df_processed.reindex(columns=model_features, fill_value=0)


        # Realiza a predição
        prob = model.predict_proba(df_processed)[:, 1]
        risco = float(prob[0])

        return {
            "risco_estimado": risco,
            "interpretacao": "ALTO" if risco >= 0.6 else "MÉDIO" if risco >= 0.3 else "BAIXO",
            "timestamp": datetime.now().isoformat(),
            "entrada_processada": df_processed.to_dict(orient="records")[0]
        }

    except Exception as e:
        logging.error(f"Erro na predição: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

# ============================
# HEALTHCHECK
# ============================
@app.get("/healthcheck")
def healthcheck():
    return {
        "status": "ok" if model else "erro",
        "modelo_carregado": model is not None,
        "features_esperadas": len(model_features)
    }
