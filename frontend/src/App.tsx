// frontend/src/App.tsx
import { useState, useEffect } from 'react';
import { useAuthStore } from '@/features/auth/store';
import { fetchMe } from '@/features/auth/api';
import { Header, Button } from '@/shared/ui';
import { LoginModal, RegisterModal } from '@/features/auth/components';
import {
  ExpeditionList,
  ExpeditionDetail,
  CreateExpeditionModal,
} from '@/features/expeditions/components';

function App() {
  const token = useAuthStore((state) => state.token);
  const user = useAuthStore((state) => state.user);
  const setAuth = useAuthStore((state) => state.setAuth);
  const logout = useAuthStore((state) => state.logout);

  const [selectedExpeditionId, setSelectedExpeditionId] = useState<string | null>(null);
  const [showLogin, setShowLogin] = useState(false);
  const [showRegister, setShowRegister] = useState(false);
  const [showCreate, setShowCreate] = useState(false);
  const [isRehydrating, setIsRehydrating] = useState(!!token && !user);

  useEffect(() => {
    if (token && !user) {
      setIsRehydrating(true);
      fetchMe()
        .then((fetchedUser) => {
          setAuth(token, fetchedUser);
        })
        .catch(() => {
          // 401 interceptor in shared/api/client.ts clears the token and reloads the page
        })
        .finally(() => {
          setIsRehydrating(false);
        });
    }
  }, [token, user, setAuth]);

  if (isRehydrating) {
    return (
      <div className="min-h-screen bg-dark-bg flex items-center justify-center">
        <div className="text-neon-cyan font-orbitron animate-pulse">LOADING...</div>
      </div>
    );
  }

  // ── Landing ──────────────────────────────────────────────────────────
  if (!user) {
    return (
      <div className="min-h-screen bg-dark-bg flex flex-col">
        <div className="flex justify-end gap-3 p-4">
          <Button variant="ghost" onClick={() => setShowLogin(true)}>
            Login
          </Button>
          <Button variant="secondary" onClick={() => setShowRegister(true)}>
            Register
          </Button>
        </div>

        <div className="flex-1 flex flex-col items-center justify-center gap-8">
          <div className="text-center space-y-3">
            <h1 className="text-5xl font-bold text-neon-cyan font-orbitron tracking-widest">
              EXPEDITION
            </h1>
            <p className="text-neon-purple text-lg">
              Увійдіть щоб продовжити
            </p>
          </div>
          <div className="flex gap-4">
            <Button variant="primary" onClick={() => setShowLogin(true)}>
              Login
            </Button>
            <Button variant="secondary" onClick={() => setShowRegister(true)}>
              Register
            </Button>
          </div>
        </div>

        <LoginModal
          isOpen={showLogin}
          onClose={() => setShowLogin(false)}
          onSwitchToRegister={() => {
            setShowLogin(false);
            setShowRegister(true);
          }}
        />
        <RegisterModal
          isOpen={showRegister}
          onClose={() => setShowRegister(false)}
          onSwitchToLogin={() => {
            setShowRegister(false);
            setShowLogin(true);
          }}
        />
      </div>
    );
  }

  // ── Main ─────────────────────────────────────────────────────────────
  return (
    <div className="h-screen bg-dark-bg flex flex-col overflow-hidden">
      <Header user={user} onLogout={logout} />

      <div className="flex flex-1 overflow-hidden">
        {/* Left column: 2/5 */}
        <div className="w-2/5 border-r border-neon-cyan/20 overflow-y-auto p-4">
          <ExpeditionList
            onSelectExpedition={setSelectedExpeditionId}
            onCreateNew={() => setShowCreate(true)}
            selectedExpeditionId={selectedExpeditionId}
          />
        </div>

        {/* Right column: 3/5 */}
        <div className="w-3/5 overflow-y-auto p-4">
          {selectedExpeditionId ? (
            <ExpeditionDetail
              expeditionId={selectedExpeditionId}
              onDeleted={() => setSelectedExpeditionId(null)}
            />
          ) : (
            <div className="flex items-center justify-center h-full">
              <p className="text-gray-500 font-mono text-sm">
                Виберіть експедицію
              </p>
            </div>
          )}
        </div>
      </div>

      <CreateExpeditionModal
        isOpen={showCreate}
        onClose={() => setShowCreate(false)}
      />
    </div>
  );
}

export default App;
