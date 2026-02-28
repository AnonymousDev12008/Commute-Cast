# Shared signal store for Vercel serverless functions.
# NOTE: Vercel functions are stateless — each cold start resets this.
# For persistence across requests use an external DB (e.g. Vercel KV / Redis).
# For demo/dev purposes the in-memory store is fine.

import collections
import threading

MAX_READINGS    = 500
MAX_SEG_HISTORY = 1000

_lock        = threading.Lock()
_history     = collections.deque(maxlen=MAX_READINGS)
_seg_history = collections.deque(maxlen=MAX_SEG_HISTORY)

CELL_DEG = 0.001  # ~111m per degree

def cell_key(lat, lng):
    clat = round(lat / CELL_DEG) * CELL_DEG
    clng = round(lng / CELL_DEG) * CELL_DEG
    return f"{clat:.4f}:{clng:.4f}"

def push(reading: dict):
    import time
    reading.setdefault("ts", int(time.time() * 1000))
    with _lock:
        _history.append(reading)
        if "lat" in reading and "lng" in reading:
            _seg_history.append(reading)

def get_history(n=MAX_READINGS):
    with _lock:
        return list(_history)[-n:]

def get_segments():
    with _lock:
        records = list(_seg_history)
    segs = {}
    for r in records:
        try:
            cell = cell_key(float(r["lat"]), float(r["lng"]))
        except (KeyError, ValueError):
            continue
        if cell not in segs:
            segs[cell] = {
                "cell": cell, "count": 0,
                "avgJitter": 0.0, "avgRtt": 0.0, "avgLoss": 0.0,
                "badness": 0.0, "lastSeen": 0, "firstSeen": r.get("ts", 0),
            }
        s     = segs[cell]
        alpha = 0.4 if s["count"] < 5 else 0.15
        j = float(r.get("jitter", 0))
        rt= float(r.get("rtt",    0))
        l = float(r.get("loss",   0))
        s["avgJitter"] = s["avgJitter"] * (1-alpha) + j  * alpha
        s["avgRtt"]    = s["avgRtt"]    * (1-alpha) + rt * alpha
        s["avgLoss"]   = s["avgLoss"]   * (1-alpha) + l  * alpha
        s["badness"]   = min(1.0, (s["avgJitter"]/300)*0.6 + (s["avgLoss"]/0.3)*0.4)
        s["count"]    += 1
        s["lastSeen"]  = r.get("ts", 0)
    return segs
