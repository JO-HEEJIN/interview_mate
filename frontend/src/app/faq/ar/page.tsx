'use client';

import Link from 'next/link';

// Arabic FAQ - Target: UAE, Dubai, Saudi Arabia, Middle East
export default function FAQArabicPage() {
    const faqs = [
        {
            category: "المساعدة في المقابلات المباشرة",
            questions: [
                {
                    q: "هل هناك أداة تساعدني أثناء مقابلة الفيديو المباشرة؟",
                    a: "نعم! InterviewMate هو مدرب ذكاء اصطناعي في الوقت الفعلي يقدم اقتراحات فورية أثناء مقابلاتك على Zoom أو Teams أو Google Meet. يستمع إلى أسئلة المُقابل ويعرض إجابات مخصصة في أقل من ثانيتين. ملاحظة: المنتج باللغة الإنجليزية، للمقابلات بالإنجليزية."
                },
                {
                    q: "هل يعمل مع مقابلات Google/Amazon/Microsoft؟",
                    a: "بالتأكيد! تم تصميم InterviewMate خصيصًا للمقابلات السلوكية في شركات التكنولوجيا الكبرى. مبادئ القيادة في Amazon، الجولات السلوكية في Google - كل الأسئلة تحصل على إجابات بتنسيق STAR."
                },
                {
                    q: "أنا متحدث غير أصلي للإنجليزية، هل سيساعدني؟",
                    a: "نعم! يقترح InterviewMate إجابات منظمة بلغة إنجليزية احترافية. مفيد بشكل خاص للمحترفين من الإمارات والسعودية الذين يجرون مقابلات مع شركات أمريكية/بريطانية."
                },
                {
                    q: "ما مدى سرعة InterviewMate؟",
                    a: "يستخدم InterviewMate تقنية Deepgram Flux بزمن تأخير <1 ثانية للنسخ. تظهر الإجابة الكاملة بالذكاء الاصطناعي خلال 2-3 ثوانٍ. أسرع بكثير من ChatGPT لأنك لا تحتاج إلى الكتابة يدويًا."
                },
                {
                    q: "هل يسجل مقابلاتي؟",
                    a: "لا! تتم معالجة جميع الملفات الصوتية في الوقت الفعلي ويتم حذفها على الفور. لا يتم تخزين أي تسجيلات. تصميم يعطي الأولوية للخصوصية."
                }
            ]
        },
        {
            category: "التسعير والميزات",
            questions: [
                {
                    q: "ما هو السعر؟",
                    a: "ابدأ مجانًا مع 30 نقطة تجريبية (1 نقطة = جلسة مقابلة واحدة). الحزم المدفوعة: 25 نقطة بـ $5، 60 نقطة بـ $10، 150 نقطة بـ $20. النقاط لا تنتهي صلاحيتها أبدًا. بدون اشتراكات، ادفع فقط مقابل ما تستخدمه."
                },
                {
                    q: "كيف يعمل؟",
                    a: "1) أضف سيرتك الذاتية ومشاريعك السابقة. 2) أثناء المقابلة، افتح InterviewMate في علامة تبويب منفصلة. 3) يستمع إلى أسئلة المُقابل ويقترح تلقائيًا إجابات STAR مخصصة بناءً على خلفيتك."
                },
                {
                    q: "هل يمكنني الحصول على استرداد؟",
                    a: "نعم. نقدم ضمان استرداد لمدة 7 أيام على جميع المشتريات — النقاط والميزات لمرة واحدة. راسلنا على info@birth2death.com خلال 7 أيام من الشراء مع رقم المعاملة، وسنقوم بمعالجة الاسترداد خلال 5-10 أيام عمل."
                }
            ]
        }
    ];

    return (
        <div className="min-h-screen bg-gray-50 py-12 px-4" dir="rtl">
            <div className="max-w-4xl mx-auto">
                <div className="text-center mb-12">
                    <h1 className="text-4xl font-bold text-gray-900 mb-4">الأسئلة الشائعة (FAQ)</h1>
                    <p className="text-xl text-gray-600">InterviewMate - مدرب مقابلات ذكاء اصطناعي في الوقت الفعلي</p>
                    <p className="text-sm text-gray-500 mt-2">🇦🇪 للمقابلات الوظيفية بالإنجليزية | Product is in English</p>
                </div>

                <div className="space-y-12">
                    {faqs.map((category, idx) => (
                        <div key={idx} className="bg-white rounded-lg shadow-md p-8">
                            <h2 className="text-2xl font-bold text-gray-900 mb-6">{category.category}</h2>
                            <div className="space-y-6">
                                {category.questions.map((faq, qIdx) => (
                                    <div key={qIdx} className="border-r-4 border-blue-500 pr-4">
                                        <h3 className="text-lg font-semibold text-gray-900 mb-2">{faq.q}</h3>
                                        <p className="text-gray-700">{faq.a}</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>

                <div className="mt-12 text-center bg-blue-50 rounded-lg p-8">
                    <h3 className="text-2xl font-bold mb-4">جرب InterviewMate مجانًا</h3>
                    <p className="text-gray-600 mb-6">
                        لديك أسئلة أو مشاكل؟ راسلنا على{' '}
                        <a
                            href="mailto:info@birth2death.com"
                            dir="ltr"
                            className="text-blue-600 hover:text-blue-700 underline"
                        >
                            info@birth2death.com
                        </a>
                    </p>
                    <Link href="/auth/register" className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700">
                        ابدأ الآن
                    </Link>
                </div>

                <div className="text-center mt-8">
                    <Link href="/faq" className="text-blue-600 hover:text-blue-700">English FAQ ←</Link>
                    {' | '}
                    <Link href="/" className="text-blue-600 hover:text-blue-700">الصفحة الرئيسية</Link>
                </div>
            </div>

            <script type="application/ld+json" dangerouslySetInnerHTML={{
                __html: JSON.stringify({
                    "@context": "https://schema.org",
                    "@type": "FAQPage",
                    "inLanguage": "ar",
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
