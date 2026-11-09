"""Render owner-facing English reports only from reconciled closed-release evidence."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];TASK=ROOT/'.local/m2-costed-20261108-v2';PUBLIC=ROOT/'docs/evidence/m2-costed-20261108-v2'


def number(v):return 'NA' if v is None else f'{v:.3f}'
def interval(r):return '['+', '.join(number(v) for v in r['conditional_seed_interval_95'])+']'
def table(headers,rows):return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(map(str,row))+' |' for row in rows])


def main():
    ledger=json.loads((TASK/'ledger.json').read_text());assert ledger['status']=='CLOSED_COMPLETE_FOR_OWNER_REVIEW'
    result=json.loads((PUBLIC/'aggregate-results-v1.json').read_text());cpu=json.loads((PUBLIC/'cpu-accounting-v1.json').read_text())
    assert json.loads((TASK/'jobs/closeout-audit-v1/result.json').read_text())['status']=='PASS_COMPLETE_M2_CLOSEOUT_AUDIT'
    primary=[r for r in result['paired_contrasts'] if r['predictor']=='rf' and r['regime']=='cheap']
    history=result['rf_ablation_contrasts'][0];scope=json.loads((ROOT/'research/manifests/m2_data_scope_20261108_v1.json').read_text())
    labels={g['id']:g['label'] for g in scope['groups']};decision=result['method_decision']
    approval=json.loads((ROOT/'research/manifests/conditional_m3_p1_j1_owner_approval_20261109_v1.json').read_text())
    conditional_entry=(decision=='PROMISING_DEVELOPMENT_SIGNAL' and approval['owner_option']=='A'
      and approval['status']=='OWNER_APPROVED_CONDITIONAL_NOT_STARTED')
    continuation=('The owner separately approved conditional option A on 9 November. M2 now satisfies its scientific and closeout entry conditions; '
      'after this evidence is delivered on main, the executor may start the separate 96 CPU-hour / 120 elapsed-hour M3 -> P1 -> J1 release. '
      'Final-label decoding still requires a frozen M3 protocol and passed readiness/calibration.' if conditional_entry else
      'The owner\'s conditional M3 -> P1 -> J1 grant is not activated because M2 did not meet its predeclared promising-signal entry condition. '
      'Review the findings with the owner before another research release; final outcomes remain closed.')
    caps=json.loads((PUBLIC/'technical-admission-v1.json').read_text())['caps']
    lines=['# Costed M2 development results','',f'**COMPLETE_FOR_OWNER_REVIEW — {decision}.** Technical closeout: **PASS**.',
      '', 'The fixed development study is complete. Final outcomes remained closed throughout M2. '+
      'Completion is a research result, including mixed or negative findings; it is not publication readiness or a production-policy release.',
      '', continuation,
      '', '## Question and evidence scope','',
      'The method learns whether to REUSE cached scores, UPDATE the predictor, or PLAN with the same nonmyopic reference used by its controls. '+
      'The incremental contribution under test is useful outcome-supervised computation allocation in molecular active search. '+
      'General metareasoning, portfolios and learned acquisition remain established prior art.',
      '', 'Six previously exposed FS-Mol development assays provide 1,285 task rows and four annotation components. '+
      'These are not four certified independent biological families. The freshly admitted training mask retained all rows, with no cross-component canonical overlap. '+
      'No final feature, label or presence payload, old validation pool, new assay or download was used.',
      '', 'Labels are assay-relative potency-derived binary classifications. Newly delivered positives exclude initial observations. '+
      'They are not validated therapeutic hits, realistic HTS prevalence, clinical outcomes or monetary savings.',
      '', '### Frozen computation limits','',
      'Caps below were derived without molecular outcomes: 1.25 times the maximum complete matched synthetic reference across both pool sizes and three repeats. They differ by predictor/n0/B; comparisons are paired within each context. Machine-readable evidence retains full precision. No high regime collapsed.', '',
      table(['Predictor','Initial n0','New-label B','Ccheap (CPU-s)','Cplan (CPU-s)'],[[key.split(':')[0],key.split(':')[1],key.split(':')[2],f"{value['cheap']:.6g}",f"{value['high']:.6g}"] for key,value in caps.items()]),
      '', '## Primary result','',
      'RF, assigned B=32 and Ccheap. Seeds and n0 are equally weighted within each assay, assays equally within component, and the four components equally. '+
      'Intervals below are 95% conditional seed-variability intervals on this fixed cohort, from 10,000 jointly resampled seed vectors. '+
      'They are not population-wide biological-family confidence intervals.', '',
      '![Absolute RF discovery and paired primary contrasts](../evidence/m2-costed-20261108-v2/primary-discovery-v1.png)', '',
      table(['Contrast','Mean change in new positives','Conditional 95% interval','Positive components'],
        [[r['contrast'],number(r['mean_delta_new_positives']),interval(r),str(r['positive_components'])+'/4'] for r in primary]),
      '', table(['Annotation component']+[r['contrast'] for r in primary]+['L minus no-history'],
        [[labels[g]]+[number(r['component_effects'][g]) for r in primary]+[number(history['component_effects'][g])] for g in labels]),
      '', 'The predeclared exploratory potential rule requires positive mean L−G1, L−T and L−E, positive L−G1 in at least three components, '+
      'and positive L−no-history, with no accounting/information artifact. No practical-effect margin or p<0.05 gate was invented. '+
      'With four dependence groups the minimum attainable two-sided sign-flip p-value is 0.125.', '',
      table(['Requirement','Observed'],[[r['contrast']+' mean > 0',str(r['mean_delta_new_positives']>0)] for r in primary]+
        [['L−G1 positive in at least 3/4 components',str(primary[0]['positive_components']>=3)],
         ['L−no-history mean > 0',str(history['mean_delta_new_positives']>0)],['Technical closeout','PASS']]),
      '', '## Full matched comparisons','',
      'R: uniform Random; G1: update each delivery; Gk: training-selected periodic update; U: p(1−p) uncertainty; '+
      'P: plan while feasible with a charged cheap tail; T: training-selected threshold rule; E: Exp3 selected-operation feedback; L: learned gate. '+
      'Both predictors, initial-label settings and all five evaluation seeds are retained. Every reported arm has 60 campaigns per CPU regime.']
    for predictor in('rf','neighbor'):
        for regime in('cheap','high'):
            rows=[r for r in result['main_summaries'] if r['predictor']==predictor and r['regime']==regime]
            lines+=['',f'### {predictor.upper()} / {regime}','',table(['Arm','Mean new positives','New delivered','Total observed','Science CPU (s)','Process CPU (s)','Process wall (s)','Full B / 60','Interrupted / 60'],
              [[r['arm'],number(r['new_positives']),number(r['new_deliveries']),number(r['total_observed']),number(r['scientific_cpu_seconds']),number(r['whole_process_cpu_seconds']),number(r['whole_process_wall_seconds']),r['full_B_campaigns'],r['interrupted_campaigns']] for r in rows])]
    lines+=['','### Paired effects across all regimes','',table(['Predictor','C regime','Contrast','Mean change','Conditional 95% interval'],
      [[r['predictor'],r['regime'],r['contrast'],number(r['mean_delta_new_positives']),interval(r)] for r in result['paired_contrasts']]),
      '', '### Descriptive compute/discovery frontier','',
      'Nondominance below compares mean scientific CPU and mean discovery across the 16 cheap/high operating points within each predictor. This is a descriptive mean-point frontier, not statistical dominance; all dominated points remain in the full tables.', '',
      table(['Predictor','C regime','Arm','Science CPU (s)','New positives'],[[r['predictor'],r['regime'],r['arm'],number(r['scientific_cpu_seconds']),number(r['new_positives'])] for r in result['descriptive_compute_discovery_frontier'] if r['nondominated_mean_point']]),
      '', '### Discovery curves','',
      'All curves use the assigned query budget. CPU-exhausted campaigns retain their last delivered count; no extra labels are acquired. Bands use the same conditional seed-vector bootstrap.', '',
      '![RF cheap discovery curves: R, G1, Gk and U versus L](../evidence/m2-costed-20261108-v2/rf-cheap-discovery-curves-1-v1.png)', '',
      '![RF cheap discovery curves: P, T and E versus L](../evidence/m2-costed-20261108-v2/rf-cheap-discovery-curves-2-v1.png)', '',
      'The [aggregate curve table](../evidence/m2-costed-20261108-v2/discovery-curves-v1.csv) includes all eight policies, both predictors and both CPU regimes. Vector SVG/PDF exports accompany the previews.',
      '', 'The [complete summary table](../evidence/m2-costed-20261108-v2/main-summary-v1.csv) also reports H/B, the discrete mean of H(k) across assigned budgets, and delivered-observation Brier/log loss. These errors are selection-biased diagnostics, not pool calibration. Process wall time includes startup/reporting but excludes queue waiting.',
      '', '## Attribution and B=16 transfer','',
      'RF history/action ablations use the same cheap budgets and five seeds. Their jobs were interleaved with the main jobs on the same paired core '+
      'before any outer evaluation. B=16 transfer uses the first three evaluation seeds, both n0/C regimes and frozen B=32 gates/controls; no retuning.', '',
      table(['RF cheap ablation contrast','Mean change','Conditional 95% interval'],[[r['contrast'],number(r['mean_delta_new_positives']),interval(r)] for r in result['rf_ablation_contrasts']]),
      '',table(['B=16 C regime','Contrast','Mean change','Conditional 95% interval'],[[r['regime'],r['contrast'],number(r['mean_delta_new_positives']),interval(r)] for r in result['rf_B16_transfer_contrasts']]),
      '', '## Operation and support diagnostics','',
      table(['Predictor','C regime','Arm','REUSE','UPDATE','PLAN','Feasibility fallbacks'],
        [[r['predictor'],r['regime'],r['arm']]+[r['operation_counts'][op] for op in('REUSE','UPDATE','PLAN')]+[r['fallbacks']]
         for r in result['main_summaries'] if r['arm']in('G1','T','E','L')]),
      '', 'Operation counts identify requested operations, not all internal forest fits. Common initial fits and cold-start uniform choices are additional charged work; PLAN at one remaining assay degenerates to cheap selection.',
      '', f"Gate supervision retained {result['training_state_support']['eligible_states']} eligible state/C combinations out of {result['training_state_support']['states']}; "+
      f"{result['audit'].get('infeasible_branches',0)} branches retained an already-exhausted prefix and invoked no continuation. "+
      'Each training state has three forced-operation continuations followed by common G1. Targets are realized terminal-hit differences, '+
      'not optimal values or independent biological observations. Gates/scalers and control selection exclude the entire held-out component.',
      '',table(['Predictor','C regime','Forced operation','Positive targets','Zero targets','Negative targets','Mean target'],
        [[r['predictor'],r['regime'],r['forced_operation'],r['positive'],r['zero'],r['negative'],number(r['mean_terminal_hit_difference'])] for r in result['descriptive_training_target_distribution']]),
      '', '## Execution and cost','',table(['Stage','Completed units'],[[k,v] for k,v in result['counts'].items()]),
      '', 'All 96 unique synthetic contexts passed, including 12 preceding RF profiles and 84 in this continuation. '+
      f"The fresh release completed 4,248 intended units and retained {cpu['retained_not_dispatched_attempts']} additional not-dispatched technical failures, each retried with unchanged parameters. "+
      'The first local calibration coordinator hit its CPU envelope; switching to in-process booking and batched transport resolved that overhead. '+
      'A later SSH connect timeout stopped tuning after 174 completed units; fresh exact job/unit absence preceded three identical-context retries. '+
      'All stopped attempts and local orchestration reservations remain retained. Controller restarts continue only unchanged frozen units after reconciling successful remote receipts. '+
      'A Windows heartbeat replacement collision was repaired without changing the molecular engine; its two actual-reader-lock checks concern telemetry only. '+
      'Eleven distinct constructed engine checks, three original analysis checks, three supplemental heterogeneous-pairing scenarios and five transport checks passed. '+
      'The pairing supplement verifies nonconstant shared-seed effects against an exhaustive finite bootstrap distribution and rejects malformed pairs. '+
      'It changes neither the estimator nor the predeclared scientific criterion. Repeated executions are not additional distinct checks.',
      '',table(['Local orchestration attempt','Final state','Retained reservation (CPU-s)'],
        [[j['job'],j['state'],j['reservation_seconds']] for j in ledger['jobs'] if j['job'].startswith('orchestration-recovery-')]),
      '',table(['Budget stage','Charged reservation (CPU-s)','Stage ceiling (CPU-s)'],[[k,v,cpu['bucket_caps_seconds'][k]] for k,v in cpu['bucket_charged_seconds'].items()]),
      '',f"Cumulative conservative charge: **{number(cpu['cumulative_charged_cpu_hours'])} CPU-hours of 48**, including {cpu['prior_retained_seconds']} retained seconds from earlier M2 steps. "+
      'Failed attempts and utility reservations remain charged in full. This is conservative reservation accounting, not measured total-host CPU consumption. '+
      f"Original deadline: {cpu['deadline_utc']}; closed: {ledger['closed_utc']}.",
      '',f"Verified training/tuning worker subtotal: {number(result['offline_training_and_tuning_verified_worker_cpu_seconds'])} CPU-seconds. "+
      f"Their charged stage reservations total {result['offline_training_and_tuning_charged_stage_seconds']} CPU-seconds. "+
      'Shared setup/orchestration/return overhead is additional and included in the project accounting. The following worker-only amortization values are lower bounds, not complete deployment cost estimates.',
      '',table(['Assumed future campaigns','Worker CPU-s per campaign'],[[k,number(v)] for k,v in result['offline_worker_cpu_amortization_lower_bound_seconds_per_campaign'].items()]),
      '',f"Every biological unit passed trace/label consistency, paired-core and budget audits. Startup/reporting CPU range: "+
      f"{result['whole_process_minus_incremental_science_cpu_range_seconds']}; all within five seconds. "+
      'Timed campaigns ran only on the admitted dr-train runtime. Feature/graph preparation, inference, fits, planning, interruptions and fallbacks consumed C. '+
      'The exact calibrated caps were not enlarged or clipped to favor a method.',
      '', '## Reviewer assessment and limits','',
      '**Publication readiness: no.** This is grouped exploratory development evidence on a small, previously exposed cohort. '+
      'Repeated seeds and correlated continuations do not increase biological independence. Similar scaffolds remain, predictor probabilities are uncalibrated, '+
      'the synchronous retrospective simulator has unit costs and immediate delivery, and CPU regimes are hardware-specific. '+
      'Delivered-observation error diagnostics are selection-biased. There is no chemical-OOD, clinical, lab-savings or universal-policy claim.',
      '', continuation+' A mixed or negative finding is not permission for an automatic M1 loop, larger dataset, new mechanism or journal submission.',
      '', 'The research controller is not integrated into the product as a validated production policy. '+
      'The existing EN/TH app and R&D plugin retain their earlier evidence limits. Workflow utility and business value require separate assessment.',
      '', '## Reproduction, return and preservation','',
      'Scientific implementation: `research/m2_costed_v2/`; original predictor/planner: `research/m2_v1/models.py`, unchanged. '+
      'The private execution root retains frozen matrices, code pins, permits, gates, controls, source projections, traces and complete remote returns. '+
      'All original inputs, previous ledgers, source roles and frozen historical findings were rechecked. Raw compound rows, structures, fingerprints, labels, '+
      'gate caches and individual histories remain private.',
      '', 'The complete task/export was returned, safely extracted and independently reread/hash-verified before exact deletion of '+
      '`/home/chaw/curaloop-tasks/m2-costed-20261108-v2` and its exact export. Fresh absence passed. The ledger is closed; do not reuse its allowance or recreate old roots.',
      '', 'Read the [aggregate evidence](../evidence/m2-costed-20261108-v2/README.md), '+
      '[execution notes](../06_execution/M2_COSTED_EXECUTION_NOTES_20261108.md), '+
      '[original plan](../06_execution/M2_EXPERIMENT_PLAN_20261108.md) and '+
      '[owner checkpoint](../06_execution/M2_OWNER_CHECKPOINT_20261108.md).']
    report=ROOT/'docs/03_research/M2_COSTED_RESULTS_20261108.md'
    with report.open('x',encoding='utf-8',newline='\n') as f:f.write('\n'.join(lines)+'\n')
    checkpoint_table=(table(['Approved stage','Required boundary','Delivery'],[
      ['M3','After M2 main delivery; freeze protocol and pass readiness/calibration before final16 labels','Protected evaluation report with all results retained'],
      ['P1','Offline prototype; no live destination writes or paid services','Typed R&D workflow and verified aggregate evidence in the EN/TH app'],
      ['J1','Draft only; human review and actual submission remain later decisions','English manuscript and reproducibility package']]) if conditional_entry else
      table(['Option','What it authorizes now','What remains a later decision'],[
      ['Discuss the M2 evidence first','Interpret effects, limitations and reviewer concerns; no new experiments','Any new research protocol or budget'],
      ['Request an M3 proposal','Plan independent evaluation and novelty checks using the retained evidence','Data access, final outcomes, experiment execution and journal submission'],
      ['Prioritize product workflow','Prepare a separate product evaluation proposal','Live integrations, customer claims, paid services and production deployment']]))
    checkpoint=ROOT/'docs/06_execution/M2_OWNER_CHECKPOINT_20261108.md'
    with checkpoint.open('x',encoding='utf-8',newline='\n') as f:
        f.write('# M2 owner checkpoint\n\n**M2 complete; '+decision+'.**\n\n'+
          'Read the [complete results](../03_research/M2_COSTED_RESULTS_20261108.md) for effects, costs and limitations. '+
          'The full fixed development matrix, accounting audit, complete private return and exact remote cleanup passed. '+
          'Final outcomes remained closed throughout M2. This is not publication readiness.\n\n'+continuation+'\n\n'+
          ('Next step: deliver M2 on main, then execute the already-approved conditional [long-run plan](CONDITIONAL_LONG_RUN_M3_P1_J1_20261109.md). Do not ask again for the same routine release. Material scope/rights/data changes still require the owner.\n\n' if conditional_entry else
           'Recommended next step: review the measured method/overhead/attribution findings with the owner before committing another research budget. Do not automatically repeat M1, enlarge the cohort or open the final set to resolve ambiguity.\n\n')+
          checkpoint_table+'\n')
    status=json.loads((ROOT/'research/configs/m2_costed_status_20261108_v2.json').read_text())
    status.update(status='COMPLETE_FOR_OWNER_REVIEW',method_efficacy=decision,biological_units_completed=4164,
      fresh_successful_units=4248,retained_not_dispatched_attempts=cpu['retained_not_dispatched_attempts'],cumulative_charged_seconds=cpu['cumulative_charged_seconds'],
      report=str(report.relative_to(ROOT)).replace('\\','/'),
      next_actor=('executor starts separate approved conditional release after main delivery; protected labels require M3 readiness' if conditional_entry else
      'owner reviews M2 findings; conditional grant not activated; release closed and exact remote roots absent'))
    (ROOT/'research/configs/m2_costed_status_20261108_v2.json').write_text(json.dumps(status,indent=2)+'\n',encoding='utf-8',newline='\n')
    result.update(status='COMPLETE_FOR_OWNER_REVIEW',technical_closeout='PASS',remote_exact_cleanup='PASS')
    (PUBLIC/'aggregate-results-v1.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':'PASS_ENGLISH_REPORT_RENDER','method_decision':decision,'report':str(report)}))


if __name__=='__main__':main()
