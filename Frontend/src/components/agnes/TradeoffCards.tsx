import { Card } from "@/components/ui/card";
import { TradeoffItem } from "@/lib/agnes-data";
import { cn } from "@/lib/utils";
import { DollarSign, Clock, Award, ShieldAlert } from "lucide-react";

type Level = "Low" | "Medium" | "High" | "Lower";

const defaultTradeoffs: { icon: any; label: string; value: Level; tone: "good" | "neutral" | "warn" }[] = [
  { icon: DollarSign, label: "Cost", value: "Lower", tone: "good" },
  { icon: Clock, label: "Lead time", value: "Medium", tone: "neutral" },
  { icon: Award, label: "Quality", value: "High", tone: "good" },
  { icon: ShieldAlert, label: "Compliance risk", value: "Medium", tone: "warn" },
];

const toneClasses = {
  good: "text-success bg-success/10",
  neutral: "text-primary bg-primary/10",
  warn: "text-warning bg-warning/15",
};

const barWidth = { Low: "25%", Lower: "30%", Medium: "55%", High: "90%" } as const;
const barTone = {
  good: "bg-success",
  neutral: "bg-primary",
  warn: "bg-warning",
};

const iconByLabel = {
  Cost: DollarSign,
  "Lead time": Clock,
  Quality: Award,
  "Compliance risk": ShieldAlert,
} as const;

export const TradeoffCards = ({ tradeoffs }: { tradeoffs?: TradeoffItem[] }) => (
  <Card className="p-6 shadow-elegant border-border/70 bg-card">
    <div className="flex items-center justify-between mb-5">
      <h3 className="text-sm font-semibold tracking-tight">Trade-offs</h3>
      <span className="text-xs text-muted-foreground">Reflects your preferences</span>
    </div>
    <div className="grid grid-cols-4 gap-4">
      {(tradeoffs && tradeoffs.length > 0 ? tradeoffs : defaultTradeoffs).map((t) => {
        const Icon = iconByLabel[t.label as keyof typeof iconByLabel] ?? ShieldAlert;
        return (
        <div key={t.label} className="rounded-lg border border-border/60 bg-secondary/30 p-4">
          <div className="flex items-center gap-2 mb-3">
            <div className={cn("h-7 w-7 rounded-md flex items-center justify-center", toneClasses[t.tone])}>
              <Icon className="h-3.5 w-3.5" />
            </div>
            <span className="text-xs uppercase tracking-wide text-muted-foreground font-medium">{t.label}</span>
          </div>
          <div className="text-lg font-semibold text-foreground mb-2">{t.value}</div>
          <div className="h-1.5 rounded-full bg-card overflow-hidden">
            <div
              className={cn("h-full rounded-full transition-all duration-700 ease-smooth", barTone[t.tone])}
              style={{ width: barWidth[t.value] }}
            />
          </div>
        </div>
        );
      })}
    </div>
  </Card>
);
