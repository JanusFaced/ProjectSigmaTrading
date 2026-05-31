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
				<h1>Добро пожаловать в SIGNALS!</h1>
				<p>Экспериментальный проект в области финтеха открытый для использования каждого!</p>
				<HeroButtons>
					<PrimaryButton as={Link} to="/signals/analyst">
						Посмотреть сгенерированные сигналы с помощью ML моделей →
					</PrimaryButton>
					<SecondaryButton as={Link} to="/signals/about">
						О проекте
					</SecondaryButton>
				</HeroButtons>
			</Hero>

			<Features>
				<Feature>
					<h3>🪙 Доступны несколько активов!</h3>
					<p>Смотрите любой актив из предоставленных в аналитике, что существует на топовых криптобиржах.</p>
				</Feature>
				<Feature>
					<h3>📈 Доступны разные таймфрэймы!</h3>
					<p>Смотрите сигналы на нескольких ТФ одновременно.</p>
				</Feature>
				<Feature>
					<h3>🧰 CatBoost для генерации сигналов</h3>
					<p>Для классификации фаз рынка была выбрана модель CatBoost как более успевающая за рынками.</p>
				</Feature>
			</Features>
		</HomeContainer>
	);
}

export default HomePage;