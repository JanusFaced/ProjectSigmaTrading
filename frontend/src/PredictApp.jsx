import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navigation from './pages/predictPages/Navigation.jsx';
import HomePage from './pages/predictPages/HomePage.jsx';
import AnalystPage from './pages/predictPages/AnalystPage.jsx';
import AboutPage from './pages/predictPages/AboutPage.jsx';

function PredictApp() {
	return (
		<div id="predict-app-root" className="predict-project">
			<Navigation />
			<Routes>
				<Route path="/" element={<HomePage />} />
				<Route path="/analyst" element={<AnalystPage />} />
				<Route path="/about" element={<AboutPage />} />
			</Routes>
		</div>
	);
}

export default PredictApp;