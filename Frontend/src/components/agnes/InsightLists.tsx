import { Card } from "@/components/ui/card";
import { AlertCircle, FileText, Link2, Lightbulb, Database, ShieldCheck } from "lucide-react";

const SectionCard = ({
  title,
  icon: Icon,
  tone = "default",
  children,
}: {
  title: string;
  icon: any;
  tone?: "default" | "warning";
  children: React.ReactNode;
}) => (
  <Card className="p-6 shadow-elegant border-border/70 bg-card h-full">
    <div className="flex items-center gap-2.5 mb-4">
      <div
        className={
          tone === "warning"
            ? "h-8 w-8 rounded-md bg-warning/10 text-warning flex items-center justify-center"
            : "h-8 w-8 rounded-md bg-secondary text-primary flex items-center justify-center"
        }
      >
        <Icon className="h-4 w-4" />
      </div>
      <h3 className="text-sm font-semibold tracking-tight">{title}</h3>
    </div>
    {children}
  </Card>
);

const Bullet = ({ children, tone = "default" }: { children: React.ReactNode; tone?: "default" | "warning" }) => (
  <li className="flex items-start gap-3 py-2 text-sm text-foreground/90 leading-relaxed">
    <span
      className={
        tone === "warning"
          ? "mt-1.5 h-1.5 w-1.5 rounded-full bg-warning shrink-0"
          : "mt-1.5 h-1.5 w-1.5 rounded-full bg-primary shrink-0"
      }
    />
    <span>{children}</span>
  </li>
);

export const ReasonList = () => (
  <SectionCard title="Why this recommendation" icon={Lightbulb}>
    <ul className="divide-y divide-border/50">
      <Bullet>High functional similarity to reference ingredient profile</Bullet>
      <Bullet>Supplier provides food-grade compatible material</Bullet>
      <Bullet>Matches user-defined priorities (Quality: High, Price: High)</Bullet>
      <Bullet>Similar ingredient usage pattern across comparable companies</Bullet>
    </ul>
  </SectionCard>
);

export const RiskList = () => (
  <SectionCard title="Risks & uncertainty" icon={AlertCircle} tone="warning">
    <ul className="divide-y divide-border/50">
      <Bullet tone="warning">Missing certification documents (ISO 22000)</Bullet>
      <Bullet tone="warning">Limited external evidence sources available</Bullet>
      <Bullet tone="warning">Compliance status not fully verified</Bullet>
      <Bullet tone="warning">Supplier documentation incomplete for batch traceability</Bullet>
    </ul>
  </SectionCard>
);

const evidence = [
  { icon: Link2, title: "Supplier product page", meta: "supplierb.com/citric-acid", tag: "External" },
  { icon: Database, title: "Internal DB match", meta: "BOM record · 4 prior usages", tag: "Internal" },
  { icon: ShieldCheck, title: "Regulatory guidance", meta: "FDA 21 CFR §184.1033", tag: "Regulatory" },
  { icon: FileText, title: "Technical description", meta: "Spec sheet v2.1", tag: "Document" },
];

export const EvidenceList = () => (
  <SectionCard title="Evidence sources" icon={FileText}>
    <div className="grid grid-cols-2 gap-2.5">
      {evidence.map((e) => (
        <div
          key={e.title}
          className="flex items-start gap-3 p-3 rounded-lg border border-border/60 bg-secondary/30 hover:border-primary/40 hover:bg-secondary/60 transition-all ease-smooth cursor-default"
        >
          <div className="h-7 w-7 rounded-md bg-card text-primary flex items-center justify-center shrink-0 border border-border/60">
            <e.icon className="h-3.5 w-3.5" />
          </div>
          <div className="min-w-0 flex-1">
            <div className="text-sm font-medium text-foreground truncate">{e.title}</div>
            <div className="text-xs text-muted-foreground truncate">{e.meta}</div>
          </div>
          <span className="text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded bg-card border border-border/60 text-muted-foreground shrink-0">
            {e.tag}
          </span>
        </div>
      ))}
    </div>
  </SectionCard>
);
