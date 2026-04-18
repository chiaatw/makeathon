// Agnes application data types and constants

export type PriorityLevel = "Low" | "Medium" | "High";

export interface Preferences {
  price: PriorityLevel;
  leadTime: PriorityLevel;
  quality: PriorityLevel;
  requireCertifications: boolean;
  maxLeadTimeDays: number;
  certifications: string[];
}

export interface SourcingCase {
  id: string;
  company: string;
  product: string;
  ingredient: string;
  supplier: string;
  preferences: Preferences;
}

export interface EnumsResponse {
  companies: string[];
  products: string[];
  ingredients: string[];
  suppliers: string[];
  certifications: string[];
  analysis_steps: string[];
}

export type RecommendationStatus = "Suitable" | "Suitable with Risk" | "Not Recommended";
export type TradeoffTone = "good" | "neutral" | "warn";
export type TradeoffLevel = "Low" | "Lower" | "Medium" | "High";

export interface TradeoffItem {
  label: string;
  value: TradeoffLevel;
  tone: TradeoffTone;
}

export interface EvidenceItem {
  title: string;
  meta: string;
  tag: "External" | "Internal" | "Regulatory" | "Document";
}

export interface AnalysisResult {
  recommendation: {
    status: RecommendationStatus;
    confidence: number;
    recommendation_text: string;
  };
  reasons: string[];
  risks: string[];
  evidence: EvidenceItem[];
  tradeoffs: TradeoffItem[];
  raw: Record<string, unknown>;
}

export interface AnalysisStatusResponse {
  analysis_id: string;
  status: "queued" | "running" | "completed" | "failed";
  current_step: number;
  total_steps: number;
  result?: AnalysisResult;
  error?: string | null;
}

export const ANALYSIS_STEPS: string[] = [
  "Compliance verification",
  "Quality assessment",
  "Price analysis",
  "Lead time evaluation",
  "Risk assessment",
  "Recommendation synthesis"
];

export const COMPANIES: string[] = [
  "Acme Healthcare",
  "BioTech Solutions",
  "GreenPharm Ltd",
  "HealthPlus Inc",
  "NutraCore Global",
  "Prime Wellness"
];

export const PRODUCTS: string[] = [
  "Multivitamin Daily",
  "Omega-3 Plus",
  "Vitamin D3 1000",
  "Protein Powder",
  "Joint Support",
  "Immune Boost"
];

export const INGREDIENTS: string[] = [
  "vitamin-a",
  "vitamin-b12",
  "vitamin-c",
  "vitamin-d3",
  "omega-3",
  "zinc",
  "magnesium",
  "calcium"
];

export const SUPPLIERS: string[] = [
  "Pharma Global",
  "NutriSource Inc",
  "BioSupply Co",
  "WellnessGenesis",
  "Pure Ingredients Ltd",
  "HealthTech Suppliers"
];

export const CERTIFICATIONS: string[] = [
  "ISO 9001",
  "GMP",
  "FDA Approved",
  "Organic Certified",
  "Third-party Tested",
  "Fair Trade"
];

export const DEFAULT_CASE: SourcingCase = {
  id: "default-case",
  company: "Acme Healthcare",
  product: "Vitamin D3 1000",
  ingredient: "vitamin-d3",
  supplier: "Pharma Global",
  preferences: {
    price: "Medium",
    leadTime: "Medium",
    quality: "High",
    requireCertifications: true,
    maxLeadTimeDays: 30,
    certifications: ["GMP", "FDA Approved"]
  }
};
