import React from 'react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  isLoading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      isLoading = false,
      disabled,
      className = '',
      children,
      ...props
    },
    ref,
  ) => {
    const isDisabled = disabled || isLoading;

    const baseStyles =
      'font-orbitron px-4 py-2 rounded-lg font-semibold transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';

    const variantStyles = {
      primary:
        'bg-neon-cyan text-dark-bg hover:shadow-[0_0_20px_rgba(0,255,255,0.5)] focus:ring-neon-cyan disabled:hover:shadow-none',
      secondary:
        'bg-neon-purple text-white hover:shadow-[0_0_20px_rgba(147,51,234,0.5)] focus:ring-neon-purple disabled:hover:shadow-none',
      danger:
        'bg-red-600 text-white hover:shadow-[0_0_20px_rgba(220,38,38,0.5)] focus:ring-red-600 disabled:hover:shadow-none',
      ghost:
        'bg-transparent border-2 border-neon-cyan text-neon-cyan hover:shadow-[0_0_20px_rgba(0,255,255,0.3)] focus:ring-neon-cyan disabled:hover:shadow-none',
    };

    return (
      <button
        ref={ref}
        disabled={isDisabled}
        className={`${baseStyles} ${variantStyles[variant]} ${className}`}
        {...props}
      >
        <div className="flex items-center justify-center gap-2">
          {isLoading && (
            <svg
              className="h-4 w-4 animate-spin"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
          )}
          <span>{children}</span>
        </div>
      </button>
    );
  },
);

Button.displayName = 'Button';
