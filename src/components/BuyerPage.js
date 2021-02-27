import React, {useState} from 'react';
import SearchField from 'react-search-field';
import logo1 from '../Chinese.jfif';
import logo2 from '../south indiam.jfif';
import logo3 from '../western.jfif';

const BuyerPage = props => {

return (
  <div className = "jumbotron">
  <h1> Search your preferred cuisine </h1>
  
  <SearchField 
  placeholder='Search your desired cuisine'
  />
  <div className="row">
        <div className="logo1">
          <img src={logo1} width="1000" height="1000" />
        </div>
  </div>
  <p className="btn btn-primary"> CHINESE HOME COOKED FOOD  </p>
  <div className="row">
        <div className="logo2">
          <img src={logo} width="1000" height="1000" />
        </div>
      </div>
  <p className="btn btn-primary"> SOUTH INDIAN FOOD </p>
  <div className="row">
        <div className="logo3">
          <img src={logo} width="1000" height="1000" />
        </div>
      </div>
  <p className="btn btn-primary"> WESTERN DELIGHTS </p>
  
  </div>
)
    
}

export default BuyerPage
