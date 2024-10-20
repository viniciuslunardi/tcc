import React, { useState } from 'react';
import { Autocomplete, TextField, Button, Container, MenuItem, Typography, CircularProgress } from '@mui/material';

const roles = ['Desenvolvedor(a)', 'Product Manager', 'Team Leader', 'Scrum Master', 'Engineering Manager'];
const experienceLevels = ['0 a 5', '6 a 9', '10 a 20', 'Mais de 20'];
const companySizes = ['Microempresa', 'Pequena empresa', 'Média empresa', 'Grande empresa'];
const agileMethods = ['Scrum', 'Kanban', 'Lean', 'Safe', 'XP', 'ScrumBan'];
const ritualsToUse = ['Reunião de Planejamento', 'Sprint Review', 'Reunião Semanal', 'Reunião Diária (daily)', 'Retrospectiva'];
const categories = ['Gestão de Tempo e Progresso', 'Gestão de Equipes', 'Desempenho do Produto', 'Eficiência dos Processos', 'Soluções Tecnológicas',  'Satisfação e Experiência do Cliente'];

const MetricRecommendation = () => {
  const [role, setRole] = useState('');
  const [experience, setExperience] = useState('');
  const [companySize, setCompanySize] = useState('');
  const [methods, setMethods] = useState([]);
  const [rituals, setRituals] = useState([]);
  const [categoriesSet, setCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState([]);
  const [error, setError] = useState('');

  const handleRecommendation = async () => {
    setLoading(true);
    setError('');
    setRecommendations([]);
  
    try {
      const response = await fetch('http://localhost:5000/recommend_metrics', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          role: role,
          years_exp: experience,
          org_size: companySize,
          use_metrics_planning: rituals.includes('Reunião de Planejamento') ? 1 :  0,
          use_metrics_review: rituals.includes('Sprint Review') ? 1 :  0,
          use_metrics_weekly: rituals.includes('Reunião Semanal') ? 1 :  0,
          use_metrics_daily: rituals.includes('Reunião Diária (daily)') ? 1 :  0,
          use_metrics_retro: rituals.includes('Retrospectiva') ? 1 :  0,
          agile_methods_scrum: methods.includes('Scrum') ? 1 :  0,
          agile_methods_kanban: methods.includes('Kanban') ? 1 :  0,
          agile_methods_scrumban: methods.includes('ScrumBan') ? 1 :  0,
          agile_methods_xp: methods.includes('XP') ? 1 :  0,
          agile_methods_safe: methods.includes('Safe') ? 1 :  0,
          agile_methods_lean: methods.includes('Lean') ? 1 :  0,
          metrics_category_cronograma_e_progresso: categoriesSet.includes('Gestão de Tempo e Progresso') ? 1 :  0,
          metrics_category_produto: categoriesSet.includes('Desempenho do Produto') ? 1 :  0,
          metrics_category_processo: categoriesSet.includes('Eficiência dos Processos') ? 1 :  0,
          metrics_category_tecnologia: categoriesSet.includes('Soluções Tecnológicas') ? 1 :  0,
          metrics_category_cliente: categoriesSet.includes('Satisfação e Experiência do Cliente') ? 1 :  0,
          metrics_category_pessoas: categoriesSet.includes('Satisfação e Experiência do Cliente') ? 1 :  0,
          top_n: 8
        }),
      });

      if (!response.ok) {
        throw new Error('Erro ao obter as recomendações da API.');
      }

      const data = await response.json();
      console.log('Data:', data);

      if (!data) {
        setError('Nenhum perfil encontrado com similaridade suficiente. Tente fornecer mais informações.');
      } else {
        setRecommendations(data);
      }
    } catch (err) {
      setError('Erro ao buscar as recomendações. Verifique a API e tente novamente.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm" style={{ marginTop: '50px', padding: '20px', backgroundColor: '#fff', borderRadius: '10px' }}>
      <Typography variant="h4" align="center" gutterBottom>
        Recomendação de Métricas
      </Typography>

      {/* Seleção da Função */}
      <TextField
        select
        label="Selecione sua função"
        value={role}
        onChange={(e) => setRole(e.target.value)}
        fullWidth
        margin="normal"
      >
        {roles.map((option) => (
          <MenuItem key={option} value={option}>
            {option}
          </MenuItem>
        ))}
      </TextField>

      {/* Seleção dos Anos de Experiência */}
      <TextField
        select
        label="Anos de experiência"
        value={experience}
        onChange={(e) => setExperience(e.target.value)}
        fullWidth
        margin="normal"
      >
        {experienceLevels.map((option) => (
          <MenuItem key={option} value={option}>
            {option}
          </MenuItem>
        ))}
      </TextField>

      {/* Seleção do Tamanho da Empresa */}
      <TextField
        select
        label="Tamanho da empresa"
        value={companySize}
        onChange={(e) => setCompanySize(e.target.value)}
        fullWidth
        margin="normal"
      >
        {companySizes.map((option) => (
          <MenuItem key={option} value={option}>
            {option}
          </MenuItem>
        ))}
      </TextField>

    
      <Autocomplete
        multiple
        id="agile-methods"
        options={agileMethods}
        value={methods}
        onChange={(event, newValue) => {
          setMethods(newValue);
        }}
        renderInput={(params) => (
          <TextField {...params} label="Métodos ágeis utilizados" placeholder="Selecione" fullWidth margin="normal" />
        )}
      />

      <Autocomplete
        multiple
        id="rituals"
        options={ritualsToUse}
        value={rituals}
        onChange={(event, newValue) => {
          setRituals(newValue);
        }}
        renderInput={(params) => (
          <TextField {...params} label="Rituais ágeis utilizados" placeholder="Selecione" fullWidth margin="normal" />
        )}
      />

      <Autocomplete
        multiple
        id="categories"
        options={categories}
        value={categoriesSet}
        onChange={(event, newValue) => {
          setCategories(newValue);
        }}
        renderInput={(params) => (
          <TextField {...params} label="Onde você acha importante aplicar métricas?" placeholder="Selecione" fullWidth margin="normal" />
        )}
      />

      {/* Botão para Obter Recomendações */}
      <Button
        variant="contained"
        color="primary"
        onClick={handleRecommendation}
        fullWidth
        style={{ marginTop: '20px', padding: '10px' }}
        disabled={loading}
      >
        {loading ? <CircularProgress size={24} color="inherit" /> : 'Obter Recomendações'}
      </Button>

      {/* Exibir Erro, se houver */}
      {error && (
        <Typography color="error" variant="body2" style={{ marginTop: '10px' }}>
          {error}
        </Typography>
      )}

      {recommendations.length > 0 && (
      <div>
        <h3>Recomendações de Métricas</h3>
        <ul>
          {recommendations.map((rec, index) => (
            <li key={index}>
              <strong>Métrica:</strong> {rec.metric} <br />
              <strong>Porcentagem de Afinidade:</strong> {rec.affinity}% <br />
              <strong>Descrição:</strong> {rec.description} <br />
              <strong>Debug: Índice do Perfil Similar:</strong> {rec.similar_profile_index}
            </li>
          ))}
        </ul>
      </div>
      )}
    </Container>
  );
};

export default MetricRecommendation;
