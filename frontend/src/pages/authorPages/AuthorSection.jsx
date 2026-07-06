import {
    HeroSection,
    Container,
    AuthorTagline,
    Description,
    CTAButton,
    SocialLinks,
    SocialIcon,
    Stats,
    StatItem
} from './AuthorSection.styles.jsx';

function AuthorSection() {
    return (
        <HeroSection>
            <Container>
                <h1>Александр Яськов</h1>
                <AuthorTagline>DS, ML, AI, DevOps и FullStack разработчик</AuthorTagline>
                <Description>
                    Решаю бизнес-задачи на стыке Data Science, разработки и инфраструктуры. Строю системы от идеи до продакшена!
                </Description>
                
                <CTAButton to="/contact">
                    Связаться со мной
                </CTAButton>

                <Stats>
                    <StatItem>
                        <h3>Полный цикл разработки</h3>
                        <p>От идеи до продакшена</p>
                    </StatItem>
                    <StatItem>
                        <h3>Широкий стек</h3>
                        <p>ML · DevOps · FullStack</p>
                    </StatItem>
                    <StatItem>
                        <h3>100% качество</h3>
                        <p>Решают задачи любой сложности</p>
                    </StatItem>
                </Stats>
            </Container>
        </HeroSection>
    );
}

export default AuthorSection;