import { Card } from "@/components/ui/card";
import { SelectField } from "./Field";
import { COMPANIES, SourcingCase } from "@/lib/agnes-data";
import { Boxes } from "lucide-react";
import { useEffect, useState } from "react";

export const InputCard = ({
  data,
  onChange,
}: {
  data: SourcingCase;
  onChange: (patch: Partial<SourcingCase>) => void;
}) => {
  const [products, setProducts] = useState<string[]>([]);

  useEffect(() => {
    if (data.company) {
      fetch(
        `http://localhost:8000/api/products/${encodeURIComponent(data.company)}`,
      )
        .then((res) => res.json())
        .then((json) => {
          if (json.products && json.products.length > 0) {
            setProducts(json.products);
            // Ensure the currently selected product is valid for this company
            if (!json.products.includes(data.product)) {
              onChange({ product: json.products[0] });
            }
          } else {
            setProducts([]);
          }
        })
        .catch((err) => {
          console.error("Failed to fetch products", err);
          setProducts([]);
        });
    } else {
      setProducts([]);
    }
  }, [data.company]);

  return (
    <Card className="p-7 shadow-elegant border-border/70 bg-card animate-fade-up">
      <div className="flex items-start gap-3 mb-6">
        <div className="h-10 w-10 rounded-lg bg-secondary text-primary flex items-center justify-center shrink-0">
          <Boxes className="h-5 w-5" />
        </div>
        <div>
          <h2 className="text-lg font-semibold tracking-tight">
            Sourcing Scenario
          </h2>
          <p className="text-sm text-muted-foreground">
            Define the company and finished good under evaluation.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-5">
        <SelectField
          label="Company"
          value={data.company}
          onChange={(v) => onChange({ company: v, product: "" })}
          options={COMPANIES}
        />
        <SelectField
          label="Finished Good"
          value={data.product}
          onChange={(v) => onChange({ product: v })}
          options={
            products.length > 0 ? products : [data.product].filter(Boolean)
          }
        />
      </div>
    </Card>
  );
};
