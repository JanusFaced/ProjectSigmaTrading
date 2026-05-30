import { BrowserRouter, Routes, Route } from 'react-router-dom';
import AuthorPageApp from './AuthorPageApp.jsx';
import SignalsApp from './SignalsApp.jsx';
import PredictApp from './PredictApp.jsx';
import './index.css'

function App() {
	return (
		<BrowserRouter>
			<Routes>
				<Route path="/*" element={<AuthorPageApp />} />
				<Route path="/signals/*" element={<SignalsApp />} />
				<Route path="/predict/*" element={<PredictApp />} />
			</Routes>
		</BrowserRouter>
	);
}

export default App;