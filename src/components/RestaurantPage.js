import React, {useState} from 'react';
import Header from "./common/Header";
import RestaurantForm from "./common/RestaurantForm";

const RestaurantPage = props => {

  const [packet, setPacket] = useState({
    wt: "",
    numOfPacket: ""
  });

  function handleTitleChange(event) {
    const updatedPacket = {...packet, wt:event.target.value};
    setPacket(updatedPacket);
  }

  function handleNmChange(event) {
    const updatedPacket = {...packet, numOfPacket:event.target.value};
    setPacket(updatedPacket);
  }

  function handleChange(event) {
    const updatedPacket = {...packet, [event.target.name]:event.target.value};
    setPacket(updatedPacket);
  }

  function handleSubmit(event) {
    alert('The form was submitted. ');
    event.preventDefault();
  }

  return (
      <div>
      <h1>Restaurant Form</h1>
      <RestaurantForm packet={packet} onTitleChange={handleTitleChange} onNmChange={handleNmChange} />
    </div>
  );
}

export default RestaurantPage
