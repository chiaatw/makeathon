import { Button } from "@/components/ui/button";
import { EnumsResponse, SourcingCase } from "@/lib/agnes-data";
import { ArrowRight, Sparkles } from "lucide-react";
import { ContextSummary } from "./ContextSummary";
import { InputCard } from "./InputCard";
import { PreferencesCard } from "./PreferencesCard";

export const InputScreen = ({
  data,
  setData,
  onRun,
  enums,
}: {
  data: SourcingCase;
  setData: (d: SourcingCase) => void;
  onRun: () => void;
  enums?: EnumsResponse;
}) => {
  const updateCase = (patch: Partial<SourcingCase>) => setData({ ...data, ...patch });
  const updatePrefs = (patch: Partial<SourcingCase["preferences"]>) =>
    setData({ ...data, preferences: { ...data.preferences, ...patch } });

  return (
    <div className="max-w-7xl mx-auto px-8 py-10">
      <div className="mb-10 animate-fade-up">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/5 border border-primary/15 text-primary text-xs font-medium mb-4">
          <Sparkles className="h-3.5 w-3.5" />
          AI-assisted decision support
        </div>
        <h1 className="text-4xl font-semibold tracking-tight text-foreground">Evaluate a sourcing decision</h1>
        <p className="mt-2 text-base text-muted-foreground max-w-2xl">
          Select a sourcing scenario and define decision criteria to evaluate supplier suitability and compliance.
        </p>
      </div>

      <div className="grid grid-cols-3 gap-7">
        <div className="col-span-2 space-y-6">
          <InputCard
            data={data}
            onChange={updateCase}
            companies={enums?.companies}
            products={enums?.products}
            ingredients={enums?.ingredients}
            suppliers={enums?.suppliers}
          />
          <PreferencesCard
            prefs={data.preferences}
            onChange={updatePrefs}
            certifications={enums?.certifications}
          />

          <div className="flex items-center justify-between p-5 rounded-xl border border-border/70 bg-card shadow-elegant animate-fade-up" style={{ animationDelay: "180ms" }}>
            <div>
              <div className="text-sm font-semibold text-foreground">Ready to analyze</div>
              <div className="text-xs text-muted-foreground">Agnes will retrieve evidence, evaluate compliance, and generate a recommendation.</div>
            </div>
            <Button
              size="lg"
              onClick={onRun}
              className="h-12 px-6 bg-gradient-primary hover:opacity-95 shadow-glow text-primary-foreground font-medium ease-smooth"
            >
              Run analysis
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </div>
        </div>

        <div className="col-span-1">
          <ContextSummary data={data} />
        </div>
      </div>
    </div>
  );
};
