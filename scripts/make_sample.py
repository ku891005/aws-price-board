#!/usr/bin/env python3
"""실제 API 호출 없이 화면을 확인하기 위한 샘플 데이터 생성기 (구조는 fetch_prices.py 출력과 동일)."""
import json, os
from datetime import datetime, timezone

OUT = os.path.join(os.path.dirname(__file__), "..", "docs", "data")
os.makedirs(OUT, exist_ok=True)

RDS_ENGINES = [
    ("Oracle", "Enterprise", ["License Included", "BYOL"]),
    ("Oracle", "Standard Two", ["License Included", "BYOL"]),
    ("SQL Server", "Enterprise", ["License Included", "BYOM"]),
    ("SQL Server", "Standard", ["License Included", "BYOM"]),
    ("SQL Server", "Web", ["License Included"]),
    ("SQL Server", "Express", ["License Included"]),
    ("MySQL", "-", ["No License Required"]),
    ("PostgreSQL", "-", ["No License Required"]),
    ("Aurora MySQL", "-", ["No License Required"]),
    ("Aurora PostgreSQL", "-", ["No License Required"]),
    ("MariaDB", "-", ["No License Required"]),
]
SIZES = [("large", 2, 16), ("xlarge", 4, 32), ("2xlarge", 8, 64),
         ("4xlarge", 16, 128), ("8xlarge", 32, 256)]
FAMS = [("r6g", 0.85, "AWS Graviton2"), ("r6i", 1.0, "Intel Xeon 8375C"),
        ("m6g", 0.70, "AWS Graviton2"), ("t4g", 0.35, "AWS Graviton2")]
ENG_MULT = {"Oracle": 2.4, "SQL Server": 2.9, "MySQL": 1.0, "PostgreSQL": 1.0,
            "Aurora MySQL": 1.15, "Aurora PostgreSQL": 1.15, "MariaDB": 1.0}
ED_MULT = {"Enterprise": 1.35, "Standard": 1.0, "Standard Two": 0.9,
           "Web": 0.55, "Express": 0.0, "-": 1.0}
LIC_MULT = {"License Included": 1.0, "BYOL": 0.45, "BYOM": 0.5, "No License Required": 1.0}

rds = []
for eng, ed, lics in RDS_ENGINES:
    for lic in lics:
        for fam, fm, proc in FAMS:
            for sz, vcpu, mem in SIZES:
                for dep in ("Single-AZ", "Multi-AZ"):
                    base = 0.062 * vcpu * fm * ENG_MULT[eng] * LIC_MULT[lic]
                    if dep == "Multi-AZ":
                        base *= 2
                    if eng == "SQL Server":
                        base = 0.062 * vcpu * fm * (1 + 1.9 * ED_MULT.get(ed, 1.0)) \
                               * LIC_MULT[lic] * (2 if dep == "Multi-AZ" else 1)
                    else:
                        base *= ED_MULT.get(ed, 1.0)
                    rds.append({
                        "sku": f"S{len(rds):05d}", "instanceType": f"db.{fam}.{sz}",
                        "family": fam, "engine": eng, "edition": ed, "license": lic,
                        "deployment": dep, "vcpu": vcpu, "memory": f"{mem} GiB",
                        "processor": proc, "network": "Up to 10 Gigabit",
                        "usagetype": f"APN2-InstanceUsage:db.{fam}.{sz}",
                        "od": round(base, 6),
                        "ri1": round(base * 0.68, 6), "ri1_po": "All Upfront",
                        "ri3": round(base * 0.45, 6), "ri3_po": "All Upfront",
                    })

EC2 = [("Linux", "No License Required"), ("RHEL", "No License Required"),
       ("Windows", "License Included"), ("Windows", "BYOL"),
       ("SUSE", "No License Required")]
ec2 = []
for os_, lic in EC2:
    for fam, fm, proc in [("m6i", 1.0, "Intel Xeon 8375C"), ("c6g", 0.8, "AWS Graviton2"),
                          ("r6i", 1.25, "Intel Xeon 8375C"), ("t3", 0.45, "Intel Xeon Platinum")]:
        for sz, vcpu, mem in [("large", 2, 8), ("xlarge", 4, 16), ("2xlarge", 8, 32),
                              ("4xlarge", 16, 64)]:
            for ten in ("Shared", "Dedicated"):
                base = 0.052 * vcpu * fm
                if os_ == "Windows" and lic == "License Included":
                    base += 0.046 * vcpu
                if os_ in ("RHEL", "SUSE"):
                    base += 0.02
                if ten == "Dedicated":
                    base *= 1.1
                ec2.append({
                    "sku": f"E{len(ec2):05d}", "instanceType": f"{fam}.{sz}", "family": fam,
                    "os": os_, "license": lic, "preSw": "NA", "tenancy": ten,
                    "vcpu": vcpu, "memory": f"{mem} GiB", "processor": proc,
                    "gen": "Yes", "network": "Up to 12500 Megabit",
                    "usagetype": f"APN2-BoxUsage:{fam}.{sz}",
                    "od": round(base, 6),
                    "ri1": round(base * 0.65, 6), "ri1_po": "All Upfront",
                    "ri3": round(base * 0.42, 6), "ri3_po": "All Upfront",
                })

storage = []
for fam, typ, unit, price, desc in [
    ("Database Storage", "General Purpose (gp3)", "GB-Mo", 0.114, "gp3 storage"),
    ("Database Storage", "General Purpose (gp2)", "GB-Mo", 0.114, "gp2 storage"),
    ("Database Storage", "Provisioned IOPS (io1)", "GB-Mo", 0.138, "io1 storage"),
    ("Provisioned IOPS", "io1", "IOPS-Mo", 0.10, "provisioned IOPS"),
    ("Provisioned Throughput", "gp3", "MBps-Mo", 0.0924, "provisioned throughput"),
    ("Storage Snapshot", "Backup", "GB-Mo", 0.095, "backup storage beyond free tier"),
]:
    for eng in ("MySQL", "PostgreSQL", "Oracle", "SQL Server"):
        for dep in ("Single-AZ", "Multi-AZ"):
            storage.append({"sku": f"T{len(storage):05d}", "family": fam, "type": typ,
                            "engine": eng, "deployment": dep, "unit": unit,
                            "price": round(price * (2 if dep == "Multi-AZ" else 1), 6),
                            "desc": desc})

def w(n, o):
    with open(os.path.join(OUT, n), "w", encoding="utf-8") as f:
        json.dump(o, f, ensure_ascii=False, separators=(",", ":"))
    print(n, len(o) if isinstance(o, list) else "-")

w("rds.json", rds)
w("ec2.json", ec2)
w("rds_storage.json", storage)
w("meta.json", {"region": "ap-northeast-2",
                "updatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "hoursPerMonth": 730,
                "counts": {"rds": len(rds), "ec2": len(ec2), "rdsStorage": len(storage)},
                "source": "SAMPLE DATA (실행 전 검증용)"})
