import { useEffect, useState } from 'react';
import { useNotificationStore } from '@/shared/store/notifications';

const DISPLAY_MS = 3000;

export function Toast() {
  const message = useNotificationStore((s) => s.message);
  const hide = useNotificationStore((s) => s.hide);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (!message) {
      setVisible(false);
      return;
    }

    setVisible(true);

    const dismiss = setTimeout(() => {
      setVisible(false);
    }, DISPLAY_MS - 300); // start fade before hide

    const clear = setTimeout(() => {
      hide();
    }, DISPLAY_MS);

    return () => {
      clearTimeout(dismiss);
      clearTimeout(clear);
    };
  }, [message, hide]);

  if (!message) return null;

  return (
    <div
      className={`fixed bottom-6 left-1/2 -translate-x-1/2 z-50 transition-opacity duration-300 ${
        visible ? 'opacity-100' : 'opacity-0'
      }`}
    >
      <div className="bg-dark-bg border border-red-500/50 text-red-300 font-mono text-sm px-5 py-3 rounded-lg shadow-[0_0_20px_rgba(239,68,68,0.3)] max-w-md text-center">
        {message}
      </div>
    </div>
  );
}
