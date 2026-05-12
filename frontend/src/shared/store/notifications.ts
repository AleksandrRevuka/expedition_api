import { create } from 'zustand';

interface NotificationState {
  message: string | null;
  show: (message: string) => void;
  hide: () => void;
}

export const useNotificationStore = create<NotificationState>((set) => ({
  message: null,
  show: (message) => set({ message }),
  hide: () => set({ message: null }),
}));
