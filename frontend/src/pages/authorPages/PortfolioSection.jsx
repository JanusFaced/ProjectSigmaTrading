import { useNavigate } from 'react-router-dom';
import {
    PortfolioSectionMain,
    Container,
    PortfolioGrid,
    ProjectCard,
    ProjectImage,
    ProjectInfo,
    TechStack,
    TechBadge,
    ClickableCard,
    LogoImage
} from './PortfolioSection.styles.jsx';

function PortfolioSection() {
    const pstName = '/images/pst_name_cut.png';

    const navigate = useNavigate();

    const projects = [
        { 
            title: 'Торговые роботы', 
            tech: 'Pandas, NumPy, Numba, SQLAlchemy, FastAPI, CCXT, Celery, Redis, PostgreSQL',
            path: '/signals',
            description: 'Параллельный запуск различных торговых стратегий и их оценка в реальном времени',
            techList: ['Pandas', 'NumPy', 'Numba', 'SQLAlchemy', 'FastAPI', 'CCXT', 'Celery', 'Redis', 'PostgreSQL']
        }
    ];

    const handleCardClick = (path) => {
        navigate(path);
    };

    return (
        <PortfolioSectionMain>
            <Container>
                <h2>Мой основной проект</h2>
                <PortfolioGrid>
                    {projects.map((project, idx) => (
                        <ProjectCard 
                            key={idx}
                            onClick={() => handleCardClick(project.path)}
                        >
                            <ProjectImage>
                                <LogoImage src={pstName} alt="PST Logo" />
                            </ProjectImage>
                            <ProjectInfo>
                                <h3>
                                    {project.title}
                                    <ClickableCard>🔗</ClickableCard>
                                </h3>
                                <p>{project.description || project.tech}</p>
                                <TechStack>
                                    {project.techList.map((tech, techIdx) => (
                                        <TechBadge key={techIdx}>{tech}</TechBadge>
                                    ))}
                                </TechStack>
                                <ClickableCard>
                                    Нажмите на карточку, чтобы перейти →
                                </ClickableCard>
                            </ProjectInfo>
                        </ProjectCard>
                    ))}
                </PortfolioGrid>
            </Container>
        </PortfolioSectionMain>
    );
}

export default PortfolioSection;