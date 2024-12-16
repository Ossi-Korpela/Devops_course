
const express = require('express');
const bodyParser = require('body-parser');
const app = express();
app.use(bodyParser.text({ type: '*/*' }));

const states = ['INIT', 'PAUSED', 'RUNNING', 'SHUTDOWN'];
let currentState = 'INIT';
let runLog = [];

function logStateTransition(oldState, newState) {
  const timestamp = new Date().toISOString();
  runLog.push(`${timestamp}: ${oldState}->${newState}`);
}



app.put('/state', (req, res) => {
  const requestedState = req.body.trim(); 
  if (!requestedState in states ){
    return res.status(400).send('Invalid status type')
  }
  if (requestedState === currentState) {
    return res.status(200).send(currentState);
  }

  logStateTransition(currentState, requestedState)
  currentState = requestedState;
  if (currentState === 'INIT'){
    
  }

  return res.status(200).send(currentState);
});


const PORT = 8197;
app.listen(PORT, () => {
  console.log(`gateway listening on ${PORT}`);
});
