#!/usr/bin/env python3
import hashlib, json, os, sqlite3, time
from pathlib import Path
ROOT = Path('/var/lib/omni-sfc/sot-helix')
CHAT = Path('/var/lib/omni-sfc/odyssey-v2/chat_lineage.sqlite3')
AMNI = Path('/var/lib/omni-sfc/amni/omnipath')
GEN = ROOT / 'generations'
REC = ROOT / 'receipts'
STATE = ROOT / 'state'
LEDGER = ROOT / 'ledger.jsonl'
for p in (GEN, REC, STATE):
    p.mkdir(parents=True, exist_ok=True)
ROLES = {
    'A': {'entity':'OMNI','role':'foreground_conscious','authority':'deterministic_continuity'},
    'B': {'entity':'AMNI','role':'shadow_subconscious','authority':'counterfactual_candidate'},
    'C': {'entity':'TOSH','role':'metacognitive_recognizance','authority':'synthesis_observer'},
}
SOT = ['experience','observation','perspective_shift','meaning','regulation','creation']
BOPS = ['constraint_transfer','failure_mode_analogy','memory_structure','routing_pattern','evaluation_pattern','counterfactual_bridge']
COPS = ['analogy','contradiction_resolution','missing_dependency','structural_transfer','observer_solution','nexus_bridge']
def canon(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=False, default=str)
def sha(x):
    return hashlib.sha256(canon(x).encode()).hexdigest()
def readj(path, default=None):
    try: return json.loads(Path(path).read_text())
    except Exception: return {} if default is None else default
def atomic(path, obj):
    path = Path(path)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n')
    os.replace(tmp, path)
def chat_state():
    c = sqlite3.connect(CHAT)
    h = hashlib.sha256()
    for row in c.execute('select message_sha256 from messages order by message_id'):
        if row[0]: h.update(row[0].encode())
    titles = [r[0].strip() for r in c.execute('select title from conversations where title is not null and trim(title)!="" order by conversation_id')]
    out = {
        'conversations': c.execute('select count(*) from conversations').fetchone()[0],
        'messages': c.execute('select count(*) from messages').fetchone()[0],
        'titles': titles,
        'root_sha': h.hexdigest(),
    }
    c.close()
    return out
def last5():
    rows = []
    for p in sorted(AMNI.glob('*.json')):
        d = readj(p, {})
        base = int(d.get('created_ns') or 0)
        for oid, v in (d.get('orders') or {}).items():
            if isinstance(v, dict):
                rows.append({'order_id':oid,'created_ns':int(v.get('created_ns') or base),'state':v.get('status') or v.get('state') or v.get('outcome') or v.get('decision') or v.get('evolution') or 'UNKNOWN'})
    rows.sort(key=lambda x:(x['created_ns'], x['order_id']))
    return rows[-5:]
def snapshot():
    ch = chat_state()
    load1, load5, load15 = os.getloadavg()
    cpus = os.cpu_count() or 1
    out = {
        'last5': last5(),
        'chat': {k:ch[k] for k in ('conversations','messages','root_sha')},
        'titles': ch['titles'],
        'load': {'one':round(load1,3),'five':round(load5,3),'fifteen':round(load15,3),'cpus':cpus,'ratio':round(load1/cpus,3)},
        'node04': readj('/var/lib/omni-sfc/worlds/world-04-iphone/promotion_gate.json', {}),
        'temple': readj('/var/lib/omni-sfc/omni-temple/training/dataset_tribunal_latest.json', {}),
        'gpu': readj('/var/lib/omni-sfc/semantic-mapping-data/gpu_admission_latest.json', {}),
        'priority': readj('/var/lib/omni-sfc/semantic-mapping-data/priority_staging_latest.json', {}),
    }
    stable = {k:v for k,v in out.items() if k not in ('titles','load')}
    out['state_sha'] = sha(stable)
    return out
def candidates(s):
    missing = sum(1 for v in (s.get('node04',{}).get('criteria') or {}).values() if not v)
    gpu_blockers = len(s.get('gpu',{}).get('blockers') or [])
    ratio = s['load']['ratio']
    samples = s.get('temple',{}).get('samples',0)
    return [
        ('node04',1000 if missing else 300,f'Preserve and re-evaluate {missing} missing NODE-04 native gates using native evidence only.'),
        ('sequence',980,'Verify last-five to next-five deterministic replay, idempotency and append-only lineage.'),
        ('resource',970 if ratio>.75 else 420,f'Protect Hivelocity foreground work at load ratio {ratio:.3f} using reversible controls.'),
        ('gpu',900 if gpu_blockers else 350,f'Re-evaluate {gpu_blockers} GPU admission blockers while keeping training default-deny.'),
        ('temple',820,f'Compare Temple corpus state at {samples} samples against sealed regression gates.'),
        ('chat',790,'Use exported chat lineage as evidence-addressed continuation history.'),
        ('crossrag',760,'Ground continuation proposals in CrossRAG provenance before promotion.'),
        ('morphogenesis',730,'Generate a bounded causal upgrade candidate with rollback evidence.'),
        ('agent_fabric',710,'Audit agent-fabric pressure and bounded routing.'),
        ('orchard',680,'Harvest Happy Orchard novelty without allowing novelty to override evidence.'),
    ]
def rank(s):
    blob = canon(s['last5']).lower()
    titles = s['titles']
    rows = []
    keys = {
        'node04':['node04','iphone','native'],
        'sequence':['sequence','omnipath','determin'],
        'resource':['load','governor','hivelocity'],
        'gpu':['gpu','training','worker'],
        'temple':['temple','dataset','eval'],
        'chat':['chat','lineage','conversation'],
        'crossrag':['crossrag','evidence','rag'],
        'morphogenesis':['morphogenesis','causal','proposal'],
        'agent_fabric':['agent','fabric','route'],
        'orchard':['orchard','novelty','seed']}
    for domain, need, task in candidates(s):
        ks = keys[domain]
        continuity = 100 if any(k in blob for k in ks) else 40
        history = min(100, 8*sum(1 for t in titles if any(k in t.lower() for k in ks)))
        novelty = 25 if continuity == 100 else 100
        repeat_penalty = 120 if continuity == 100 else 0
        total = 4*need + 2*continuity + history + novelty - repeat_penalty
        rows.append({'domain':domain,'task':task,'need':need,'continuity':continuity,'history':history,'novelty':novelty,'score':total})
    return sorted(rows, key=lambda x:(-x['score'], sha(x['domain'])))
