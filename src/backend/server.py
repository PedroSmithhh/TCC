from fastapi import FastAPI
import joblib
import pandas as pd
import numpy as np
from pydantic import BaseModel
from datetime import datetime
import traceback
from pathlib import Path

src_path = Path(__file__).parent.parent

# Carregar o modelo treinado
try:
    model = joblib.load(src_path / 'model' / 'modelo_risco_viario.pkl')
    model_features = model.get_booster().feature_names
except FileNotFoundError:
    print("ERRO CRÍTICO: Ficheiro 'modelo_risco_viario.pkl' não encontrado. A API não funcionará.")
    model = None
    model_features = []
except Exception as e:
    print(f"ERRO CRÍTICO ao carregar modelo: {e}")
    model = None
    model_features = []

app = FastAPI()

class InputFeatures(BaseModel):
    latitude: float
    longitude: float

@app.post("/calcular_risco")
async def calcular_risco(features: InputFeatures):
    if model is None:
        return {"erro": "Modelo não está disponível."}

    try:
        now = datetime.now()

        input_data = { ... }
        df_input = pd.DataFrame([input_data])

        df_processed  = pd.DataFrame(columns=model_features)
        df_processed = pd.concat([df_processed, df_input[df_input.columns.intersection(model_features)]], ignore_index=True)
        df_processed.fillna(0, inplace=True)

        # Fazer a previsão de probabilidade
        prob = model.predict_proba(df_processed[model_features])[: , 1]

        return {"risco": float(prob[0])}

    except Exception as e:
        print(f"Erro durante a previsão: {e}")
        traceback.print_exc()
        return {"error": "Erro no processamento", "risco": -1.0}
    
