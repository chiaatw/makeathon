import { Card } from "@/components/ui/card";
import { SourcingCase } from "@/lib/agnes-data";
import {
  Building2,
  Package,
  FlaskConical,
  Truck,
  Sparkles,
} from "lucide-react";

const Row = ({
  icon: Icon,
  label,
  value,
}: {
  icon: any;
  label: string;
  value: string;
}) => (
  <div className="flex items-center gap-3 py-2.5 border-b border-border/60 last:border-0">
    <div className="h-8 w-8 rounded-md bg-secondary text-primary flex items-center justify-center shrink-0">
      <Icon className="h-4 w-4" />
    </div>
    <div className="min-w-0 flex-1">
      <div className="text-[11px] uppercase tracking-wide text-muted-foreground">
        {label}
      </div>
      <div className="text-sm font-medium text-foreground truncate">
        {value}
      </div>
    </div>
  </div>
);

export const ContextSummary = ({ data }: { data: SourcingCase }) => (
  <Card
    className="p-6 shadow-elegant border-border/70 bg-card sticky top-24 animate-fade-up"
    style={{ animationDelay: "120ms" }}
  >
    <div className="flex items-center gap-2 mb-4">
      <Sparkles className="h-4 w-4 text-accent" />
      <h3 className="text-sm font-semibold uppercase tracking-wide text-foreground">
        Context preview
      </h3>
    </div>

    <div className="space-y-0">
      <Row icon={Building2} label="Company" value={data.company} />
      <Row icon={Package} label="Finished Good" value={data.product} />
    </div>

    <div className="mt-5 pt-5 border-t border-border/60">
      <div className="text-[11px] uppercase tracking-wide text-muted-foreground mb-3">
        Preferences
      </div>
      <div className="grid grid-cols-3 gap-2 text-center">
        {[
          { k: "Price", v: data.preferences.price },
          { k: "Lead", v: data.preferences.leadTime },
          { k: "Quality", v: data.preferences.quality },
        ].map((p) => (
          <div
            key={p.k}
            className="rounded-lg border border-border/60 bg-secondary/50 py-2.5"
          >
            <div className="text-[10px] uppercase tracking-wider text-muted-foreground">
              {p.k}
            </div>
            <div className="text-sm font-semibold text-primary">{p.v}</div>
          </div>
        ))}
      </div>
      <div className="mt-3 flex flex-wrap gap-1.5">
        {data.preferences.certifications.length === 0 && (
          <span className="text-xs text-muted-foreground italic">
            No required certifications
          </span>
        )}
        {data.preferences.certifications.map((c) => (
          <span
            key={c}
            className="text-xs px-2 py-0.5 rounded-full bg-primary/10 text-primary font-medium"
          >
            {c}
          </span>
        ))}
      </div>
    </div>
  </Card>
);
