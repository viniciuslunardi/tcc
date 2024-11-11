import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './LandingPage';
import ContentRecommendation from './ContentRecommendation';
import FilteringRecommendation from './FilteringRecommendation';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/multilabel" element={<ContentRecommendation />} />
        <Route path="/collaborative-filtering" element={<FilteringRecommendation />} />
      </Routes>
    </Router>
  );
}

export default App;
