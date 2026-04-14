import React from 'react';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className = '', ...props }, ref) => {
    return (
      <div className="flex flex-col gap-2">
        {label && (
          <label className="font-orbitron text-sm font-semibold text-neon-cyan">
            {label}
          </label>
        )}
        <input
          ref={ref}
          className={`
            glass-panel
            bg-dark-bg bg-opacity-30
            border-2 border-dark-gray
            text-white
            placeholder-gray-500
            rounded-lg
            px-4 py-2
            font-mono
            transition-all duration-200
            focus:border-neon-cyan
            focus:outline-none
            focus:ring-2
            focus:ring-neon-cyan
            focus:ring-offset-2
            focus:ring-offset-dark-bg
            disabled:opacity-50
            disabled:cursor-not-allowed
            ${error ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : ''}
            ${className}
          `}
          {...props}
        />
        {error && (
          <span className="text-xs font-semibold text-red-500">{error}</span>
        )}
      </div>
    );
  },
);

Input.displayName = 'Input';
