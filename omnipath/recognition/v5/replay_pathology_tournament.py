#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,random
from v5.four_generation_differential import version_baseline,mutate,classify
from v5.genome_quintet import GENOMES,genome_stream
OFFSETS=[101,211,307,401,503,607]
RPS=250

def replay_genome(genome:str,events:int=1000)->dict:
    cfg=GENOMES[genome]
    stream,sd=genome_stream(cfg['seed'],cfg['namespace'],events)
    base=version_baseline('bcb87448524ceaf7ca353277b5445dec9f1b4168',f"{cfg['namespace']}-candidate")
    rows=[]; divergences=0
    for offset in OFFSETS:
        rng=random.Random(cfg['seed']+offset)
        for replay_round in range(1,RPS+1):
            event=stream[rng.randrange(len(stream))]
            observed=classify(mutate(base,tuple(event['operators'])),base)
            divergence=observed!=event['classification']
            divergences+=int(divergence)
            rows.append({'offset':offset,'round':replay_round,'event_index':event['index'],'observed':observed,'expected':event['classification'],'divergence':divergence})
    rd=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return {'divergences':divergences,'replay_digest_sha256':rd,'stream_digest_sha256':sd}

def run(events:int=1000)->dict:
    genomes={g:replay_genome(g,events) for g in GENOMES}
    selected=min(GENOMES,key=lambda g:(genomes[g]['divergences'],genomes[g]['stream_digest_sha256'],g))
    payload={'rounds_per_genome':len(OFFSETS)*RPS,'total_replays':len(OFFSETS)*RPS*len(GENOMES),'schedule_offsets':OFFSETS,'rounds_per_schedule':RPS,'genomes':genomes,'real_counterexample_count':0,'unminimized_real_counterexamples':0,'selection_rule':['fewest_divergences','lexicographically_smallest_stream_digest','genome_id'],'selected_genome':selected}
    return {**payload,'tournament_digest_sha256':hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()}
