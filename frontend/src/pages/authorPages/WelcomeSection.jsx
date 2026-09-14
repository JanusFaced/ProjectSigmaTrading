import {
    WelcomeHeader,
    Container,
    Tagline,
    ScrollButton
} from './WelcomeSection.styles.jsx';

function WelcomeSection() {
    return (
        <WelcomeHeader>
            <Container>
                <h1>Welcome to my personal website!</h1>
                <Tagline>
                    Here I will tell you about myself and my projects
                </Tagline>
            </Container>
        </WelcomeHeader>
    );
}

export default WelcomeSection;