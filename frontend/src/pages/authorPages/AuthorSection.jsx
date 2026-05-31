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
                <AuthorTagline>ML и FullStack разработчик</AuthorTagline>
                <Description>
                    Разрабатываю решения задач с применением машинного обучения. 
                    В частности решения для автоматизации финансовых задач.
                </Description>
                
                <CTAButton href="mailto:Yascov64@gmail.com">
                    Связаться по почте
                </CTAButton>
                
                {/* Опционально: социальные ссылки */}
                <SocialLinks>
                    <SocialIcon href="https://github.com/JanusFaced" target="_blank" rel="noopener noreferrer">
                        GitHub
                    </SocialIcon>
                    <SocialIcon href="https://www.linkedin.com/in/alexander-yascov-b22116228" target="_blank" rel="noopener noreferrer">
                        LinkedIn
                    </SocialIcon>
                </SocialLinks>
                <Stats>
                    <StatItem>
                        <h3>5+</h3>
                        <p>лет опыта</p>
                    </StatItem>
                    <StatItem>
                        <h3>3+</h3>
                        <p>комплексных проекта</p>
                    </StatItem>
                    <StatItem>
                        <h3>100%</h3>
                        <p>качество</p>
                    </StatItem>
                </Stats>
            </Container>
        </HeroSection>
    );
}

export default AuthorSection;