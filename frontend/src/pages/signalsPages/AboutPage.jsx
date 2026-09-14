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
            <h1>About the Project</h1>
            
            <Section>
                <h2>📖 Project Description of ProjectSigmaTrading</h2>
                <p>
                    ProjectSigmaTrading - a project aimed at experimenting with the application of automated trading in financial markets.
                </p>
                <p>
                    The project employs various popular concepts as well as original ideas to achieve maximum stability and profitability.
                </p>
                <p>
                    The website features a page where you can view performance statistics for various strategies.
                </p>
                <p>
                    Each strategy consists of a combination of an algorithm, an asset, and a timeframe.
                </p>
            </Section>

            <Section>
                <h2>👨‍💻 About author</h2>
                <AuthorCard>
                    <AuthorDetails>
                        <p><strong>Name:</strong> Alexander ;</p>
                        <p><strong>Role:</strong> DevOps, FullStack and ML developer ;</p>
                        <p><strong>Stack (DevOps):</strong> Linux, Docker, Kubernetes, GitHub, GitLab, Terraform, Ansible ;</p>
                        <p><strong>Stack (FullStack):</strong> React.js, FastAPI, PostgreSQL, Node.js, SQLAlchemy, Celery, Redis ;</p>
                        <p><strong>Stack (ML):</strong> SKlearn, PyTorch, CatBoost, TensorFlow, Keras, Darts .</p>
                    </AuthorDetails>
                </AuthorCard>
                
                <VisitButton to="/">
                    🌐 View the brochure website
                </VisitButton>
            </Section>

            <ContactSection>
                <h2>📞 Contact Information</h2>
                <p>Email: <a href="mailto:Yascov64@gmail.com">Yascov64@gmail.com</a></p>
                <p>LinkedIn: <a href="https://www.linkedin.com/in/alexander-yascov">alexander-yascov</a></p>
                <p>GitHub: <a href="https://github.com/JanusFaced">github.com/JanusFaced</a></p>
                <p>Telegram: <a href="https://t.me/JanusFacedOfficial">@JanusFacedOfficial</a></p>
            </ContactSection>
        </AboutContainer>
    );
}

export default AboutPage;