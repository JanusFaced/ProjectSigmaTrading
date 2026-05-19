import { useState, useEffect } from 'react';
import CryptoCard from '../components/CryptoCard.js';

function AnalystPage() {
	const [cards, setCards] = useState([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState(null);

	useEffect(() => {
		const loadCards = async () => {
			try {
				const response = await fetch('http://localhost:8000/getTableAnalyst');
				
				if (!response.ok) {
					throw new Error(`HTTP error! status: ${response.status}`);
				}
				
				const data = await response.json();
				setCards(data);
			} catch (error) {
				console.error('Ошибка загрузки:', error);
				setError(error.message);
				alert('Не удалось загрузить карточки');
			} finally {
				setLoading(false);
			}
		};

		loadCards();
	}, []);

	if (loading) {
		return (
			<div className="cards-page">
				<h1>Аналитика</h1>
				<div className="load-section">
					<p>Загрузка данных...</p>
					<div className="spinner">⏳</div>
				</div>
			</div>
		);
	}

	if (error) {
		return (
			<div className="cards-page">
				<h1>Аналитика</h1>
				<div className="load-section">
					<p>❌ Ошибка: {error}</p>
					<button onClick={() => window.location.reload()}>
						Попробовать снова
					</button>
				</div>
			</div>
		);
	}

	return (
		<div className="cards-page">
			<h1>Аналитика</h1>
			
			{cards.length === 0 ? (
				<div className="load-section">
					<p>📭 Нет данных для отображения</p>
				</div>
			) : (
				<div className="cards-list">
					{cards.map(card => (
						<CryptoCard key={card.id} data={card} />
					))}
				</div>
			)}
		</div>
	);
}

export default AnalystPage;