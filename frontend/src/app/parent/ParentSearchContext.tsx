"use client";

import React, { createContext, useContext, useState, ReactNode } from "react";

interface ParentSearchContextType {
  searchQuery: string;
  setSearchQuery: (q: string) => void;
  openWeeklyReportModal: boolean;
  setOpenWeeklyReportModal: (open: boolean) => void;
  openMentorChatModal: boolean;
  setOpenMentorChatModal: (open: boolean) => void;
  openConsentModal: boolean;
  setOpenConsentModal: (open: boolean) => void;
  selectedChild: string;
  setSelectedChild: (child: string) => void;
}

const ParentSearchContext = createContext<ParentSearchContextType | undefined>(undefined);

export function ParentSearchProvider({ children }: { children: ReactNode }) {
  const [searchQuery, setSearchQuery] = useState("");
  const [openWeeklyReportModal, setOpenWeeklyReportModal] = useState(false);
  const [openMentorChatModal, setOpenMentorChatModal] = useState(false);
  const [openConsentModal, setOpenConsentModal] = useState(false);
  const [selectedChild, setSelectedChild] = useState("علی محمدی (پایه دهم ریاضی)");

  return (
    <ParentSearchContext.Provider
      value={{
        searchQuery,
        setSearchQuery,
        openWeeklyReportModal,
        setOpenWeeklyReportModal,
        openMentorChatModal,
        setOpenMentorChatModal,
        openConsentModal,
        setOpenConsentModal,
        selectedChild,
        setSelectedChild,
      }}
    >
      {children}
    </ParentSearchContext.Provider>
  );
}

export function useParentSearch() {
  const context = useContext(ParentSearchContext);
  if (!context) {
    throw new Error("useParentSearch must be used within a ParentSearchProvider");
  }
  return context;
}
