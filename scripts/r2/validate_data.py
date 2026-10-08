#!/usr/bin/env python3
"""R2 data validator. Run: python3 scripts/validate_data.py [data_dir]
Add --report for sourced-vs-estimate counts.
Checks files against 05_BACKEND_SCHEMA section 2 and the audit rule (every field has a source or estimate label)."""
import json, sys, pathlib

CITIES = {"Chennai","Bengaluru","Hyderabad","Pune","Mumbai","Delhi NCR","Coimbatore","Kolkata"}
SKILLS = {"math","statistics","programming","logic","communication","design","biology","electronics"}
WINDOWS = {"0-3","3-6","6-12"}
DIMS = list("RIASEC")
AUDITED = ["riasec","tuition_per_year","living_per_year","years","coaching","salary.y1","salary.y3","salary.y5",
           "years_to_first_income","static_national","city_demand","growth_index","automation_risk","career_risk",
           "entrance_required","expected_scholarship","skills","exams"]
errs, warns = [], []
def e(m): errs.append(m)
def unit(v): return isinstance(v,(int,float)) and not isinstance(v,bool) and 0 <= v <= 1

args = [a for a in sys.argv[1:] if not a.startswith("--")]
REPORT = "--report" in sys.argv
d = pathlib.Path(args[0] if args else "data")
load = lambda n: json.loads((d/n).read_text(encoding="utf-8")) if (d/n).exists() else (e(f"{n}: missing") or [])
careers, schol, local, qs = load("careers.json"), load("scholarships.json"), load("local_opportunities.json"), load("questions.json")
cids = [c.get("id") for c in careers]
sids = {s.get("id") for s in schol}
if len(cids) != len(set(cids)): e("careers: duplicate ids")

for c in careers:
    i = c.get("id","?")
    for f in ["id","name","riasec","tuition_per_year","living_per_year","years","coaching","salary","years_to_first_income",
              "static_national","city_demand","growth_index","automation_risk","career_risk","entrance_required",
              "expected_scholarship","skills","roadmap","exams","scholarship_ids","adjacent","sources","estimated_fields"]:
        if f not in c: e(f"{i}: missing field {f}")
    r = c.get("riasec",[])
    if len(r) != 6 or not all(unit(x) for x in r): e(f"{i}: riasec must be 6 floats in [0,1]")
    elif max(r) - min(r) == 0: e(f"{i}: riasec is flat (all equal)")
    for f in ["tuition_per_year","living_per_year","coaching","expected_scholarship"]:
        if not isinstance(c.get(f),int) or c[f] < 0: e(f"{i}: {f} must be a non-negative integer (INR)")
    s = c.get("salary",{})
    for k in ["y1","y3","y5"]:
        if not isinstance(s.get(k),int) or s[k] <= 0: e(f"{i}: salary.{k} must be a positive integer (monthly INR)")
    if all(isinstance(s.get(k),int) for k in ["y1","y3","y5"]) and not (s["y1"] <= s["y3"] <= s["y5"]): warns.append(f"{i}: salary not increasing y1<=y3<=y5")
    if not isinstance(c.get("years"),(int,float)) or c["years"] <= 0: e(f"{i}: years must be > 0")
    if c.get("years_to_first_income",0) < c.get("years",0): warns.append(f"{i}: years_to_first_income < years (check)")
    for f in ["static_national","growth_index","automation_risk","career_risk"]:
        if not unit(c.get(f)): e(f"{i}: {f} must be in [0,1]")
    for city,v in c.get("city_demand",{}).items():
        if city not in CITIES: e(f"{i}: unknown city '{city}'")
        if not unit(v): e(f"{i}: city_demand[{city}] must be in [0,1]")
    for sk in c.get("skills",[]):
        if sk.get("name") not in SKILLS: e(f"{i}: unknown skill '{sk.get('name')}'")
        if not unit(sk.get("required_level")): e(f"{i}: skill level must be in [0,1]")
    for st in c.get("roadmap",[]):
        if st.get("window") not in WINDOWS: e(f"{i}: bad roadmap window '{st.get('window')}'")
        if st.get("skill") is not None and st["skill"] not in SKILLS: e(f"{i}: roadmap skill '{st['skill']}' unknown")
        if not st.get("step"): e(f"{i}: empty roadmap step")
    for a in c.get("adjacent",[]):
        if a not in cids: e(f"{i}: adjacent '{a}' not in dataset")
    for sid in c.get("scholarship_ids",[]):
        if sid not in sids: e(f"{i}: scholarship_id '{sid}' not in scholarships.json")
    src, est = c.get("sources",{}), set(c.get("estimated_fields",[]))
    for f in AUDITED:
        parent = f.split(".")[0]
        if not (f in src or parent in src or f in est or parent in est):
            e(f"{i}: AUDIT FAIL no source or estimate label for '{f}'")
    if "stub" in est: warns.append(f"{i}: still a STUB")

for s in schol:
    for f in ["id","name","provider","url","checked_on"]:
        if not s.get(f): e(f"scholarship {s.get('id','?')}: missing {f}")
    if s.get("deadline") is not None and not s.get("deadline_year_note"): warns.append(f"scholarship {s.get('id')}: add deadline_year_note")
for o in local:
    if o.get("city") not in CITIES: e(f"local {o.get('id')}: unknown city")
    for f in ["problem","project_idea","source"]:
        if not o.get(f): e(f"local {o.get('id')}: missing {f}")
    if o.get("source") == "idea" : pass
if qs:
    inter = [q for q in qs if q.get("kind")=="interest"]; skl = [q for q in qs if q.get("kind")=="skill"]
    for q in inter:
        if q.get("dimension") not in DIMS: e(f"question {q.get('id')}: bad dimension")
    for q in skl:
        if q.get("skill") not in SKILLS: e(f"question {q.get('id')}: bad skill")
    full = len(inter) == 24 and len(skl) == 8
    if not full: warns.append(f"questions: {len(inter)}/24 interest, {len(skl)}/8 skill (incomplete)")
    else:
        for dm in DIMS:
            if sum(q["dimension"]==dm for q in inter) != 4: e(f"questions: dimension {dm} must have exactly 4 items")
        if {q["skill"] for q in skl} != SKILLS: e("questions: skill items must cover all 8 skills once")
    if len({q.get('id') for q in qs}) != len(qs): e("questions: duplicate ids")

if REPORT:
    print("\nSOURCED vs ESTIMATE (audited fields; a field in both lists counts as estimate)")
    tot_s = tot_e = 0
    for c in careers:
        src, est = c.get("sources",{}), set(c.get("estimated_fields",[]))
        sourced, unver = [], []
        for f in AUDITED:
            par = f.split(".")[0]
            if f in est or par in est: continue
            if f in src or par in src:
                sourced.append(f)
                if "not yet verified" in str(src.get(f, src.get(par))).lower(): unver.append(f)
        n = len(AUDITED); tot_s += len(sourced); tot_e += n - len(sourced)
        print(f"  {c['id']:<20} sourced {len(sourced):>2}/{n}  estimate {n-len(sourced):>2}/{n}" + (f"  UNVERIFIED-but-sourced: {unver}" if unver else ""))
        bad = [f for f in sourced if not str(src.get(f, src.get(f.split('.')[0],''))).startswith("http")]
        if bad: print(f"    WARN sourced without a URL: {bad}")
    print(f"  TOTAL sourced {tot_s}, estimate {tot_e}")
print(f"careers: {len(careers)} | scholarships: {len(schol)} | local: {len(local)} | questions: {len(qs)}")
for w in warns: print("WARN ", w)
for x in errs: print("ERROR", x)
print("PASS" if not errs else f"FAIL ({len(errs)} errors)")
sys.exit(1 if errs else 0)
