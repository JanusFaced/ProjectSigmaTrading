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
                <h1>Alexander Yascov</h1>
                <AuthorTagline>DevOps, FullStack and ML-developer</AuthorTagline>
                <Description>
                    I solve business challenges at the intersection of development and infrastructure. 
                    I build systems from concept to production!
                </Description>
                
                <CTAButton to="/contact">
                    Contact me
                </CTAButton>

                <Stats>
                    <StatItem>
                        <h3>Full development cycle</h3>
                        <p>From idea to production</p>
                    </StatItem>
                    <StatItem>
                        <h3>Broad technology stack</h3>
                        <p>ML · DevOps · FullStack</p>
                    </StatItem>
                    <StatItem>
                        <h3>100% quality</h3>
                        <p>They solve problems of any complexity</p>
                    </StatItem>
                </Stats>
            </Container>
        </HeroSection>
    );
}

export default AuthorSection;