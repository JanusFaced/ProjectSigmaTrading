import { Link } from 'react-router-dom';

function HomePage() {
    return (
        <div className="home-page">
            <div className="hero">
                <h1>Добро пожаловать в SigmaProjectTrading!</h1>
                <p>Экспериментальный проект в области финтеха открытый для использования каждого!</p>
                <div className="hero-buttons">
                    <Link to="/analyst" className="btn btn-primary">
                        Посмотреть ML-аналитику криптовалют →
                    </Link>
                    <Link to="/about" className="btn btn-secondary">
                        Узнать о проекте больше!
                    </Link>
                </div>
            </div>

            <div className="features">
                <div className="feature">
                    <h3>🪙 Любой криптовалютный актив!</h3>
                    <p>Выбирайте любой актив из предоставленного списка, что существует на топовых криптобиржах.</p>
                </div>
                <div className="feature">
                    <h3>📈 Любой интересный вам масштаб движений!</h3>
                    <p>Выбирайте любой интересующий вас таймфрэйм от дневки до минутки.</p>
                </div>
                <div className="feature">
                    <h3>🧰 Любая модель!</h3>
                    <p>Выбирайте любые разработанные в этом проекте модели: классификация, регрессия и тд.</p>
                </div>
            </div>
        </div>
    );
}

export default HomePage;