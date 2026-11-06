export type Policy =
  "random" | "greedy" | "uncertainty" | "q_learning" | "contextual_bandit";
export type Dataset =
  "hiv_moleculenet_replay_v1" | "synthetic_linear_v1" | "synthetic_shift_v1";
export interface Scenario {
  dataset: Dataset;
  seed: number;
  candidate_count: number;
  initial_count: number;
  budget_units: number;
  batch_size: number;
  delay_steps: number;
  assay_cost_units: number;
  delay_jitter: number;
  missing_percent: number;
}
export interface Metrics {
  step: number;
  spent_units: number;
  reserved_units: number;
  remaining_units: number;
  confirmed_hits: number;
  delivered_assays: number;
  missing_assays: number;
  pending_assays: number;
  seed_hits: number;
  hit_rate: number | null;
  auc_discovery_budget_normalized: number;
  controller_requests: number;
  controller_fallback_requests: number;
}
export interface CurvePoint {
  event_index: number;
  step: number;
  spent_units: number;
  confirmed_hits: number;
  pending_assays: number;
  reserved_units: number;
  remaining_units: number;
}
export interface AssayEvent {
  event_id: string;
  event_type: string;
  step: number;
  compound_id: string | null;
  request_id: string | null;
  cost_units: number;
  delivered_active: boolean | null;
  explanation: string;
}
export interface Experiment {
  request_id: string;
  compound_id: string;
  due_at_step: number;
  scheduled_at_step: number;
  cost_units: number;
  explanation: string;
  predicted_probability: number | null;
  model_status: string;
}
export interface Outcome {
  compound_id: string;
  request_id: string;
  delivered_at_step: number;
  active: boolean | null;
  quality_flag: string;
}
export interface Manifest {
  run_id: string;
  scenario_id: string;
  repo_git_sha: string;
  source_sha256: string;
  algorithm_version: string;
  policy_id: Policy;
  seed: number;
  data_origin: string;
  scenario_origin: string;
  digital_twin_maturity: string;
  initial_label_ids: string[];
  initial_label_selection: string;
  initial_labels_budget_rule: string;
  scenario_config: Scenario;
  algorithm_status: string;
  dataset: {
    name: string;
    release: string;
    sha256: string;
    feature_sha256: string;
    assay_id: string;
    label_semantics: string;
    terms_status: string;
    source: string;
  };
  dataset_provenance: Record<string, unknown>;
  limitations: string[];
  controller: null | Record<string, unknown>;
  finished: boolean;
}
export interface RunReport {
  manifest: Manifest;
  metrics: Metrics;
  events: AssayEvent[];
  curve: CurvePoint[];
  requests: Experiment[];
  delivered_results: Outcome[];
  initial_results: Outcome[];
}
export interface RunView {
  session_id: string;
  revision: number;
  done: boolean;
  report: RunReport;
  pending: Experiment[];
  eligible_count: number;
  can_select: boolean;
  persistence?: {
    created_at: string;
    updated_at: string;
    recovered: boolean;
    creation_identity: Record<string, unknown>;
    identity_note: string;
  };
}
export interface RecoveryIssue { kind: string; id: string; message: string }
export interface SavedRun {
  session_id: string;
  revision: number;
  dataset: Dataset;
  policy: Policy;
  done: boolean;
  pending_assays: number;
  spent_units: number;
  updated_at: string;
}
export interface SavedRuns {
  items: SavedRun[];
  recovery_issues: RecoveryIssue[];
  storage: { schema_version: number; status: string };
}
export interface SavedComparisons { items: Job[]; recovery_issues: RecoveryIssue[] }
export interface Meta {
  working_tree_dirty?: boolean | null;
  frontend_build_sha256?: string | null;
  repo_git_sha: string;
  source_sha256: string;
  web_version: string;
  engine_version: string;
  molecule_rendering: boolean;
  limitations: string[];
  session_note: string;
  digital_twin_maturity: string;
  test_evidence: { historical_python_tests: number; historical_claim: string };
  storage?: { schema_version: number; status: string; error: string | null; recovery_help: string };
}
export interface DatasetInfo {
  id: Dataset;
  name: string;
  data_origin: string;
  candidate_count: number;
  default_initial_count: number;
  feature_description: string;
}
export interface PolicyInfo {
  id: Policy;
  status: string;
  training_episodes: number | null;
  checkpoint_sha256: string | null;
  warning: string | null;
}
export interface Candidate {
  compound_id: string;
  status: string;
  canonical_smiles: string | null;
  scaffold_id: string | null;
  feature_count: number;
  feature_nonzero: number;
  public_features_preview: number[];
  revealed_active: boolean | null;
  predicted_probability: number | null;
  explanation: string | null;
}
export interface CandidatePage {
  items: Candidate[];
  total: number;
  page: number;
  page_size: number;
}
export interface Job {
  job_id: string;
  status: "queued" | "running" | "completed" | "failed" | "interrupted";
  scenario: Scenario;
  policies: Policy[];
  reports: RunReport[];
  error: string | null;
}
export interface SummaryRow {
  policy: Policy;
  n_seeds: number;
  mean_hits: number;
  sd_hits: number;
  min_hits: number;
  max_hits: number;
}
export interface Evidence {
  recorded_release: string;
  label: string;
  statistics: {
    summary: SummaryRow[];
    interpretation: string;
    paired_contrasts: unknown[];
  };
  seeds: number[];
  scenario: Scenario;
  predictor: {
    train_count: number;
    test_count: number;
    train_actives: number;
    test_actives: number;
    scaffold_overlap: number;
    auroc: number;
    average_precision: number;
    brier_score: number;
    test_prevalence: number;
    scope: string;
  };
  controller_historical_fallback: string;
  source_links: { title: string; url: string }[];
  controllers: {
    policy_id: string;
    training_episodes: number;
    episode_returns: number[];
    checkpoint_sha256: string;
  }[];
}
export const policyNames: Record<Policy, string> = {
  random: "Random",
  greedy: "Greedy",
  uncertainty: "Uncertainty",
  q_learning: "Q-learning",
  contextual_bandit: "Contextual bandit",
};
export const colors: Record<Policy, string> = {
  random: "#28282B",
  greedy: "#A6492D",
  uncertainty: "#8A641F",
  q_learning: "#6E5A98",
  contextual_bandit: "#3F6785",
};
