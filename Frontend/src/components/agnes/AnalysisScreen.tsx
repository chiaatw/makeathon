import { Button } from "@/components/ui/button";
import { SourcingCase } from "@/lib/agnes-data";
import { useEffect, useState } from "react";
import { ArrowLeft, RefreshCw, AlertCircle } from "lucide-react";
import { CaseSummary } from "./CaseSummary";
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
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [backendData, setBackendData] = useState<any>(null);

  useEffect(() => {
    setDone(false);
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
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
