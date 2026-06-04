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
            tech: 'CatBoost, SKlearn, FastAPI', 
            path: '/signals',
            description: 'Генерация торговых сигналов на основе ML моделей',
            techList: ['CatBoost', 'SKlearn', 'FastAPI', 'PostgreSQL']
        },
        { 
            title: 'Предсказатель графика', 
            tech: 'Darts, CatBoost, FastAPI', 
            path: '/predict',
            description: 'Предсказание движения цены криптовалют',
            techList: ['Darts', 'CatBoost', 'FastAPI', 'PostgreSQL']
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
                                <ProjectLink 
                                    as={Link}
                                    to={project.path}
                                >
                                    <h3>
                                        {project.title}
                                        <ExternalIcon> → ПЕРЕЙТИ В ПРОЕКТ </ExternalIcon>
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