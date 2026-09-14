import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'promotion_genealogy/historical_recovery_proofs.json'

def test_recovery_proof():
    x=json.loads(P.read_text()); seal=x.pop('proof_set_sha256')
    assert seal==hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    p=x['proofs'][0]
    assert x['order']=='O31.7'
    assert p['classification']=='HISTORICALLY_REACHABLE'
    assert p['expected_blob_sha']==p['observed_path_blob_sha']==p['git_hash_object_sha']
