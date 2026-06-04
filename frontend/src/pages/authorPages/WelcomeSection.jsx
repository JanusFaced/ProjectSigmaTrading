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
                <h1>Добро пожаловать на мою сайт-визитку!</h1>
                <Tagline>
                    Здесь я расскажу о себе и о моих пет-проектах
                </Tagline>
            </Container>
        </WelcomeHeader>
    );
}

export default WelcomeSection;