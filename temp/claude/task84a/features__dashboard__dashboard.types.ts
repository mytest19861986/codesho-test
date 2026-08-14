export type DashboardViewState =
  | "ready"
  | "loading"
  | "empty"
  | "lessons-empty"
  | "error"
  | "unauthenticated"
  | "parent-not-found"
  | "forbidden"
  | "invalid-request"
  | "recoverable-error";

export interface DashboardStudent {
  readonly displayName: string;
}

export interface CourseItem {
  readonly id: string;
  readonly code: string;
  readonly title: string;
  readonly state: "published";
}

export interface LessonItem {
  readonly id: string;
  readonly code: string;
  readonly title: string;
  readonly position: number;
  readonly state: "published";
}

export interface DashboardLearning {
  readonly courses: readonly CourseItem[];
  readonly lessons: readonly LessonItem[];
  readonly selectedCourseId: string | null;
}

export interface DashboardModel {
  readonly student: DashboardStudent;
  readonly learning: DashboardLearning;
}
