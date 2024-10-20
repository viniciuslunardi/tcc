import React from 'react';
import { Container, Typography, Button, Grid } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const LandingPage = () => {
  const navigate = useNavigate();

  const handleContentBased = () => {
    navigate('/content-based');
  };

  const handleCollaborativeFiltering = () => {
    navigate('/collaborative-filtering');
  };

  return (
    <Container maxWidth="sm" style={{ marginTop: '50px', padding: '20px', backgroundColor: '#fff', borderRadius: '10px' }}>
      <Typography variant="h4" align="center" gutterBottom>
        Sistema de Recomendação de Métricas Ágeis
      </Typography>
      <Typography variant="body1" align="center" gutterBottom>
        Escolha o tipo de recomendação que deseja explorar:
      </Typography>
      
      <Grid container spacing={3} style={{ marginTop: '20px' }}>
        <Grid item xs={12}>
          <Button
            variant="contained"
            color="primary"
            fullWidth
            onClick={handleContentBased}
          >
            Recomendação Baseada em Conteúdo
          </Button>
        </Grid>

        <Grid item xs={12}>
          <Button
            variant="contained"
            color="secondary"
            fullWidth
            onClick={handleCollaborativeFiltering}
          >
            Recomendação por Filtro Colaborativo
          </Button>
        </Grid>
      </Grid>
    </Container>
  );
};

export default LandingPage;
