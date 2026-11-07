"""Restricted role interfaces. Values stay inside the trusted validator."""
import math
import sqlite3

SAFE_ACTIVITY={'activity_id','assay_id','molregno','standard_type','standard_units','standard_relation','doc_id'}
SAFE_TABLES={
    'activities':SAFE_ACTIVITY,
    'assays':set('assay_id chembl_id description assay_type assay_test_type assay_category assay_organism assay_tax_id assay_strain assay_tissue assay_cell_type assay_subcellular_fraction tid doc_id confidence_score relationship_type bao_format assay_group variant_id cell_id tissue_id src_id'.split()),
    'target_dictionary':set('tid chembl_id target_type pref_name organism tax_id species_group_flag'.split()),
    'target_components':set('tid component_id targcomp_id homologue'.split()),
    'component_sequences':set('component_id component_type accession sequence description tax_id organism'.split()),
    'component_class':{'component_id','protein_class_id'},
    'protein_classification':set('protein_class_id parent_id pref_name short_name definition class_level l1 l2 l3 l4 l5 l6 l7 l8'.split()),
    'variant_sequences':set('variant_id accession mutation sequence isoform organism'.split()),
    'compound_structures':{'molregno','canonical_smiles','standard_inchi','standard_inchi_key'},
    'molecule_dictionary':set('molregno chembl_id structure_type molecule_type pref_name'.split()),
    'molecule_hierarchy':{'molregno','parent_molregno','active_molregno'},
    'docs':set('doc_id chembl_id doi pubmed_id title year src_id'.split()),
    'source':set('src_id src_description src_short_name src_url src_comment'.split()),
    # Raw parameter values need a separate context-input projector, never this
    # metadata SQL role. Type/unit presence remains visible for completeness.
    'assay_parameters':set('assay_param_id assay_id type units standard_type standard_units'.split()),
    'sqlite_master':{'type','name','tbl_name','rootpage','sql'},
}
SCALES={'M':1.,'mM':1e-3,'uM':1e-6,'\u03bcM':1e-6,'nM':1e-9,'pM':1e-12,'fM':1e-15}


def protect_metadata_connection(conn):
    def authorizer(action,arg1,arg2,db,trigger):
        if action==sqlite3.SQLITE_READ:
            if arg1.lower() not in SAFE_TABLES or (arg2 and arg2.lower() not in SAFE_TABLES[arg1.lower()]):return sqlite3.SQLITE_DENY
        if action==sqlite3.SQLITE_FUNCTION and (arg2 or '').lower() not in {'count','min','max','length','coalesce','typeof','lower','upper'}:return sqlite3.SQLITE_DENY
        if action==sqlite3.SQLITE_PRAGMA and (arg1 or '').lower() not in {'table_info','index_list','index_info','user_version','query_only'}:return sqlite3.SQLITE_DENY
        if action in {sqlite3.SQLITE_INSERT,sqlite3.SQLITE_UPDATE,sqlite3.SQLITE_DELETE,
                      sqlite3.SQLITE_ATTACH,sqlite3.SQLITE_DETACH}:return sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_OK
    conn.set_authorizer(authorizer)


class PresenceValidator:
    """Caller supplies a frozen, protection-cleared activity-ID allowlist.

    No arbitrary SQL or numeric values are returned. The host process remains
    trusted; this interface is not cryptographic isolation from its operator.
    """
    def __init__(self,conn,allowed_ids):
        self.__conn=conn;self.__allowed=frozenset(allowed_ids)

    def check(self,ids):
        ids=list(ids)
        if not set(ids)<=self.__allowed:raise PermissionError('Activity ID outside frozen protection-cleared allowlist')
        output=[]
        for activity_id in ids:
            row=self.__conn.execute('SELECT activity_id,standard_type,standard_relation,standard_units,standard_value FROM activities WHERE activity_id=?',(activity_id,)).fetchone()
            valid=False
            if row and row[1] in {'Ki','Kd','IC50'} and row[2]=='=' and row[3] in SCALES:
                try:
                    value=float(row[4]);molar=value*SCALES[row[3]]
                    valid=math.isfinite(value) and math.isfinite(molar) and value>0 and molar>0
                except (TypeError,ValueError,OverflowError):pass
            output.append({'activity_id':activity_id,'exact_positive_finite_support':bool(valid)})
        return output
