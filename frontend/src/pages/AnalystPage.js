import { useState } from 'react';

function AnalystPage() {
	const [users, setUsers] = useState([]);
	const [loading, setLoading] = useState(false);
	const [loaded, setLoaded] = useState(false);

	const loadUsers = async () => {
		setLoading(true);
		try {
			const response = await fetch('http://localhost:8000/users');
			const data = await response.json();
			setUsers(data);
			setLoaded(true);
		} catch (error) {
			console.error('Ошибка загрузки:', error);
			alert('Не удалось загрузить карточки');
		} finally {
			setLoading(false);
		}
	};

	return (
		<div className="users-page">
			<h1>Аналитика</h1>
			
			{!loaded ? (
				<div className="load-section">
					<p>Нажмите кнопку, чтобы загрузить карточки!</p>
					<button onClick={loadUsers} disabled={loading}>
						{loading ? 'Загрузка...' : 'Загрузить карточки'}
					</button>
				</div>
			) : (
				<div className="users-list">
					{users.map(user => (
						<div key={user.id} className="user-card">
							<h3>{user.name}</h3>
							<p>📧 {user.email}</p>
							<p>📞 {user.phone}</p>
							<p>🏢 {user.company_name}</p>
						</div>
					))}
				</div>
			)}
		</div>
	);
}

export default AnalystPage;