import styled from 'styled-components';

export const HomeContainer = styled.div`
    min-height: 100vh;
    padding: 4rem 1.25rem 5rem;

    color: #f1f5f9;
    background:
        radial-gradient(
            circle at 50% 0%,
            rgba(40, 83, 132, 0.24) 0%,
            rgba(11, 15, 20, 0) 42%
        ),
        #0b0f14;

    @media (max-width: 768px) {
        padding: 2.5rem 1rem 3rem;
    }
`;

export const Hero = styled.div`
    max-width: 850px;
    margin: 0 auto;
    padding: 5rem 1.25rem 4.5rem;
    text-align: center;

    h1 {
        margin: 0 0 1.25rem;

        color: #f8fafc;
        font-size: clamp(2.25rem, 6vw, 4.25rem);
        font-weight: 700;
        line-height: 1.08;
        letter-spacing: -0.055em;
    }

    p {
        max-width: 650px;
        margin: 0 auto 2.5rem;

        color: #9caabd;
        font-size: clamp(1rem, 2vw, 1.25rem);
        line-height: 1.65;
    }

    @media (max-width: 768px) {
        padding: 3.5rem 0.5rem 3rem;
    }
`;

export const HeroButtons = styled.div`
    display: flex;
    justify-content: center;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.85rem;

    @media (max-width: 480px) {
        flex-direction: column;
    }
`;

const BaseButton = styled.div`
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-height: 48px;
    padding: 0.8rem 1.35rem;

    border-radius: 7px;

    font-size: 0.95rem;
    font-weight: 600;
    line-height: 1;
    text-decoration: none;
    white-space: nowrap;

    cursor: pointer;
    transition:
        color 0.25s ease,
        background 0.25s ease,
        border-color 0.25s ease,
        box-shadow 0.25s ease,
        transform 0.25s ease;

    &:hover {
        transform: translateY(-2px);
    }

    &:active {
        transform: translateY(0);
    }

    &:focus-visible {
        outline: 2px solid #8ab4f8;
        outline-offset: 3px;
    }

    @media (max-width: 480px) {
        width: 100%;
        max-width: 280px;
    }
`;

export const PrimaryButton = styled(BaseButton)`
    color: #07111d;
    background: #8ab4f8;
    border: 1px solid #8ab4f8;
    box-shadow: 0 8px 24px rgba(138, 180, 248, 0.16);

    &:hover {
        color: #ffffff;
        background: #6f9fe8;
        border-color: #6f9fe8;
        box-shadow: 0 10px 28px rgba(138, 180, 248, 0.24);
    }
`;

export const SecondaryButton = styled(BaseButton)`
    color: #c6d0dd;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.16);

    &:hover {
        color: #f1f5f9;
        background: rgba(255, 255, 255, 0.07);
        border-color: rgba(138, 180, 248, 0.55);
    }
`;

export const Features = styled.div`
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 1.25rem;

    max-width: 1160px;
    margin: 0 auto;
    padding: 1rem 0;

    @media (max-width: 900px) {
        grid-template-columns: 1fr;
        max-width: 650px;
    }
`;

export const Feature = styled.div`
    min-height: 220px;
    padding: 1.75rem;

    text-align: left;

    background: rgba(20, 27, 36, 0.78);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.18);

    transition:
        transform 0.25s ease,
        border-color 0.25s ease,
        background 0.25s ease,
        box-shadow 0.25s ease;

    &:hover {
        transform: translateY(-5px);

        background: rgba(24, 33, 44, 0.92);
        border-color: rgba(138, 180, 248, 0.28);
        box-shadow: 0 18px 38px rgba(0, 0, 0, 0.28);
    }

    h3 {
        margin: 0 0 1rem;

        color: #e7edf5;
        font-size: 1.2rem;
        font-weight: 600;
        line-height: 1.4;
        letter-spacing: -0.015em;
    }

    p {
        margin: 0;

        color: #929eae;
        font-size: 0.95rem;
        line-height: 1.7;
    }

    @media (max-width: 900px) {
        min-height: auto;
    }

    @media (max-width: 480px) {
        padding: 1.4rem;
    }
`;
