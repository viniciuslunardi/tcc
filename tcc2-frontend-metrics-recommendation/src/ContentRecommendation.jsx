import React, { useState } from 'react';
import { TextField, MenuItem, Autocomplete, Container, Typography, Button, CircularProgress, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Slider } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const roles = [
  'Team leader',
  'Product manager',
  'Scrum master',
  'cd ',
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
const companySizes = ['Microempresa (< 10 empregados)', 'Pequena empresa (10-99 empregados)', 'Média empresa (100-500 empregados)', 'Grande empresa (>500 empregados)'];
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
  const [threshold, setThreshold] = useState(50); // Novo estado para o threshold
  const [isApiCalled, setIsApiCalled] = useState(false);


  const handleThresholdChange = (event, newValue) => {
    setThreshold(newValue);
  };

  const handleRecommendation = async () => {
    setLoading(true);
    setError('');
    setRecommendations([]);
    
    if (!role || !experience || !companySize || methods.length === 0 || rituals.length === 0) { 
      setError('Por favor, preencha todos os campos.');
      setLoading(false);
      return;
    }
    
    try {
      const currentUrl = window.location.origin;
      const response = await fetch( urrentUrl + '/recommend_metrics_multilabel', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          role: role, 
          years_exp: experience, 
          org_size: companySize.replace(/\s*\(.*\)/, ''),
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
          threshold: parseFloat(threshold * 0.01),
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
      setIsApiCalled(true);
    }
  };

  const navigate = useNavigate();
  return (
    <Container maxWidth="md" style={{ marginTop: '50px', padding: '20px', backgroundColor: '#fff', borderRadius: '10px' }}>
      <Typography variant="h4" align="center" gutterBottom>
        Recomendação de Métricas Ágeis - Classificação Multi-Label
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

      
      {/* Slider para Threshold de Similaridade */}
      <Typography variant="body1" style={{ marginTop: '20px' }}>
         Similaridade (%): {threshold} </Typography>
      <Slider
        value={threshold}
        onChange={handleThresholdChange}
        step={10}
        min={0}
        max={100}
        valueLabelDisplay="auto"
        marks={[{ value: 0, label: '0%' }, { value: 100, label: '100%' }]}
        style={{ marginBottom: '20px' }}
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

<>
    {recommendations.length > 0 ? (
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
    ) : (
      isApiCalled && (
        <Typography variant="h6" style={{ marginTop: '20px', textAlign: 'center' }}>
          Nenhuma métrica recomendada foi encontrada. Ajuste a porcentagem de similaridade e os parâmetros informados e tente novamente.
        </Typography>
      )
    )}
  </>

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
          alt="Imagem do tcc" 
          style={{ width: '100%', maxWidth: '50px', marginBottom: '10px' }} 
        />
          <img 
          src="logo_ine.png" 
          alt="Imagem do ine" 
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
