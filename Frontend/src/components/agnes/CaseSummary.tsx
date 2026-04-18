import { Card } from "@/components/ui/card";
import { SourcingCase } from "@/lib/agnes-data";
import { Building2, FlaskConical, Package, Truck } from "lucide-react";

const Cell = ({
  icon: Icon,
  label,
  value,
}: {
  icon: any;
  label: string;
  value: string;
}) => (
  <div className="flex items-center gap-3 px-5 py-4 flex-1 min-w-0">
    <div className="h-9 w-9 rounded-lg bg-secondary text-primary flex items-center justify-center shrink-0">
      <Icon className="h-4 w-4" />
    </div>
    <div className="min-w-0">
      <div className="text-[10px] uppercase tracking-wider text-muted-foreground">
        {label}
      </div>
      <div className="text-sm font-semibold text-foreground truncate">
        {value}
      </div>
    </div>
  </div>
);

export const CaseSummary = ({ data }: { data: SourcingCase }) => (
  <Card className="overflow-hidden border-border/70 shadow-elegant bg-card animate-fade-up">
    <div className="flex divide-x divide-border/60">
      <Cell icon={Building2} label="Company" value={data.company} />
      <Cell icon={Package} label="Finished Good" value={data.product} />
    </div>
    <div className="flex items-center gap-3 px-5 py-3 bg-secondary/40 border-t border-border/60">
      <span className="text-[10px] uppercase tracking-wider text-muted-foreground">
        Preferences
      </span>
      <div className="flex flex-wrap gap-1.5">
        <span className="text-xs px-2 py-0.5 rounded-full bg-card border border-border/70 text-foreground">
          Price · {data.preferences.price}
        </span>
        <span className="text-xs px-2 py-0.5 rounded-full bg-card border border-border/70 text-foreground">
          Lead · {data.preferences.leadTime}
        </span>
        <span className="text-xs px-2 py-0.5 rounded-full bg-card border border-border/70 text-foreground">
          Quality · {data.preferences.quality}
        </span>
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
