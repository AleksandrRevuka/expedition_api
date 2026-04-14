import { useEffect } from 'react';
import { useAuthStore } from '@/features/auth/store';
import { fetchMe } from '@/features/auth/api';

function App() {
  const token = useAuthStore((state) => state.token);
  const user = useAuthStore((state) => state.user);
  const setAuth = useAuthStore((state) => state.setAuth);

  useEffect(() => {
    // On app mount, if token is present but user is null, rehydrate the user
    if (token && !user) {
      fetchMe()
        .then((fetchedUser) => {
          setAuth(token, fetchedUser);
        })
        .catch(() => {
          // If fetchMe fails, the 401 interceptor will clear the token
          // and reload the page
        });
    }
  }, [token, user, setAuth]);

  return (
    <div className="min-h-screen bg-dark-bg text-neon-cyan">
      <h1 className="text-4xl font-bold text-center pt-20">
        Expedition
      </h1>
      <p className="text-center text-neon-purple mt-4">
        Frontend scaffold ready
      </p>
    </div>
  )
}

export default App
