import { Card } from "@/components/ui/card";
import { SelectField } from "./Field";
import { COMPANIES, INGREDIENTS, PRODUCTS, SUPPLIERS, SourcingCase } from "@/lib/agnes-data";
import { Boxes } from "lucide-react";

export const InputCard = ({
  data,
  onChange,
}: {
  data: SourcingCase;
  onChange: (patch: Partial<SourcingCase>) => void;
}) => (
  <Card className="p-7 shadow-elegant border-border/70 bg-card animate-fade-up">
    <div className="flex items-start gap-3 mb-6">
      <div className="h-10 w-10 rounded-lg bg-secondary text-primary flex items-center justify-center shrink-0">
        <Boxes className="h-5 w-5" />
      </div>
      <div>
        <h2 className="text-lg font-semibold tracking-tight">Sourcing Scenario</h2>
        <p className="text-sm text-muted-foreground">Define the company, product, and ingredient under evaluation.</p>
      </div>
    </div>

    <div className="grid grid-cols-2 gap-5">
      <SelectField label="Company" value={data.company} onChange={(v) => onChange({ company: v })} options={COMPANIES} />
      <SelectField label="Product" value={data.product} onChange={(v) => onChange({ product: v })} options={PRODUCTS} />
      <SelectField label="Ingredient" value={data.ingredient} onChange={(v) => onChange({ ingredient: v })} options={INGREDIENTS} />
      <SelectField
        label="Supplier candidate"
        value={data.supplier}
        onChange={(v) => onChange({ supplier: v })}
        options={SUPPLIERS}
        hint="Optional — leave default to auto-select"
      />
    </div>
  </Card>
);
