import React from 'react';
import Alert from 'react-bootstrap/Alert'

<Alert variant="success">
  <Alert.Heading>Welcome, User!</Alert.Heading>
  <p>
    Looks like you successfully read this important alert message!
  </p>
  <hr />
  <p className="mb-0">
    This is a margin where you place other things. Like links and other goodies for the user. It breaks things up well. 
  </p>
</Alert>

class BuyerPage extends React.Component{
  render() {
    return (
        <div>
        <h2> About </h2>
        <p> This app uses React</p>
    </div>
  );
  }
}

export default BuyerPage
