"use client";

import { createContext, useContext, useState, type ReactNode } from "react";

interface MentorSearchContextType {
  searchQuery: string;
  setSearchQuery: (q: string) => void;
  openSessionModal: boolean;
  setOpenSessionModal: (open: boolean) => void;
  openReviewModal: boolean;
  setOpenReviewModal: (open: boolean) => void;
  openGuideModal: boolean;
  setOpenGuideModal: (open: boolean) => void;
}

const MentorSearchContext = createContext<MentorSearchContextType | undefined>(undefined);

export function MentorSearchProvider({ children }: { children: ReactNode }) {
  const [searchQuery, setSearchQuery] = useState("");
  const [openSessionModal, setOpenSessionModal] = useState(false);
  const [openReviewModal, setOpenReviewModal] = useState(false);
  const [openGuideModal, setOpenGuideModal] = useState(false);

  return (
    <MentorSearchContext.Provider
      value={{
        searchQuery,
        setSearchQuery,
        openSessionModal,
        setOpenSessionModal,
        openReviewModal,
        setOpenReviewModal,
        openGuideModal,
        setOpenGuideModal,
      }}
    >
      {children}
    </MentorSearchContext.Provider>
  );
}

export function useMentorSearch() {
  const context = useContext(MentorSearchContext);
  if (!context) {
    throw new Error("useMentorSearch must be used within MentorSearchProvider");
  }
  return context;
}
