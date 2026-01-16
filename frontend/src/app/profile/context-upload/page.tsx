'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabase';
import { useUserFeatures } from '@/hooks/useUserFeatures';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type UploadStep = 'resume' | 'company' | 'job' | 'review';
type InputMode = 'file' | 'text';

interface UploadedContext {
  id: string;
  context_type: string;
  source_format: string;
  file_name?: string;
  extracted_text: string;
  created_at: string;
}

interface GenerationResult {
  batch_id: string;
  generated_count: number;
  category_breakdown: {
    resume_based: number;
    company_aligned: number;
    job_posting: number;
    general: number;
  };
}

export default function ContextUploadPage() {
  const router = useRouter();
  const [userId, setUserId] = useState<string | null>(null);

  // Feature gating - check ai_generator access
  const { ai_generator_available, isLoading: featuresLoading } = useUserFeatures(userId);
  const canGenerate = ai_generator_available;

  const [currentStep, setCurrentStep] = useState<UploadStep>('resume');

  // Upload states
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [companyMode, setCompanyMode] = useState<InputMode>('file');
  const [companyFile, setCompanyFile] = useState<File | null>(null);
  const [companyText, setCompanyText] = useState('');
  const [jobMode, setJobMode] = useState<InputMode>('file');
  const [jobFile, setJobFile] = useState<File | null>(null);
  const [jobText, setJobText] = useState('');

  // Uploaded contexts
  const [uploadedContexts, setUploadedContexts] = useState<UploadedContext[]>([]);

  // Generation states
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationResult, setGenerationResult] = useState<GenerationResult | null>(null);

  // UI states
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Auth check
  useEffect(() => {
    const checkAuth = async () => {
      const { data: { session } } = await supabase.auth.getSession();

      if (!session) {
        router.push('/auth/login');
        return;
      }

      setUserId(session.user.id);

      // Load existing contexts
      await loadContexts(session.user.id);
    };

    checkAuth();

    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        if (session) {
          setUserId(session.user.id);
        } else {
          router.push('/auth/login');
        }
      }
    );

    return () => {
      subscription.unsubscribe();
    };
  }, [router]);

  // Load existing contexts
  const loadContexts = async (uid: string) => {
    try {
      const response = await fetch(`${API_URL}/api/context/${uid}/contexts`);
      if (!response.ok) throw new Error('Failed to load contexts');
      const data = await response.json();
      setUploadedContexts(data);
    } catch (err) {
      console.error('Failed to load contexts:', err);
    }
  };

  // Upload resume (PDF)
  const handleResumeUpload = async () => {
    if (!resumeFile || !userId) return;

    setIsUploading(true);
    setError(null);
    setSuccess(null);

    try {
      const formData = new FormData();
      formData.append('file', resumeFile);

      const response = await fetch(`${API_URL}/api/context/${userId}/upload-resume`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to upload resume');
      }

      const result = await response.json();
      setSuccess('Resume uploaded successfully!');

      // Reload contexts
      await loadContexts(userId);

      // Move to next step
      setTimeout(() => {
        setCurrentStep('company');
        setSuccess(null);
      }, 1000);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsUploading(false);
    }
  };

  // Upload company info (screenshot or text)
  const handleCompanyUpload = async () => {
    if (!userId) return;

    setIsUploading(true);
    setError(null);
    setSuccess(null);

    try {
      if (companyMode === 'file') {
        if (!companyFile) {
          setError('Please select a screenshot');
          setIsUploading(false);
          return;
        }

        const formData = new FormData();
        formData.append('file', companyFile);
        formData.append('context_type', 'company_info');

        const response = await fetch(`${API_URL}/api/context/${userId}/upload-screenshot`, {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Failed to upload screenshot');
        }
      } else {
        if (!companyText.trim()) {
          setError('Please enter company information');
          setIsUploading(false);
          return;
        }

        const response = await fetch(`${API_URL}/api/context/${userId}/upload-text`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            context_type: 'company_info',
            text_content: companyText,
          }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Failed to upload text');
        }
      }

      setSuccess('Company info uploaded successfully!');
      await loadContexts(userId);

      setTimeout(() => {
        setCurrentStep('job');
        setSuccess(null);
      }, 1000);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsUploading(false);
    }
  };

  // Upload job posting (screenshot or text)
  const handleJobUpload = async () => {
    if (!userId) return;

    setIsUploading(true);
    setError(null);
    setSuccess(null);

    try {
      if (jobMode === 'file') {
        if (!jobFile) {
          setError('Please select a screenshot');
          setIsUploading(false);
          return;
        }

        const formData = new FormData();
        formData.append('file', jobFile);
        formData.append('context_type', 'job_posting');

        const response = await fetch(`${API_URL}/api/context/${userId}/upload-screenshot`, {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Failed to upload screenshot');
        }
      } else {
        if (!jobText.trim()) {
          setError('Please enter job posting');
          setIsUploading(false);
          return;
        }

        const response = await fetch(`${API_URL}/api/context/${userId}/upload-text`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            context_type: 'job_posting',
            text_content: jobText,
          }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Failed to upload text');
        }
      }

      setSuccess('Job posting uploaded successfully!');
      await loadContexts(userId);

      setTimeout(() => {
        setCurrentStep('review');
        setSuccess(null);
      }, 1000);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsUploading(false);
    }
  };

  // Generate Q&A pairs
  const handleGenerateQA = async () => {
    if (!userId) return;

    setIsGenerating(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/api/context/${userId}/generate-qa`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error?.message || 'Failed to generate Q&A pairs');
      }

      const result = await response.json();
      setGenerationResult(result);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsGenerating(false);
    }
  };

  // Skip optional steps
  const handleSkipCompany = () => {
    setCurrentStep('job');
  };

  const handleSkipJob = () => {
    setCurrentStep('review');
  };

  // Get uploaded context by type
  const getContextByType = (type: string) => {
    return uploadedContexts.find(ctx => ctx.context_type === type);
  };

  const hasResume = !!getContextByType('resume');
  const hasCompany = !!getContextByType('company_info');
  const hasJob = !!getContextByType('job_posting');

  if (!userId) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-6">
        <p className="text-zinc-600 dark:text-zinc-400">Loading...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-black">
      <div className="mx-auto max-w-4xl px-4 py-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-zinc-900 dark:text-zinc-100">
            AI-Powered Q&A Generation
          </h1>
          <p className="mt-2 text-zinc-600 dark:text-zinc-400">
            Upload your background documents to auto-generate 30 personalized Q&A pairs for any interview
          </p>
        </div>

        {/* Step Indicator */}
        <div className="mb-8 flex items-center justify-between">
          {[
            { key: 'resume', label: 'Background', icon: '📄' },
            { key: 'company', label: 'Organization', icon: '🏢' },
            { key: 'job', label: 'Details', icon: '📋' },
            { key: 'review', label: 'Generate', icon: '✨' },
          ].map((step, index) => (
            <div key={step.key} className="flex flex-1 items-center">
              <div className="flex flex-col items-center">
                <div
                  className={`flex h-12 w-12 items-center justify-center rounded-full text-2xl ${
                    currentStep === step.key
                      ? 'bg-zinc-900 dark:bg-zinc-100'
                      : uploadedContexts.some(ctx =>
                          (step.key === 'resume' && ctx.context_type === 'resume') ||
                          (step.key === 'company' && ctx.context_type === 'company_info') ||
                          (step.key === 'job' && ctx.context_type === 'job_posting')
                        ) || step.key === 'review'
                      ? 'bg-green-500'
                      : 'bg-zinc-200 dark:bg-zinc-800'
                  }`}
                >
                  {step.icon}
                </div>
                <p className="mt-2 text-sm font-medium text-zinc-700 dark:text-zinc-300">
                  {step.label}
                </p>
              </div>
              {index < 3 && (
                <div className="mx-2 h-0.5 flex-1 bg-zinc-200 dark:bg-zinc-800"></div>
              )}
            </div>
          ))}
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 flex items-center justify-between rounded-lg bg-red-50 p-4 dark:bg-red-950">
            <p className="text-red-700 dark:text-red-300">{error}</p>
            <button
              onClick={() => setError(null)}
              className="text-red-500 hover:text-red-700"
            >
              ✕
            </button>
          </div>
        )}

        {/* Success Message */}
        {success && (
          <div className="mb-6 rounded-lg bg-green-50 p-4 dark:bg-green-950">
            <p className="text-green-700 dark:text-green-300">{success}</p>
          </div>
        )}

        {/* Step 1: Resume Upload */}
        {currentStep === 'resume' && (
          <div className="rounded-lg border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-950">
            <h2 className="mb-4 text-xl font-semibold text-zinc-900 dark:text-zinc-100">
              📄 Upload Your Background Document
            </h2>
            <p className="mb-6 text-sm text-zinc-600 dark:text-zinc-400">
              Upload your resume, CV, or research summary in PDF format. This is required for Q&A generation.
            </p>

            {hasResume ? (
              <div className="mb-4 rounded-lg border border-green-200 bg-green-50 p-4 dark:border-green-800 dark:bg-green-950">
                <p className="text-green-700 dark:text-green-300">
                  ✅ Document already uploaded: {getContextByType('resume')?.file_name}
                </p>
                <button
                  onClick={() => setCurrentStep('company')}
                  className="mt-4 rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200"
                >
                  Continue to Organization Info
                </button>
              </div>
            ) : (
              <>
                <input
                  type="file"
                  accept=".pdf"
                  onChange={(e) => setResumeFile(e.target.files?.[0] || null)}
                  className="mb-4 w-full rounded-lg border border-zinc-300 px-3 py-2 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
                />

                {resumeFile && (
                  <p className="mb-4 text-sm text-zinc-600 dark:text-zinc-400">
                    Selected: {resumeFile.name} ({(resumeFile.size / 1024).toFixed(1)} KB)
                  </p>
                )}

                <button
                  onClick={handleResumeUpload}
                  disabled={!resumeFile || isUploading}
                  className="rounded-lg bg-zinc-900 px-6 py-2 text-sm font-medium text-white hover:bg-zinc-800 disabled:opacity-50 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200"
                >
                  {isUploading ? 'Uploading...' : 'Upload Resume'}
                </button>
              </>
            )}
          </div>
        )}

        {/* Step 2: Company Info Upload */}
        {currentStep === 'company' && (
          <div className="rounded-lg border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-950">
            <h2 className="mb-4 text-xl font-semibold text-zinc-900 dark:text-zinc-100">
              🏢 Organization Information (Optional)
            </h2>
            <p className="mb-6 text-sm text-zinc-600 dark:text-zinc-400">
              Upload info about the company, university, school, or organization. This helps generate context-specific questions.
            </p>

            {hasCompany ? (
              <div className="mb-4 rounded-lg border border-green-200 bg-green-50 p-4 dark:border-green-800 dark:bg-green-950">
                <p className="text-green-700 dark:text-green-300">
                  ✅ Organization info already uploaded
                </p>
                <div className="mt-2 flex gap-2">
                  <button
                    onClick={() => setCurrentStep('job')}
                    className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200"
                  >
                    Continue to Interview Details
                  </button>
                </div>
              </div>
            ) : (
              <>
                {/* Toggle Screenshot / Text */}
                <div className="mb-4 flex gap-2">
                  <button
                    onClick={() => setCompanyMode('file')}
                    className={`rounded-lg px-4 py-2 text-sm font-medium ${
                      companyMode === 'file'
                        ? 'bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900'
                        : 'border border-zinc-300 text-zinc-700 hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800'
                    }`}
                  >
                    📸 Screenshot
                  </button>
                  <button
                    onClick={() => setCompanyMode('text')}
                    className={`rounded-lg px-4 py-2 text-sm font-medium ${
                      companyMode === 'text'
                        ? 'bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900'
                        : 'border border-zinc-300 text-zinc-700 hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800'
                    }`}
                  >
                    📝 Paste Text
                  </button>
                </div>

                {companyMode === 'file' ? (
                  <>
                    <input
                      type="file"
                      accept=".jpg,.jpeg,.png,.webp"
                      onChange={(e) => setCompanyFile(e.target.files?.[0] || null)}
                      className="mb-4 w-full rounded-lg border border-zinc-300 px-3 py-2 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
                    />
                    {companyFile && (
                      <p className="mb-4 text-sm text-zinc-600 dark:text-zinc-400">
                        Selected: {companyFile.name}
                      </p>
                    )}
                  </>
                ) : (
                  <textarea
                    value={companyText}
                    onChange={(e) => setCompanyText(e.target.value)}
                    placeholder="Paste organization info: company mission, university program details, school culture..."
                    className="mb-4 h-40 w-full rounded-lg border border-zinc-300 px-3 py-2 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
                  />
                )}

                <div className="flex gap-2">
                  <button
                    onClick={handleCompanyUpload}
                    disabled={isUploading || (companyMode === 'file' ? !companyFile : !companyText.trim())}
                    className="rounded-lg bg-zinc-900 px-6 py-2 text-sm font-medium text-white hover:bg-zinc-800 disabled:opacity-50 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200"
                  >
                    {isUploading ? 'Uploading...' : 'Upload Organization Info'}
                  </button>
                  <button
                    onClick={handleSkipCompany}
                    className="rounded-lg border border-zinc-300 px-6 py-2 text-sm font-medium text-zinc-700 hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
                  >
                    Skip (Optional)
                  </button>
                </div>
              </>
            )}
          </div>
        )}

        {/* Step 3: Job Posting Upload */}
        {currentStep === 'job' && (
          <div className="rounded-lg border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-950">
            <h2 className="mb-4 text-xl font-semibold text-zinc-900 dark:text-zinc-100">
              📋 Interview Details (Optional)
            </h2>
            <p className="mb-6 text-sm text-zinc-600 dark:text-zinc-400">
              Upload additional context: job posting, thesis abstract, program details, or interview agenda.
            </p>

            {hasJob ? (
              <div className="mb-4 rounded-lg border border-green-200 bg-green-50 p-4 dark:border-green-800 dark:bg-green-950">
                <p className="text-green-700 dark:text-green-300">
                  ✅ Interview details already uploaded
                </p>
                <button
                  onClick={() => setCurrentStep('review')}
                  className="mt-4 rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200"
                >
                  Continue to Review
                </button>
              </div>
            ) : (
              <>
                {/* Toggle Screenshot / Text */}
                <div className="mb-4 flex gap-2">
                  <button
                    onClick={() => setJobMode('file')}
                    className={`rounded-lg px-4 py-2 text-sm font-medium ${
                      jobMode === 'file'
                        ? 'bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900'
                        : 'border border-zinc-300 text-zinc-700 hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800'
                    }`}
                  >
                    📸 Screenshot
                  </button>
                  <button
                    onClick={() => setJobMode('text')}
                    className={`rounded-lg px-4 py-2 text-sm font-medium ${
                      jobMode === 'text'
                        ? 'bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900'
                        : 'border border-zinc-300 text-zinc-700 hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800'
                    }`}
                  >
                    📝 Paste Text
                  </button>
                </div>

                {jobMode === 'file' ? (
                  <>
                    <input
                      type="file"
                      accept=".jpg,.jpeg,.png,.webp"
                      onChange={(e) => setJobFile(e.target.files?.[0] || null)}
                      className="mb-4 w-full rounded-lg border border-zinc-300 px-3 py-2 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
                    />
                    {jobFile && (
                      <p className="mb-4 text-sm text-zinc-600 dark:text-zinc-400">
                        Selected: {jobFile.name}
                      </p>
                    )}
                  </>
                ) : (
                  <textarea
                    value={jobText}
                    onChange={(e) => setJobText(e.target.value)}
                    placeholder="Paste details: job posting, thesis summary, program requirements, interview topics..."
                    className="mb-4 h-40 w-full rounded-lg border border-zinc-300 px-3 py-2 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
                  />
                )}

                <div className="flex gap-2">
                  <button
                    onClick={handleJobUpload}
                    disabled={isUploading || (jobMode === 'file' ? !jobFile : !jobText.trim())}
                    className="rounded-lg bg-zinc-900 px-6 py-2 text-sm font-medium text-white hover:bg-zinc-800 disabled:opacity-50 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200"
                  >
                    {isUploading ? 'Uploading...' : 'Upload Details'}
                  </button>
                  <button
                    onClick={handleSkipJob}
                    className="rounded-lg border border-zinc-300 px-6 py-2 text-sm font-medium text-zinc-700 hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
                  >
                    Skip (Optional)
                  </button>
                </div>
              </>
            )}
          </div>
        )}

        {/* Step 4: Review & Generate */}
        {currentStep === 'review' && (
          <div className="space-y-6">
            {/* Uploaded Contexts Summary */}
            <div className="rounded-lg border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-950">
              <h2 className="mb-4 text-xl font-semibold text-zinc-900 dark:text-zinc-100">
                ✨ Review & Generate Q&A Pairs
              </h2>

              <div className="mb-6 space-y-3">
                <div className={`rounded-lg p-3 ${hasResume ? 'bg-green-50 dark:bg-green-950' : 'bg-red-50 dark:bg-red-950'}`}>
                  <p className={hasResume ? 'text-green-700 dark:text-green-300' : 'text-red-700 dark:text-red-300'}>
                    📄 Background: {hasResume ? '✅ Uploaded' : '❌ Required'}
                  </p>
                </div>
                <div className={`rounded-lg p-3 ${hasCompany ? 'bg-green-50 dark:bg-green-950' : 'bg-zinc-50 dark:bg-zinc-900'}`}>
                  <p className={hasCompany ? 'text-green-700 dark:text-green-300' : 'text-zinc-600 dark:text-zinc-400'}>
                    🏢 Organization: {hasCompany ? '✅ Uploaded (+7 questions)' : 'Not uploaded'}
                  </p>
                </div>
                <div className={`rounded-lg p-3 ${hasJob ? 'bg-green-50 dark:bg-green-950' : 'bg-zinc-50 dark:bg-zinc-900'}`}>
                  <p className={hasJob ? 'text-green-700 dark:text-green-300' : 'text-zinc-600 dark:text-zinc-400'}>
                    📋 Details: {hasJob ? '✅ Uploaded (+5 questions)' : 'Not uploaded'}
                  </p>
                </div>
              </div>

              <div className="mb-6 rounded-lg border border-blue-200 bg-blue-50 p-4 dark:border-blue-800 dark:bg-blue-950">
                <h3 className="mb-2 font-semibold text-blue-900 dark:text-blue-100">
                  Expected Q&A Generation:
                </h3>
                <ul className="space-y-1 text-sm text-blue-800 dark:text-blue-200">
                  <li>• Background-based: 18 Q&A pairs</li>
                  {hasCompany && <li>• Organization-aligned: 7 Q&A pairs</li>}
                  {hasJob && <li>• Context-specific: 5 Q&A pairs</li>}
                  <li>• General: 5 Q&A pairs (common questions)</li>
                  <li className="font-semibold pt-2">
                    Total: {18 + (hasCompany ? 7 : 0) + (hasJob ? 5 : 0) + 5} Q&A pairs
                  </li>
                </ul>
              </div>

              {!hasResume && (
                <p className="mb-4 text-sm text-red-600 dark:text-red-400">
                  Background document is required to generate Q&A pairs. Please go back and upload.
                </p>
              )}

              <div className="flex gap-2">
                <button
                  onClick={() => {
                    if (!canGenerate) { router.push('/pricing'); return; }
                    handleGenerateQA();
                  }}
                  disabled={!hasResume || isGenerating}
                  className="rounded-lg bg-zinc-900 px-6 py-2 text-sm font-medium text-white hover:bg-zinc-800 disabled:opacity-50 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200"
                >
                  {isGenerating ? 'Generating Q&A pairs...' : 'Generate Q&A Pairs'}
                </button>
                <button
                  onClick={() => setCurrentStep('resume')}
                  disabled={isGenerating}
                  className="rounded-lg border border-zinc-300 px-6 py-2 text-sm font-medium text-zinc-700 hover:bg-zinc-100 disabled:opacity-50 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
                >
                  Edit Contexts
                </button>
              </div>
            </div>

            {/* Generation Progress */}
            {isGenerating && (
              <div className="rounded-lg border border-blue-200 bg-blue-50 p-6 dark:border-blue-800 dark:bg-blue-950">
                <div className="flex items-center gap-3 mb-4">
                  <div className="flex items-center justify-center">
                    <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-200 border-t-blue-600 dark:border-blue-800 dark:border-t-blue-400"></div>
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-100">
                      Generating Q&A Pairs...
                    </h3>
                    <p className="text-sm text-blue-700 dark:text-blue-300">
                      AI is analyzing your context and creating 30+ personalized interview questions (takes about 10-15 seconds)
                    </p>
                  </div>
                </div>

                {/* Animated Progress Bar */}
                <div className="mb-4">
                  <div className="h-2 w-full overflow-hidden rounded-full bg-blue-200 dark:bg-blue-900">
                    <div className="h-full animate-progress bg-gradient-to-r from-blue-500 to-blue-600 dark:from-blue-400 dark:to-blue-500"></div>
                  </div>
                </div>

                {/* Progress Steps */}
                <div className="space-y-2 text-sm text-blue-800 dark:text-blue-200">
                  <div className="flex items-center gap-2">
                    <div className="h-1.5 w-1.5 rounded-full bg-blue-600 dark:bg-blue-400 animate-pulse"></div>
                    <span>Generating 18 background-based Q&As</span>
                  </div>
                  {hasCompany && (
                    <div className="flex items-center gap-2">
                      <div className="h-1.5 w-1.5 rounded-full bg-blue-600 dark:bg-blue-400 animate-pulse"></div>
                      <span>Generating 7 organization-aligned Q&As</span>
                    </div>
                  )}
                  {hasJob && (
                    <div className="flex items-center gap-2">
                      <div className="h-1.5 w-1.5 rounded-full bg-blue-600 dark:bg-blue-400 animate-pulse"></div>
                      <span>Generating 5 context-specific Q&As</span>
                    </div>
                  )}
                  <div className="flex items-center gap-2">
                    <div className="h-1.5 w-1.5 rounded-full bg-blue-600 dark:bg-blue-400 animate-pulse"></div>
                    <span>Generating 5 general interview Q&As</span>
                  </div>
                </div>

                <div className="mt-4 space-y-1">
                  <p className="text-xs text-blue-600 dark:text-blue-400 font-semibold">
                    All categories are being generated simultaneously for faster results!
                  </p>
                  <p className="text-xs text-blue-600 dark:text-blue-400">
                    Estimated time: 10-15 seconds (optimized with GPT-4o-mini + concurrent processing)
                  </p>
                </div>
              </div>
            )}

            {/* Generation Results */}
            {generationResult && (
              <div className="rounded-lg border border-green-200 bg-green-50 p-6 dark:border-green-800 dark:bg-green-950">
                <h3 className="mb-4 text-xl font-semibold text-green-900 dark:text-green-100">
                  🎉 Successfully Generated {generationResult.generated_count} Q&A Pairs!
                </h3>

                <div className="mb-6 space-y-2 text-sm text-green-800 dark:text-green-200">
                  <p>• Background-based: {generationResult.category_breakdown.resume_based}</p>
                  <p>• Organization-aligned: {generationResult.category_breakdown.company_aligned}</p>
                  <p>• Context-specific: {generationResult.category_breakdown.job_posting}</p>
                  <p>• General: {generationResult.category_breakdown.general}</p>
                </div>

                <button
                  onClick={() => router.push('/profile/qa-pairs')}
                  className="rounded-lg bg-green-700 px-6 py-2 text-sm font-medium text-white hover:bg-green-800 dark:bg-green-600 dark:hover:bg-green-700"
                >
                  View Generated Q&A Pairs →
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
