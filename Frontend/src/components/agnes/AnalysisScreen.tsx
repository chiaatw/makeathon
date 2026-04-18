import { Button } from "@/components/ui/button";
import { ANALYSIS_STEPS, SourcingCase } from "@/lib/agnes-data";
import { useEffect, useState } from "react";
import { ArrowLeft, RefreshCw } from "lucide-react";
import { CaseSummary } from "./CaseSummary";
import { AnalysisStepper } from "./AnalysisStepper";
import { RecommendationCard } from "./RecommendationCard";
import { ReasonList, RiskList, EvidenceList } from "./InsightLists";
import { TradeoffCards } from "./TradeoffCards";

export const AnalysisScreen = ({
  data,
  onBack,
  onAnother,
}: {
  data: SourcingCase;
  onBack: () => void;
  onAnother: () => void;
}) => {
  const [step, setStep] = useState(0);
  const [done, setDone] = useState(false);

  useEffect(() => {
    setStep(0);
    setDone(false);
    const interval = setInterval(() => {
      setStep((s) => {
        if (s >= ANALYSIS_STEPS.length - 1) {
          clearInterval(interval);
          setTimeout(() => setDone(true), 450);
          return s + 1;
        }
        return s + 1;
      });
    }, 480);
    return () => clearInterval(interval);
  }, [data]);

  return (
    <div className="max-w-7xl mx-auto px-8 py-10 space-y-7">
      <div className="flex items-center justify-between animate-fade-up">
        <div>
          <div className="text-xs uppercase tracking-wider text-muted-foreground mb-1">Decision report</div>
          <h1 className="text-3xl font-semibold tracking-tight">Sourcing analysis</h1>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={onBack} className="ease-smooth">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to setup
          </Button>
          <Button onClick={onAnother} className="bg-primary hover:bg-primary-glow ease-smooth">
            <RefreshCw className="mr-2 h-4 w-4" />
            Analyze another case
          </Button>
        </div>
      </div>

      <CaseSummary data={data} />

      <div className="grid grid-cols-3 gap-7">
        <div className="col-span-1">
          <AnalysisStepper currentStep={step} done={done} />
        </div>

        <div className="col-span-2 space-y-6">
          {done ? (
            <>
              <RecommendationCard data={data} />
              <div className="grid grid-cols-2 gap-6">
                <ReasonList />
                <RiskList />
              </div>
              <EvidenceList />
              <TradeoffCards />
            </>
          ) : (
            <div className="rounded-xl border border-border/70 bg-card shadow-elegant p-12 flex flex-col items-center justify-center text-center min-h-[400px]">
              <div className="relative h-16 w-16 mb-5">
                <div className="absolute inset-0 rounded-full bg-gradient-primary opacity-20 animate-pulse-ring" />
                <div className="absolute inset-2 rounded-full bg-gradient-primary shadow-glow flex items-center justify-center">
                  <RefreshCw className="h-6 w-6 text-primary-foreground animate-spin" />
                </div>
              </div>
              <div className="text-base font-semibold text-foreground">Analyzing sourcing decision</div>
              <div className="text-sm text-muted-foreground mt-1 max-w-sm">
                Agnes is gathering evidence, evaluating compliance, and weighing your preferences.
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
