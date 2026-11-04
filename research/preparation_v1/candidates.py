"""Fixed source-derived candidate census, never selected by activity prevalence."""

TOX21 = [
    (743040, "AR", "AR", "steroid_nuclear_receptors"),
    (743053, "AR-LBD", "AR", "steroid_nuclear_receptors"),
    (743079, "ER", "ESR1", "steroid_nuclear_receptors"),
    (743077, "ER-LBD", "ESR1", "steroid_nuclear_receptors"),
    (743139, "aromatase", "CYP19A1", "cytochrome_P450"),
    (743219, "ARE", "NFE2L2_response", "oxidative_stress_response"),
    (720516, "ATAD5", "ATAD5_response", "genome_maintenance"),
    (743228, "HSE", "heat_shock_response", "proteostasis_response"),
    (720637, "MMP", "mitochondrial_membrane_potential", "mitochondrial_phenotype"),
]
LIT = [
    (492947, "ADRB2", "ADRB2", "GPCR"),
    (1030, "ALDH1", "ALDH1", "aldehyde_dehydrogenase"),
    (743075, "ESR_ago", "ESR1", "steroid_nuclear_receptors"),
    (743080, "ESR_antago", "ESR1", "steroid_nuclear_receptors"),
    (588795, "FEN1", "FEN1", "genome_maintenance"),
    (2101, "GBA", "GBA1", "glycoside_hydrolase"),
    (602179, "IDH1", "IDH1", "isocitrate_dehydrogenase"),
    (504327, "KAT2A", "KAT2A", "acetyltransferase"),
    (995, "MAPK1", "MAPK1", "protein_kinase"),
    (493208, "MTORC1", "MTOR_complex", "protein_kinase"),
    (1777, "OPRK1", "OPRK1", "GPCR"),
    (1631, "PKM2", "PKM2", "glycolytic_phosphotransferase"),
    (743094, "PPARG", "PPARG", "exposed_PPARG"),
    (651631, "TP53", "TP53_related", "exposed_TP53"),
    (504847, "VDR", "VDR", "unresolved_VDR_phenotype"),
]
CANDIDATES = [
    dict(
        aid=aid,
        source_program=source,
        short_name=name,
        proposed_target_group=target,
        provisional_planning_family=family,
    )
    for source, values in (("NCATS_Tox21_training_index", TOX21), ("LIT_PCBA_source_index", LIT))
    for aid, name, target, family in values
]
