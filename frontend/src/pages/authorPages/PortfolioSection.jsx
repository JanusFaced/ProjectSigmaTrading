import { Link } from 'react-router-dom';
import {
    PortfolioSectionMain,
    Container,
    PortfolioGrid,
    ProjectCard,
    ProjectImage,
    ProjectInfo,
    ProjectLink,
    TechStack,
    TechBadge,
    ExternalIcon
} from './PortfolioSection.styles.jsx';

function PortfolioSection() {
    const projects = [
        { 
            title: 'Генератор сигналов', 
            tech: 'CatBoost, React, Flask', 
            path: '/signals',  // ← изменено с href на path
            description: 'Генерация торговых сигналов на основе ML моделей',
            techList: ['CatBoost', 'React', 'Flask', 'PostgreSQL']
        },
        { 
            title: 'Предсказатель графика', 
            tech: 'SKlearn, React, Flask', 
            path: '/predict',   // ← изменено с href на path
            description: 'Предсказание движения цены криптовалют',
            techList: ['SKlearn', 'React', 'Flask', 'Pandas']
        },
    ];

    return (
        <PortfolioSectionMain>
            <Container>
                <h2>Мои презентативные проекты</h2>
                <PortfolioGrid>
                    {projects.map((project, idx) => (
                        <ProjectCard key={idx}>
                            <ProjectImage />
                            <ProjectInfo>
                                {/* Используем Link вместо обычной ссылки */}
                                <ProjectLink 
                                    as={Link}
                                    to={project.path}
                                >
                                    <h3>
                                        {project.title}
                                        <ExternalIcon>→</ExternalIcon>
                                    </h3>
                                </ProjectLink>
                                <p>{project.description || project.tech}</p>
                                <TechStack>
                                    {project.techList.map((tech, techIdx) => (
                                        <TechBadge key={techIdx}>{tech}</TechBadge>
                                    ))}
                                </TechStack>
                            </ProjectInfo>
                        </ProjectCard>
                    ))}
                </PortfolioGrid>
            </Container>
        </PortfolioSectionMain>
    );
}

export default PortfolioSection;