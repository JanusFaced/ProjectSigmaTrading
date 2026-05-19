import { Link } from 'react-router-dom';

function Navigation() {
    return (
        <nav className="navigation">
            <div className="nav-container">
                <div className="logo">
                    <Link to="/">SigmaProjectTrading</Link>
                </div>
                <ul className="nav-links">
                    <li><Link to="/">Главная</Link></li>
                    <li><Link to="/analyst">Аналитика</Link></li>
                    <li><Link to="/about">О проекте</Link></li>
                </ul>
            </div>
        </nav>
    );
}

export default Navigation;