import os
from flask import Flask, request, jsonify, send_from_directory
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
from flask_cors import CORS
import re

class MetricsRecommendationService:
    def __init__(self):
        self.app = Flask(__name__, static_folder='static')
        CORS(self.app)
        self.setup_routes()
        
        # Carregar o modelo de filtragem colaborativa
        self.model_data = joblib.load('collaborative_filtering.joblib')
        self.df = self.model_data['df']
        self.tfidf_matrices = self.model_data['tfidf_matrices']
        self.features = self.model_data['features']
        self.feature_weights_default = self.model_data['feature_weights']
        self.tfidf_vectorizers = self.model_data['tfidf_vectorizers']
        self.df_metrics = pd.read_excel('extracted_metrics.xlsx', sheet_name='Descriptions')


    def setup_routes(self):
        # Definir rotas para as APIs
        self.app.add_url_rule('/recommend_metrics_content', 'recommend_metrics_content', self.recommend_metrics_content, methods=['POST'])
        self.app.add_url_rule('/recommend_metrics_collaborative', 'recommend_metrics_collaborative', self.recommend_metrics_collaborative, methods=['POST'])

        # Rota para servir o frontend React
        self.app.add_url_rule('/', 'serve_frontend', self.serve_frontend)
        self.app.add_url_rule('/<path:path>', 'serve_frontend', self.serve_frontend)

    def process_user_input(self, user_data):
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
        
        return user_df

    def serve_frontend(self, path=''):
        if path != "" and os.path.exists(os.path.join(self.app.static_folder, path)):
            return send_from_directory(self.app.static_folder, path)
        else:
            return send_from_directory(self.app.static_folder, 'index.html')
        
    def classify_user(self, categories, category_probabilities, user_df):
        for category in categories:
            model_filename = f"modelo_{category}_ajustado.joblib"
            rf_binary = joblib.load(model_filename)

            user_affinities = rf_binary.predict_proba(user_df)[:, 1]

            for user_idx, affinity in enumerate(user_affinities):
                category_probabilities[user_idx][category] = affinity

    def recommend_metrics_content(self):
        try:
            threshold = request.json.get('threshold', 0.5)

            # Processar a entrada do usuário
            user_data = request.json
            user_df = self.process_user_input(user_data)

            # Inicializar as variáveis para armazenar as probabilidades de afinidade
            category_probabilities = {user_idx: {} for user_idx in range(len(user_df))}
            metrics_data = pd.read_excel('extracted_metrics.xlsx', sheet_name="Extracted metrics")

            metrics_data = metrics_data.copy()
            category_to_metrics = metrics_data.groupby('Translation')['Metric Name'].apply(list).to_dict()

            categories = ['Cronograma e progresso', 'Produto', 'Processo', 'Tecnologia', 'Pessoas', 'Cliente']
            self.classify_user(categories, category_probabilities, user_df)

            metric_recommendations_with_affinity = self.recomendar_metricas_com_afinidade(
                category_probabilities, category_to_metrics, threshold
            )

             # Adicionar a descrição das métricas no retorno
            for user_idx, recommendations in metric_recommendations_with_affinity.items():
                for rec in recommendations:
                    rec['description'] = self.get_metric_description(rec['metric'])

            response = {
                'threshold': threshold,
                'metric_recommendations': metric_recommendations_with_affinity
            }

            return jsonify(response), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    def recomendar_metricas_com_afinidade(self, category_probabilities, category_to_metrics, threshold):
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

        # Função para adicionar o perfil do usuário ao dataframe existente
    def add_user_to_dataframe(self, user_profile):
        user_data = {feature: user_profile.get(feature, np.nan) for feature in self.features}
        user_df = pd.DataFrame([user_data])
        return pd.concat([self.df, user_df], ignore_index=True)

    # Função para calcular a similaridade total ponderada
    def calculate_total_similarity(self, df_with_user, user_index, feature_weights=None):
        total_similarity = np.zeros(df_with_user.shape[0])

        if feature_weights is None:
            feature_weights = self.feature_weights_default.copy()

        for feature in self.features:
            if df_with_user[feature].dtype == 'object':
                tfidf_vectorizer = self.tfidf_vectorizers[feature]
                tfidf_matrix = tfidf_vectorizer.transform(df_with_user[feature].fillna(''))
                cosine_sim = cosine_similarity(tfidf_matrix[user_index], tfidf_matrix).flatten()
            else:
                binary_matrix = df_with_user[feature].fillna(0).values.reshape(-1, 1)
                cosine_sim = cosine_similarity([binary_matrix[user_index]], binary_matrix).flatten()

                # Ajustar o peso se a feature binária for 1
                if df_with_user[feature].iloc[user_index] == 1:
                    feature_weights[feature] = feature_weights.get(feature, 1.0) * 2.0

            total_similarity += cosine_sim * feature_weights.get(feature, 1.0)

        return total_similarity

    # Função para recomendar métricas com base em perfis similares
 # Função para recomendar métricas com base em perfis similares usando "matched_metrics"
    
    def recommend_metrics_col(self, user_profile, top_n=5, feature_weights=None):
        df_with_user = self.add_user_to_dataframe(user_profile)
        user_index = len(df_with_user) - 1

        total_similarity = self.calculate_total_similarity(df_with_user, user_index, feature_weights)
        total_similarity[user_index] = -1  # Excluir o próprio usuário da recomendação

        similar_indices = total_similarity.argsort()[-top_n:][::-1]
        similar_profiles = df_with_user.iloc[similar_indices]
        similar_affinity = total_similarity[similar_indices]

        recommended_metrics = []

        for idx, metrics in enumerate(similar_profiles['matched_metrics']):
            # Verificar se 'metrics' não é NaN e é uma string válida
            if pd.notna(metrics) and isinstance(metrics, str):
                if metrics not in [rec['metric'] for rec in recommended_metrics]:
                    affinity = similar_affinity[idx]
                    affinity = min(affinity, 100)  # Limitar afinidade a 100

                    id_integer_value = similar_profiles.iloc[idx]['id_integer']

                    # Obter o nome e a descrição da métrica
                    metric_name, description = self.get_metric_description(metrics, get_name_and_description=True)

                    if metric_name and description:  # Somente adicionar se encontrar correspondência
                        recommended_metrics.append({
                            "metric": metric_name,
                            "affinity": float(affinity),
                            "description": description,
                            "similar_profile_index": int(id_integer_value)
                        })

            if len(recommended_metrics) == top_n:
                break

        return recommended_metrics

    def recommend_metrics_collaborative(self):
        try:
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
            recommendations = self.recommend_metrics_col(user_profile, top_n=data.get('top_n', 5), feature_weights=feature_weights)

            return jsonify(recommendations), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
    def get_metric_description(self, matched_metric, get_name_and_description=False):
    # Buscar a métrica correspondente no dataset
        match = self.df_metrics[self.df_metrics['Metric Name'].str.lower() == matched_metric]
        
        if not match.empty:
            if get_name_and_description:
                return match.iloc[0]['Metric Name'], match.iloc[0]['Metric Description']
            return match.iloc[0]['Metric Description']
        
        return None  # Retornar None se não houver correspondência
    
    def run(self):
        self.app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    service = MetricsRecommendationService()
    service.run()
