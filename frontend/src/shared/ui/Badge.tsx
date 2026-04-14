import React from 'react';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'cyan' | 'purple' | 'green' | 'yellow' | 'red' | 'gray';
  children?: React.ReactNode;
}

export const Badge: React.FC<BadgeProps> = ({
  variant = 'cyan',
  className = '',
  children,
  ...props
}) => {
  const variantStyles = {
    cyan: 'bg-neon-cyan bg-opacity-20 text-neon-cyan border-neon-cyan',
    purple: 'bg-neon-purple bg-opacity-20 text-neon-purple border-neon-purple',
    green: 'bg-green-500 bg-opacity-20 text-green-400 border-green-400',
    yellow: 'bg-yellow-500 bg-opacity-20 text-yellow-300 border-yellow-300',
    red: 'bg-red-500 bg-opacity-20 text-red-400 border-red-400',
    gray: 'bg-gray-500 bg-opacity-20 text-gray-300 border-gray-400',
  };

  return (
    <span
      className={`
        inline-flex
        items-center
        rounded-full
        border
        px-3
        py-1
        text-xs
        font-semibold
        font-orbitron
        transition-all
        duration-200
        ${variantStyles[variant]}
        ${className}
      `}
      {...props}
    >
      {children}
    </span>
  );
};

Badge.displayName = 'Badge';
