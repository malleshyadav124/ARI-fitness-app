import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sidebar } from '../components/Sidebar';
import { DashboardCards } from '../components/DashboardCards';
import { ChatPanel } from '../components/ChatPanel';
import { HealthAssessmentForm } from '../components/HealthAssessmentForm';
import { NutritionTracker } from '../components/NutritionTracker';
import { api } from '../lib/api';
import { clearToken } from '../lib/auth';

type NavKey = 'dashboard' | 'assessment' | 'coach' | 'nutrition';

interface DashboardData {
  latest_assessment?: { summary?: string | null } | null;
  total_workouts: number;
  total_meals: number;
  total_messages: number;
}

interface UserMe {
  id: number;
  name: string;
  email: string;
}

export const Dashboard: React.FC = () => {
  const [active, setActive] = useState<NavKey>('dashboard');
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [user, setUser] = useState<UserMe | null>(null);
  const navigate = useNavigate();

  const sessionId = useMemo(
    () => `local-${Math.random().toString(36).slice(2, 10)}`,
    []
  );

  useEffect(() => {
    const loadUser = async () => {
      try {
        const resp = await api.get<UserMe>('/auth/me');
        setUser(resp.data);
      } catch {
        clearToken();
        navigate('/login', { replace: true });
      }
    };
    void loadUser();
  }, [navigate]);

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        const resp = await api.get('/dashboard-data');
        setDashboard(resp.data as DashboardData);
      } catch {
        setDashboard({
          latest_assessment: null,
          total_meals: 0,
          total_messages: 0,
          total_workouts: 0
        });
      }
    };
    void loadDashboard();
  }, []);

  const handleLogout = () => {
    clearToken();
    navigate('/login', { replace: true });
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 flex items-center justify-center">
        <div className="text-muted-foreground">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-foreground">
      <div className="max-w-7xl mx-auto py-6 px-4 md:px-6 lg:px-8">
        <div className="grid grid-cols-[auto,1fr] gap-6 h-[calc(100vh-4rem)]">
          <Sidebar
            active={active}
            onChange={setActive}
            userName={user.name}
            onLogout={handleLogout}
          />

          <main className="flex flex-col gap-4">
            {active === 'dashboard' && (
              <>
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <h2 className="text-xl font-semibold">Your ArogyaMitra overview</h2>
                    <p className="text-xs text-muted-foreground">
                      Snapshot of your workouts, nutrition, and AROMI conversations.
                    </p>
                  </div>
                </div>
                <DashboardCards
                  totalWorkouts={dashboard?.total_workouts ?? 0}
                  totalMeals={dashboard?.total_meals ?? 0}
                  totalMessages={dashboard?.total_messages ?? 0}
                  latestSummary={dashboard?.latest_assessment?.summary ?? null}
                />
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 flex-1 min-h-0">
                  <HealthAssessmentForm />
                  <ChatPanel sessionId={sessionId} />
                </div>
              </>
            )}

            {active === 'assessment' && (
              <div className="h-full">
                <HealthAssessmentForm />
              </div>
            )}

            {active === 'coach' && (
              <div className="h-full">
                <ChatPanel sessionId={sessionId} />
              </div>
            )}

            {active === 'nutrition' && (
              <div className="h-full">
                <NutritionTracker />
              </div>
            )}
          </main>
        </div>
      </div>
    </div>
  );
};
