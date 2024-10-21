from flask import Flask, request, jsonify
import numpy as np
import pandas as pd
import joblib
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def recomendar_metricas_com_afinidade(category_probabilities, category_to_metrics, threshold):
    recommendations = {}

    for user_idx, category_affinities in category_probabilities.items():
        user_recommendations = []
        for categoria, afinidade in category_affinities.items():
            if categoria in category_to_metrics and afinidade >= threshold:
                for metrica in category_to_metrics[categoria]:
                    if pd.notna(metrica):
                        user_recommendations.append({'metric': metrica, 'affinity': afinidade, 'category': categoria})

        user_recommendations.sort(key=lambda x: x['affinity'], reverse=True)
        recommendations[user_idx] = user_recommendations

    return recommendations

def process_user_input(user_data):
    user_df = pd.DataFrame([user_data])
    column_structure = joblib.load('column_structure.joblib')

    # Adicionar as colunas faltantes no user_df e preencher com 0
    missing_cols = set(column_structure) - set(user_df.columns)
    for col in missing_cols:
        user_df[col] = 0

    years_exp_col = f"years_exp_{user_data.get('years_exp', '')}"
    org_size_col = f"org_size_{user_data.get('org_size', '')}"
    role_col = f"role_{user_data.get('role', '')}"

    if years_exp_col in user_df.columns:
        user_df[years_exp_col] = 1

    if org_size_col in user_df.columns:
        user_df[org_size_col] = 1

    if role_col in user_df.columns:
        user_df[role_col] = 1

     # Mapear os métodos ágeis para o formato esperado
    agile_methods_map = {
        "agile_methods_scrum": "Scrum",
        "agile_methods_kanban": "Kanban",
        "agile_methods_lean": "Lean",
        "agile_methods_xp": "XP",
        "agile_methods_safe": "Safe",
        "agile_methods_scrumban": "ScrumBan"
    }

    for api_key, model_col in agile_methods_map.items():
        if api_key in user_data and model_col in user_df.columns:
            user_df[model_col] = user_data[api_key]

    # Reordenar as colunas para garantir a mesma ordem do treino
    user_df = user_df[column_structure].copy()

    categories = ['Cronograma e progresso', 'Produto', 'Processo', 'Tecnologia', 'Pessoas', 'Cliente']
    user_df = user_df.drop(columns=categories, errors='ignore').copy()
    

    user_df.to_excel('test.xlsx')   

    return user_df

def classify_user(categories, category_probabilities, user_df):
    for category in categories:
        model_filename = f"modelo_{category}_ajustado.joblib"
        rf_binary = joblib.load(model_filename)

        user_affinities = rf_binary.predict_proba(user_df)[:, 1]

        for user_idx, affinity in enumerate(user_affinities):
            category_probabilities[user_idx][category] = affinity


@app.route('/recommend_metrics_content', methods=['POST'])
def api_recommend_metrics():
    try:
        # Obter o threshold da requisição ou usar o padrão de 0.5
        threshold = request.json.get('threshold', 0.5)

        # Processar a entrada do usuário
        user_data = request.json
        user_df = process_user_input(user_data)

        # Inicializar as variáveis para armazenar as probabilidades de afinidade
        category_probabilities = {user_idx: {} for user_idx in range(len(user_df))}
        metrics_data = pd.read_excel('extracted_metrics.xlsx', sheet_name="Extracted metrics")

        # Criar cópias dos dados críticos
        metrics_data = metrics_data.copy()
        category_to_metrics = metrics_data.groupby('Translation')['Metric Name'].apply(list).to_dict()

        categories = ['Cronograma e progresso', 'Produto', 'Processo', 'Tecnologia', 'Pessoas', 'Cliente']
        classify_user(categories, category_probabilities, user_df)

        # Obter recomendações de métricas com base nas afinidades
        metric_recommendations_with_affinity = recomendar_metricas_com_afinidade(
            category_probabilities, category_to_metrics, threshold
        )

        # Preparar a resposta com as recomendações e o threshold usado
        response = {
            'threshold': threshold,
            'metric_recommendations': metric_recommendations_with_affinity
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
