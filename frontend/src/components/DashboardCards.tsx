import React from 'react';

interface DashboardCardsProps {
  totalWorkouts: number;
  totalMeals: number;
  totalMessages: number;
  latestSummary?: string | null;
}

export const DashboardCards: React.FC<DashboardCardsProps> = ({
  totalWorkouts,
  totalMeals,
  totalMessages,
  latestSummary
}) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div className="glass-card p-4 flex flex-col justify-between">
        <div className="text-xs text-muted-foreground mb-2">Workouts created</div>
        <div className="text-3xl font-semibold">{totalWorkouts}</div>
      </div>
      <div className="glass-card p-4 flex flex-col justify-between">
        <div className="text-xs text-muted-foreground mb-2">Meals logged</div>
        <div className="text-3xl font-semibold">{totalMeals}</div>
      </div>
      <div className="glass-card p-4 flex flex-col justify-between">
        <div className="text-xs text-muted-foreground mb-2">Messages with AROMI</div>
        <div className="text-3xl font-semibold">{totalMessages}</div>
      </div>
      <div className="glass-card p-4 flex flex-col justify-between">
        <div className="text-xs text-muted-foreground mb-2">Latest assessment summary</div>
        <div className="text-sm text-muted-foreground line-clamp-3">
          {latestSummary ?? 'No health assessment submitted yet.'}
        </div>
      </div>
    </div>
  );
};

