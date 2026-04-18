import { Card } from "@/components/ui/card";
import { TradeoffItem } from "@/lib/agnes-data";
import { cn } from "@/lib/utils";
import { CheckCircle2, Clock, DollarSign, Factory, Award, ShieldAlert, Package } from "lucide-react";

type Level = "Low" | "Medium" | "High" | "Lower";

type DetailedBackendData = {
  finished_goods_compliance?: {
    product_sku?: string;
    required_compliance?: string[];
  };
  raw_materials_comparison?: Array<
    | string
    | {
        raw_material_sku?: string;
        supplier_comparison?: Array<{
          supplier?: string;
          fulfilled_compliance?: string[];
        }>;
      }
  >;
};

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

function parseBackendData(raw: unknown): DetailedBackendData | null {
  if (!raw || typeof raw !== "object") {
    return null;
  }

  const maybeDetailed = raw as DetailedBackendData;
  if (maybeDetailed.finished_goods_compliance || maybeDetailed.raw_materials_comparison) {
    return maybeDetailed;
  }

  const wrapper = raw as { detailed_supply_chain?: DetailedBackendData };
  if (wrapper.detailed_supply_chain) {
    return wrapper.detailed_supply_chain;
  }

  return null;
}

export const TradeoffCards = ({
  tradeoffs,
  backendData,
}: {
  tradeoffs?: TradeoffItem[];
  backendData?: unknown;
}) => {
  const detailed = parseBackendData(backendData);

  if (detailed) {
    const fgs = detailed.finished_goods_compliance || {};
    const rms = detailed.raw_materials_comparison || [];

    let parsedRms: Array<{
      raw_material_sku?: string;
      supplier_comparison?: Array<{ supplier?: string; fulfilled_compliance?: string[] }>;
    }> = [];

    try {
      parsedRms = rms.map((rm) => (typeof rm === "string" ? JSON.parse(rm) : rm));
    } catch {
      parsedRms = [];
    }

    const required = fgs.required_compliance || [];

    return (
      <Card className="p-6 shadow-elegant border-border/70 bg-card">
        <div className="flex items-center justify-between mb-5">
          <h3 className="text-lg font-semibold tracking-tight">Supply Chain AI Compliance Analysis</h3>
        </div>

        <div className="space-y-6">
          <div className="rounded-xl border border-primary/20 bg-primary/5 p-5">
            <div className="flex items-center gap-3 mb-4">
              <Package className="w-5 h-5 text-primary" />
              <div className="font-semibold text-primary-foreground text-md">
                Required Direct Compliance for {fgs.product_sku || "Main Product"}
              </div>
            </div>
            <ul className="list-disc list-inside space-y-1 ml-4 text-sm text-foreground">
              {required.map((req, i) => (
                <li key={`${req}-${i}`}>{req}</li>
              ))}
              {required.length === 0 && (
                <span className="text-muted-foreground">No specific compliance requirements discovered.</span>
              )}
            </ul>
          </div>

          <div className="space-y-4">
            <h4 className="text-md font-semibold font-medium text-foreground">Available Suppliers & Fulfillments</h4>
            {parsedRms.map((rmItem, idx) => {
              const suppliers = [...(rmItem.supplier_comparison || [])].sort(
                (a, b) => (b.fulfilled_compliance?.length || 0) - (a.fulfilled_compliance?.length || 0),
              );

              return (
                <div key={idx} className="border border-border/60 rounded-xl p-5 bg-card shadow-sm">
                  <div className="text-sm uppercase tracking-wide font-bold text-muted-foreground mb-3">
                    Raw Material: {rmItem.raw_material_sku || "Unknown"}
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    {suppliers.map((s, sIdx) => (
                      <div key={sIdx} className="rounded-lg bg-secondary/30 border border-border/50 p-4">
                        <div className="flex items-center gap-2 mb-2">
                          <Factory className="w-4 h-4 text-muted-foreground" />
                          <span className="font-semibold text-foreground">{s.supplier || "Unknown supplier"}</span>
                        </div>
                        <div className="text-xs text-muted-foreground mb-2">Verified Compliance:</div>
                        <ul className="space-y-1.5 list-none">
                          {(s.fulfilled_compliance || []).map((fc, fcIdx) => (
                            <li key={`${fc}-${fcIdx}`} className="flex gap-2 text-xs items-start">
                              <CheckCircle2 className="w-3.5 h-3.5 text-success shrink-0 mt-0.5" />
                              <span className="text-foreground">{fc}</span>
                            </li>
                          ))}
                          {!(s.fulfilled_compliance || []).length && (
                            <span className="text-xs text-muted-foreground italic">None explicitly found.</span>
                          )}
                        </ul>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </Card>
    );
  }

  return (
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
                  style={{ width: barWidth[t.value as Level] }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
};
