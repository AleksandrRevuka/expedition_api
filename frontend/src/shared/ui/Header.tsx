import { User } from '@/shared/types';
import { Button } from './Button';

export interface HeaderProps {
  user: User;
  onLogout: () => void;
}

export function Header({ user, onLogout }: HeaderProps) {
  return (
    <header className="border-b border-neon-cyan/20 backdrop-blur-sm bg-dark-bg/80 px-6 py-3 flex justify-end items-center gap-4 shrink-0">
      <span className="text-neon-cyan text-sm font-mono">
        {user.name} · {user.role}
      </span>
      <Button variant="ghost" onClick={onLogout} className="text-sm py-1 px-3">
        Logout
      </Button>
    </header>
  );
}
