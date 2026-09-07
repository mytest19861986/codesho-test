from django.urls import path

from .views import (
    AdminLearningCurriculumView,
    AdminLearningTransitionView,
    CourseLessonListView,
    CourseListView,
    LearningPathListView,
    MentorCompleteReviewView,
    MentorReviewQueueView,
    MentorStartReviewView,
    MentorSubmissionDetailView,
    ParentStudentFeedbackListView,
    ParentStudentProgressListView,
    ParentStudentSummaryView,
    StudentDashboardSummaryView,
    StudentFeedbackView,
    SubmissionDraftView,
    SubmissionSubmitView,
)

urlpatterns = [
    path("paths/", LearningPathListView.as_view(), name="learning-path-list"),
    path("courses/", CourseListView.as_view(), name="learning-course-list"),
    path(
        "courses/<str:course_id>/lessons/",
        CourseLessonListView.as_view(),
        name="learning-course-lesson-list",
    ),
    path(
        "student/dashboard/",
        StudentDashboardSummaryView.as_view(),
        name="learning-student-dashboard",
    ),
    path("submissions/draft/", SubmissionDraftView.as_view(), name="learning-submission-draft"),
    path(
        "submissions/<str:submission_id>/submit/",
        SubmissionSubmitView.as_view(),
        name="learning-submission-submit",
    ),
    path("mentor/queue/", MentorReviewQueueView.as_view(), name="learning-mentor-queue"),
    path(
        "mentor/submissions/<str:submission_id>/",
        MentorSubmissionDetailView.as_view(),
        name="learning-mentor-submission-detail",
    ),
    path(
        "mentor/submissions/<str:submission_id>/start-review/",
        MentorStartReviewView.as_view(),
        name="learning-mentor-start-review",
    ),
    path(
        "mentor/submissions/<str:submission_id>/complete-review/",
        MentorCompleteReviewView.as_view(),
        name="learning-mentor-complete-review",
    ),
    path(
        "student/submissions/<str:submission_id>/feedback/",
        StudentFeedbackView.as_view(),
        name="learning-student-submission-feedback",
    ),
    # Parent Experience Endpoints
    path(
        "parent/students/<str:student_id>/summary/",
        ParentStudentSummaryView.as_view(),
        name="learning-parent-student-summary",
    ),
    path(
        "parent/students/<str:student_id>/progress/",
        ParentStudentProgressListView.as_view(),
        name="learning-parent-student-progress",
    ),
    path(
        "parent/students/<str:student_id>/feedbacks/",
        ParentStudentFeedbackListView.as_view(),
        name="learning-parent-student-feedbacks",
    ),
    # Admin Curriculum Operations Endpoints
    path(
        "admin/curriculum/",
        AdminLearningCurriculumView.as_view(),
        name="learning-admin-curriculum",
    ),
    path(
        "admin/curriculum/transition/",
        AdminLearningTransitionView.as_view(),
        name="learning-admin-curriculum-transition",
    ),
]
