import {
    WelcomeHeader,
    Container,
    Tagline,
    ScrollButton
} from './WelcomeSection.styles.jsx';

function WelcomeSection() {
    // Функция для плавного скролла вниз (опционально)
    const scrollToNext = () => {
        window.scrollBy({
            top: window.innerHeight,
            behavior: 'smooth'
        });
    };

    return (
        <WelcomeHeader>
            <Container>
                <h1>Добро пожаловать на мою сайт-визитку!</h1>
                <Tagline>
                    Здесь я расскажу всё о себе и о моих пет-проектах
                </Tagline>
                
                {/* Опционально - кнопка для скролла */}
                <ScrollButton onClick={scrollToNext}>
                    Узнать больше ↓
                </ScrollButton>
            </Container>
        </WelcomeHeader>
    );
}

export default WelcomeSection;