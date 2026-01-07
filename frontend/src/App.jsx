import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Categories from './pages/Categories';
import Transactions from './pages/Transactions';
import Receipt from './pages/Receipt';
import Dashboard from './pages/Dashboard';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/transactions" element={<Transactions />} />
        <Route path="/receipt" element={<Receipt />} />
        <Route path="/statistics" element={<div>Statistics (Coming Soon)</div>} />
        <Route path="/categories" element={<Categories />} />
        <Route path="/budgets" element={<div>Budgets (Coming Soon)</div>} />
        <Route path="/settings" element={<div>Settings (Coming Soon)</div>} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
