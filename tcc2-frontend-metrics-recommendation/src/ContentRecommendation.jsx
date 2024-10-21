import React, { useState } from 'react';
import { TextField, MenuItem, Autocomplete, Container, Typography, Button, CircularProgress, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const roles = [
  'Team leader',
  'Product manager',
  'Scrum master',
  'Engineering Manager',
  'Project Manager',
  'Product owner',
  'Desenvolvedor(a)',
  'Technical leader',
  'Agile Master',
  'IT Director',
  'Agile Coach',
  'Gerente de Serviços',
  'Customer success',
  'Superintendente',
  'Pesquisador',
  'Head comercial',
  'Governança',
  'Digital Analytics',
  'DevOps/SRE',
  'Consultor de implantação', 
  'Arquiteto de software', 
  'Administrador de Dados, DBA',
  'CTO',
  'CIO',
  'CEO',
];
const experienceLevels = ['0 a 5', '6 a 9', '10 a 20', 'Mais de 20'];
const companySizes = ['Microempresa', 'Pequena empresa', 'Média empresa', 'Grande empresa'];
const agileMethods = ['Scrum', 'Kanban', 'Lean', 'Safe', 'XP', 'ScrumBan'];
const ritualsToUse = ['Reunião de Planejamento', 'Sprint Review', 'Reunião Semanal', 'Reunião Diária (daily)', 'Retrospectiva'];

const ContentRecommendation = () => {
  const [role, setRole] = useState('');
  const [experience, setExperience] = useState('');
  const [companySize, setCompanySize] = useState('');
  const [methods, setMethods] = useState([]);
  const [rituals, setRituals] = useState([]);
  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState([]);
  const [error, setError] = useState('');  
  const [threshold, setThreshold] = useState(0.5);


  const handleRecommendation = async () => {
    setLoading(true);
    setError('');
    setRecommendations([]);
  
    try {
      const response = await fetch('http://localhost:5000/recommend_metrics_content', {
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
          thrashold: 0.5,
        }),
      });

      if (!response.ok) {
        throw new Error('Erro ao obter as recomendações da API.');
      }

      const data = await response.json();

      if (data.metric_recommendations && data.metric_recommendations['0']) {
        setRecommendations(data.metric_recommendations['0']);
      } else {
        setError('Nenhuma métrica recomendada.');
      }
    } catch (err) {
      setError('Erro ao buscar as recomendações. Verifique a API e tente novamente.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const navigate = useNavigate();
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
        <TableContainer component={Paper} style={{ marginTop: '20px' }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell><strong>Métrica</strong></TableCell>
                <TableCell><strong>Afinidade</strong></TableCell>
                <TableCell><strong>Categoria</strong></TableCell>
                <TableCell><strong>Descrição</strong></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {recommendations.map((rec, index) => (
                <TableRow key={index}>
                  <TableCell>{rec.metric}</TableCell>
                  <TableCell>{(rec.affinity * 100).toFixed(2)} %</TableCell>
                  <TableCell>{rec.category}</TableCell>
                  <TableCell>{rec.description}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <Button 
        variant="outlined" 
        color="primary" 
        fullWidth 
        style={{ marginTop: '20px' }}
        onClick={() => navigate('/')}
      >
        Voltar para a Página Inicial
      </Button>
      
       {/* Rodapé com imagem e texto */}
       <footer style={{ marginTop: '50px', textAlign: 'center' }}>
        <img 
          src="logo_ufsc.png" 
          alt="Imagem do Trabalho" 
          style={{ width: '100%', maxWidth: '50px', marginBottom: '10px' }} 
        />
        <Typography variant="caption" display="block" gutterBottom>
          Trabalho de Conclusão de Curso apresentado ao Curso de Graduação em Sistemas de Informação 
          pela Universidade Federal de Santa Catarina. Aluno Vinicius Araldi Lunardi Farias, 
          matrícula 18200653. Orientador Prof. Dr. Jean Carlo Rossa Hauck.
        </Typography>
      </footer>
    </Container>
  );
};

export default ContentRecommendation;