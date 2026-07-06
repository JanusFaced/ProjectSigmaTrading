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
            desc: 'Разработка моделей машинного обучения, глубокого обучения и систем искусственного интеллекта',
            tech: ['SKlearn', 'PyTorch', 'CatBoost', 'TensorFlow', 'Keras', 'Darts']
        },
        {
            title: 'DevOps-инженерия',
            icon: '🚀',
            desc: 'Настройка CI/CD, контейнеризация, оркестрация и автоматизация инфраструктуры',
            tech: ['Linux', 'Docker', 'Kubernetes', 'GitHub', 'GitLab', 'Terraform', 'Ansible']
        },
        {
            title: 'FullStack-разработка',
            icon: '💻',
            desc: 'Создание полноценных веб-приложений с нуля: от фронтенда до бэкенда и БД',
            tech: ['React.js', 'FastAPI', 'PostgreSQL', 'Node.js', 'SQLAlchemy', 'Celery', 'Redis']
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