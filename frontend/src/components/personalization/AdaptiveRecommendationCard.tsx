"use client";

import React from "react";

export interface LearningRecommendationData {
  id: string;
  student_id: string;
  recommendation_type: "REMEDIAL_PRACTICE" | "NEXT_CHALLENGE" | "SKILL_EXPANSION" | "REVISION";
  status: "GENERATED" | "VIEWED" | "ACCEPTED" | "COMPLETED" | "DISMISSED" | "SUPERSEDED";
  priority: number;
  recommendation_reason: string;
  evidence_context: Record<string, unknown>;
  target_skill_slug?: string | null;
  target_skill_title?: string | null;
  created_at: string;
}

interface AdaptiveRecommendationCardProps {
  recommendation: LearningRecommendationData;
  onAccept: (id: string) => void;
  onDismiss: (id: string) => void;
  isLoading?: boolean;
}

export const AdaptiveRecommendationCard: React.FC<AdaptiveRecommendationCardProps> = ({
  recommendation,
  onAccept,
  onDismiss,
  isLoading = false,
}) => {
  const getTypeBadge = (type: string) => {
    switch (type) {
      case "REMEDIAL_PRACTICE":
        return { label: "تمرین تکمیلی و شکوفایی", bg: "bg-amber-100 text-amber-800 border-amber-300" };
      case "NEXT_CHALLENGE":
        return { label: "چالش گام بعدی", bg: "bg-emerald-100 text-emerald-800 border-emerald-300" };
      case "SKILL_EXPANSION":
        return { label: "توسعه افقی مهارت", bg: "bg-indigo-100 text-indigo-800 border-indigo-300" };
      case "REVISION":
        return { label: "یادآوری و تثبیت آموخته‌ها", bg: "bg-blue-100 text-blue-800 border-blue-300" };
      default:
        return { label: "پیشنهاد یادگیری", bg: "bg-slate-100 text-slate-800 border-slate-300" };
    }
  };

  const badge = getTypeBadge(recommendation.recommendation_type);

  return (
    <article
      data-testid={`recommendation-card-${recommendation.id}`}
      className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm hover:shadow-md transition-all duration-200 text-right"
      dir="rtl"
    >
      <header className="flex items-center justify-between gap-4 mb-4">
        <span
          className={`px-3 py-1 text-xs font-semibold rounded-full border ${badge.bg}`}
          data-testid="recommendation-badge"
        >
          {badge.label}
        </span>
        {recommendation.target_skill_slug && (
          <span className="text-xs text-slate-500 font-mono bg-slate-50 px-2.5 py-1 rounded-md border border-slate-200">
            <bdi dir="ltr">{recommendation.target_skill_slug}</bdi>
          </span>
        )}
      </header>

      {recommendation.target_skill_title && (
        <h3 className="text-lg font-bold text-slate-900 mb-2">
          {recommendation.target_skill_title}
        </h3>
      )}

      {/* Pedagogical Explanation (Explainability First) */}
      <p className="text-sm text-slate-700 leading-relaxed mb-6 bg-slate-50 p-3.5 rounded-xl border border-slate-100">
        {recommendation.recommendation_reason}
      </p>

      {/* Touch-target compliant actions (>= 44px min height) */}
      <footer className="flex items-center gap-3 pt-2">
        <button
          type="button"
          onClick={() => onAccept(recommendation.id)}
          disabled={isLoading || recommendation.status !== "GENERATED" && recommendation.status !== "VIEWED"}
          className="flex-1 min-h-[44px] px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 text-white font-medium text-sm rounded-xl transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          data-testid="btn-accept-recommendation"
        >
          شروع تمرین هدفمند
        </button>

        <button
          type="button"
          onClick={() => onDismiss(recommendation.id)}
          disabled={isLoading || recommendation.status !== "GENERATED" && recommendation.status !== "VIEWED"}
          className="min-h-[44px] px-4 py-2.5 bg-slate-100 hover:bg-slate-200 active:bg-slate-300 text-slate-700 font-medium text-sm rounded-xl transition-colors focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          data-testid="btn-dismiss-recommendation"
        >
          بعداً
        </button>
      </footer>
    </article>
  );
};
export default AdaptiveRecommendationCard;
