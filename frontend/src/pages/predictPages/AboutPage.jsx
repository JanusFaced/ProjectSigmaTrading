import {
    AboutContainer,
    Section,
    AuthorCard,
    AuthorDetails,
    RequisitesCard,
    RequisiteItem,
    RequisiteLabel,
    RequisiteValue,
    RequisitesNote,
    ContactSection
} from './AboutPage.styles.jsx';

function AboutPage() {
    return (
        <AboutContainer>
            <h1>О проекте</h1>
            
            <Section>
                <h2>📖 Описание проекта PREDICT</h2>
                <p>
                    Это экспериментальный проект для предоставления
                    простых возможностей машинного обучения на рынке криптовалют.
                </p>
                <p>
                    Проект использует модель CatBoost для предсказания движения цены.
                </p>
                <p>
                    На сайте представлена страница где сразу открываются заранее
                    предопределённые сборки для просмотра прогнозов.
                </p>
            </Section>

            <Section>
                <h2>👨‍💻 About author</h2>
                <AuthorCard>
                    <AuthorDetails>
                        <p><strong>Name:</strong> Alexander</p>
                        <p><strong>Role:</strong> ML-developer</p>
                        <p><strong>Stack:</strong> Docker, Python, Sklearn, Flask, React.js</p>
                    </AuthorDetails>
                </AuthorCard>
            </Section>

            <ContactSection>
                <h2>📞 Контакты</h2>
                <p>Email: <a href="mailto:Yascov64@gmail.com">Yascov64@gmail.com</a></p>
                <p>LinkedIn: <a href="https://www.linkedin.com/in/alexander-yascov-b22116228">alexander-yascov-b22116228</a></p>
                <p>GitHub: <a href="https://github.com/JanusFaced">github.com/JanusFaced</a></p>
            </ContactSection>
        </AboutContainer>
    );
}

export default AboutPage;