"""Compare declared GSIS identities using explicit registry rows, never names."""
FIELDS=['gsis_id','display_name','esb_id','pfr_id','position','rookie_season','last_season','latest_team']

def compare_registry_ids(rows,left_id,right_id):
    left=[r for r in rows if r.get('gsis_id')==left_id] if left_id else []
    right=[r for r in rows if r.get('gsis_id')==right_id] if right_id else []
    if len(left)>1 or len(right)>1:status='ambiguous-registry'
    elif not left or not right:status='unresolved-registry'
    elif left_id==right_id:status='same-registry-identity'
    else:status='different-registry-identities'
    return {'status':status,'left':[dict((k,r.get(k)) for k in FIELDS) for r in left],
        'right':[dict((k,r.get(k)) for k in FIELDS) for r in right],
        'meaning':'Registry identity comparison, not independent roster or injury confirmation. Names and identifiers from other namespaces are not automatic joins.'}
