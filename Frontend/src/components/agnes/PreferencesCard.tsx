import { Card } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import { CERTIFICATIONS, Preferences, PriorityLevel } from "@/lib/agnes-data";
import { SlidersHorizontal, ShieldCheck, Check } from "lucide-react";
import { cn } from "@/lib/utils";

const LEVELS: PriorityLevel[] = ["Low", "Medium", "High"];

const PriorityToggle = ({
  label,
  value,
  onChange,
}: {
  label: string;
  value: PriorityLevel;
  onChange: (v: PriorityLevel) => void;
}) => (
  <div className="space-y-2">
    <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">{label}</Label>
    <div className="grid grid-cols-3 gap-1 p-1 rounded-lg bg-secondary border border-border/70">
      {LEVELS.map((l) => (
        <button
          key={l}
          type="button"
          onClick={() => onChange(l)}
          className={cn(
            "h-9 text-sm font-medium rounded-md transition-all ease-smooth",
            value === l
              ? "bg-card text-foreground shadow-sm"
              : "text-muted-foreground hover:text-foreground"
          )}
        >
          {l}
        </button>
      ))}
    </div>
  </div>
);

const CertChip = ({
  label,
  active,
  onClick,
}: {
  label: string;
  active: boolean;
  onClick: () => void;
}) => (
  <button
    type="button"
    onClick={onClick}
    className={cn(
      "inline-flex items-center gap-1.5 h-9 px-3.5 rounded-full text-sm font-medium border transition-all ease-smooth",
      active
        ? "bg-primary text-primary-foreground border-primary shadow-sm"
        : "bg-card text-foreground border-border hover:border-primary/40"
    )}
  >
    {active && <Check className="h-3.5 w-3.5" />}
    {label}
  </button>
);

export const PreferencesCard = ({
  prefs,
  onChange,
}: {
  prefs: Preferences;
  onChange: (patch: Partial<Preferences>) => void;
}) => {
  const toggleCert = (c: string) => {
    onChange({
      certifications: prefs.certifications.includes(c)
        ? prefs.certifications.filter((x) => x !== c)
        : [...prefs.certifications, c],
    });
  };

  return (
    <Card className="p-7 shadow-elegant border-border/70 bg-card animate-fade-up" style={{ animationDelay: "60ms" }}>
      <div className="flex items-start gap-3 mb-6">
        <div className="h-10 w-10 rounded-lg bg-secondary text-primary flex items-center justify-center shrink-0">
          <SlidersHorizontal className="h-5 w-5" />
        </div>
        <div>
          <h2 className="text-lg font-semibold tracking-tight">Sourcing Preferences</h2>
          <p className="text-sm text-muted-foreground">What matters most for this decision?</p>
        </div>
      </div>

      <div className="space-y-7">
        <div className="grid grid-cols-3 gap-5">
          <PriorityToggle label="Price importance" value={prefs.price} onChange={(v) => onChange({ price: v })} />
          <PriorityToggle label="Lead time importance" value={prefs.leadTime} onChange={(v) => onChange({ leadTime: v })} />
          <PriorityToggle label="Quality importance" value={prefs.quality} onChange={(v) => onChange({ quality: v })} />
        </div>

        <div className="h-px bg-border/70" />

        <div className="grid grid-cols-2 gap-7">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label className="text-sm font-medium">Require certifications</Label>
              <Switch
                checked={prefs.requireCertifications}
                onCheckedChange={(v) => onChange({ requireCertifications: v })}
              />
            </div>
            <p className="text-xs text-muted-foreground">Reject suppliers without listed certifications.</p>
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label className="text-sm font-medium">Max lead time</Label>
              <span className="text-sm font-semibold text-primary">{prefs.maxLeadTimeDays} days</span>
            </div>
            <Slider
              value={[prefs.maxLeadTimeDays]}
              min={7}
              max={90}
              step={1}
              onValueChange={([v]) => onChange({ maxLeadTimeDays: v })}
            />
          </div>
        </div>

        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-4 w-4 text-primary" />
            <Label className="text-sm font-medium">Required certifications</Label>
          </div>
          <div className="flex flex-wrap gap-2">
            {CERTIFICATIONS.map((c) => (
              <CertChip key={c} label={c} active={prefs.certifications.includes(c)} onClick={() => toggleCert(c)} />
            ))}
          </div>
        </div>
      </div>
    </Card>
  );
};
