# Symphony-IR Frontend - UI Implementation Guide

## Overview

This document provides implementation patterns, code examples, and best practices for building the Symphony-IR SaaS frontend according to the Design System specifications.

---

## Design Tokens & CSS Variables

### Root CSS Variables

```css
/* colors/palette.css */

:root {
  /* Primary Colors */
  --color-primary-50: #eff6ff;
  --color-primary-100: #dbeafe;
  --color-primary-200: #bfdbfe;
  --color-primary-300: #93c5fd;
  --color-primary-400: #60a5fa;
  --color-primary-500: #3b82f6;
  --color-primary-600: #2563eb;
  --color-primary-700: #1d4ed8;
  --color-primary-800: #1e40af;
  --color-primary-900: #1e3a8a;

  /* Accent Colors */
  --color-accent-50: #ecfdff;
  --color-accent-100: #cffafe;
  --color-accent-200: #a5f3fc;
  --color-accent-300: #67e8f9;
  --color-accent-400: #22d3ee;
  --color-accent-500: #06b6d4;
  --color-accent-600: #0891b2;
  --color-accent-700: #0e7490;
  --color-accent-800: #155e75;
  --color-accent-900: #164e63;

  /* Semantic Colors */
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  --color-info: #3b82f6;

  /* Neutrals - Slate Palette */
  --color-slate-50: #f8fafc;
  --color-slate-100: #f1f5f9;
  --color-slate-200: #e2e8f0;
  --color-slate-300: #cbd5e1;
  --color-slate-400: #94a3b8;
  --color-slate-500: #64748b;
  --color-slate-600: #475569;
  --color-slate-700: #334155;
  --color-slate-800: #1e293b;
  --color-slate-900: #0f172a;
  --color-slate-950: #020617;

  /* Theme Background */
  --bg-primary: var(--color-slate-900);
  --bg-secondary: var(--color-slate-800);
  --bg-tertiary: var(--color-slate-700);
  --bg-interactive: var(--color-primary-500);

  /* Text Colors */
  --text-primary: var(--color-slate-200);
  --text-secondary: var(--color-slate-400);
  --text-tertiary: var(--color-slate-500);
  --text-inverse: var(--color-slate-900);

  /* Borders */
  --border-color: var(--color-slate-700);
  --border-color-light: var(--color-slate-600);

  /* Shadows */
  --shadow-xs: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  --shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);

  /* Radius */
  --radius-xs: 4px;
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-2xl: 24px;
  --radius-full: 9999px;

  /* Spacing */
  --space-0: 0;
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-7: 28px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
  --space-16: 64px;

  /* Typography */
  --font-family-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  --font-family-mono: 'JetBrains Mono', 'Fira Code', 'Source Code Pro', monospace;

  /* Z-Index */
  --z-dropdown: 1000;
  --z-sticky: 1020;
  --z-fixed: 1030;
  --z-modal-backdrop: 1040;
  --z-modal: 1050;
  --z-tooltip: 1100;
}
```

---

## Component Implementation Examples

### 1. Button Component

```tsx
// Button.tsx
import { ReactNode } from 'react';

type ButtonVariant = 'primary' | 'secondary' | 'tertiary' | 'ghost';
type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps {
  children: ReactNode;
  onClick?: () => void;
  variant?: ButtonVariant;
  size?: ButtonSize;
  disabled?: boolean;
  loading?: boolean;
  icon?: ReactNode;
  className?: string;
}

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  icon,
  className = '',
  ...props
}: ButtonProps) {
  const baseStyles = `
    inline-flex items-center justify-center gap-2
    font-medium rounded-md transition-all duration-200
    disabled:opacity-50 disabled:cursor-not-allowed
    focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500
  `;

  const variants = {
    primary: `
      bg-primary-500 text-white
      hover:bg-primary-600 hover:-translate-y-0.5 hover:shadow-lg
      active:bg-primary-700 active:translate-y-0
    `,
    secondary: `
      bg-transparent border-2 border-slate-600 text-slate-200
      hover:bg-slate-700 hover:border-primary-500
      active:bg-slate-800
    `,
    tertiary: `
      bg-transparent text-primary-400
      hover:text-primary-300 hover:underline
      active:text-primary-500
    `,
    ghost: `
      bg-transparent text-slate-200
      hover:bg-slate-700 hover:text-slate-100
      active:bg-slate-800
    `,
  };

  const sizes = {
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-3 text-base',
    lg: 'px-6 py-4 text-lg',
  };

  return (
    <button
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <Spinner size={size === 'sm' ? 'xs' : 'sm'} />}
      {icon}
      {children}
    </button>
  );
}
```

### 2. Card Component

```tsx
// Card.tsx
interface CardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  border?: 'default' | 'gradient';
}

export function Card({
  children,
  className = '',
  hover = false,
  border = 'default',
}: CardProps) {
  const baseStyles = `
    bg-slate-800 rounded-lg p-6
    border transition-all duration-200
  `;

  const borderStyles = {
    default: 'border border-slate-700',
    gradient: 'border border-transparent bg-gradient-to-br from-slate-800 to-slate-800 bg-clip-border',
  };

  const hoverStyles = hover
    ? 'hover:-translate-y-1 hover:shadow-lg hover:border-slate-600'
    : '';

  return (
    <div className={`${baseStyles} ${borderStyles[border]} ${hoverStyles} ${className}`}>
      {children}
    </div>
  );
}
```

### 3. Input Component

```tsx
// Input.tsx
interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  icon?: ReactNode;
}

export function Input({
  label,
  error,
  helperText,
  icon,
  className = '',
  ...props
}: InputProps) {
  return (
    <div className="flex flex-col gap-2">
      {label && (
        <label className="text-sm font-medium text-slate-200">
          {label}
        </label>
      )}
      <div className="relative">
        {icon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
            {icon}
          </div>
        )}
        <input
          className={`
            w-full px-4 py-2 bg-slate-700 border border-slate-600
            text-slate-200 placeholder-slate-500 rounded-md
            focus:border-primary-500 focus:outline-none
            focus:ring-2 focus:ring-primary-500 focus:ring-opacity-10
            transition-all duration-200
            disabled:opacity-50 disabled:cursor-not-allowed
            ${icon ? 'pl-10' : ''}
            ${error ? 'border-error bg-error bg-opacity-10' : ''}
            ${className}
          `}
          {...props}
        />
      </div>
      {error && (
        <p className="text-sm text-error">{error}</p>
      )}
      {helperText && !error && (
        <p className="text-sm text-slate-400">{helperText}</p>
      )}
    </div>
  );
}
```

### 4. Tabs Component

```tsx
// Tabs.tsx
interface TabsProps {
  tabs: Array<{ label: string; id: string; content: ReactNode }>;
  defaultTab?: string;
  onChange?: (tabId: string) => void;
}

export function Tabs({
  tabs,
  defaultTab = tabs[0]?.id,
  onChange,
}: TabsProps) {
  const [activeTab, setActiveTab] = React.useState(defaultTab);

  const handleTabClick = (tabId: string) => {
    setActiveTab(tabId);
    onChange?.(tabId);
  };

  return (
    <div>
      <div className="flex gap-0 border-b border-slate-700">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => handleTabClick(tab.id)}
            className={`
              px-6 py-3 font-medium text-sm transition-all duration-200
              border-b-2 border-transparent
              ${
                activeTab === tab.id
                  ? 'text-slate-200 border-primary-500'
                  : 'text-slate-400 hover:text-slate-300'
              }
            `}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <div className="mt-4">
        {tabs.find((tab) => tab.id === activeTab)?.content}
      </div>
    </div>
  );
}
```

### 5. Badge Component

```tsx
// Badge.tsx
type BadgeVariant = 'success' | 'warning' | 'error' | 'info' | 'default';

interface BadgeProps {
  children: ReactNode;
  variant?: BadgeVariant;
  icon?: ReactNode;
}

export function Badge({ children, variant = 'default', icon }: BadgeProps) {
  const variants = {
    success: 'bg-success bg-opacity-20 text-success',
    warning: 'bg-warning bg-opacity-20 text-warning',
    error: 'bg-error bg-opacity-20 text-error',
    info: 'bg-info bg-opacity-20 text-info',
    default: 'bg-slate-700 text-slate-200',
  };

  return (
    <span
      className={`
        inline-flex items-center gap-1.5 px-3 py-1
        text-xs font-medium rounded-full
        ${variants[variant]}
      `}
    >
      {icon}
      {children}
    </span>
  );
}
```

---

## Layout Patterns

### Responsive Grid Layout

```tsx
// Grid.tsx
interface GridProps {
  children: React.ReactNode;
  cols?: {
    mobile?: number;
    tablet?: number;
    desktop?: number;
  };
  gap?: number;
}

export function Grid({
  children,
  cols = { mobile: 1, tablet: 2, desktop: 4 },
  gap = 4,
}: GridProps) {
  return (
    <div
      className={`
        grid gap-${gap}
        grid-cols-${cols.mobile}
        md:grid-cols-${cols.tablet}
        lg:grid-cols-${cols.desktop}
      `}
    >
      {children}
    </div>
  );
}
```

### Two-Column Layout

```tsx
// TwoColumnLayout.tsx
export function TwoColumnLayout({
  left,
  right,
}: {
  left: React.ReactNode;
  right: React.ReactNode;
}) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="lg:col-span-1">{left}</div>
      <div className="lg:col-span-1">{right}</div>
    </div>
  );
}
```

---

## Animation & Transition Patterns

### CSS Transitions

```css
/* animations/transitions.css */

/* Smooth fade */
.fade-in {
  animation: fadeIn 200ms ease-out forwards;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* Smooth slide up */
.slide-up {
  animation: slideUp 300ms ease-out forwards;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Button lift on hover */
.lift-on-hover {
  transition: transform 200ms ease-out, box-shadow 200ms ease-out;
}

.lift-on-hover:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

/* Loading spinner */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.spinner {
  animation: spin 2s linear infinite;
}
```

### React Transition Pattern

```tsx
// useTransition.tsx
export function useTransition(isVisible: boolean) {
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    let timer: NodeJS.Timeout;

    if (isVisible) {
      setMounted(true);
    } else {
      timer = setTimeout(() => setMounted(false), 300);
    }

    return () => clearTimeout(timer);
  }, [isVisible]);

  return {
    mounted,
    isVisible,
    className: isVisible ? 'opacity-100' : 'opacity-0',
  };
}
```

---

## Form Patterns

### Form with Validation

```tsx
// Form.tsx
interface FormValues {
  email: string;
  password: string;
}

export function LoginForm() {
  const [values, setValues] = React.useState<FormValues>({
    email: '',
    password: '',
  });
  const [errors, setErrors] = React.useState<Partial<FormValues>>({});
  const [isLoading, setIsLoading] = React.useState(false);

  const validate = () => {
    const newErrors: Partial<FormValues> = {};

    if (!values.email) newErrors.email = 'Email is required';
    if (!values.password) newErrors.password = 'Password is required';

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) return;

    setIsLoading(true);
    try {
      // Submit logic
    } catch (error) {
      setErrors({ email: 'Login failed' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        label="Email"
        type="email"
        value={values.email}
        onChange={(e) =>
          setValues({ ...values, email: e.target.value })
        }
        error={errors.email}
      />
      <Input
        label="Password"
        type="password"
        value={values.password}
        onChange={(e) =>
          setValues({ ...values, password: e.target.value })
        }
        error={errors.password}
      />
      <Button
        type="submit"
        disabled={isLoading}
        loading={isLoading}
      >
        Sign In
      </Button>
    </form>
  );
}
```

---

## Data Display Patterns

### Data Table

```tsx
// Table.tsx
interface Column<T> {
  key: keyof T;
  label: string;
  render?: (value: T[keyof T], item: T) => ReactNode;
}

interface TableProps<T> {
  data: T[];
  columns: Column<T>[];
  onRowClick?: (item: T) => void;
}

export function Table<T extends { id: string }>({
  data,
  columns,
  onRowClick,
}: TableProps<T>) {
  return (
    <div className="overflow-x-auto rounded-lg border border-slate-700">
      <table className="w-full">
        <thead>
          <tr className="border-b border-slate-700 bg-slate-800">
            {columns.map((col) => (
              <th
                key={String(col.key)}
                className="px-6 py-3 text-left text-sm font-medium text-slate-200"
              >
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((item, idx) => (
            <tr
              key={item.id}
              onClick={() => onRowClick?.(item)}
              className={`
                border-b border-slate-700 transition-colors
                ${
                  idx % 2 === 0 ? 'bg-slate-900' : 'bg-slate-800'
                }
                hover:bg-slate-700 cursor-pointer
              `}
            >
              {columns.map((col) => (
                <td
                  key={String(col.key)}
                  className="px-6 py-4 text-sm text-slate-200"
                >
                  {col.render
                    ? col.render(item[col.key], item)
                    : String(item[col.key])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

---

## Common Implementations

### Loading Skeleton

```tsx
// Skeleton.tsx
export function Skeleton({
  className = '',
}: {
  className?: string;
}) {
  return (
    <div
      className={`
        bg-slate-700 rounded animate-pulse
        ${className}
      `}
    />
  );
}

// Usage
export function CardSkeleton() {
  return (
    <Card>
      <Skeleton className="h-8 w-3/4 mb-4" />
      <Skeleton className="h-4 w-full mb-2" />
      <Skeleton className="h-4 w-5/6" />
    </Card>
  );
}
```

### Toast Notification

```tsx
// Toast.tsx
type ToastType = 'success' | 'error' | 'warning' | 'info';

interface ToastMessage {
  id: string;
  message: string;
  type: ToastType;
}

const useToast = () => {
  const [toasts, setToasts] = React.useState<ToastMessage[]>([]);

  const add = (message: string, type: ToastType = 'info') => {
    const id = Math.random().toString(36);
    setToasts((prev) => [...prev, { id, message, type }]);

    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 5000);
  };

  return { toasts, add };
};
```

---

## Best Practices

### 1. **Responsive Design**
- Mobile-first approach
- Use Tailwind breakpoints: `sm`, `md`, `lg`, `xl`, `2xl`
- Test on multiple screen sizes

### 2. **Accessibility**
- Always include semantic HTML
- Use ARIA labels where needed
- Ensure keyboard navigation
- Test with screen readers

### 3. **Performance**
- Lazy load components
- Memoize expensive computations
- Use pagination for large lists
- Optimize images and assets

### 4. **Code Organization**
- One component per file
- Clear naming conventions
- Props interface defined above component
- Export components from index.ts

### 5. **Styling**
- Use CSS variables for colors/spacing
- Avoid inline styles
- Keep Tailwind classes organized
- Use consistent naming for custom classes

---

## File Structure

```
src/
├── components/
│   ├── ui/
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── input.tsx
│   │   ├── tabs.tsx
│   │   ├── badge.tsx
│   │   └── index.ts
│   ├── layout/
│   │   ├── header.tsx
│   │   ├── sidebar.tsx
│   │   ├── main.tsx
│   │   └── index.ts
│   └── features/
│       ├── orchestrator/
│       │   ├── input-panel.tsx
│       │   ├── output-panel.tsx
│       │   └── index.ts
│       └── history/
│           ├── table.tsx
│           └── index.ts
├── styles/
│   ├── globals.css
│   ├── variables.css
│   ├── animations.css
│   └── index.css
├── hooks/
│   ├── useToast.ts
│   ├── useTheme.ts
│   └── index.ts
├── utils/
│   ├── cn.ts
│   └── colors.ts
├── types/
│   ├── index.ts
│   └── orchestrator.ts
└── pages/
    ├── orchestrator.tsx
    ├── flow.tsx
    ├── history.tsx
    └── settings.tsx
```

