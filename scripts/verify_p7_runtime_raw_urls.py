import urllib.request
import sys

SHA = "0535747acc8834024054ec1f20a618e984feacce"
REPO = "mytest19861986/codesho-test"

files = [
    # Qwen
    "temp/fleet_exchange/P7-REAL-PILOT-MANAGER-DECISION-AND-ADMISSION-PREPARATION-RUNTIME-FINAL/qwen/P7_REAL_PILOT_MANAGER_DECISION_DISCOVERY_DOSSIER.md",
    "temp/fleet_exchange/P7-REAL-PILOT-MANAGER-DECISION-AND-ADMISSION-PREPARATION-RUNTIME-FINAL/qwen/P7_REAL_PILOT_ADMISSION_ARCHITECTURE.md",
    "temp/fleet_exchange/P7-REAL-PILOT-MANAGER-DECISION-AND-ADMISSION-PREPARATION-RUNTIME-FINAL/qwen/P7_MANAGER_GO_NO_GO_MATRIX.md",
    "temp/fleet_exchange/P7-REAL-PILOT-MANAGER-DECISION-AND-ADMISSION-PREPARATION-RUNTIME-FINAL/qwen/P7_REAL_PILOT_SCOPE_PROPOSAL.md",
    "temp/fleet_exchange/P7-REAL-PILOT-MANAGER-DECISION-AND-ADMISSION-PREPARATION-RUNTIME-FINAL/qwen/P7_SYNTHETIC_MANAGER_DECISION_REHEARSAL.md",
    "temp/fleet_exchange/P7-REAL-PILOT-MANAGER-DECISION-AND-ADMISSION-PREPARATION-RUNTIME-FINAL/qwen/P7_NEGATIVE_TEST_MATRIX.md",
    "temp/fleet_exchange/P7-REAL-PILOT-MANAGER-DECISION-AND-ADMISSION-PREPARATION-RUNTIME-FINAL/qwen/P7_MANAGER_DECISION_PACKAGE.md",
    "temp/fleet_exchange/P7-REAL-PILOT-MANAGER-DECISION-AND-ADMISSION-PREPARATION-RUNTIME-FINAL/qwen/P7_FLEET_QWEN_DISCOVERY.md",
    # GLM
    "temp/fleet_exchange/P7-REAL-PILOT-MANAGER-DECISION-AND-ADMISSION-PREPARATION-RUNTIME-FINAL/glm/P7_REAL_PILOT_ADMISSION_ARCHITECTURE.md",
    "temp/fleet_exchange/P7-REAL-PILOT-MANAGER-DECISION-AND-ADMISSION-PREPARATION-RUNTIME-FINAL/glm/P7_REAL_DATA_ADMISSION_DECISION_PACKAGE.md",
    "temp/fleet_exchange/P7-REAL-PILOT-MANAGER-DECISION-AND-ADMISSION-PREPARATION-RUNTIME-FINAL/glm/P7_REAL_PILOT_SCOPE_PROPOSAL.md",
    "temp/fleet_exchange/P7-REAL-PILOT-MANAGER-DECISION-AND-ADMISSION-PREPARATION-RUNTIME-FINAL/glm/P7_REAL_PILOT_EXIT_PLAN.md",
    "temp/fleet_exchange/P7-REAL-PILOT-MANAGER-DECISION-AND-ADMISSION-PREPARATION-RUNTIME-FINAL/glm/P7_NEGATIVE_TEST_MATRIX.md",
    "temp/fleet_exchange/P7-REAL-PILOT-MANAGER-DECISION-AND-ADMISSION-PREPARATION-RUNTIME-FINAL/glm/P7_REAL_PILOT_WRITE_MANIFEST.md",
    "temp/fleet_exchange/P7-REAL-PILOT-MANAGER-DECISION-AND-ADMISSION-PREPARATION-RUNTIME-FINAL/glm/P7_FLEET_GLM_DISCOVERY.md",
    # Gemini
    "temp/fleet_exchange/P7-REAL-PILOT-MANAGER-DECISION-AND-ADMISSION-PREPARATION-RUNTIME-FINAL/gemini/P7_MANAGER_GO_NO_GO_MATRIX.md",
    "temp/fleet_exchange/P7-REAL-PILOT-MANAGER-DECISION-AND-ADMISSION-PREPARATION-RUNTIME-FINAL/gemini/P7_REAL_PILOT_SCOPE_PROPOSAL.md",
    "temp/fleet_exchange/P7-REAL-PILOT-MANAGER-DECISION-AND-ADMISSION-PREPARATION-RUNTIME-FINAL/gemini/P7_PRODUCTION_ADMISSION_READINESS.md",
    "temp/fleet_exchange/P7-REAL-PILOT-MANAGER-DECISION-AND-ADMISSION-PREPARATION-RUNTIME-FINAL/gemini/P7_REAL_PILOT_EXIT_PLAN.md",
    "temp/fleet_exchange/P7-REAL-PILOT-MANAGER-DECISION-AND-ADMISSION-PREPARATION-RUNTIME-FINAL/gemini/P7_MANAGER_DECISION_PACKAGE.md",
    "temp/fleet_exchange/P7-REAL-PILOT-MANAGER-DECISION-AND-ADMISSION-PREPARATION-RUNTIME-FINAL/gemini/P7_SYNTHETIC_MANAGER_DECISION_REHEARSAL.md",
    "temp/fleet_exchange/P7-REAL-PILOT-MANAGER-DECISION-AND-ADMISSION-PREPARATION-RUNTIME-FINAL/gemini/P7_FLEET_GEMINI_DISCOVERY.md",
    "temp/fleet_exchange/P7-REAL-PILOT-MANAGER-DECISION-AND-ADMISSION-PREPARATION-RUNTIME-FINAL/gemini/ManagerDecisionCockpit_desktop_1440x900.png",
    "temp/fleet_exchange/P7-REAL-PILOT-MANAGER-DECISION-AND-ADMISSION-PREPARATION-RUNTIME-FINAL/gemini/ManagerDecisionCockpit_mobile_390x844.png",
    "temp/fleet_exchange/P7-REAL-PILOT-MANAGER-DECISION-AND-ADMISSION-PREPARATION-RUNTIME-FINAL/gemini/ManagerDecisionCockpit_confirm_modal_1440x900.png",
    "temp/fleet_exchange/P7-REAL-PILOT-MANAGER-DECISION-AND-ADMISSION-PREPARATION-RUNTIME-FINAL/gemini/ManagerDecisionCockpit_revocation_modal_1440x900.png",
    # Authoritative Code Evidence
    "backend/modules/learning/migrations/0053_phase7_manager_decision_ledger_runtime.py",
    "backend/modules/learning/models.py",
    "backend/modules/learning/enterprise_governance_service.py",
    "backend/tests/test_p7_manager_decision_fsm.py",
    "backend/tests/test_p7_negative_matrix.py",
    "frontend/src/features/admin_learning/PilotGoNoGoView.tsx"
]

print(f"VERIFYING IMMUTABLE RAW URLS FOR PHASE 7 EVIDENCE SHA {SHA}:")
all_ok = True

for path in files:
    raw_url = f"https://raw.githubusercontent.com/{REPO}/{SHA}/{path}"
    try:
        req = urllib.request.Request(raw_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read()
            status = resp.status
            size = len(content)
            is_ok = (status == 200 and size > 0)
            print(f"[{status}] Size: {size} bytes | URL: {raw_url}")
            if not is_ok:
                all_ok = False
    except Exception as e:
        print(f"[FAIL] URL: {raw_url} | Error: {e}")
        all_ok = False

if all_ok:
    print("\nALL STAGED IMMUTABLE RAW URLS VERIFIED 100% (STATUS 200 & NON-EMPTY)")
else:
    print("\nSOME URLS FAILED VERIFICATION")
    sys.exit(1)
