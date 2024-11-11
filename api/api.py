import os
from flask import Flask, request, jsonify, send_from_directory
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
from flask_cors import CORS
import logging

# Configura o logging
logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')


class MetricsRecommendationService:
    def __init__(self):
        self.app = Flask(__name__, static_folder='static')
        self.app.config['JSON_AS_ASCII'] = False

        CORS(self.app)
        self.setup_routes()
        logging.info("Iniciando a API de recomendação de métricas.")

        # Carregar o modelo de filtragem colaborativa
        self.model_data = joblib.load('collaborative_filtering.joblib')
        self.df = self.model_data['df']
        self.tfidf_matrices = self.model_data['tfidf_matrices']
        self.features = self.model_data['features']
        self.feature_weights_default = self.model_data['feature_weights']
        self.tfidf_vectorizers = self.model_data['tfidf_vectorizers']
        self.df_metrics = pd.read_excel('extracted_metrics.xlsx', sheet_name='Descriptions')

        self.metrics_data = pd.read_excel('extracted_metrics.xlsx', sheet_name="Extracted metrics")
        self.metrics_data = self.metrics_data.copy()
        self.category_to_metrics = self.metrics_data.groupby('Translation')['Metric Name'].apply(list).to_dict()
        self.model_columns = joblib.load('model_columns.joblib')



    def setup_routes(self):
        # Definir rotas para as APIs
        self.app.add_url_rule('/recommend_metrics_multilabel', 'recommend_metrics_multilabel', self.recommend_metrics_multilabel, methods=['POST'])
        self.app.add_url_rule('/recommend_metrics_collaborative', 'recommend_metrics_collaborative', self.recommend_metrics_collaborative, methods=['POST'])

        # Rota para servir o frontend React
        self.app.add_url_rule('/', 'serve_frontend', self.serve_frontend)
        self.app.add_url_rule('/<path:path>', 'serve_frontend', self.serve_frontend)


    def serve_frontend(self, path=''):
        if path != "" and os.path.exists(os.path.join(self.app.static_folder, path)):
            return send_from_directory(self.app.static_folder, path)
        else:
            return send_from_directory(self.app.static_folder, 'index.html')
        
    def classify_user(self, categories, category_probabilities, user_df):
        logging.info(f"Classificando usuário com base nas categorias. {categories}")

        for category in categories:
            model_filename = f"model_{category}.joblib"
            model = joblib.load(model_filename)
            probabilities = model.predict_proba(user_df)[:, 1]

            for user_idx, affinity in enumerate(probabilities):
                category_probabilities[user_idx][category] = affinity
            logging.debug(f"Probabilidades para {category}: {probabilities}")
            

    def process_user_input(self, user_data):
        # Converter dados do usuário em DataFrame
        user_df = pd.DataFrame([user_data])
        logging.debug(f"Processando dados de entrada do usuário: {user_data}")
        # Aplicar pd.get_dummies às variáveis categóricas
        user_df = pd.get_dummies(user_df)

        # Adicionar colunas faltantes com valor 0 e remover colunas extras
        for col in self.model_columns:
            if col not in user_df.columns:
                user_df[col] = 0
        user_df = user_df[self.model_columns]

        category_cols = [
        'metrics_category_cronograma_e_progresso', 'metrics_category_produto',
        'metrics_category_processo', 'metrics_category_tecnologia',
        'metrics_category_pessoas', 'metrics_category_cliente'
        ]
        user_df.drop(columns=category_cols, errors='ignore', inplace=True)
        
        logging.debug("Dados de entrada processados com sucesso.")

        return user_df

    def recommend_metrics_multilabel(self):
        try:
            threshold = request.json.get('threshold', 0.5)

            # Processar a entrada do usuário
            user_data = request.json
            user_df = self.process_user_input(user_data)

            categories = ['metrics_category_cronograma_e_progresso', 'metrics_category_produto',
              'metrics_category_processo', 'metrics_category_tecnologia',
              'metrics_category_pessoas', 'metrics_category_cliente']
            
            # Inicializar as variáveis para armazenar as probabilidades de afinidade
            category_probabilities = {user_idx: {} for user_idx in range(len(user_df))}

            self.classify_user(categories, category_probabilities, user_df)
            metric_recommendations_with_affinity = self.recomendar_metricas_com_afinidade(
                category_probabilities, self.category_to_metrics, threshold
            )
         
            for user_idx, recommendations in metric_recommendations_with_affinity.items():
                for rec in recommendations:
                    if isinstance(rec['metric'], str):
                        rec['description'] = self.get_metric_description(rec['metric'])
                    else:
                        #remover a metrica das recomendações
                        recommendations.remove(rec)
            
            print()
            response = {
                'threshold': threshold,
                'metric_recommendations': metric_recommendations_with_affinity
            }

            return jsonify(response), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

  
    def recomendar_metricas_com_afinidade(self, category_probabilities, category_to_metrics, threshold):
        logging.info("Recomendando métricas com base nas afinidades calculadas.")
        category_map = {
            'metrics_category_cronograma_e_progresso': 'Cronograma e progresso',
            'metrics_category_produto': 'Produto',
            'metrics_category_processo': 'Processo',
            'metrics_category_tecnologia': 'Tecnologia',
            'metrics_category_pessoas': 'Pessoas',
            'metrics_category_cliente': 'Cliente'
        }

        recommendations = {}
        for user_idx, probs in category_probabilities.items():
            user_recommendations = []
            for category, affinity in probs.items():
                category = category_map.get(category) 

                if affinity >= threshold:
                    for metric in category_to_metrics.get(category, []):
                        if isinstance(metric, str):
                            user_recommendations.append({
                                'metric': metric,
                                'affinity': affinity,
                                'category': category
                            })
            recommendations[user_idx] = user_recommendations
            logging.debug(f"Recomendações para usuário {user_idx}: {user_recommendations}")
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

            print(recommendations)
            return jsonify(recommendations), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
    def get_metric_description(self, matched_metric, get_name_and_description=False):
    # Buscar a métrica correspondente no dataset
        match = self.df_metrics[self.df_metrics['Metric Name'].str.lower() == matched_metric.lower()]
        
        if not match.empty:
            if get_name_and_description:
                return match.iloc[0]['Metric Name'], match.iloc[0]['Metric Description']
            return match.iloc[0]['Metric Description']
        
        return None  # Retornar None se não houver correspondência
    
    def run(self):
        self.app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    service = MetricsRecommendationService()
    service.run()
