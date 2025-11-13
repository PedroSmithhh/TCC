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
# ATUALIZADO: Caminho para o modelo Random Forest salvo no notebook
model_path = src_path / "model" / "modelo_risco_viario_RF.pkl" 

app = FastAPI(
    title="API de Risco Viário (Random Forest)",
    description="API para previsão de risco de acidentes de trânsito com base em coordenadas geográficas, usando um modelo Random Forest.",
    version="1.2.0" # Versão atualizada
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CARREGAMENTO DO MODELO
try:
    model = joblib.load(model_path)
    model_features = []  # valor padrão

    # ATUALIZADO: Lógica para carregar features de modelos Scikit-learn (como RandomForest)
    # Modelos SKLearn treinados com DataFrames Pandas armazenam as features em 'feature_names_in_'
    
    if hasattr(model, "named_steps"):
        # Se for um Pipeline, tenta encontrar o estimador final
        try:
            # Pega o último passo do pipeline
            final_estimator_name = model.steps[-1][0]
            final_estimator = model.named_steps[final_estimator_name]
            
            if hasattr(final_estimator, "feature_names_in_"):
                model_features = list(final_estimator.feature_names_in_)
                logging.info(f"Modelo carregado (Pipeline, {len(model_features)} features detectadas no passo '{final_estimator_name}').")
            else:
                 logging.warning(f"Modelo carregado (Pipeline), mas o passo final '{final_estimator_name}' não possui 'feature_names_in_'.")

        except Exception as e:
             logging.error(f"Erro ao inspecionar pipeline: {e}")

    elif hasattr(model, "feature_names_in_"):
        # Se for um modelo puro (ex: RandomForestClassifier treinado diretamente)
        model_features = list(model.feature_names_in_)
        logging.info(f"Modelo SKLearn (RandomForest) carregado ({len(model_features)} features).")

    else:
        # Fallback se o modelo não tiver 'feature_names_in_' (ex: versões antigas do sklearn)
        logging.warning("Modelo carregado (tipo desconhecido, não foi possível extrair feature_names_in_).")


except Exception as e:
    logging.error(f"Falha ao carregar modelo: {e}")
    model = None
    model_features = []


# SCHEMA DE ENTRADA (sem alteração)
class InputFeatures(BaseModel):
    latitude: float
    longitude: float
    tp_veiculo_selecionado: str = Field(..., description="Tipo de veículo selecionado")


# ENDPOINT PRINCIPAL (lógica de predição mantida)
@app.post("/calcular_risco")
async def calcular_risco(features: InputFeatures):
    if model is None:
        raise HTTPException(status_code=500, detail="Modelo não disponível no servidor.")
        
    if not model_features:
        logging.error("O modelo foi carregado, mas a lista de 'model_features' está vazia. Verifique o artefato .pkl.")
        raise HTTPException(status_code=500, detail="Configuração de modelo inválida no servidor.")

    try:
        # Conversão e enriquecimento temporal (sem alteração)
        now = datetime.now()
        dia_semana = now.weekday()
        mes = now.month
        is_weekend = 1 if dia_semana >= 5 else 0
        hora_int = now.hour

        # Criação do DataFrame inicial (sem alteração)
        input_data = {
            "latitude": features.latitude,
            "longitude": features.longitude,
            "dia_semana": dia_semana,
            "mes": mes,
            "is_weekend": is_weekend,
            "hora": hora_int,
            "tp_veiculo_bicicleta": 0,
            "tp_veiculo_caminhao": 0,
            "tp_veiculo_motocicleta": 0,
            "tp_veiculo_nao_disponivel": 0,
            "tp_veiculo_onibus": 0,
            "tp_veiculo_outros": 0,
            "tp_veiculo_automovel": 0
            # NOTA: O 'random_forest.ipynb' mostra que 'tipo_via_num' e 'Chuva' 
            # foram usados no treino. A API antiga não os enviava.
            # A lógica abaixo (Feature Alignment) cuidará disso.
        }

        # Ativa o veículo que o frontend enviou (sem alteração)
        if features.tp_veiculo_selecionado in input_data:
            input_data[features.tp_veiculo_selecionado] = 1
        elif features.tp_veiculo_selecionado != "tp_veiculo_nao_disponivel":
            # Se o tipo de veículo enviado não for uma das colunas esperadas
            logging.warning(f"Tipo de veículo '{features.tp_veiculo_selecionado}' não é uma feature esperada. Usando 'nao_disponivel'.")
            input_data["tp_veiculo_nao_disponivel"] = 1


        df_input = pd.DataFrame([input_data])
        logging.info(f"Dados para predição: {df_input.to_dict()}")

        # Adiciona colunas que o modelo espera mas não vieram do input (sem alteração)
        # Isso é crucial, pois o RF espera 'Chuva' e 'tipo_via_num'
        for col in model_features:
            if col not in df_input.columns:
                df_input[col] = 0  # Adiciona a coluna com valor padrão 0 (ex: 'Chuva' = 0)

        # Garante a ordem exata das colunas e remove extras (sem alteração)
        df_processed = df_input[model_features]
        df_processed = df_processed.astype(float)

        # Realiza a predição (sem alteração)
        # RandomForestClassifier.predict_proba() também retorna [prob_0, prob_1]
        prob = model.predict_proba(df_processed[model_features])[:, 1]
        risco = float(prob[0])

        # Lógica de limiar
        limiar = 0.5

        if risco >= limiar:
            interpretacao = "ALTO"
        elif risco >= 0.3:
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
# HEALTHCHECK (sem alteração)
# ============================
@app.get("/healthcheck")
def healthcheck():
    return {
        "status": "ok" if model else "erro",
        "modelo_carregado": model is not None,
        "features_esperadas": len(model_features)
    }