"use client";

import React, { createContext, useContext, useState, ReactNode } from "react";

interface StudentSearchContextType {
  searchQuery: string;
  setSearchQuery: (q: string) => void;
}

const StudentSearchContext = createContext<StudentSearchContextType | undefined>(undefined);

export function StudentSearchProvider({ children }: { children: ReactNode }) {
  const [searchQuery, setSearchQuery] = useState("");

  return (
    <StudentSearchContext.Provider value={{ searchQuery, setSearchQuery }}>
      {children}
    </StudentSearchContext.Provider>
  );
}

export function useStudentSearch() {
  const context = useContext(StudentSearchContext);
  if (!context) {
    throw new Error("useStudentSearch must be used within a StudentSearchProvider");
  }
  return context;
}
