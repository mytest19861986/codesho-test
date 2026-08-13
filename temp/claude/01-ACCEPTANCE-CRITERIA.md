# AUTHORITATIVE AC-01..AC-43
AC-01 Course read: GET /api/v1/learning/courses/?page=1&page_size=20; correct method, endpoint and bounded read.
AC-02 Lesson read: validated course ID; GET /api/v1/learning/courses/{course_id}/lessons/?page=1&page_size=20; bounded and stale-safe.
AC-03 Preserve authenticated same-origin session; never invent tenant/role/org/user authority.
AC-04 Runtime-validate successful Course/Lesson payloads; malformed 2xx fails closed.
AC-05 Validate UUID-like opaque Course/Lesson IDs before trusted state, rendering, URL interpolation, or switching.
AC-06 Accept/render only state === "published" where required; malformed state is invalid.
AC-07 Enforce bounded page-size/cardinality for courses and lessons.
AC-08 Do not fabricate total/count/next/previous/page_count.
AC-09 Do not invent learner metrics: progress, XP, rank, streak, cohort, enrollment, attendance, assignments, recommendations, AI insights, lock/unlock.
AC-10 Do not infer tenant membership, eligibility, or authorization from payloads.
AC-11 Distinguish authenticated empty courses from auth, boundary, malformed, and transient failures.
AC-12 Valid selected published course with zero lessons has truthful lessons-empty state.
AC-13 Keep 401/authentication distinct from empty data.
AC-14 Keep 403/security-boundary distinct from normal empty where architecture requires.
AC-15 Preserve non-enumerating 404; do not claim sensitive existence/access distinctions.
AC-16 Malformed success produces explicit safe invalid/data-boundary state, not partial trusted rendering.
AC-17 Distinguish recoverable network/server failure from auth, boundary, invalid, and empty states.
AC-18 Old course/session response must not overwrite newer state.
AC-19 Old lesson response must not populate a newly selected course.
AC-20 Obsolete session/auth responses must not enter current state.
AC-21 Course switch clears/fails closed stale lessons and prevents stale failures corrupting current state.
AC-22 Review explicit typed CourseItem/LessonItem migration and return TASK81A_P2_01_DISPOSITION.
AC-23 Review explicit state/error strategy preserving auth/security-boundary distinctions and return TASK81A_P2_02_DISPOSITION.
AC-24 No broad TypeScript any bypass; justify any narrow escape.
AC-25 Preserve Persian/RTL dashboard experience.
AC-26 Course selection/interactions keyboard accessible.
AC-27 Valid interactive markup; button content uses non-interactive phrasing descendants.
AC-28 No focus traps or destructive focus behavior on transitions/errors/changes.
AC-29 Correct, non-noisy live-region/status communication for async state changes.
AC-30 Do not weaken tenant isolation, choose tenant authority, enumerate cross-tenant resources, or reinterpret 404.
AC-31 No token persistence/forwarding, credential exposure, or new inconsistent auth authority.
AC-32 Only validated opaque IDs enter lesson URL.
AC-33 No sensitive tenant/auth/session debug leakage in UI/logs.
AC-34 Diff limited to exact seven authorized Task81B files.
AC-35 No backend/OpenAPI behavior, migration, dependency, auth protocol, or contract mutation.
AC-36 Evidence transport remains review artifact, not implementation.
AC-37 Tests meaningfully cover valid/malformed/IDs/state/cardinality/empty/auth-boundary/404/stale/no-fabrication behavior.
AC-38 Exact-head frontend typecheck succeeds.
AC-39 Exact-head lint succeeds.
AC-40 Exact-head frontend production build succeeds.
AC-41 Diff is BASE d2b9803972f0c20bc154df471ad941b2f78855fd to HEAD e98d1c575903f7b5657a20c004ea2802189e4394.
AC-42 Exact-head CI run 31624692088 supports success.
AC-43 Exact-head Compose smoke/restore run 31624692028 supports success.
