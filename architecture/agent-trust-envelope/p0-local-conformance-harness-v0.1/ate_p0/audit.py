import hashlib, json
class AuditLedger:
    def __init__(self): self.records=[]
    def append(self,event,data):
        prev=self.records[-1]["record_hash"] if self.records else "GENESIS"
        rec={"seq":len(self.records)+1,"event":event,"data":data,"previous_record_hash":prev}
        rec["record_hash"]=hashlib.sha256(json.dumps(rec,sort_keys=True,separators=(",",":")).encode()).hexdigest()
        self.records.append(rec); return rec
