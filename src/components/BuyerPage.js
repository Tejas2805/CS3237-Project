import React, {useState} from 'react';
import Header from "./common/Header";
import BuyerForm from "./common/BuyerForm";

const BuyerPage = props => {

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
    alert('An essay was submitted: ');
    event.preventDefault();
  }

  return (
      <div>
      <BuyerForm packet={packet} onTitleChange={handleTitleChange} onNmChange={handleNmChange} onSubmit={handleSubmit}/>
    </div>
  );
}

export default BuyerPage
