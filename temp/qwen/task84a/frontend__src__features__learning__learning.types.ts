import type { CourseItem, LessonItem } from "@/features/dashboard/dashboard.types";

export type LearningViewState = "loading" | "empty" | "lessons-empty" | "ready" | "unauthenticated" | "error";
export interface LearningModel { readonly displayName: string; readonly courses: readonly CourseItem[]; readonly lessons: readonly LessonItem[]; readonly selectedCourseId: string | null; }
