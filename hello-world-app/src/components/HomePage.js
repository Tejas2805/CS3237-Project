import React from 'react';
import { Link } from 'react-router-dom';

function HomePage() {
  return (
      <div className = "jumbotron">
        <h1> WELCOME TO OUR WEBSITE </h1>
        <p> Click to select your user profile </p>
        <p> <Link to="about" className="btn btn-primary">RESTAURANT</Link></p>
        <p><Link to="about" className="btn btn-primary">VOLUNTEER</Link></p>
        <p><Link to="about" className="btn btn-primary">BUYER/CUSTOMER</Link></p>
        <Link to="about" className="btn btn-primary">About</Link>
      </div>
  );
}

export default HomePage;
