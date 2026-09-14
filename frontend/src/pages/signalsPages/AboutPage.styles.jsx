import styled from 'styled-components';
import { NavLink } from 'react-router-dom';

export const AboutContainer = styled.div`
    min-height: 100vh;
    padding: 3.5rem 1.25rem 5rem;

    color: #dbe4ee;
    background:
        radial-gradient(
            circle at 50% 0%,
            rgba(40, 83, 132, 0.2) 0%,
            rgba(11, 15, 20, 0) 42%
        ),
        #0b0f14;

    h1 {
        max-width: 1000px;
        margin: 0 auto 3rem;

        color: #f1f5f9;
        font-size: clamp(2.2rem, 5vw, 3.4rem);
        font-weight: 700;
        line-height: 1.1;
        letter-spacing: -0.05em;
        text-align: center;
    }

    h2 {
        margin: 0 0 1.25rem;

        color: #e7edf5;
        font-size: 1.45rem;
        font-weight: 600;
        line-height: 1.35;
        letter-spacing: -0.02em;
    }

    @media (max-width: 768px) {
        padding: 2.5rem 1rem 3.5rem;

        h1 {
            margin-bottom: 2rem;
        }

        h2 {
            font-size: 1.2rem;
        }
    }
`;

export const Section = styled.section`
    max-width: 1000px;
    margin: 0 auto 1.25rem;
    padding: 1.75rem;

    background: rgba(20, 27, 36, 0.88);
    border: 1px solid rgba(255, 255, 255, 0.075);
    border-radius: 10px;
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.18);

    transition:
        transform 0.25s ease,
        border-color 0.25s ease,
        box-shadow 0.25s ease;

    &:hover {
        border-color: rgba(138, 180, 248, 0.22);
        box-shadow: 0 16px 36px rgba(0, 0, 0, 0.25);
        transform: translateY(-2px);
    }

    p {
        margin: 0 0 1rem;

        color: #9daaba;
        font-size: 0.98rem;
        line-height: 1.75;

        &:last-child {
            margin-bottom: 0;
        }
    }

    @media (max-width: 768px) {
        padding: 1.25rem;
        margin-bottom: 1rem;

        p {
            font-size: 0.93rem;
        }
    }
`;

export const AuthorCard = styled.div`
    margin-top: 1rem;
    padding: 1.25rem;

    background: #111820;
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 8px;
`;

export const AuthorDetails = styled.div`
    p {
        margin: 0;
        padding: 0.75rem 0;

        color: #aebaca;
        font-size: 0.92rem;
        line-height: 1.6;

        border-bottom: 1px solid rgba(255, 255, 255, 0.06);

        &:first-child {
            padding-top: 0;
        }

        &:last-child {
            padding-bottom: 0;
            border-bottom: none;
        }

        strong {
            display: inline-block;
            min-width: 155px;
            color: #e3eaf2;
            font-weight: 600;
        }
    }

    @media (max-width: 650px) {
        p strong {
            display: block;
            min-width: auto;
            margin-bottom: 0.25rem;
        }
    }
`;

export const RequisitesCard = styled.div`
    padding: 1.25rem;

    background: #111820;
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 8px;
`;

export const RequisiteItem = styled.div`
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;

    padding: 0.8rem 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);

    &:last-child {
        border-bottom: none;
    }

    @media (max-width: 768px) {
        align-items: flex-start;
        flex-direction: column;
        gap: 0.35rem;
    }
`;

export const RequisiteLabel = styled.span`
    color: #8ab4f8;
    font-size: 0.9rem;
    font-weight: 600;
`;

export const RequisiteValue = styled.span`
    max-width: 100%;
    padding: 0.35rem 0.55rem;

    overflow-wrap: anywhere;
    color: #c9d4e0;
    background: #0b0f14;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 5px;

    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', monospace;
    font-size: 0.8rem;

    @media (max-width: 768px) {
        width: 100%;
    }
`;

export const RequisitesNote = styled.p`
    margin-top: 1rem !important;

    color: #718093 !important;
    font-size: 0.78rem !important;
    font-style: italic;
    text-align: center;
`;

export const ContactSection = styled(Section)`
    a {
        color: #8ab4f8;
        text-decoration: none;
        overflow-wrap: anywhere;

        transition:
            color 0.2s ease,
            text-decoration-color 0.2s ease;

        &:hover {
            color: #b5d2ff;
            text-decoration: underline;
            text-underline-offset: 3px;
        }

        &:focus-visible {
            outline: 2px solid #8ab4f8;
            outline-offset: 3px;
            border-radius: 3px;
        }
    }

    p {
        margin: 0;
        padding: 0.75rem 0;

        border-bottom: 1px solid rgba(255, 255, 255, 0.06);

        &:last-child {
            margin-bottom: 0;
            border-bottom: none;
        }
    }
`;

export const AddressCode = styled.code`
    padding: 0.15rem 0.4rem;

    color: #a9caff;
    background: #111820;
    border: 1px solid rgba(138, 180, 248, 0.18);
    border-radius: 4px;

    font-size: 0.85rem;
`;

export const SectionIcon = styled.span`
    margin-right: 0.55rem;

    font-size: 1.7rem;
    vertical-align: middle;
`;

export const SectionHeader = styled.div`
    display: flex;
    align-items: center;
    margin-bottom: 1.25rem;

    h2 {
        margin-bottom: 0;
    }
`;

export const VisitButton = styled(NavLink)`
    display: inline-flex;
    align-items: center;
    justify-content: center;

    margin-top: 1.5rem;
    padding: 0.8rem 1.3rem;

    color: #07111d;
    background: #8ab4f8;
    border: 1px solid #8ab4f8;
    border-radius: 7px;

    font-size: 0.92rem;
    font-weight: 600;
    text-align: center;
    text-decoration: none;

    box-shadow: 0 8px 22px rgba(138, 180, 248, 0.14);

    transition:
        color 0.25s ease,
        background 0.25s ease,
        border-color 0.25s ease,
        box-shadow 0.25s ease,
        transform 0.25s ease;

    &:hover {
        color: #ffffff;
        background: #6f9fe8;
        border-color: #6f9fe8;
        box-shadow: 0 10px 28px rgba(138, 180, 248, 0.24);
        transform: translateY(-2px);
    }

    &:focus-visible {
        outline: 2px solid #8ab4f8;
        outline-offset: 3px;
    }

    @media (max-width: 768px) {
        width: 100%;
        padding: 0.9rem 1rem;
    }
`;
