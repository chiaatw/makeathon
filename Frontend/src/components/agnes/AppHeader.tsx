import { AgnesLogo } from "./Logo";

export const AppHeader = () => (
  <header className="border-b border-border/70 bg-card/70 backdrop-blur-md sticky top-0 z-30">
    <div className="max-w-7xl mx-auto px-8 h-16 flex items-center justify-between">
      <AgnesLogo />
      <nav className="flex items-center gap-1 text-sm">
        <span className="px-3 py-1.5 rounded-md text-foreground font-medium bg-secondary">Decision Studio</span>
        <span className="px-3 py-1.5 rounded-md text-muted-foreground hover:text-foreground transition-colors cursor-default">Suppliers</span>
        <span className="px-3 py-1.5 rounded-md text-muted-foreground hover:text-foreground transition-colors cursor-default">Audit Log</span>
      </nav>
      <div className="flex items-center gap-3">
        <div className="text-xs text-muted-foreground hidden md:block">Demo workspace</div>
        <div className="h-9 w-9 rounded-full bg-gradient-accent text-accent-foreground flex items-center justify-center text-xs font-semibold shadow-elegant">AC</div>
      </div>
    </div>
  </header>
);
