'use client';

import Link from 'next/link';

// Russian FAQ - Target: Russia, Central Asia
export default function FAQRussianPage() {
    const faqs = [
        {
            category: "Помощь на собеседовании в реальном времени",
            questions: [
                {
                    q: "Есть ли инструмент, который поможет мне во время видеособеседования?",
                    a: "Да! InterviewMate — это AI-тренер в реальном времени, который дает мгновенные подсказки во время собеседования в Zoom, Teams или Google Meet. Слушает вопросы интервьюера и показывает персонализированные ответы за 2 секунды. Примечание: продукт на английском языке, для собеседований на английском."
                },
                {
                    q: "Работает ли для собеседований в Google/Amazon/Microsoft?",
                    a: "Конечно! InterviewMate специально разработан для поведенческих собеседований в крупных технологических компаниях. Leadership Principles Amazon, поведенческие раунды Google — все вопросы получают ответы в формате STAR."
                },
                {
                    q: "Английский не мой родной язык, поможет ли мне это?",
                    a: "Да! InterviewMate предлагает хорошо структурированные ответы на профессиональном английском. Особенно полезно для российских специалистов, проходящих собеседования в американских/британских компаниях."
                },
                {
                    q: "Насколько быстро работает InterviewMate?",
                    a: "InterviewMate использует Deepgram Flux с задержкой <1 секунды для транскрипции. Полный AI-ответ появляется через 2-3 секунды. Намного быстрее ChatGPT, потому что не нужно вводить вручную."
                },
                {
                    q: "Записывает ли мое собеседование?",
                    a: "Нет! Все аудио обрабатывается в реальном времени и сразу удаляется. Никакие записи не сохраняются. Дизайн с приоритетом конфиденциальности."
                }
            ]
        },
        {
            category: "Цены и функции",
            questions: [
                {
                    q: "Какая цена?",
                    a: "Начните бесплатно с 30 пробных сессий. Платные пакеты: 25 сессий за $5, 60 сессий за $10, 150 сессий за $20. Кредиты никогда не истекают. Без подписки, платите только за то, что используете. 7-дневная гарантия возврата средств на все покупки."
                },
                {
                    q: "Как это работает?",
                    a: "1) Добавьте свое резюме и прошлые проекты. 2) Во время собеседования откройте InterviewMate в отдельной вкладке браузера. 3) Слушает вопросы интервьюера и автоматически предлагает персонализированные ответы STAR на основе вашего опыта."
                }
            ]
        }
    ];

    return (
        <div className="min-h-screen bg-gray-50 py-12 px-4">
            <div className="max-w-4xl mx-auto">
                <div className="text-center mb-12">
                    <h1 className="text-4xl font-bold text-gray-900 mb-4">Часто задаваемые вопросы (FAQ)</h1>
                    <p className="text-xl text-gray-600">InterviewMate - AI-тренер для собеседований в реальном времени</p>
                    <p className="text-sm text-gray-500 mt-2">🇷🇺 Для собеседований на английском | Product is in English</p>
                </div>

                <div className="space-y-12">
                    {faqs.map((category, idx) => (
                        <div key={idx} className="bg-white rounded-lg shadow-md p-8">
                            <h2 className="text-2xl font-bold text-gray-900 mb-6">{category.category}</h2>
                            <div className="space-y-6">
                                {category.questions.map((faq, qIdx) => (
                                    <div key={qIdx} className="border-l-4 border-blue-500 pl-4">
                                        <h3 className="text-lg font-semibold text-gray-900 mb-2">{faq.q}</h3>
                                        <p className="text-gray-700">{faq.a}</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>

                <div className="mt-12 text-center bg-blue-50 rounded-lg p-8">
                    <h3 className="text-2xl font-bold mb-4">Попробуйте InterviewMate бесплатно</h3>
                    <p className="text-gray-600 mb-6">
                        Вопросы или проблемы? Пишите на{' '}
                        <a href="mailto:info@birth2death.com" className="text-blue-600 hover:text-blue-700 underline">
                            info@birth2death.com
                        </a>
                        . 7-дневная гарантия возврата.
                    </p>
                    <Link href="/auth/register" className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700">
                        Начать сейчас
                    </Link>
                </div>

                <div className="text-center mt-8">
                    <Link href="/faq" className="text-blue-600 hover:text-blue-700">← English FAQ</Link>
                    {' | '}
                    <Link href="/" className="text-blue-600 hover:text-blue-700">Главная</Link>
                </div>
            </div>

            <script type="application/ld+json" dangerouslySetInnerHTML={{
                __html: JSON.stringify({
                    "@context": "https://schema.org",
                    "@type": "FAQPage",
                    "inLanguage": "ru",
                    "mainEntity": faqs.flatMap(cat => cat.questions.map(faq => ({
                        "@type": "Question",
                        "name": faq.q,
                        "acceptedAnswer": { "@type": "Answer", "text": faq.a }
                    })))
                })
            }} />
        </div>
    );
}
