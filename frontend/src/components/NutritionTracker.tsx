import React, { useState } from 'react';
import { api } from '../lib/api';

interface MealSummary {
  calories?: number | null;
  protein_g?: number | null;
  carbs_g?: number | null;
  fat_g?: number | null;
}

export const NutritionTracker: React.FC = () => {
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState<MealSummary | null>(null);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!description.trim()) return;
    try {
      setLoading(true);
      const resp = await api.post('/meal-analysis', {
        user_id: null,
        description: description.trim()
      });
      const data = resp.data as MealSummary;
      setSummary(data);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-card h-full flex flex-col">
      <div className="p-4 border-b border-white/5">
        <div className="text-sm font-semibold">Nutrition Tracker</div>
        <div className="text-xs text-muted-foreground mt-1">
          Paste what you ate, and AROMI will estimate macros via CalorieNinjas.
        </div>
      </div>
      <form onSubmit={handleAnalyze} className="flex-1 p-4 flex flex-col gap-3">
        <textarea
          className="w-full rounded-xl bg-muted/70 border border-white/5 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/70"
          rows={3}
          placeholder="E.g. 2 boiled eggs, 1 cup rice, grilled chicken breast..."
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        <button
          type="submit"
          disabled={loading}
          className="inline-flex items-center justify-center rounded-xl bg-primary text-primary-foreground text-sm font-medium px-4 py-2 disabled:opacity-60"
        >
          {loading ? 'Analyzing...' : 'Analyze meal'}
        </button>

        {summary && (
          <div className="mt-2 grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
            <div className="glass-card p-3">
              <div className="text-muted-foreground">Calories</div>
              <div className="text-lg font-semibold">
                {summary.calories != null ? Math.round(summary.calories) : '—'}
              </div>
            </div>
            <div className="glass-card p-3">
              <div className="text-muted-foreground">Protein (g)</div>
              <div className="text-lg font-semibold">
                {summary.protein_g != null ? Math.round(summary.protein_g) : '—'}
              </div>
            </div>
            <div className="glass-card p-3">
              <div className="text-muted-foreground">Carbs (g)</div>
              <div className="text-lg font-semibold">
                {summary.carbs_g != null ? Math.round(summary.carbs_g) : '—'}
              </div>
            </div>
            <div className="glass-card p-3">
              <div className="text-muted-foreground">Fat (g)</div>
              <div className="text-lg font-semibold">
                {summary.fat_g != null ? Math.round(summary.fat_g) : '—'}
              </div>
            </div>
          </div>
        )}
      </form>
    </div>
  );
};

