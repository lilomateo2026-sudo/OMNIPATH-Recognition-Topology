#!/usr/bin/env python3
import json, os, subprocess, time
from pathlib import Path
ROOT=Path('/var/lib/omni-sfc/sot-helix')
RUNTIME=ROOT/'helix_runtime.py'
STATUS=ROOT/'state'/'infinity_loop.json'
def atomic(obj):
    tmp=STATUS.with_suffix('.tmp'); tmp.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n'); os.replace(tmp,STATUS)
while True:
    load1=os.getloadavg()[0]; cpus=os.cpu_count() or 1; ratio=load1/cpus
    interval=1800 if ratio>0.75 else 900
    started=time.time_ns()
    run=subprocess.run(['/usr/bin/python3',str(RUNTIME)],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True,timeout=120)
    atomic({'schema':'omni.sot-helix.infinity-loop.v1','pid':os.getpid(),'started_ns':started,'completed_ns':time.time_ns(),'load_ratio':round(ratio,4),'next_interval_seconds':interval,'runtime_returncode':run.returncode,'stderr_tail':run.stderr[-500:],'operational_consciousness_model':True,'phenomenal_consciousness_claim':False})
    time.sleep(interval)
