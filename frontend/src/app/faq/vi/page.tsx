'use client';

import Link from 'next/link';

// Vietnamese FAQ - Target: Vietnam, Southeast Asia
export default function FAQVietnamesePage() {
    const faqs = [
        {
            category: "Hỗ trợ phỏng vấn thời gian thực",
            questions: [
                {
                    q: "Có công cụ nào giúp tôi trong khi phỏng vấn video trực tiếp không?",
                    a: "Có! InterviewMate là huấn luyện viên AI thời gian thực cung cấp gợi ý ngay lập tức trong khi bạn phỏng vấn trên Zoom, Teams hoặc Google Meet. Nó lắng nghe câu hỏi của người phỏng vấn và hiển thị câu trả lời được cá nhân hóa trong vòng 2 giây. Lưu ý: Sản phẩm bằng tiếng Anh, dành cho phỏng vấn tiếng Anh."
                },
                {
                    q: "Có hoạt động với phỏng vấn Google/Amazon/Microsoft không?",
                    a: "Hoàn toàn có! InterviewMate được thiết kế đặc biệt cho các cuộc phỏng vấn hành vi tại các công ty công nghệ lớn. Nguyên tắc lãnh đạo của Amazon, vòng hành vi của Google - tất cả các câu hỏi đều có câu trả lời định dạng STAR."
                },
                {
                    q: "Tôi không phải người bản xứ nói tiếng Anh, nó có giúp tôi không?",
                    a: "Có! InterviewMate gợi ý câu trả lời có cấu trúc tốt bằng tiếng Anh chuyên nghiệp. Đặc biệt hữu ích cho các chuyên gia Việt Nam phỏng vấn với các công ty Mỹ/Anh."
                },
                {
                    q: "InterviewMate nhanh như thế nào?",
                    a: "InterviewMate sử dụng Deepgram Flux với độ trễ <1 giây để chuyển văn bản. Câu trả lời AI đầy đủ xuất hiện trong 2-3 giây. Nhanh hơn nhiều so với ChatGPT vì bạn không cần gõ thủ công."
                }
            ]
        },
        {
            category: "Giá và Tính năng",
            questions: [
                {
                    q: "Giá bao nhiêu?",
                    a: "$10 cho 10 tín chỉ (1 tín chỉ = 1 phiên phỏng vấn). Tín chỉ không bao giờ hết hạn. Không có đăng ký, chỉ trả tiền cho những gì bạn sử dụng."
                },
                {
                    q: "Nó hoạt động như thế nào?",
                    a: "1) Thêm CV và các dự án trước đây của bạn. 2) Trong khi phỏng vấn, mở InterviewMate trong tab trình duyệt riêng. 3) Nó lắng nghe câu hỏi của người phỏng vấn và tự động gợi ý câu trả lời STAR được cá nhân hóa dựa trên nền tảng của bạn."
                }
            ]
        }
    ];

    return (
        <div className="min-h-screen bg-gray-50 py-12 px-4">
            <div className="max-w-4xl mx-auto">
                <div className="text-center mb-12">
                    <h1 className="text-4xl font-bold text-gray-900 mb-4">Câu hỏi thường gặp (FAQ)</h1>
                    <p className="text-xl text-gray-600">InterviewMate - Huấn luyện viên phỏng vấn AI thời gian thực</p>
                    <p className="text-sm text-gray-500 mt-2">🇻🇳 Cho phỏng vấn việc làm tiếng Anh | Product is in English</p>
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
                    <h3 className="text-2xl font-bold mb-4">Dùng thử InterviewMate miễn phí</h3>
                    <Link href="/auth/register" className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700">
                        Bắt đầu ngay
                    </Link>
                </div>

                <div className="text-center mt-8">
                    <Link href="/faq" className="text-blue-600 hover:text-blue-700">← English FAQ</Link>
                    {' | '}
                    <Link href="/" className="text-blue-600 hover:text-blue-700">Trang chủ</Link>
                </div>
            </div>

            <script type="application/ld+json" dangerouslySetInnerHTML={{
                __html: JSON.stringify({
                    "@context": "https://schema.org",
                    "@type": "FAQPage",
                    "inLanguage": "vi",
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
