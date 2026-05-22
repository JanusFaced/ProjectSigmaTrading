import { BrowserRouter, Routes, Route } from 'react-router-dom';
import AuthorPageApp from './AuthorPageApp.jsx';
import SignalsApp from './SignalsApp.jsx';
import './index.css'

function App() {
	return (
		<BrowserRouter>
			<Routes>
				<Route path="/*" element={<AuthorPageApp />} />
				<Route path="/signals/*" element={<SignalsApp />} />
			</Routes>
		</BrowserRouter>
	);
}

export default App;