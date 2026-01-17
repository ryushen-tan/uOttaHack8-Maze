import './App.css'
import { Route, Routes } from 'react-router-dom';
import Landing from './pages/Landing';
import Navbar from './components/Navbar';
import Maze from './pages/Maze';

function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/maze" element={<Maze />} />
      </Routes>
    </>
  )
}

export default App;