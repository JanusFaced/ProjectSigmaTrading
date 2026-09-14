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
    const pstName = '/images/pst_name_cut_remove.png';

    const navigate = useNavigate();

    const projects = [
        { 
            title: 'Trading robots', 
            tech: 'Polars, NumPy, Numba, SQLAlchemy, CCXT, Celery, Redis, PostgreSQL',
            path: '/signals',
            description: 'Simultaneous launch of various trading strategies and their real-time evaluation',
            techList: ['Polars', 'NumPy', 'Numba', 'SQLAlchemy', 'CCXT', 'Celery', 'Redis', 'PostgreSQL']
        }
    ];

    const handleCardClick = (path) => {
        navigate(path);
    };

    return (
        <PortfolioSectionMain>
            <Container>
                <h2>My main project</h2>
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
                                    Tap the card to go to →
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