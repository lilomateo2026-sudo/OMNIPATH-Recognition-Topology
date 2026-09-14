from __future__ import annotations
import argparse, hashlib, json, subprocess
from pathlib import Path

ORDER="O31.5"
SCHEMA="omnipath.historical-recovery-proof/v1"
GAPS="omnipath/recognition/promotion_genealogy/legacy_evidence_gaps.json"


def run(repo:Path,*args:str,binary:bool=False):
    return subprocess.run(["git",*args],cwd=repo,capture_output=True,check=False,text=not binary)


def tree_entry(repo:Path,rev:str,path:str):
    p=run(repo,"ls-tree",rev,"--",path)
    if p.returncode or not p.stdout.strip(): return None
    meta=p.stdout.split("\t",1)[0].split()
    return {"type":meta[1],"sha":meta[2]} if len(meta)==3 else None


def prove(repo_root:str|Path):
    repo=Path(repo_root).resolve()
    gaps=json.loads((repo/GAPS).read_text())
    out=[]
    for gap in gaps.get("gaps",[]):
        path=gap["declared_ref"]; commit=gap["declared_commit"]; expected=gap["declared_blob_sha"]
        current=tree_entry(repo,"HEAD",path)
        if current and current["type"]=="blob" and current["sha"]==expected:
            status="CURRENTLY_PRESENT"; rev="HEAD"
        else:
            exists=run(repo,"cat-file","-e",f"{commit}^{{commit}}").returncode==0
            historical=tree_entry(repo,commit,path) if exists else None
            if exists and historical and historical["type"]=="blob" and historical["sha"]==expected:
                status="HISTORICALLY_REACHABLE"; rev=commit
            else:
                status="PERMANENTLY_UNRECOVERED" if gap.get("permanently_unrecovered") else "HASH_KNOWN_BUT_UNREACHABLE"
                out.append({"gap_id":gap["gap_id"],"classification":status,"declared_commit":commit,"declared_ref":path,"expected_blob_sha":expected,"observed_tree_sha":None,"observed_path_blob_sha":None,"git_hash_object_sha":None,"content_sha256":None}); continue
        entry=tree_entry(repo,rev,path)
        blob=run(repo,"cat-file","blob",expected,binary=True).stdout
        git_sha=subprocess.run(["git","hash-object","--stdin"],cwd=repo,input=blob,capture_output=True,check=True).stdout.decode().strip()
        tree=run(repo,"show","-s","--format=%T",rev).stdout.strip()
        out.append({"gap_id":gap["gap_id"],"classification":status,"declared_commit":commit,"declared_ref":path,"expected_blob_sha":expected,"observed_tree_sha":tree,"observed_path_blob_sha":entry["sha"],"git_hash_object_sha":git_sha,"content_sha256":hashlib.sha256(blob).hexdigest()})
    proof={"schema":SCHEMA,"order":ORDER,"gap_registry_manifest_sha256":gaps.get("manifest_sha256"),"proofs":out}
    raw=json.dumps(proof,sort_keys=True,separators=(",",":" )).encode(); proof["proof_set_sha256"]=hashlib.sha256(raw).hexdigest()
    return proof


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repository-root",default="."); ap.add_argument("--write"); ap.add_argument("--check"); a=ap.parse_args()
    proof=prove(a.repository_root)
    if a.write: Path(a.write).write_text(json.dumps(proof,indent=2,sort_keys=True)+"\n")
    if a.check:
        expected=json.loads(Path(a.check).read_text()); ok=expected==proof
        print(json.dumps({"order":ORDER,"valid":ok,"proof_set_sha256":proof["proof_set_sha256"],"proofs":proof["proofs"]},indent=2,sort_keys=True)); return 0 if ok else 7
    if not a.write: print(json.dumps(proof,indent=2,sort_keys=True))
    return 0

if __name__=="__main__": raise SystemExit(main())
