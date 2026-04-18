import { useEffect, useState } from "react";
import { AppHeader } from "@/components/agnes/AppHeader";
import { InputScreen } from "@/components/agnes/InputScreen";
import { AnalysisScreen } from "@/components/agnes/AnalysisScreen";
import { DEFAULT_CASE, EnumsResponse, SourcingCase } from "@/lib/agnes-data";
import { getEnums } from "@/lib/api";

const Index = () => {
  const [view, setView] = useState<"input" | "analysis">("input");
  const [data, setData] = useState<SourcingCase>(DEFAULT_CASE);
  const [enums, setEnums] = useState<EnumsResponse | undefined>(undefined);

  useEffect(() => {
    let mounted = true;
    getEnums()
      .then((res) => {
        if (!mounted) {
          return;
        }
        setEnums(res);
      })
      .catch(() => {
        // UI keeps local defaults if backend metadata is unavailable.
      });

    return () => {
      mounted = false;
    };
  }, []);

  return (
    <div className="min-h-screen bg-gradient-surface">
      <AppHeader />
      <main>
        {view === "input" ? (
          <InputScreen
            data={data}
            setData={setData}
            enums={enums}
            onRun={() => setView("analysis")}
          />
        ) : (
          <AnalysisScreen
            data={data}
            analysisSteps={enums?.analysis_steps}
            onBack={() => setView("input")}
            onAnother={() => setView("input")}
          />
        )}
      </main>
      <footer className="border-t border-border/60 py-6 mt-12">
        <div className="max-w-7xl mx-auto px-8 flex items-center justify-between text-xs text-muted-foreground">
          <div>Agnes · AI Sourcing Decision Support</div>
          <div>Demo build · mock data only</div>
        </div>
      </footer>
    </div>
  );
};

export default Index;
