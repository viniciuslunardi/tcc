import React, { useState } from 'react';
import { Autocomplete, TextField, Button, Container, MenuItem, Typography } from '@mui/material';

const roles = ['Desenvolvedor(a)', 'Product Manager', 'Team Leader', 'Scrum Master', 'Engineering Manager'];
const experienceLevels = ['0 a 5', '5 a 10', '10 a 20'];
const companySizes = ['Pequena', 'Média', 'Grande'];
const agileMethods = ['Scrum', 'Kanban', 'Lean', 'SAFe'];

const MetricRecommendation = () => {
  const [role, setRole] = useState('');
  const [experience, setExperience] = useState('');
  const [companySize, setCompanySize] = useState('');
  const [methods, setMethods] = useState([]);

  const handleRecommendation = () => {
    const features = {
      role,
      experience,
      companySize,
      methods,
    };
    console.log('Features:', features);

    // Aqui você pode fazer a chamada para a API com as features
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

      {/* Seleção Múltipla de Métodos Ágeis */}
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

      {/* Botão para Obter Recomendações */}
      <Button
        variant="contained"
        color="primary"
        onClick={handleRecommendation}
        fullWidth
        style={{ marginTop: '20px', padding: '10px' }}
      >
        Obter Recomendações
      </Button>
    </Container>
  );
};

export default MetricRecommendation;
