TASK81A_P2_AUTHORITY_SOURCE=Commander-authoritative Task81A review disposition
TASK81A_P2_01=Nonblocking typed-domain-item migration: use explicit CourseItem/LessonItem-style structures at the boundary and avoid broad weak typing.
TASK81A_P2_01_CURRENT_EVIDENCE=Task81B defines typed CourseItem/LessonItem structures and runtime validation; no broad any is used in the reviewed seven-file scope.
TASK81A_P2_01_DISPOSITION=RESOLVED_FOR_TASK81B_SCOPE

TASK81A_P2_02=Nonblocking explicit state/error strategy: preserve authentication and security-boundary distinctions instead of flattening all failures into one generic error.
TASK81A_P2_02_CURRENT_EVIDENCE=Task81B preserves unauthenticated, forbidden-or-boundary, parent-not-found, recoverable-error, and stale-session states; late responses are ignored after session or selection changes.
TASK81A_P2_02_DISPOSITION=RESOLVED_FOR_TASK81B_SCOPE

These were nonblocking Task81A P2 items. Claude must independently verify the supplied implementation evidence and may disagree; this file does not require PASS.
