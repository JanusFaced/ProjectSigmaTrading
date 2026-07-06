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
				<h1>Добро пожаловать в PST v2.0!</h1>
				<p>Экспериментальный проект в области финтеха открытый для использования каждого!</p>
				<HeroButtons>
					<PrimaryButton as={Link} to="/signals/analyst">
						Перейти к странице с роботами →
					</PrimaryButton>
					<SecondaryButton as={Link} to="/signals/about">
						О проекте
					</SecondaryButton>
				</HeroButtons>
			</Hero>

			<Features>
				<Feature>
					<h3>🪙 Стратегии на разных активов!</h3>
					<p>Смотрите результаты стратегий на активах предоставленных в аналитике.</p>
				</Feature>
				<Feature>
					<h3>📈 Стратегии на разных таймфрэймах!</h3>
					<p>Работа на нескольких ТФ одновременно.</p>
				</Feature>
				<Feature>
					<h3>🧰 Pandas + NumPy + Numba для генерации торговых сигналов</h3>
					<p>Pandas - таблицы. NumPy - математика. Numba - компиляция.</p>
				</Feature>
			</Features>
		</HomeContainer>
	);
}

export default HomePage;