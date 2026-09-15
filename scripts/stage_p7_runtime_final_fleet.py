import shutil
import os

BASE_DOCS = "docs/coordination"
ROOT = "temp/fleet_exchange/P7-REAL-PILOT-MANAGER-DECISION-AND-ADMISSION-PREPARATION-RUNTIME-FINAL"

os.makedirs(os.path.join(ROOT, "qwen"), exist_ok=True)
os.makedirs(os.path.join(ROOT, "glm"), exist_ok=True)
os.makedirs(os.path.join(ROOT, "gemini"), exist_ok=True)

QWEN_FILES = [
    "P7_REAL_PILOT_MANAGER_DECISION_DISCOVERY_DOSSIER.md",
    "P7_REAL_PILOT_ADMISSION_ARCHITECTURE.md",
    "P7_MANAGER_GO_NO_GO_MATRIX.md",
    "P7_REAL_PILOT_SCOPE_PROPOSAL.md",
    "P7_SYNTHETIC_MANAGER_DECISION_REHEARSAL.md",
    "P7_NEGATIVE_TEST_MATRIX.md",
    "P7_MANAGER_DECISION_PACKAGE.md",
    "P7_FLEET_QWEN_DISCOVERY.md",
]

GLM_FILES = [
    "P7_REAL_PILOT_ADMISSION_ARCHITECTURE.md",
    "P7_REAL_DATA_ADMISSION_DECISION_PACKAGE.md",
    "P7_REAL_PILOT_SCOPE_PROPOSAL.md",
    "P7_REAL_PILOT_EXIT_PLAN.md",
    "P7_NEGATIVE_TEST_MATRIX.md",
    "P7_REAL_PILOT_WRITE_MANIFEST.md",
    "P7_FLEET_GLM_DISCOVERY.md",
]

GEMINI_FILES = [
    "P7_MANAGER_GO_NO_GO_MATRIX.md",
    "P7_REAL_PILOT_SCOPE_PROPOSAL.md",
    "P7_PRODUCTION_ADMISSION_READINESS.md",
    "P7_REAL_PILOT_EXIT_PLAN.md",
    "P7_MANAGER_DECISION_PACKAGE.md",
    "P7_SYNTHETIC_MANAGER_DECISION_REHEARSAL.md",
    "P7_FLEET_GEMINI_DISCOVERY.md",
]

for f in QWEN_FILES:
    src = os.path.join(BASE_DOCS, f)
    if os.path.exists(src):
        dst = os.path.join(ROOT, "qwen", f)
        shutil.copyfile(src, dst)
        print("Staged Qwen:", dst)

for f in GLM_FILES:
    src = os.path.join(BASE_DOCS, f)
    if os.path.exists(src):
        dst = os.path.join(ROOT, "glm", f)
        shutil.copyfile(src, dst)
        print("Staged GLM:", dst)

for f in GEMINI_FILES:
    src = os.path.join(BASE_DOCS, f)
    if os.path.exists(src):
        dst = os.path.join(ROOT, "gemini", f)
        shutil.copyfile(src, dst)
        print("Staged Gemini:", dst)

print("\nP7 Runtime Final Fleet Staging Complete!")
