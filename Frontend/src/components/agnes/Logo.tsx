export const AgnesLogo = ({ className = "" }: { className?: string }) => (
  <div className={`flex items-center gap-2.5 ${className}`}>
    <div className="relative h-9 w-9 rounded-lg bg-gradient-primary shadow-glow flex items-center justify-center">
      <svg viewBox="0 0 24 24" className="h-5 w-5 text-primary-foreground" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 2 L4 7 v10 l8 5 8-5 V7 z" />
        <path d="M12 7 v10 M7 9.5 l10 5 M17 9.5 l-10 5" opacity="0.6" />
      </svg>
    </div>
    <div className="leading-tight">
      <div className="text-base font-semibold tracking-tight text-foreground">Agnes</div>
      <div className="text-[10px] uppercase tracking-[0.14em] text-muted-foreground font-medium">Sourcing Intelligence</div>
    </div>
  </div>
);
