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
            title: 'DS/ML/AI Development',
            icon: '🤖',
            desc: 'Development of machine learning models, deep learning models, and artificial intelligence systems',
            tech: ['SKlearn', 'PyTorch', 'CatBoost', 'TensorFlow', 'Keras', 'Darts']
        },
        {
            title: 'DevOps Engineering',
            icon: '🚀',
            desc: 'CI/CD setup, containerization, orchestration, and infrastructure automation',
            tech: ['Linux', 'Docker', 'Kubernetes', 'GitHub', 'GitLab', 'Terraform', 'Ansible']
        },
        {
            title: 'FullStack Development',
            icon: '💻',
            desc: 'Building full-fledged web applications from scratch: from frontend to backend and database',
            tech: ['React.js', 'FastAPI', 'PostgreSQL', 'Node.js', 'SQLAlchemy', 'Celery', 'Redis']
        }
    ];

    return (
        <ServicesSection>
            <Container>
                <h2>What I'm doing</h2>
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