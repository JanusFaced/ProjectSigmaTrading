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
				<h1>Добро пожаловать в PREDICT!</h1>
				<p>Экспериментальный проект в области предсказания движения цен на активы!</p>
				<HeroButtons>
					<PrimaryButton as={Link} to="/predict/analyst">
						Посмотреть сгенерированные прогнозы с помощью ML моделей →
					</PrimaryButton>
					<SecondaryButton as={Link} to="/predict/about">
						О проекте
					</SecondaryButton>
				</HeroButtons>
			</Hero>

			<Features>
				<Feature>
					<h3>🪙 Доступны несколько активов!</h3>
					<p>Смотрите прогнозы по нескольким основным активам на криптобиржах.</p>
				</Feature>
				<Feature>
					<h3>📈 Доступны разные таймфрэймы!</h3>
					<p>Смотрите прогнозы на разных таймфрэймах.</p>
				</Feature>
				<Feature>
					<h3>🧰 CatBoost для задачи регрессии</h3>
					<p>Для задачи регресии была использована CatBoost для регрессии.</p>
				</Feature>
			</Features>
		</HomeContainer>
	);
}

export default HomePage;