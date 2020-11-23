import React from 'react';
import './App.css';
import Navbar from './components/Navbar';
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom';
import Home from './pages/Home';
import Team from './pages/Team';
import Detection from './pages/Detection';


function App() {
  return (
    <>
      <Router>
        <Navbar />
        <Switch>
          <Route path='/' exact component={Home} />
          <Route path='/detection'>
            {/* class component */}
            <Detection />
          </Route>
          <Route path='/team' component={Team} />
        </Switch>
      </Router>
    </>
  );
}

export default App;
