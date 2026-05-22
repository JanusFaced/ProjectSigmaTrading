import {
    ServicesSection,
    Container,
    ServicesGrid,
    ServiceCard,
    ServiceIcon,
    TechStack,
    TechBadge,
    DecorativeLine
} from './SkillSection.styles.jsx';

function SkillSection() {
    const services = [
        {
            title: 'DS/ML/AI-разработка',
            icon: '🤖',
            desc: 'Разработка моделей машинного обучения и искусственного интеллекта',
            tech: ['SKlearn', 'PyTorch', 'CatBoost', 'TensorFlow']
        },
        {
            title: 'FullStack-разработка',
            icon: '💻',
            desc: 'Создание полноценных веб-приложений с нуля',
            tech: ['React', 'Flask', 'PostgreSQL', 'Node.js']
        }
    ];

    return (
        <ServicesSection>
            <Container>
                <h2>Что я делаю</h2>
                <ServicesGrid>
                    {services.map((service, idx) => (
                        <ServiceCard key={idx}>
                            <ServiceIcon>{service.icon}</ServiceIcon>
                            <h3>{service.title}</h3>
                            <p>{service.desc}</p>
                            <TechStack>
                                {service.tech.map((tech, techIdx) => (
                                    <TechBadge key={techIdx}>{tech}</TechBadge>
                                ))}
                            </TechStack>
                        </ServiceCard>
                    ))}
                </ServicesGrid>
            </Container>
            <DecorativeLine />
        </ServicesSection>
    );
}

export default SkillSection;