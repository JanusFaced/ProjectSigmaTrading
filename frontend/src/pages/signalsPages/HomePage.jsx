import { Link } from 'react-router-dom';
import {
	HomeContainer,
	Hero,
	HeroButtons,
	PrimaryButton,
	SecondaryButton,
	Features,
	Feature
} from './HomePage.styles.jsx';

function HomePage() {
	return (
		<HomeContainer>
			<Hero>
				<h1>Добро пожаловать в SigmaProjectTrading!</h1>
				<p>Экспериментальный проект в области финтеха открытый для использования каждого!</p>
				<HeroButtons>
					<PrimaryButton as={Link} to="/signals/analyst">
						Посмотреть ML-аналитику криптовалют →
					</PrimaryButton>
					<SecondaryButton as={Link} to="/signals/about">
						Узнать о проекте больше!
					</SecondaryButton>
				</HeroButtons>
			</Hero>

			<Features>
				<Feature>
					<h3>🪙 Любой криптовалютный актив!</h3>
					<p>Выбирайте любой актив из предоставленного списка, что существует на топовых криптобиржах.</p>
				</Feature>
				<Feature>
					<h3>📈 Любой интересный вам масштаб движений!</h3>
					<p>Выбирайте любой интересующий вас таймфрэйм от дневки до минутки.</p>
				</Feature>
				<Feature>
					<h3>🧰 Любая модель!</h3>
					<p>Выбирайте любые разработанные в этом проекте модели: классификация, регрессия и тд.</p>
				</Feature>
			</Features>
		</HomeContainer>
	);
}

export default HomePage;