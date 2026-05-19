import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation.js';
import HomePage from './pages/HomePage.js';
import AnalystPage from './pages/AnalystPage.js';
import AboutPage from './pages/AboutPage.js';
import './App.css';

function App() {
	return (
		<BrowserRouter>
			<div className="app">
				<Navigation />
				<main className="main-content">
					<Routes>
						<Route path="/" element={<HomePage />} />
						<Route path="/analyst" element={<AnalystPage />} />
						<Route path="/about" element={<AboutPage />} />
					</Routes>
				</main>
			</div>
		</BrowserRouter>
	);
}

export default App;