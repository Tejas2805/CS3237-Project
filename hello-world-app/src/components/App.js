import React from 'react';
import HomePage from './HomePage';
import AboutPage from './AboutPage';
import RestaurantPage from './RestaurantPage';
import VolunteerPage from './VolunteerPage';
import BuyersPage from './BuyersPage';
import Header from './common/Header';
import { Route } from 'react-router-dom';

function App() {

  return (
    <div className="container-fluid">
        <Header />
        <Route path="/" exact component={HomePage} />
        <Route path="/about" component={AboutPage} />
    </div>
  );
}

export default App
