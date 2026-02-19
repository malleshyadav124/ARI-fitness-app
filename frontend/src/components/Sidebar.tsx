import React from 'react';

type NavItemKey = 'dashboard' | 'assessment' | 'coach' | 'nutrition';

interface SidebarProps {
  active: NavItemKey;
  onChange: (key: NavItemKey) => void;
  userName: string;
  onLogout: () => void;
}

const items: { key: NavItemKey; label: string }[] = [
  { key: 'dashboard', label: 'Dashboard' },
  { key: 'assessment', label: 'Health Assessment' },
  { key: 'coach', label: 'AI Coach (AROMI)' },
  { key: 'nutrition', label: 'Nutrition Tracker' }
];

export const Sidebar: React.FC<SidebarProps> = ({ active, onChange, userName, onLogout }) => {
  return (
    <aside className="glass-card h-full w-64 flex flex-col p-4">
      <div className="mb-6">
        <div className="text-xs uppercase tracking-[0.25em] text-muted-foreground">
          ArogyaMitra
        </div>
        <div className="mt-2 text-lg font-semibold">AROMI Coach</div>
      </div>

      <nav className="space-y-1">
        {items.map((item) => {
          const isActive = active === item.key;
          return (
            <button
              key={item.key}
              type="button"
              className={`sidebar-item w-full text-left ${
                isActive ? 'sidebar-item-active' : 'sidebar-item-inactive'
              }`}
              onClick={() => onChange(item.key)}
            >
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="mt-auto pt-4 border-t border-white/5 space-y-2">
        <div className="text-sm font-medium text-foreground truncate px-2" title={userName}>
          {userName}
        </div>
        <button
          type="button"
          onClick={onLogout}
          className="sidebar-item w-full text-left text-red-400/90 hover:bg-red-500/10 hover:text-red-300"
        >
          Logout
        </button>
      </div>
    </aside>
  );
};

