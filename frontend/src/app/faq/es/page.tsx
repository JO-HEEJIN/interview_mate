'use client';

import Link from 'next/link';

// Spanish FAQ - Target: Latin America, Spain
export default function FAQSpanishPage() {
    const faqs = [
        {
            category: "Ayuda en entrevistas en tiempo real",
            questions: [
                {
                    q: "¿Hay alguna herramienta que me ayude durante una entrevista de video en vivo?",
                    a: "¡Sí! InterviewMate es un entrenador de IA en tiempo real que proporciona sugerencias instantáneas durante tus entrevistas en Zoom, Teams o Google Meet. Escucha las preguntas del entrevistador y muestra respuestas personalizadas en 2 segundos. Nota: El producto está en inglés, para entrevistas en inglés."
                },
                {
                    q: "¿Funciona para entrevistas de Google/Amazon/Microsoft?",
                    a: "¡Por supuesto! InterviewMate está diseñado específicamente para entrevistas de comportamiento en grandes empresas tecnológicas. Leadership Principles de Amazon, rondas de comportamiento de Google - todas las preguntas obtienen respuestas en formato STAR."
                },
                {
                    q: "No soy hablante nativo de inglés, ¿me ayudará?",
                    a: "¡Sí! InterviewMate sugiere respuestas bien estructuradas en inglés profesional. Especialmente útil para profesionales hispanos que entrevistan con empresas estadounidenses/británicas."
                },
                {
                    q: "¿Qué tan rápido es InterviewMate?",
                    a: "InterviewMate usa Deepgram Flux con latencia <1 segundo para transcripción. La respuesta completa de IA aparece en 2-3 segundos. Mucho más rápido que ChatGPT porque no necesitas escribir manualmente."
                },
                {
                    q: "¿Graba mi entrevista?",
                    a: "¡No! Todo el audio se procesa en tiempo real y se elimina inmediatamente. No se almacenan grabaciones. Diseño que prioriza la privacidad."
                }
            ]
        },
        {
            category: "Precios y características",
            questions: [
                {
                    q: "¿Cuál es el precio?",
                    a: "$10 por 10 créditos (1 crédito = 1 sesión de entrevista). Los créditos nunca expiran. Sin suscripción, paga solo por lo que usas."
                },
                {
                    q: "¿Cómo funciona?",
                    a: "1) Agrega tu CV y proyectos anteriores. 2) Durante la entrevista, abre InterviewMate en una pestaña separada del navegador. 3) Escucha las preguntas del entrevistador y automáticamente sugiere respuestas STAR personalizadas basadas en tu experiencia."
                }
            ]
        }
    ];

    return (
        <div className="min-h-screen bg-gray-50 py-12 px-4">
            <div className="max-w-4xl mx-auto">
                <div className="text-center mb-12">
                    <h1 className="text-4xl font-bold text-gray-900 mb-4">Preguntas Frecuentes (FAQ)</h1>
                    <p className="text-xl text-gray-600">InterviewMate - Entrenador de entrevistas con IA en tiempo real</p>
                    <p className="text-sm text-gray-500 mt-2">🇪🇸 Para entrevistas de trabajo en inglés | Product is in English</p>
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
                    <h3 className="text-2xl font-bold mb-4">Prueba InterviewMate gratis</h3>
                    <Link href="/auth/register" className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700">
                        Comenzar ahora
                    </Link>
                </div>

                <div className="text-center mt-8">
                    <Link href="/faq" className="text-blue-600 hover:text-blue-700">← English FAQ</Link>
                    {' | '}
                    <Link href="/" className="text-blue-600 hover:text-blue-700">Inicio</Link>
                </div>
            </div>

            <script type="application/ld+json" dangerouslySetInnerHTML={{
                __html: JSON.stringify({
                    "@context": "https://schema.org",
                    "@type": "FAQPage",
                    "inLanguage": "es",
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
