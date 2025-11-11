from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np
import joblib
import traceback
import logging

# CONFIGURAÇÕES E LOGS
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

src_path = Path(__file__).parent.parent
model_path = src_path / "model" / "modelo_risco_viario_3.pkl"

app = FastAPI(
    title="API de Risco Viário",
    description="API para previsão de risco de acidentes de trânsito com base em coordenadas geográficas.",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  # inclui OPTIONS, GET, POST etc
    allow_headers=["*"],
)

# CARREGAMENTO DO MODELO
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


# SCHEMA DE ENTRADA
class InputFeatures(BaseModel):
    latitude: float
    longitude: float
    tp_veiculo_selecionado: str = Field(..., description="Tipo de veículo selecionado")


# ENDPOINT PRINCIPAL
@app.post("/calcular_risco")
async def calcular_risco(features: InputFeatures):
    if model is None:
        raise HTTPException(status_code=500, detail="Modelo não disponível no servidor.")

    try:
        # Conversão e enriquecimento temporal
        now = datetime.now()
        dia_semana = now.weekday()
        mes = now.month
        is_weekend = 1 if dia_semana >= 5 else 0
        hora_int = now.hour

        # Criação do DataFrame inicial
        input_data = {
            "latitude": features.latitude,
            "longitude": features.longitude,
            "dia_semana": dia_semana,
            "mes": mes,
            "is_weekend": is_weekend,
            "hora": hora_int,
            "Chuva": 0, # Valor padrão para teste
            "tipo_via_num": 0, # Valor padrão para teste
            "tp_veiculo_bicicleta": 0,
            "tp_veiculo_caminhao": 0,
            "tp_veiculo_motocicleta": 0,
            "tp_veiculo_nao_disponivel": 0,
            "tp_veiculo_onibus": 0,
            "tp_veiculo_outros": 0,
            "tp_veiculo_automovel": 0
        }

        # Ativa o veículo que o frontend enviou
        if features.tp_veiculo_selecionado in input_data:
            input_data[features.tp_veiculo_selecionado] = 1

        df_input = pd.DataFrame([input_data])

        # Adiciona colunas que o modelo espera mas não vieram do input
        for col in model_features:
            if col not in df_input.columns:
                df_input[col] = 0  # Adiciona a coluna com valor padrão 0

        # Garante a ordem exata das colunas e remove extras
        df_processed = df_input[model_features]
        df_processed = df_processed.astype(float)

        # Realiza a predição
        prob = model.predict_proba(df_processed[model_features])[:, 1]
        risco = float(prob[0])

        limiar = 0.45

        if risco >= limiar:
            interpretacao = "ALTO"
        elif risco >= 0.2:
            interpretacao = "MÉDIO"
        else:
            interpretacao = "BAIXO"

        return {
            "risco_estimado": risco,
            "interpretacao": interpretacao,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logging.error(f"Erro na predição: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

# ============================
# HEALTHCHECK (sem alterações)
# ============================
@app.get("/healthcheck")
def healthcheck():
    return {
        "status": "ok" if model else "erro",
        "modelo_carregado": model is not None,
        "features_esperadas": len(model_features)
    }