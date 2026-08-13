import type { CourseItem, LessonItem } from "./dashboard.types";

type LearningErrorKind = "unauthenticated" | "forbidden" | "parent-not-found" | "invalid-request" | "recoverable";
export class LearningRequestError extends Error { constructor(readonly kind: LearningErrorKind, message: string) { super(message); this.name = "LearningRequestError"; } }

const pageSize = 20;
const coursesPath = `/api/v1/learning/courses/?page=1&page_size=${pageSize}`;
const lessonsPath = (courseId: string) => `/api/v1/learning/courses/${encodeURIComponent(courseId)}/lessons/?page=1&page_size=${pageSize}`;
const uuidLike = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

function record(value: unknown): Record<string, unknown> | null { return typeof value === "object" && value !== null ? value as Record<string, unknown> : null; }
function stringValue(value: unknown): value is string { return typeof value === "string" && value.length > 0; }
function opaqueId(value: unknown): value is string { return stringValue(value) && uuidLike.test(value); }
function course(value: unknown): CourseItem | null { const r = record(value); return r && opaqueId(r.id) && stringValue(r.code) && stringValue(r.title) && r.state === "published" ? { id: r.id, code: r.code, title: r.title, state: "published" } : null; }
function lesson(value: unknown): LessonItem | null { const r = record(value); return r && opaqueId(r.id) && stringValue(r.code) && stringValue(r.title) && typeof r.position === "number" && Number.isInteger(r.position) && r.position > 0 && r.state === "published" ? { id: r.id, code: r.code, title: r.title, position: r.position, state: "published" } : null; }
function statusError(status: number): LearningRequestError { if (status === 401) return new LearningRequestError("unauthenticated", "session required"); if (status === 403) return new LearningRequestError("forbidden", "access denied"); if (status === 404) return new LearningRequestError("parent-not-found", "parent not found"); if (status === 400) return new LearningRequestError("invalid-request", "invalid request"); return new LearningRequestError("recoverable", `learning request failed: ${status}`); }
async function readResults<T extends CourseItem | LessonItem>(response: Response, parse: (value: unknown) => T | null, signal?: AbortSignal): Promise<readonly T[]> { if (!response.ok) throw statusError(response.status); const payload: unknown = await response.json(); const root = record(payload); if (!root || !Array.isArray(root.results) || root.results.length > pageSize) throw new LearningRequestError("recoverable", "malformed learning envelope"); const output = root.results.map(parse); if (output.some((value) => value === null)) throw new LearningRequestError("recoverable", "malformed learning item"); if (signal?.aborted) throw new DOMException("aborted", "AbortError"); return output as readonly T[]; }
async function get<T extends CourseItem | LessonItem>(path: string, parse: (value: unknown) => T | null, signal?: AbortSignal): Promise<readonly T[]> { try { return await readResults(await fetch(path, { credentials: "same-origin", headers: { Accept: "application/json" }, signal }), parse, signal); } catch (error) { if (error instanceof LearningRequestError || (error instanceof DOMException && error.name === "AbortError")) throw error; throw new LearningRequestError("recoverable", "learning request unavailable"); } }
export async function fetchCourses(options: { readonly signal?: AbortSignal } = {}): Promise<readonly CourseItem[]> { return await get(coursesPath, course, options.signal); }
export async function fetchLessons(courseId: string, options: { readonly signal?: AbortSignal } = {}): Promise<readonly LessonItem[]> { if (!opaqueId(courseId)) throw new LearningRequestError("invalid-request", "valid course id required"); return await get(lessonsPath(courseId), lesson, options.signal); }
