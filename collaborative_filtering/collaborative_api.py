from flask import Flask, request, jsonify
from flask_cors import CORS  # Import Flask-CORS
import joblib
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# Inicializar o Flask
app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas as rotas

# Carregar os modelos salvos
vectorizer = joblib.load('tfidf_vectorizer_for_recommendation.joblib')
svd = joblib.load('svd_model_for_recommendation.joblib')
X_svd_transformed = joblib.load('svd_transformed_data_for_recommendation.joblib')

# Carregar o dataset para as recomendações
df = pd.read_excel('ready_for_filtering.xlsx')
df.fillna('', inplace=True)

# Função para recomendar métricas para um novo usuário
def recommend_metrics_for_new_user(new_user_data, vectorizer, svd, X_svd_transformed, df, top_n=5, min_similarity=0.2):
    # Vetorizar o novo perfil usando o mesmo TF-IDF vectorizer
    new_user_tfidf = vectorizer.transform([new_user_data])
    
    # Reduzir dimensionalidade com SVD
    new_user_svd = svd.transform(new_user_tfidf)
    
    # Calcular a similaridade entre o novo perfil e todos os perfis existentes
    cosine_sim_new_user = cosine_similarity(new_user_svd, X_svd_transformed).flatten()
    
    # Filtrar por similaridade mínima
    sim_scores = [(i, score) for i, score in enumerate(cosine_sim_new_user) if score >= min_similarity]
    
    # Ordenar por similaridade (maior -> menor)
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # Verificar se há perfis com similaridade suficiente
    if len(sim_scores) == 0:
        return {"message": "Nenhum perfil encontrado com similaridade suficiente."}, 200
    
    # Selecionar os top_n perfis mais semelhantes
    recommended_metrics = [df['sanitized_metrics'].iloc[i] for i, _ in sim_scores[:top_n]]
    
    return recommended_metrics

# Endpoint para receber as features e recomendar métricas
@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        # Receber os dados do usuário
        user_data = request.json.get('features')
        
        if not user_data:
            return jsonify({"error": "Dados de usuário não fornecidos"}), 400
        
        # Recomendar métricas para o usuário
        recommended_metrics = recommend_metrics_for_new_user(user_data, vectorizer, svd, X_svd_transformed, df)
        
        # Retornar a resposta em JSON
        return jsonify({"recommended_metrics": recommended_metrics}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Iniciar o servidor Flask
if __name__ == '__main__':
    app.run(debug=True)
