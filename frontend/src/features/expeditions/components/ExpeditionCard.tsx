import React from 'react';
import { Expedition, ExpeditionStatus } from '@/shared/types';
import { GlassPanel } from '@/shared/ui/GlassPanel';
import { Badge } from '@/shared/ui/Badge';

export interface ExpeditionCardProps {
  expedition: Expedition;
  isSelected?: boolean;
  onSelect?: (id: string) => void;
}

export const ExpeditionCard: React.FC<ExpeditionCardProps> = ({
  expedition,
  isSelected = false,
  onSelect,
}) => {
  const handleClick = () => {
    onSelect?.(expedition.id);
  };

  const getStatusBadgeVariant = (status: ExpeditionStatus) => {
    switch (status) {
      case ExpeditionStatus.Planned:
        return 'yellow' as const;
      case ExpeditionStatus.InProgress:
        return 'cyan' as const;
      case ExpeditionStatus.Completed:
        return 'green' as const;
      case ExpeditionStatus.Cancelled:
        return 'red' as const;
      default:
        return 'gray' as const;
    }
  };

  const getStatusLabel = (status: ExpeditionStatus) => {
    return status
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const memberCount = expedition.members?.length ?? 0;
  const startDate = new Date(expedition.start_at).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });

  const glowColor = isSelected ? 'cyan' : 'none';

  return (
    <GlassPanel
      glow={glowColor}
      onClick={handleClick}
      className={`
        p-4
        cursor-pointer
        transition-all
        duration-200
        ${
          isSelected
            ? 'shadow-[0_0_40px_rgba(0,255,255,0.6)]'
            : 'hover:shadow-[0_0_20px_rgba(0,255,255,0.2)]'
        }
      `}
    >
      <div className="space-y-3">
        {/* Title and Status */}
        <div className="flex items-start justify-between gap-2">
          <h3 className="text-lg font-bold text-neon-cyan flex-1 truncate font-orbitron">
            {expedition.title}
          </h3>
          <Badge variant={getStatusBadgeVariant(expedition.status)}>
            {getStatusLabel(expedition.status)}
          </Badge>
        </div>

        {/* Description */}
        <p className="text-sm text-gray-300 line-clamp-2">
          {expedition.description}
        </p>

        {/* Footer: Members and Date */}
        <div className="flex items-center justify-between pt-2 border-t border-dark-gray">
          <div className="text-xs font-orbitron text-neon-purple">
            {memberCount} / {expedition.capacity} members
          </div>
          <div className="text-xs text-gray-400">
            {startDate}
          </div>
        </div>
      </div>
    </GlassPanel>
  );
};

ExpeditionCard.displayName = 'ExpeditionCard';
