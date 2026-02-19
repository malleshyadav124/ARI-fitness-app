import React, { useState } from 'react';
import { api } from '../lib/api';

const QUESTIONS = [
  'How would you rate your overall energy levels?',
  'How many days per week do you currently exercise?',
  'What is your primary fitness goal?',
  'Do you have any chronic health conditions?',
  'How many hours of sleep do you usually get?',
  'How often do you feel stressed?',
  'Describe your typical daily activity level (sedentary/active etc.)',
  'Do you have any injuries or pain that affect exercise?',
  'How would you rate your current diet quality?',
  'Do you smoke or consume alcohol regularly?',
  'What is your preferred workout style (gym/home/outdoor/etc.)?',
  'In 3 months, what would success look like for you?'
];

export const HealthAssessmentForm: React.FC = () => {
  const [answers, setAnswers] = useState<string[]>(Array(QUESTIONS.length).fill(''));
  const [submitting, setSubmitting] = useState(false);
  const [summary, setSummary] = useState<string | null>(null);

  const handleChange = (index: number, value: string) => {
    const next = [...answers];
    next[index] = value;
    setAnswers(next);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (answers.some((a) => !a.trim())) {
      // simple guard; you can surface a toast here
      return;
    }
    try {
      setSubmitting(true);
      const resp = await api.post('/health-assessment', {
        user_id: null,
        answers,
        metadata: {}
      });
      const data = resp.data as { summary?: string };
      setSummary(data.summary ?? 'Assessment submitted successfully.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="glass-card h-full flex flex-col">
      <div className="p-4 border-b border-white/5">
        <div className="text-sm font-semibold">Health Assessment</div>
        <div className="text-xs text-muted-foreground mt-1">
          Answer 12 quick questions so AROMI can calibrate your workout and nutrition plans.
        </div>
      </div>
      <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-4 space-y-4">
        {QUESTIONS.map((q, idx) => (
          <div key={idx} className="space-y-1">
            <label className="block text-xs font-medium text-muted-foreground">
              Q{idx + 1}. {q}
            </label>
            <textarea
              className="w-full rounded-xl bg-muted/70 border border-white/5 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/70"
              rows={2}
              value={answers[idx]}
              onChange={(e) => handleChange(idx, e.target.value)}
            />
          </div>
        ))}
        <button
          type="submit"
          disabled={submitting}
          className="mt-2 inline-flex items-center justify-center rounded-xl bg-primary text-primary-foreground text-sm font-medium px-4 py-2 disabled:opacity-60"
        >
          {submitting ? 'Submitting...' : 'Submit assessment'}
        </button>

        {summary && (
          <div className="mt-4 text-xs text-muted-foreground border-t border-white/5 pt-3">
            <div className="font-semibold mb-1">AROMI summary</div>
            <p>{summary}</p>
          </div>
        )}
      </form>
    </div>
  );
};

