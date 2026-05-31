import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navigation from './pages/signalsPages/Navigation.jsx';
import HomePage from './pages/signalsPages/HomePage.jsx';
import AnalystPage from './pages/signalsPages/AnalystPage.jsx';
import AboutPage from './pages/signalsPages/AboutPage.jsx';

function SignalsApp() {
	return (
		<div id="signals-app-root" className="signals-project">
			<Navigation />
			<Routes>
				<Route path="/" element={<HomePage />} />
				<Route path="/analyst" element={<AnalystPage />} />
				<Route path="/about" element={<AboutPage />} />
			</Routes>
		</div>
	);
}

export default SignalsApp;