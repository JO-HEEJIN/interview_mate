'use client';

import Link from 'next/link';

// Thai FAQ - Target: Thailand
export default function FAQThaiPage() {
    const faqs = [
        {
            category: "ความช่วยเหลือสัมภาษณ์แบบเรียลไทม์",
            questions: [
                {
                    q: "มีเครื่องมือที่ช่วยระหว่างการสัมภาษณ์วิดีโอสดไหม?",
                    a: "มีค่ะ! InterviewMate คือโค้ช AI แบบเรียลไทม์ที่ให้คำแนะนำทันทีระหว่างการสัมภาษณ์บน Zoom, Teams หรือ Google Meet ฟังคำถามของผู้สัมภาษณ์และแสดงคำตอบที่ปรับแต่งเฉพาะบุคคลภายใน 2 วินาที หมายเหตุ: ผลิตภัณฑ์เป็นภาษาอังกฤษ สำหรับการสัมภาษณ์ภาษาอังกฤษ"
                },
                {
                    q: "ใช้ได้กับการสัมภาษณ์ Google/Amazon/Microsoft ไหม?",
                    a: "แน่นอน! InterviewMate ออกแบบมาโดยเฉพาะสำหรับการสัมภาษณ์พฤติกรรมในบริษัทเทคโนโลยีใหญ่ หลักการความเป็นผู้นำของ Amazon, รอบพฤติกรรมของ Google - คำถามทั้งหมดได้รับคำตอบในรูปแบบ STAR"
                },
                {
                    q: "ฉันไม่ใช่เจ้าของภาษาอังกฤษ จะช่วยได้ไหม?",
                    a: "ได้ค่ะ! InterviewMate แนะนำคำตอบที่มีโครงสร้างดีเป็นภาษาอังกฤษระดับมืออาชีพ เป็นประโยชน์อย่างยิ่งสำหรับมืออาชีพไทยที่สัมภาษณ์กับบริษัทอเมริกัน/อังกฤษ"
                },
                {
                    q: "InterviewMate เร็วแค่ไหน?",
                    a: "InterviewMate ใช้ Deepgram Flux ที่มีความล่าช้า <1 วินาทีในการถอดเสียง คำตอบ AI แบบเต็มจะปรากฏใน 2-3 วินาที เร็วกว่า ChatGPT มากเพราะไม่ต้องพิมพ์ด้วยตัวเอง"
                },
                {
                    q: "จะบันทึกการสัมภาษณ์ของฉันไหม?",
                    a: "ไม่! เสียงทั้งหมดจะถูกประมวลผลแบบเรียลไทม์และลบทันที ไม่มีการบันทึกใดๆ ถูกเก็บไว้ การออกแบบที่ให้ความสำคัญกับความเป็นส่วนตัวเป็นอันดับแรก"
                }
            ]
        },
        {
            category: "ราคาและคุณสมบัติ",
            questions: [
                {
                    q: "ราคาเท่าไหร่?",
                    a: "เริ่มต้นฟรีด้วย 30 เซสชันทดลอง แพ็คเกจชำระเงิน: 25 เซสชัน $5, 60 เซสชัน $10, 150 เซสชัน $20 เครดิตไม่มีวันหมดอายุ ไม่มีการสมัครสมาชิก จ่ายเฉพาะสิ่งที่คุณใช้ รับประกันคืนเงิน 7 วันสำหรับการซื้อทั้งหมด"
                },
                {
                    q: "ทำงานอย่างไร?",
                    a: "1) เพิ่มเรซูเม่และโครงการก่อนหน้าของคุณ 2) ระหว่างการสัมภาษณ์ เปิด InterviewMate ในแท็บเบราว์เซอร์แยกต่างหาก 3) ฟังคำถามของผู้สัมภาษณ์และแนะนำคำตอบ STAR ที่ปรับแต่งตามพื้นหลังของคุณโดยอัตโนมัติ"
                }
            ]
        }
    ];

    return (
        <div className="min-h-screen bg-gray-50 py-12 px-4">
            <div className="max-w-4xl mx-auto">
                <div className="text-center mb-12">
                    <h1 className="text-4xl font-bold text-gray-900 mb-4">คำถามที่พบบ่อย (FAQ)</h1>
                    <p className="text-xl text-gray-600">InterviewMate - โค้ชสัมภาษณ์ AI แบบเรียลไทม์</p>
                    <p className="text-sm text-gray-500 mt-2">🇹🇭 สำหรับการสัมภาษณ์งานภาษาอังกฤษ | Product is in English</p>
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
                    <h3 className="text-2xl font-bold mb-4">ทดลองใช้ InterviewMate ฟรี</h3>
                    <p className="text-gray-600 mb-6">
                        มีคำถามหรือปัญหา? ส่งอีเมลถึงเราที่{' '}
                        <a href="mailto:info@birth2death.com" className="text-blue-600 hover:text-blue-700 underline">
                            info@birth2death.com
                        </a>
                        . รับประกันคืนเงิน 7 วัน.
                    </p>
                    <Link href="/auth/register" className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700">
                        เริ่มต้นเลย
                    </Link>
                </div>

                <div className="text-center mt-8">
                    <Link href="/faq" className="text-blue-600 hover:text-blue-700">← English FAQ</Link>
                    {' | '}
                    <Link href="/" className="text-blue-600 hover:text-blue-700">หน้าแรก</Link>
                </div>
            </div>

            <script type="application/ld+json" dangerouslySetInnerHTML={{
                __html: JSON.stringify({
                    "@context": "https://schema.org",
                    "@type": "FAQPage",
                    "inLanguage": "th",
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
