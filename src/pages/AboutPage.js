function AboutPage() {
	return (
		<div className="about-page">
			<h1>О проекте</h1>
			
			<section className="project-description">
				<h2>📖 Описание проекта</h2>
				<p>
						Это экспериментальный показательный проект для предоставления
					простых возможностей машинного обучения на финансовых рынках.
					В частности на рынке криптовалют.
				</p>
				<p>
						Проект использует модель CatBoost для классификации рыночных фаз
					в одном способе. А так же использует данную модель для задачи
					регрессии с целью предсказания временного ряда в другом способе.
				</p>
				<p>
						На сайте представлена страница где сразу открываются заранее
					предопределённые сборки. А так же можно посмотреть свой частный
					вариант. Можно выбрать актив, модель, таймфрэйм. Сайт выглядит
					как уложенные карточки где показан актив, модель, таймфрэйм, сигнал,
					предположительное время жизни сигнала, среднее время жизни сигналов
					и их максимальное и минимальное время жизни на истории.
					Так же показана годовая доходность полученая с помощью простых
					бэкстестов.
				</p>
			</section>

			<section className="author-info">
				<h2>👨‍💻 About author</h2>
				<div className="author-card">
					<div className="author-details">
						<p><strong>Name:</strong> Alexander</p>
						<p><strong>Rule:</strong> ML-developer</p>
						<p><strong>Stack:</strong> Docker, Python, Sklearn, Flask, React.js</p>
					</div>
				</div>
			</section>

			<section className="requisites">
				<h2>💳 Реквизиты</h2>
				<div className="requisites-card">
					<div className="requisite-item">
						<span className="requisite-label">Crypto:</span>
						<span>Bitcoin</span>
					</div>
					<div className="requisite-item">
						<span className="requisite-label">Address:</span>
						<span>1234567abcdfg</span>
					</div>
				</div>
				<p className="requisites-note">
					* Внимательно проверяйте все данные!
				</p>
			</section>

			<section className="contact">
				<h2>📞 Контакты</h2>
				<p>Email: <a href="mailto:Yascov64@gmail.com">Yascov64@gmail.com</a></p>
				<p>LinkedIn: <a href="https://www.linkedin.com/in/alexander-yascov-b22116228">alexander-yascov-b22116228</a></p>
				<p>GitHub: <a href="https://github.com/JanusFaced">github.com/JanusFaced</a></p>
			</section>
		</div>
	);
}

export default AboutPage;