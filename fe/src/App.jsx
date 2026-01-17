import './App.css'
import { Route, Routes } from 'react-router-dom';
import Landing from './pages/Landing';
import Navbar from './components/Navbar';
import Snow from './pages/Snow';

function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/Snow" element={<Snow />} />
      </Routes>
    </>
  )
}

export default App;