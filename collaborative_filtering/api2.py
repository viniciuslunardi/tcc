from flask import Flask, request, jsonify
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


model_data = joblib.load('/Users/viniciuslunardifarias/projects/ufsc/tcc/collaborative_filtering/collaborative_filtering.joblib')

df = model_data['df']
tfidf_matrices = model_data['tfidf_matrices']
features = model_data['features']
feature_weights_default = model_data['feature_weights']
tfidf_vectorizers = model_data['tfidf_vectorizers'] 


# Função para processar e adicionar o perfil do usuário ao dataframe
def add_user_to_dataframe(user_profile):
    user_data = {feature: user_profile.get(feature, np.nan) for feature in features}
    user_df = pd.DataFrame([user_data])
    return pd.concat([df, user_df], ignore_index=True)


# Função para calcular a similaridade total ponderada entre o usuário e os perfis existentes
def calculate_total_similarity(df_with_user, user_index, feature_weights=None):
    total_similarity = np.zeros(df_with_user.shape[0])  # Reinicializa a similaridade total

    if feature_weights is None:
        feature_weights = feature_weights_default.copy()  # Reiniciar pesos padrão

    for feature in features:
        if df_with_user[feature].dtype == 'object':
            tfidf_vectorizer = tfidf_vectorizers[feature]
            tfidf_matrix = tfidf_vectorizer.transform(df_with_user[feature].fillna(''))
            cosine_sim = cosine_similarity(tfidf_matrix[user_index], tfidf_matrix).flatten()
        else:
            binary_matrix = df_with_user[feature].fillna(0).values.reshape(-1, 1)
            cosine_sim = cosine_similarity([binary_matrix[user_index]], binary_matrix).flatten()

            # Amplificar o peso se a feature binária for 1
            if df_with_user[feature].iloc[user_index] == 1:
                feature_weights[feature] = feature_weights.get(feature, 1.0) * 2.0

        total_similarity += cosine_sim * feature_weights.get(feature, 1.0)
    return total_similarity


# Função para recomendar métricas com base em perfis similares
def recommend_metrics(user_profile, top_n=5, feature_weights=None):
    df_with_user = add_user_to_dataframe(user_profile)
    user_index = len(df_with_user) - 1

    total_similarity = calculate_total_similarity(df_with_user, user_index, feature_weights)
    total_similarity[user_index] = -1  # Excluir o próprio usuário da recomendação

    similar_indices = total_similarity.argsort()[-top_n:][::-1]
    similar_profiles = df_with_user.iloc[similar_indices]
    similar_affinity = total_similarity[similar_indices]

    recommended_metrics = []

    for idx, metrics in enumerate(similar_profiles['sanitized_metrics']):
        if metrics not in [rec['metric'] for rec in recommended_metrics]:
            affinity = similar_affinity[idx]
            affinity = min(affinity, 100)  # Limitar afinidade a 100

            # Obter o valor de 'id_integer' do perfil similar
            id_integer_value = similar_profiles.iloc[idx]['id_integer']

            recommended_metrics.append({
                "metric": metrics,
                "affinity": float(affinity),
                "similar_profile_index": int(id_integer_value)  # Retornar o 'id_integer' correto
            })

        if len(recommended_metrics) == top_n:
            break

    # Remover o usuário adicionado temporariamente
    df_with_user = df_with_user.drop(user_index).reset_index(drop=True)

    return recommended_metrics


# Endpoint para recomendar métricas
@app.route('/recommend_metrics', methods=['POST'])
def api_recommend_metrics():
    data = request.json

    # Validar se o perfil do usuário foi fornecido corretamente
    required_fields = ['role', 'years_exp', 'org_size', 'use_metrics_planning', 'use_metrics_review', 
                       'use_metrics_weekly', 'use_metrics_daily', 'use_metrics_retro'] + \
                      [f'agile_methods_{method.lower()}' for method in ['Scrum', 'Kanban', 'Scrumban', 'XP', 'Safe', 'Lean']] + \
                      [f'metrics_category_{category.lower().replace(" ", "_")}' for category in ['Cronograma e progresso', 'Produto', 'Processo', 'Tecnologia', 'Pessoas', 'Cliente']]
    
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    # Definir o perfil do usuário a partir do JSON recebido
    user_profile = {field: data[field] for field in required_fields}

    # Verificar se feature_weights foram fornecidos ou usar padrão
    feature_weights = data.get('feature_weights', None)

    # Obter as métricas recomendadas
    recommendations = recommend_metrics(user_profile, top_n=data.get('top_n', 5), feature_weights=feature_weights)

    return jsonify(recommendations), 200

if __name__ == '__main__':
    app.run(debug=True)
