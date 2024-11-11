import React from 'react';
import { Container, Typography, Button, Box } from '@mui/material';
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
      
      <Box display="flex" flexDirection="column" gap={2} mt={2}>
        <Button
          variant="contained"
          color="primary"
          fullWidth
          onClick={handleContentBased}
        >
          Modelo de Classificação MultiLabel
        </Button>

        <Button
          variant="contained"
          color="primary"
          fullWidth
          onClick={handleCollaborativeFiltering}
        >
          Modelo de Filtragem Colaborativa
        </Button>
      </Box>

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

export default LandingPage;
