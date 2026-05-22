import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import { AnimatePresence } from "framer-motion";
import Navigator from "./pages/authorPages/Navigator.jsx";
import AnimatedPage from "./pages/authorPages/AnimatedPage.jsx";
import WelcomeSection from "./pages/authorPages/WelcomeSection.jsx"
import AuthorSection from "./pages/authorPages/AuthorSection.jsx"
import SkillSection from "./pages/authorPages/SkillSection.jsx"
import PortfolioSection from "./pages/authorPages/PortfolioSection.jsx"
import ContactSection from "./pages/authorPages/ContactSection.jsx"

function AuthorPageApp() {
	const location = useLocation();
	return (
		<div id="author-app-root" className="author-project">
			<Navigator />
		    <AnimatePresence mode="wait">
		      <Routes location={location} key={location.pathname}>
		        <Route path="/" element={<AnimatedPage><WelcomeSection /></AnimatedPage>} />
		        <Route path="/author" element={<AnimatedPage><AuthorSection /></AnimatedPage>} />
		        <Route path="/skills" element={<AnimatedPage><SkillSection /></AnimatedPage>} />
		        <Route path="/portfolio" element={<AnimatedPage><PortfolioSection /></AnimatedPage>} />
		        <Route path="/contact" element={<AnimatedPage><ContactSection /></AnimatedPage>} />
		      </Routes>
		    </AnimatePresence>
		</div>
	);
}

export default AuthorPageApp;