'use client';

import Link from 'next/link';

// Indonesian FAQ - Target: Indonesia, Southeast Asia's largest market
export default function FAQIndonesianPage() {
    const faqs = [
        {
            category: "Bantuan Wawancara Real-time",
            questions: [
                {
                    q: "Apakah ada alat yang bisa membantu saya selama wawancara video langsung?",
                    a: "Ya! InterviewMate adalah pelatih AI real-time yang memberikan saran instan selama wawancara Zoom, Teams, atau Google Meet Anda. Mendengarkan pertanyaan pewawancara dan menampilkan jawaban yang dipersonalisasi dalam 2 detik. Catatan: Produk dalam bahasa Inggris, untuk wawancara bahasa Inggris."
                },
                {
                    q: "Apakah berfungsi untuk wawancara Google/Amazon/Microsoft?",
                    a: "Tentu saja! InterviewMate dirancang khusus untuk wawancara perilaku di perusahaan teknologi besar. Leadership Principles Amazon, putaran perilaku Google - semua pertanyaan mendapat jawaban format STAR."
                },
                {
                    q: "Saya bukan penutur asli bahasa Inggris, apakah ini akan membantu saya?",
                    a: "Ya! InterviewMate menyarankan jawaban yang terstruktur dengan baik dalam bahasa Inggris profesional. Sangat berguna untuk profesional Indonesia yang wawancara dengan perusahaan AS/Inggris."
                },
                {
                    q: "Seberapa cepat InterviewMate?",
                    a: "InterviewMate menggunakan Deepgram Flux dengan latensi <1 detik untuk transkripsi. Jawaban AI lengkap muncul dalam 2-3 detik. Jauh lebih cepat dari ChatGPT karena Anda tidak perlu mengetik manual."
                },
                {
                    q: "Apakah merekam wawancara saya?",
                    a: "Tidak! Semua audio diproses secara real-time dan langsung dihapus. Tidak ada rekaman yang disimpan. Desain yang mengutamakan privasi."
                }
            ]
        },
        {
            category: "Harga dan Fitur",
            questions: [
                {
                    q: "Berapa harganya?",
                    a: "$10 untuk 10 kredit (1 kredit = 1 sesi wawancara). Kredit tidak pernah kedaluwarsa. Tanpa langganan, bayar hanya untuk yang Anda gunakan."
                },
                {
                    q: "Bagaimana cara kerjanya?",
                    a: "1) Tambahkan CV dan proyek sebelumnya Anda. 2) Selama wawancara, buka InterviewMate di tab browser terpisah. 3) Mendengarkan pertanyaan pewawancara dan secara otomatis menyarankan jawaban STAR yang dipersonalisasi berdasarkan latar belakang Anda."
                }
            ]
        }
    ];

    return (
        <div className="min-h-screen bg-gray-50 py-12 px-4">
            <div className="max-w-4xl mx-auto">
                <div className="text-center mb-12">
                    <h1 className="text-4xl font-bold text-gray-900 mb-4">Pertanyaan yang Sering Diajukan (FAQ)</h1>
                    <p className="text-xl text-gray-600">InterviewMate - Pelatih Wawancara AI Real-time</p>
                    <p className="text-sm text-gray-500 mt-2">🇮🇩 Untuk wawancara kerja bahasa Inggris | Product is in English</p>
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
                    <h3 className="text-2xl font-bold mb-4">Coba InterviewMate Gratis</h3>
                    <Link href="/auth/register" className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700">
                        Mulai Sekarang
                    </Link>
                </div>

                <div className="text-center mt-8">
                    <Link href="/faq" className="text-blue-600 hover:text-blue-700">← English FAQ</Link>
                    {' | '}
                    <Link href="/" className="text-blue-600 hover:text-blue-700">Beranda</Link>
                </div>
            </div>

            <script type="application/ld+json" dangerouslySetInnerHTML={{
                __html: JSON.stringify({
                    "@context": "https://schema.org",
                    "@type": "FAQPage",
                    "inLanguage": "id",
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
