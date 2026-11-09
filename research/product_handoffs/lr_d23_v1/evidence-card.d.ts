/** Aggregate evidence only. This type deliberately carries no compound labels. */
export interface LR_D23_EvidenceCard {
  schema: 'curaloop.lr_d23.evidence_card.v1';
  research_status: 'PASS_D2' | 'INCONCLUSIVE_D2' | 'STOPPED_TECHNICAL' | 'STOPPED_SUPPORT';
  D3_status: string;
  evaluation_scope: 'six exposed FS-Mol development assays / four annotation components';
  result: { path: string; sha256: string };
  comparisons: Array<{ arm: string; mean_new_positives: number; mean_scientific_cpu_seconds: number }>;
  decision: { en: string; th: string };
  limitations: string[];
  runtime_integration: 'NOT_RUN_OFFLINE_HANDOFF_ONLY';
}
