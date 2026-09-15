"use client";

import React from "react";

export interface JourneyMilestoneData {
  id: string;
  student_id: string;
  event_key: string;
  event_title: string;
  narrative_description: string;
  milestone_date: string;
  metadata?: Record<string, unknown>;
}

interface StudentJourneyNarrativeProps {
  milestones: JourneyMilestoneData[];
}

export const StudentJourneyNarrative: React.FC<StudentJourneyNarrativeProps> = ({
  milestones,
}) => {
  if (!milestones || milestones.length === 0) {
    return (
      <div
        data-testid="student-journey-empty"
        className="p-8 rounded-2xl border border-dashed border-slate-200 bg-slate-50/50 text-center text-slate-500 font-sans text-sm"
        dir="rtl"
      >
        روایت مسیر آموزشی در حال شکل‌گیری است. با پیشرفت در درس‌ها و انجام تمرین‌ها، نقاط عطف یادگیری شما ثبت خواهند شد.
      </div>
    );
  }

  return (
    <section
      data-testid="student-journey-narrative"
      className="p-6 rounded-2xl border border-slate-200/80 bg-white/95 shadow-sm flex flex-col gap-6 text-right font-sans"
      dir="rtl"
    >
      <header className="flex flex-col gap-1 border-b border-slate-100 pb-4">
        <h2 className="text-xl font-bold text-slate-900 tracking-tight">
          روایت سفر آموزشی و رشد فردی
        </h2>
        <p className="text-sm text-slate-500">
          نقاط عطف مسیر یادگیری و تلاش‌های مستمر بدون قضاوت یا رتبه‌بندی رقابتی
        </p>
      </header>

      {/* Chronological Timeline */}
      <ol className="relative border-r border-slate-200 mr-3 space-y-6 list-none p-0">
        {milestones.map((item) => (
          <li
            key={item.id}
            data-testid={`journey-milestone-${item.id}`}
            className="mb-8 mr-6 group"
          >
            {/* Timeline Bullet */}
            <span className="absolute flex items-center justify-center w-6 h-6 bg-blue-100 rounded-full -right-3 ring-4 ring-white">
              <span className="w-2.5 h-2.5 bg-blue-600 rounded-full" />
            </span>

            {/* Content Box */}
            <div className="p-4 rounded-xl border border-slate-100 bg-slate-50/60 hover:bg-slate-50 transition-colors flex flex-col gap-2">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <h3 className="text-base font-bold text-slate-900">
                  {item.event_title}
                </h3>
                <time
                  dateTime={item.milestone_date}
                  className="text-xs font-medium text-slate-500 bg-white px-2.5 py-1 rounded-md border border-slate-200/60 shadow-2xs"
                >
                  <bdi dir="ltr">{item.milestone_date}</bdi>
                </time>
              </div>

              <p className="text-sm text-slate-700 leading-relaxed whitespace-pre-line">
                {item.narrative_description}
              </p>
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
};
