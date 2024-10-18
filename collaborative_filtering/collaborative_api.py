from flask import Flask, request, jsonify
import joblib
import numpy as np
from flask_cors import CORS
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

# Inicializar o Flask
app = Flask(__name__)
CORS(app)

# Carregar o modelo salvo, incluindo os vectorizers
model_path = '/Users/viniciuslunardifarias/projects/ufsc/tcc/collaborative_filtering/collaborative_filtering_model.joblib'  # Caminho do seu arquivo
model_data = joblib.load(model_path)

# Recuperar os dados do modelo
tfidf_matrices = model_data['tfidf_matrices']
feature_weights = model_data['feature_weights']
df = model_data['df']
features = model_data['features']
tfidf_vectorizers = model_data['tfidf_vectorizers']  # Carrega os vectorizers originais para cada feature

# Função para preencher as features faltantes no novo usuário
def fill_missing_features(new_user_data):
    # Para cada feature no modelo, verificar se está presente no input
    for feature in features:
        if feature not in new_user_data:
            # Preencher com valor padrão: 0 para binários e '' para texto
            if df[feature].dtype == 'object':
                new_user_data[feature] = ''
            else:
                new_user_data[feature] = 0
    return new_user_data

# Função para calcular a similaridade do novo usuário
def calculate_new_user_similarity(new_user_data):
    total_similarity = np.zeros(df.shape[0])  # Inicializa similaridade total

    # Loop sobre cada feature e calcular a similaridade
    for feature in features:
        if df[feature].dtype == 'object':  # Para colunas de texto
            new_user_text = [new_user_data[feature]] 
            vectorizer = tfidf_vectorizers[feature]  # Pega o vectorizer específico para a feature

            new_user_vector = vectorizer.transform(new_user_text)  # Usar o vectorizer original para transformar
            cosine_sim = cosine_similarity(new_user_vector, tfidf_matrices[feature])
        else:  # Para colunas binárias
            new_user_value = np.array(new_user_data[feature]).reshape(1, -1)  # Converter em matriz 2D
            feature_matrix = tfidf_matrices[feature].reshape(-1, 1)  # Garantir que a matriz também seja 2D
            cosine_sim = cosine_similarity(new_user_value, feature_matrix).flatten()

        cosine_sim = cosine_sim.flatten()  # Achatar para 1D para uso subsequente

        # Aplicar os pesos nas features
        total_similarity += cosine_sim * feature_weights[feature]

    return total_similarity

# Função para recomendar métricas com base em perfis similares
def recommend_metrics_for_new_user(new_user_data, top_n=20, min_similarity=0.2):
    total_similarity = calculate_new_user_similarity(new_user_data)

    # Filtrar perfis com similaridade mínima
    sim_scores = [(i, score) for i, score in enumerate(total_similarity) if score >= min_similarity]

    # Ordenar por similaridade (maior -> menor)
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Verificar se há perfis com similaridade suficiente
    if len(sim_scores) == 0:
        return {"message": "Nenhum perfil encontrado com similaridade suficiente."}, 200

    # Selecionar os top_n perfis mais semelhantes
    top_sim_scores = sim_scores[:top_n]

    # Calcular a soma total das similaridades para calcular a porcentagem
    total_affinity = sum([score for _, score in top_sim_scores])

    # Retornar as métricas e a porcentagem de afinidade
    recommended_metrics = []
    for i, score in top_sim_scores:
        metric = df['sanitized_metrics'].iloc[i]
        affinity_percentage = (score / total_affinity) * 100  # Calcular a porcentagem de afinidade
        recommended_metrics.append({
            "metric": metric,
            "affinity_percentage": round(affinity_percentage, 2),
            "similar_profile_index": i
        })

    return recommended_metrics

# Rota para recomendar métricas
@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        # Receber as features do usuário
        user_data = request.json.get('features')

        if not user_data:
            return jsonify({"error": "Dados de usuário não fornecidos"}), 400

        # Preencher valores faltantes com valores padrão
        user_data = fill_missing_features(user_data)

        # Recomendar métricas para o novo usuário
        recommended_metrics = recommend_metrics_for_new_user(user_data, top_n=5)

        # Retornar as métricas recomendadas
        return jsonify({"recommended_metrics": recommended_metrics}), 200

    except Exception as e:
        print(f"Erro: {e}")
        return jsonify({"error": str(e)}), 500

# Inicializar o servidor Flask
if __name__ == '__main__':
    app.run(debug=True)
