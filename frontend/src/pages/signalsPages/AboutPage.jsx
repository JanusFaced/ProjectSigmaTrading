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
    ContactSection,
    VisitButton
} from './AboutPage.styles.jsx';

function AboutPage() {
    return (
        <AboutContainer>
            <h1>О проекте</h1>
            
            <Section>
                <h2>📖 Описание проекта ProjectSigmaTrading</h2>
                <p>
                    ProjectSigmaTrading - проект нацеленный на эксперименты в применении автоматизации торговли на финансовых рынках.
                </p>
                <p>
                    Проект использует различные популярные идеи, а так же личные идеи для реализации максимальной стабильности и доходности.
                </p>
                <p>
                    На сайте представлена страница где можно наблюдать за статистикой работы различных стратегий.
                </p>
                <p>
                    Каждая стратегия представляет из себя комбинацию алгоритма + актива + таймфрэйма.
                </p>
            </Section>

            <Section>
                <h2>👨‍💻 About author</h2>
                <AuthorCard>
                    <AuthorDetails>
                        <p><strong>Name:</strong> Alexander</p>
                        <p><strong>Role:</strong> DS, ML, AI, DevOps и FullStack разработчик</p>
                        <p><strong>Stack (ML):</strong> SKlearn, PyTorch, CatBoost, TensorFlow, Keras, Darts</p>
                        <p><strong>Stack (DevOps):</strong> Linux, Docker, Kubernetes, GitHub, GitLab, Terraform, Ansible</p>
                        <p><strong>Stack (FullStack):</strong> React.js, FastAPI, PostgreSQL, Node.js, SQLAlchemy, Celery, Redis</p>
                    </AuthorDetails>
                </AuthorCard>
                
                <VisitButton to="/">
                    🌐 Посмотреть сайт-визитку
                </VisitButton>
            </Section>

            <ContactSection>
                <h2>📞 Контакты</h2>
                <p>Email: <a href="mailto:Yascov64@gmail.com">Yascov64@gmail.com</a></p>
                <p>LinkedIn: <a href="https://www.linkedin.com/in/alexander-yascov">alexander-yascov</a></p>
                <p>GitHub: <a href="https://github.com/JanusFaced">github.com/JanusFaced</a></p>
                <p>Telegram: <a href="https://t.me/JanusFacedOfficial">@JanusFacedOfficial</a></p>
            </ContactSection>
        </AboutContainer>
    );
}

export default AboutPage;