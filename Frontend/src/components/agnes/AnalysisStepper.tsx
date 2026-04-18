import { Card } from "@/components/ui/card";
import { ANALYSIS_STEPS } from "@/lib/agnes-data";
import { Check, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

export const AnalysisStepper = ({
  currentStep,
  done,
  steps = ANALYSIS_STEPS,
}: {
  currentStep: number;
  done: boolean;
  steps?: readonly string[];
}) => (
  <Card className="p-7 shadow-elegant border-border/70 bg-card">
    <div className="flex items-baseline justify-between mb-6">
      <h3 className="text-base font-semibold tracking-tight">Analysis pipeline</h3>
      <span className="text-xs text-muted-foreground">
        {done ? "Completed" : `Step ${Math.min(currentStep + 1, steps.length)} of ${steps.length}`}
      </span>
    </div>

    <ol className="relative">
      {steps.map((step, i) => {
        const isDone = done || i < currentStep;
        const isActive = !done && i === currentStep;
        const isPending = !done && i > currentStep;

        return (
          <li
            key={step}
            className="relative flex items-start gap-4 pb-5 last:pb-0 animate-step-in"
            style={{ animationDelay: `${i * 60}ms` }}
          >
            {i < steps.length - 1 && (
              <div
                className={cn(
                  "absolute left-[15px] top-8 bottom-0 w-px transition-colors",
                  isDone ? "bg-primary/40" : "bg-border"
                )}
              />
            )}
            <div
              className={cn(
                "relative h-8 w-8 rounded-full flex items-center justify-center shrink-0 transition-all ease-smooth border-2",
                isDone && "bg-primary border-primary text-primary-foreground",
                isActive && "bg-card border-primary text-primary animate-pulse-ring",
                isPending && "bg-card border-border text-muted-foreground"
              )}
            >
              {isDone ? (
                <Check className="h-4 w-4" strokeWidth={3} />
              ) : isActive ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <span className="text-xs font-semibold">{i + 1}</span>
              )}
            </div>
            <div className="pt-1">
              <div
                className={cn(
                  "text-sm font-medium transition-colors",
                  isDone || isActive ? "text-foreground" : "text-muted-foreground"
                )}
              >
                {step}
              </div>
              {isActive && <div className="text-xs text-muted-foreground mt-0.5">Working…</div>}
            </div>
          </li>
        );
      })}
    </ol>
  </Card>
);
