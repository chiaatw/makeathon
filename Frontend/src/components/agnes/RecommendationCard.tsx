import { Card } from "@/components/ui/card";
import { RecommendationStatus, SourcingCase } from "@/lib/agnes-data";
import { AlertTriangle, CheckCircle2, XCircle } from "lucide-react";
import { cn } from "@/lib/utils";

type Status = RecommendationStatus;

const statusConfig: Record<Status, { icon: any; color: string; bg: string; ring: string }> = {
  Suitable: {
    icon: CheckCircle2,
    color: "text-success",
    bg: "bg-success/10",
    ring: "ring-success/20",
  },
  "Suitable with Risk": {
    icon: AlertTriangle,
    color: "text-warning",
    bg: "bg-warning/10",
    ring: "ring-warning/30",
  },
  "Not Recommended": {
    icon: XCircle,
    color: "text-destructive",
    bg: "bg-destructive/10",
    ring: "ring-destructive/20",
  },
};

export const RecommendationCard = ({
  data,
  status = "Suitable with Risk",
  confidence = 78,
  recommendationText,
}: {
  data: SourcingCase;
  status?: Status;
  confidence?: number;
  recommendationText?: string;
}) => {
  const cfg = statusConfig[status];
  const Icon = cfg.icon;

  return (
    <Card className="relative overflow-hidden border-border/70 shadow-elevated bg-card animate-fade-up">
      <div className="absolute inset-x-0 top-0 h-32 bg-gradient-glow pointer-events-none" />
      <div className="relative p-7">
        <div className="flex items-start gap-5">
          <div className={cn("h-14 w-14 rounded-xl flex items-center justify-center ring-8", cfg.bg, cfg.ring)}>
            <Icon className={cn("h-7 w-7", cfg.color)} />
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span
                className={cn(
                  "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold",
                  cfg.bg,
                  cfg.color
                )}
              >
                {status}
              </span>
              <span className="text-xs text-muted-foreground">Final recommendation</span>
            </div>
            <h2 className="text-xl font-semibold tracking-tight text-foreground leading-snug">
              {recommendationText ??
                `${data.supplier} appears to be a viable candidate for ${data.ingredient.replace("-", " ")} based on functional similarity and available evidence, but certification verification remains incomplete.`}
            </h2>
          </div>

          <div className="text-right shrink-0">
            <div className="text-[11px] uppercase tracking-wider text-muted-foreground mb-1">Confidence</div>
            <div className="text-3xl font-semibold tracking-tight text-primary tabular-nums">{confidence}%</div>
            <div className="mt-2 h-1.5 w-24 rounded-full bg-secondary overflow-hidden">
              <div
                className="h-full bg-gradient-primary rounded-full transition-all duration-700 ease-smooth"
                style={{ width: `${confidence}%` }}
              />
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};
