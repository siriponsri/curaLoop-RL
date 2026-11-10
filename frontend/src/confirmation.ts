export interface MetricRange { mean: number; sd: number; min: number; max: number }
export type ConfirmationMetric = "confirmation_count" | "confirmed_positives" | "positive_structure_groups" | "positive_fingerprint_groups" | "hits_per_confirmation" | "groups_per_confirmation";
export interface ConfirmationArm {
  ranker: string;
  operator: string;
  seed_count: number;
  metrics: Record<ConfirmationMetric, MetricRange>;
}
export interface ConfirmationStudy {
  schema: "curaloop.confirmation.study-view.v1";
  study_id: "cf1";
  integration_status: string;
  research_status: string;
  source_snapshot: string;
  campaign: string;
  budget_percent: number;
  campaigns: { campaign: string; provider_block: string; universe_size: number; retained_primary_rows: number; budgets: number[] }[];
  budgets: number[];
  seeds: number[];
  arms: ConfirmationArm[];
  universe_observations: number;
  primary_observations: number;
  source_experiment_blocks: number;
  annotation_connected_components: number;
  aggregation: string;
  uncertainty: string;
  limitations: string[];
  source_labels: Record<"en" | "th", { title: string; status: string; scope: string; confirmation_zero: string; next_step: string }>;
  source_hashes: { path: string; bytes: number; sha256: string }[];
  source_url: string;
  paper_url: string;
  final16_access: false;
  new_selector_training: false;
  publication_ready: false;
}
export const rankerNames: Record<string, string> = { mvsa: "MVS-A", rf: "Random forest", gbm: "GBM", primary_score: "Primary score", nearest_primary: "Nearest primary", random: "Random" };
export const operatorNames: Record<string, string> = { top_ranked: "Top ranked", cluster_round_robin: "Group round-robin", classical_max_min: "Classical max-min" };
export function confirmationExport(campaign: string, budget: number, ranker: string, operator: string, locale: string) {
  return "/api/v1/studies/cf1/export?" + new URLSearchParams({ campaign, budget_percent: String(budget), ranker, operator, locale });
}
