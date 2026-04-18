import { Card } from "@/components/ui/card";
import { SourcingCase } from "@/lib/agnes-data";
import { AlertTriangle, CheckCircle2, XCircle } from "lucide-react";
import { cn } from "@/lib/utils";

type Status = "Suitable" | "Suitable with Risk" | "Not Recommended";

const statusConfig: Record<
  Status,
  { icon: any; color: string; bg: string; ring: string }
> = {
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
  backendData,
}: {
  data: SourcingCase;
  backendData?: any;
}) => {
  let rms = backendData?.raw_materials_comparison || [];
  let parsedRms: any[] = [];
  try {
    parsedRms = rms.map((rm: any) =>
      typeof rm === "string" ? JSON.parse(rm) : rm,
    );
  } catch (e) {}

  let totalRMs = parsedRms.length;
  let rmsWithAtLeastOneCompliantSupplier = 0;

  parsedRms.forEach((rmItem) => {
    const suppliers = rmItem.supplier_comparison || [];
    const hasCompliant = suppliers.some(
      (s: any) => (s.fulfilled_compliance || []).length > 0,
    );
    if (hasCompliant) {
      rmsWithAtLeastOneCompliantSupplier++;
    }
  });

  let status: Status = "Suitable with Risk";
  let colorTheme = statusConfig["Suitable with Risk"];
  let message = "";
  let confidence = 0;

  if (totalRMs === 0) {
    status = "Suitable with Risk";
    message = `No active raw material compliance data returned for ${data.product}. Proceed with manual verification.`;
    confidence = 50;
  } else if (rmsWithAtLeastOneCompliantSupplier === totalRMs) {
    status = "Suitable";
    colorTheme = statusConfig["Suitable"];
    message = `The ${data.product} from ${data.company} appears highly viable. All ${totalRMs} major sub-components have at least one valid substitute supplier verifying strict compliance limits.`;
    confidence = 94;
  } else if (rmsWithAtLeastOneCompliantSupplier > 0) {
    status = "Suitable with Risk";
    message = `The ${data.product} finished good from ${data.company} has mixed viability. Only ${rmsWithAtLeastOneCompliantSupplier} out of ${totalRMs} raw materials have a cleanly compliant supplier available. Expect sourcing bottlenecks.`;
    confidence =
      Math.round((rmsWithAtLeastOneCompliantSupplier / totalRMs) * 100) - 10;
  } else {
    status = "Not Recommended";
    colorTheme = statusConfig["Not Recommended"];
    message = `We strongly advise against sourcing ${data.product} right now. 0 out of ${totalRMs} required raw materials have compliance-verified suppliers. Significant supply chain block.`;
    confidence = 22;
  }

  const Icon = colorTheme.icon;

  return (
    <Card className="relative overflow-hidden border-border/70 shadow-elevated bg-card animate-fade-up">
      <div className="absolute inset-x-0 top-0 h-32 bg-gradient-glow pointer-events-none" />
      <div className="relative p-7">
        <div className="flex items-start gap-5">
          <div
            className={cn(
              "h-14 w-14 rounded-xl flex items-center justify-center ring-8",
              colorTheme.bg,
              colorTheme.ring,
            )}
          >
            <Icon className={cn("h-7 w-7", colorTheme.color)} />
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span
                className={cn(
                  "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold",
                  colorTheme.bg,
                  colorTheme.color,
                )}
              >
                {status}
              </span>
              <span className="text-xs text-muted-foreground">
                Final recommendation
              </span>
            </div>
            <h2 className="text-xl font-semibold tracking-tight text-foreground leading-snug">
              {message}
            </h2>
          </div>

          <div className="text-right shrink-0">
            <div className="text-[11px] uppercase tracking-wider text-muted-foreground mb-1">
              Confidence
            </div>
            <div className="text-3xl font-semibold tracking-tight text-primary tabular-nums">
              {confidence}%
            </div>
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
