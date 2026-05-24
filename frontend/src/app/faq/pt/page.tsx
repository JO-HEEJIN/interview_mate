'use client';

import Link from 'next/link';

// Portuguese FAQ - Target: Brazil, Portugal
export default function FAQPortuguesePage() {
    const faqs = [
        {
            category: "Ajuda em entrevistas em tempo real",
            questions: [
                {
                    q: "Existe alguma ferramenta que me ajude durante uma entrevista de vídeo ao vivo?",
                    a: "Sim! InterviewMate é um treinador de IA em tempo real que fornece sugestões instantâneas durante suas entrevistas no Zoom, Teams ou Google Meet. Ouve as perguntas do entrevistador e exibe respostas personalizadas em 2 segundos. Nota: O produto está em inglês, para entrevistas em inglês."
                },
                {
                    q: "Funciona para entrevistas do Google/Amazon/Microsoft?",
                    a: "Com certeza! InterviewMate foi projetado especificamente para entrevistas comportamentais em grandes empresas de tecnologia. Leadership Principles da Amazon, rodadas comportamentais do Google - todas as perguntas recebem respostas no formato STAR."
                },
                {
                    q: "Não sou falante nativo de inglês, isso vai me ajudar?",
                    a: "Sim! InterviewMate sugere respostas bem estruturadas em inglês profissional. Especialmente útil para profissionais brasileiros que fazem entrevistas com empresas americanas/britânicas."
                },
                {
                    q: "Quão rápido é o InterviewMate?",
                    a: "InterviewMate usa Deepgram Flux com latência <1 segundo para transcrição. A resposta completa da IA aparece em 2-3 segundos. Muito mais rápido que ChatGPT porque você não precisa digitar manualmente."
                },
                {
                    q: "Ele grava minha entrevista?",
                    a: "Não! Todo o áudio é processado em tempo real e excluído imediatamente. Nenhuma gravação é armazenada. Design com foco em privacidade."
                }
            ]
        },
        {
            category: "Preços e recursos",
            questions: [
                {
                    q: "Qual é o preço?",
                    a: "Comece grátis com 30 sessões de teste. Pacotes pagos: 25 sessões por $5, 60 sessões por $10, 150 sessões por $20. Os créditos nunca expiram. Sem assinatura, pague apenas pelo que usar. Garantia de devolução de 7 dias em todas as compras."
                },
                {
                    q: "Como funciona?",
                    a: "1) Adicione seu currículo e projetos anteriores. 2) Durante a entrevista, abra o InterviewMate em uma aba separada do navegador. 3) Ele ouve as perguntas do entrevistador e sugere automaticamente respostas STAR personalizadas com base na sua experiência."
                }
            ]
        }
    ];

    return (
        <div className="min-h-screen bg-gray-50 py-12 px-4">
            <div className="max-w-4xl mx-auto">
                <div className="text-center mb-12">
                    <h1 className="text-4xl font-bold text-gray-900 mb-4">Perguntas Frequentes (FAQ)</h1>
                    <p className="text-xl text-gray-600">InterviewMate - Treinador de entrevistas com IA em tempo real</p>
                    <p className="text-sm text-gray-500 mt-2">🇧🇷 Para entrevistas de emprego em inglês | Product is in English</p>
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
                    <h3 className="text-2xl font-bold mb-4">Experimente o InterviewMate gratuitamente</h3>
                    <p className="text-gray-600 mb-6">
                        Dúvidas ou problemas? Escreva para{' '}
                        <a href="mailto:info@birth2death.com" className="text-blue-600 hover:text-blue-700 underline">
                            info@birth2death.com
                        </a>
                        . Garantia de devolução de 7 dias.
                    </p>
                    <Link href="/auth/register" className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700">
                        Começar agora
                    </Link>
                </div>

                <div className="text-center mt-8">
                    <Link href="/faq" className="text-blue-600 hover:text-blue-700">← English FAQ</Link>
                    {' | '}
                    <Link href="/" className="text-blue-600 hover:text-blue-700">Início</Link>
                </div>
            </div>

            <script type="application/ld+json" dangerouslySetInnerHTML={{
                __html: JSON.stringify({
                    "@context": "https://schema.org",
                    "@type": "FAQPage",
                    "inLanguage": "pt",
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
