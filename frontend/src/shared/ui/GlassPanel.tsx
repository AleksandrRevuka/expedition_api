import React from 'react';

export interface GlassPanelProps extends React.HTMLAttributes<HTMLDivElement> {
  glow?: 'cyan' | 'purple' | 'none';
  children?: React.ReactNode;
}

export const GlassPanel: React.FC<GlassPanelProps> = ({
  glow = 'none',
  className = '',
  children,
  ...props
}) => {
  const glowStyles = {
    cyan: 'border-neon-cyan shadow-[0_0_30px_rgba(0,255,255,0.3)]',
    purple: 'border-neon-purple shadow-[0_0_30px_rgba(147,51,234,0.3)]',
    none: 'border-dark-gray',
  };

  const borderStyle = glow !== 'none' ? 'border-2' : 'border';

  return (
    <div
      className={`
        glass-panel
        rounded-xl
        bg-dark-bg
        bg-opacity-50
        backdrop-blur-md
        ${borderStyle}
        ${glowStyles[glow]}
        transition-all
        duration-200
        ${className}
      `}
      {...props}
    >
      {children}
    </div>
  );
};

GlassPanel.displayName = 'GlassPanel';
