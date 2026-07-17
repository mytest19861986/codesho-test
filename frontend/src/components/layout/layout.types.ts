import type { ReactNode } from "react";

export type ShellTone = "learner" | "teacher" | "admin" | "mentor" | "project";

export interface NavigationItem {
  id: string;
  label: string;
  href: string;
  icon: ReactNode;
  badge?: ReactNode;
}

export interface AppShellProps {
  activeItemId: string;
  brand: ReactNode;
  children: ReactNode;
  drawerCloseLabel: string;
  headerActionsSlot?: ReactNode;
  headerPrimarySlot?: ReactNode;
  menuButtonLabel: string;
  bottomNavigationItems: NavigationItem[];
  navigationItems: NavigationItem[];
  navigationLabel: string;
  profileSlot?: ReactNode;
  sidebarFooterSlot?: ReactNode;
  sidebarSupplementarySlot?: ReactNode;
  tone: ShellTone;
}
