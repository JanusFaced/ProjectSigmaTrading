import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './pages/signalsPages/AuthContext.jsx';
import Navigation from './pages/signalsPages/Navigation.jsx';
import HomePage from './pages/signalsPages/HomePage.jsx';
import BacktestPage from './pages/signalsPages/BacktestPage.jsx';
import AnalystPage from './pages/signalsPages/AnalystPage.jsx';
import TradesPage from './pages/signalsPages/TradesPage.jsx';
import AboutPage from './pages/signalsPages/AboutPage.jsx';
import AdminPanel from './pages/signalsPages/AdminPanel.jsx';
import Login from './pages/signalsPages/Login.jsx';
import ProtectedRoute from './pages/signalsPages/ProtectedRoute.jsx';

function SignalsApp() {
	return (
		<AuthProvider>
			<div id="signals-app-root" className="signals-project">
				<Navigation />
				<Routes>
					<Route path="/" element={<HomePage />} />
					<Route path="/backtest" element={<BacktestPage />} />
					<Route path="/analyst" element={<AnalystPage />} />
					<Route path="/trades/:signalId" element={<TradesPage />} />
					<Route path="/about" element={<AboutPage />} />
					<Route path="/login" element={<Login />} />
					<Route 
						path="/admin" 
						element={
							<ProtectedRoute>
								<AdminPanel />
							</ProtectedRoute>
						} 
					/>
					<Route 
						path="/admin/*" 
						element={
							<ProtectedRoute>
								<AdminPanel />
							</ProtectedRoute>
						} 
					/>
				</Routes>
			</div>
		</AuthProvider>
	);
}

export default SignalsApp;