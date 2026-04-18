import { Button } from "@/components/ui/button";
<<<<<<< HEAD
import { ANALYSIS_STEPS, AnalysisResult, SourcingCase } from "@/lib/agnes-data";
=======
import { SourcingCase } from "@/lib/agnes-data";
>>>>>>> cd98d932d8b724f66afd788683a78074649a63a7
import { useEffect, useState } from "react";
import { ArrowLeft, RefreshCw, AlertCircle } from "lucide-react";
import { CaseSummary } from "./CaseSummary";
import { RecommendationCard } from "./RecommendationCard";
import { ReasonList, RiskList, EvidenceList } from "./InsightLists";
import { TradeoffCards } from "./TradeoffCards";
import { createAnalysisEventSource, getAnalysisStatus, startAnalysis } from "@/lib/api";

export const AnalysisScreen = ({
  data,
  onBack,
  onAnother,
  analysisSteps = ANALYSIS_STEPS,
}: {
  data: SourcingCase;
  onBack: () => void;
  onAnother: () => void;
  analysisSteps?: readonly string[];
}) => {
  const [done, setDone] = useState(false);
<<<<<<< HEAD
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
=======
  const [error, setError] = useState<string | null>(null);
  const [backendData, setBackendData] = useState<any>(null);
>>>>>>> cd98d932d8b724f66afd788683a78074649a63a7

  useEffect(() => {
    setDone(false);
<<<<<<< HEAD
    setResult(null);
    setError(null);

    let eventSource: EventSource | null = null;

    const run = async () => {
      try {
        const started = await startAnalysis(data);
        eventSource = createAnalysisEventSource(started.analysis_id);

        eventSource.addEventListener("step_started", (ev) => {
          const parsed = JSON.parse((ev as MessageEvent).data) as {
            step_index?: number;
          };
          setStep(parsed.step_index ?? 0);
        });

        eventSource.addEventListener("final_result", (ev) => {
          const parsed = JSON.parse((ev as MessageEvent).data) as {
            payload?: AnalysisResult;
          };
          if (parsed.payload) {
            setResult(parsed.payload);
          }
          setDone(true);
          eventSource?.close();
        });

        eventSource.addEventListener("error", async () => {
          try {
            const status = await getAnalysisStatus(started.analysis_id);
            if (status.result) {
              setResult(status.result);
              setStep(Math.max(0, status.total_steps - 1));
              setDone(status.status === "completed");
              return;
            }
            setError(status.error ?? "Analysis stream disconnected");
          } catch {
            setError("Unable to fetch analysis status after stream interruption");
          }
        });
      } catch (e) {
        const message = e instanceof Error ? e.message : "Failed to start analysis";
        setError(message);
      }
    };

    run();

    return () => {
      eventSource?.close();
=======
    setError(null);
    let isMounted = true;

    async function fetchData() {
      try {
        const res = await fetch("http://localhost:8000/api/analyze", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            company: data.company,
            product_sku: data.product,
          }),
        });

        if (!res.ok) {
          throw new Error("Failed to fetch analysis.");
        }

        const result = await res.json();

        if (result.error) {
          throw new Error(result.error);
        }

        if (isMounted) {
          setBackendData(result);
          setDone(true);
        }
      } catch (e: any) {
        if (isMounted) {
          setError(e.message);
          setDone(true);
        }
      }
    }

    fetchData();

    return () => {
      isMounted = false;
>>>>>>> cd98d932d8b724f66afd788683a78074649a63a7
    };
  }, [data]);

  return (
    <div className="max-w-7xl mx-auto px-8 py-10 space-y-7">
      <div className="flex items-center justify-between animate-fade-up">
        <div>
          <div className="text-xs uppercase tracking-wider text-muted-foreground mb-1">
            Decision report
          </div>
          <h1 className="text-3xl font-semibold tracking-tight">
            Sourcing analysis
          </h1>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={onBack} className="ease-smooth">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to setup
          </Button>
          <Button
            onClick={onAnother}
            className="bg-primary hover:bg-primary-glow ease-smooth text-white"
          >
            <RefreshCw className="mr-2 h-4 w-4" />
            Analyze another case
          </Button>
        </div>
      </div>

      <CaseSummary data={data} />

      <div className="grid grid-cols-3 gap-7">
<<<<<<< HEAD
        <div className="col-span-1">
          <AnalysisStepper currentStep={step} done={done} steps={analysisSteps} />
        </div>

        <div className="col-span-2 space-y-6">
          {done ? (
            <>
              <RecommendationCard
                data={data}
                status={result?.recommendation.status}
                confidence={result?.recommendation.confidence}
                recommendationText={result?.recommendation.recommendation_text}
              />
              <div className="grid grid-cols-2 gap-6">
                <ReasonList reasons={result?.reasons} />
                <RiskList risks={result?.risks} />
              </div>
              <EvidenceList items={result?.evidence} />
              <TradeoffCards tradeoffs={result?.tradeoffs} />
            </>
=======
        <div className="col-span-3 space-y-6">
          {done ? (
            error ? (
              <div className="rounded-xl border border-destructive/30 bg-destructive/10 p-6 flex items-center text-destructive">
                <AlertCircle className="w-5 h-5 mr-3" />
                <span>{error}</span>
              </div>
            ) : (
              <>
                {/* Currently passing mocked data to the cards below. In the next step we will read from backendData */}
                <TradeoffCards backendData={backendData} />
                <RecommendationCard data={data} />
                <div className="grid grid-cols-2 gap-6">
                  <ReasonList />
                  <RiskList />
                </div>
                <EvidenceList />
              </>
            )
>>>>>>> cd98d932d8b724f66afd788683a78074649a63a7
          ) : (
            <div className="rounded-xl border border-border/70 bg-card shadow-elegant p-12 flex flex-col items-center justify-center text-center min-h-[400px]">
              <div className="relative h-16 w-16 mb-5">
                <div className="absolute inset-0 rounded-full bg-primary opacity-20 animate-pulse" />
                <div className="absolute inset-2 rounded-full bg-primary shadow-glow flex items-center justify-center">
                  <RefreshCw className="h-6 w-6 text-white animate-spin text-primary-foreground" />
                </div>
              </div>
              <div className="text-base font-semibold text-foreground">
                Analyzing sourcing decision...
              </div>
              <div className="text-sm text-muted-foreground mt-1 max-w-sm">
                Agnes is gathering evidence, evaluating compliance, and weighing
                your preferences using the knowledge graph and LLM.
              </div>
              {error && <div className="text-sm text-destructive mt-3 max-w-md">{error}</div>}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
