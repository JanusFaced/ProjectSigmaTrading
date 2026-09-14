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
				<h1>Welcome to PST v2.0!</h1>
				<p>An experimental fintech project open for everyone to use!</p>
				<HeroButtons>
					<PrimaryButton as={Link} to="/signals/analyst">
						Go to the robots page →
					</PrimaryButton>
					<SecondaryButton as={Link} to="/signals/about">
						About the Project
					</SecondaryButton>
				</HeroButtons>
			</Hero>

			<Features>
				<Feature>
					<h3>🪙 Strategies for various assets!</h3>
					<p>View the results of strategies applied to the assets featured in the analysis</p>
				</Feature>
				<Feature>
					<h3>📈 Strategies based on various analysis methods!</h3>
					<p>Working with various decision-making algorithms</p>
				</Feature>
				<Feature>
					<h3>🧰 Polars + NumPy + Numba for trading signal generation</h3>
					<p>Polars - dataframe. NumPy - mathematics. Numba - compilation</p>
				</Feature>
			</Features>
		</HomeContainer>
	);
}

export default HomePage;