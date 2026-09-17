"use client";

export function PageHeader({
  eyebrow,
  title,
  right,
}: {
  eyebrow: string;
  title: string;
  right?: React.ReactNode;
}) {
  return (
    <div className="flex items-end justify-between mb-6 flex-wrap gap-3">
      <div>
        <p className="text-xs uppercase tracking-wide text-muted mb-1">{eyebrow}</p>
        <h1 className="text-3xl" style={{ fontFamily: "var(--font-head)" }}>
          {title}
        </h1>
      </div>
      {right}
    </div>
  );
}

export function Panel({
  title,
  action,
  children,
}: {
  title: string;
  action?: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <div className="bg-panel border border-border p-5 rounded-lg">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm uppercase tracking-wide text-muted">{title}</h2>
        {action}
      </div>
      {children}
    </div>
  );
}

export function StatCard({ label, value, sub }: { label: string; value: string; sub: string }) {
  return (
    <div className="bg-panel border border-border p-4 rounded-lg" style={{ borderLeft: "3px solid var(--accent)" }}>
      <p className="text-xs uppercase tracking-wide text-muted-2 mb-2">{label}</p>
      <p className="text-2xl mb-1" style={{ fontFamily: "var(--font-head)" }}>
        {value}
      </p>
      <p className="text-xs text-muted">{sub}</p>
    </div>
  );
}

export function VerseBlock({ text, reference }: { text: string; reference: string }) {
  return (
    <blockquote>
      <p className="leading-relaxed text-text/90" style={{ fontFamily: "var(--font-head)" }}>
        &ldquo;{text}&rdquo;
      </p>
      <footer className="text-sm text-muted mt-2">— {reference}</footer>
    </blockquote>
  );
}
