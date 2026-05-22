import {
    AboutContainer,
    Section,
    AuthorCard,
    AuthorDetails,
    RequisitesCard,
    RequisiteItem,
    RequisiteLabel,
    RequisiteValue,
    RequisitesNote,
    ContactSection
} from './AboutPage.styles.jsx';

function AboutPage() {
    return (
        <AboutContainer>
            <h1>О проекте</h1>
            
            <Section>
                <h2>📖 Описание проекта</h2>
                <p>
                    Это экспериментальный показательный проект для предоставления
                    простых возможностей машинного обучения на финансовых рынках.
                    В частности на рынке криптовалют.
                </p>
                <p>
                    Проект использует модель CatBoost для классификации рыночных фаз
                    в одном способе. А так же использует данную модель для задачи
                    регрессии с целью предсказания временного ряда в другом способе.
                </p>
                <p>
                    На сайте представлена страница где сразу открываются заранее
                    предопределённые сборки. А так же можно посмотреть свой частный
                    вариант. Можно выбрать актив, модель, таймфрэйм. Сайт выглядит
                    как уложенные карточки где показан актив, модель, таймфрэйм, сигнал,
                    предположительное время жизни сигнала, среднее время жизни сигналов
                    и их максимальное и минимальное время жизни на истории.
                    Так же показана годовая доходность полученая с помощью простых
                    бэкстестов.
                </p>
            </Section>

            <Section>
                <h2>👨‍💻 About author</h2>
                <AuthorCard>
                    <AuthorDetails>
                        <p><strong>Name:</strong> Alexander</p>
                        <p><strong>Role:</strong> ML-developer</p>
                        <p><strong>Stack:</strong> Docker, Python, Sklearn, Flask, React.js</p>
                    </AuthorDetails>
                </AuthorCard>
            </Section>

            <Section>
                <h2>💳 Реквизиты</h2>
                <RequisitesCard>
                    <RequisiteItem>
                        <RequisiteLabel>Crypto:</RequisiteLabel>
                        <RequisiteValue>Bitcoin</RequisiteValue>
                    </RequisiteItem>
                    <RequisiteItem>
                        <RequisiteLabel>Address:</RequisiteLabel>
                        <RequisiteValue>1234567abcdfg</RequisiteValue>
                    </RequisiteItem>
                </RequisitesCard>
                <RequisitesNote>
                    * Внимательно проверяйте все данные!
                </RequisitesNote>
            </Section>

            <ContactSection>
                <h2>📞 Контакты</h2>
                <p>Email: <a href="mailto:Yascov64@gmail.com">Yascov64@gmail.com</a></p>
                <p>LinkedIn: <a href="https://www.linkedin.com/in/alexander-yascov-b22116228">alexander-yascov-b22116228</a></p>
                <p>GitHub: <a href="https://github.com/JanusFaced">github.com/JanusFaced</a></p>
            </ContactSection>
        </AboutContainer>
    );
}

export default AboutPage;