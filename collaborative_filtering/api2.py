from flask import Flask, request, jsonify
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib

app = Flask(__name__)

# Carregar o modelo salvo
model_data = joblib.load('collaborative_filtering.joblib')
df = model_data['df']
tfidf_matrices = model_data['tfidf_matrices']
features = model_data['features']
feature_weights_default = model_data['feature_weights']
tfidf_vectorizers = model_data['tfidf_vectorizers']  # Carregando os vetorizadores TF-IDF

# Função para processar e adicionar o perfil do usuário ao dataframe
def add_user_to_dataframe(user_profile):
    # Criar uma nova linha com os valores do perfil do usuário
    user_data = {}
    
    for feature in features:
        if feature in user_profile:
            user_data[feature] = user_profile[feature]
        else:
            user_data[feature] = np.nan  # Para colunas faltantes, preencher com NaN

    # Adicionar o perfil do usuário ao dataframe como uma nova linha
    user_df = pd.DataFrame([user_data])
    return pd.concat([df, user_df], ignore_index=True)

# Função para calcular a similaridade total ponderada entre o usuário e os perfis existentes
def calculate_total_similarity(df_with_user, user_index, feature_weights=None):
    total_similarity = np.zeros(df_with_user.shape[0])  # Inicializa a similaridade total

    # Usar pesos padrão se não forem fornecidos
    if feature_weights is None:
        feature_weights = feature_weights_default

    # Calcular a similaridade de cosseno para cada feature
    for feature in features:
        if df_with_user[feature].dtype == 'object':
            tfidf_vectorizer = tfidf_vectorizers[feature]
            tfidf_matrix = tfidf_vectorizer.transform(df_with_user[feature].fillna(''))
            cosine_sim = cosine_similarity(tfidf_matrix[user_index], tfidf_matrix).flatten()
        else:
            # Similaridade para colunas binárias
            binary_matrix = df_with_user[feature].fillna(0).values.reshape(-1, 1)
            cosine_sim = cosine_similarity([binary_matrix[user_index]], binary_matrix).flatten()

            # Amplificar o peso se a feature binária for 1
            if df_with_user[feature].iloc[user_index] == 1:
                feature_weights[feature] = feature_weights.get(feature, 1.0) * 2.0

        total_similarity += cosine_sim * feature_weights.get(feature, 1.0)

    return total_similarity

# Função para recomendar métricas com base em perfis similares
def recommend_metrics(user_profile, top_n=5, feature_weights=None):
    # Adicionar o perfil do usuário ao dataframe
    df_with_user = add_user_to_dataframe(user_profile)

    # O índice do usuário será a última linha do dataframe
    user_index = len(df_with_user) - 1

    # Calcular a similaridade total usando o dataframe com o usuário
    total_similarity = calculate_total_similarity(df_with_user, user_index, feature_weights)

    # Excluir o próprio perfil do usuário dos resultados
    total_similarity[user_index] = -1

    # Obter os índices dos perfis mais similares
    similar_indices = total_similarity.argsort()[-top_n:][::-1]
    similar_profiles = df_with_user.iloc[similar_indices]
    similar_affinity = total_similarity[similar_indices]

    recommended_metrics = []

    # Recomendar métricas dos perfis mais similares
    for idx, metrics in enumerate(similar_profiles['sanitized_metrics']):
        if metrics not in [rec['metric'] for rec in recommended_metrics]:
            affinity = similar_affinity[idx]
            recommended_metrics.append({
                "metric": metrics,
                "affinity": float(affinity),  # Converter para float nativo do Python
                "similar_profile_index": int(similar_indices[idx])  # Converter para int nativo do Python
            })

        if len(recommended_metrics) == top_n:
            break

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

    # Retornar recomendações em formato JSON
    return jsonify(recommendations), 200

if __name__ == '__main__':
    app.run(debug=True)
