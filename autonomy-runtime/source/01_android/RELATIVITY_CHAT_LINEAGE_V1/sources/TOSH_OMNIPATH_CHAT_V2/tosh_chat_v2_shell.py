#!/data/data/com.termux/files/usr/bin/python3
from pathlib import Path
import json
R=Path(__file__).resolve().parent
O=json.loads((R/'orders/chat_cognitive_overlay_v2.json').read_text())['orders']
by={x['id']:x for x in O};cur=O[0]
def led(o):
 print('\nOMNIPATH NEXT-5 LEDGER')
 for x in o['omnipath_next5']:
  y=by[x];print(f"→ {y['id']} {y['name']} [{y['sha_id'][7:19]}]")
while True:
 print('\nTOSH CHAT V2 // shell OPEN // 72 overlay orders // package view 432 // OMNIVERSE V26 view 3375')
 print('1 menu  2 order  3 search  4 state  5 next5  0 exit');led(cur)
 try:s=input('tosh://chat-v2> ').strip()
 except EOFError:break
 if s=='0':break
 if s=='1':print((R/'FULL_CHAT_COGNITIVE_MENU_V2.txt').read_text())
 elif s=='2':
  q=input('id/ordinal/sha> ').strip();z=next((x for x in O if x['id']==q or str(x['ordinal'])==q or x['sha_id']==q),None)
  if z:cur=z;print(json.dumps(z,indent=2));led(cur)
 elif s=='3':
  q=input('search> ').lower();[print(f"{x['id']} {x['name']}") for x in O if q in (x['name']+' '+x['section']).lower()]
 elif s=='4':print((R/'state/LIVE_SHELL_STATE_V2.json').read_text())
 elif s=='5':led(cur)
