import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './LandingPage';
//import ContentBasedRecommendation from './ContentBasedRecommendation';
import FilteringRecommendation from './FilteringRecommendation';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        {/* <Route path="/content-based" element={<ContentBasedRecommendation />} /> */}
        <Route path="/collaborative-filtering" element={<FilteringRecommendation />} />
      </Routes>
    </Router>
  );
}

export default App;
