import { useState } from 'react';
import {
    ContactSectionMain,
    Container,
    ContactLinks,
    ContactItem,
    ContactIcon,
    ContactText,
    SocialGrid,
    SocialLink,
    CopyButton
} from './ContactSection.styles.jsx';

function ContactSection() {
    const [copied, setCopied] = useState(false);

    const copyToClipboard = (text) => {
        navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <ContactSectionMain id="contact">
            <Container>
                <h2>Let's work together!</h2>
                <p>I’m ready to discuss your project or idea. Just drop me a line!</p>
                
                <ContactLinks>
                    <ContactItem 
                        href="mailto:Yascov64@gmail.com"
                        onClick={(e) => {
                            e.preventDefault();
                            window.location.href = "mailto:Yascov64@gmail.com";
                        }}
                    >
                        <ContactIcon>📧</ContactIcon>
                        <ContactText>Yascov64@gmail.com</ContactText>
                        <CopyButton onClick={(e) => {
                            e.stopPropagation();
                            copyToClipboard("Yascov64@gmail.com");
                        }}>
                            {copied ? '✓' : '📋'}
                        </CopyButton>
                    </ContactItem>
                    
                    <ContactItem href="tel:+375336368230">
                        <ContactIcon>📞</ContactIcon>
                        <ContactText>🇧🇾 +375 (33) 636-82-30</ContactText>
                        <CopyButton onClick={(e) => {
                            e.stopPropagation();
                            copyToClipboard("+375336368230");
                        }}>
                            {copied ? '✓' : '📋'}
                        </CopyButton>
                    </ContactItem>
                    
                    <ContactItem 
                        href="https://github.com/JanusFaced"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        <ContactIcon>🐙</ContactIcon>
                        <ContactText>github.com/JanusFaced</ContactText>
                    </ContactItem>
                </ContactLinks>
                
                <SocialGrid>
                    <SocialLink 
                        href="https://www.linkedin.com/in/alexander-yascov"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        💼 LinkedIn
                    </SocialLink>
                    <SocialLink 
                        href="https://t.me/JanusFacedOfficial"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        📱 Telegram
                    </SocialLink>
                </SocialGrid>
            </Container>
        </ContactSectionMain>
    );
}

export default ContactSection;