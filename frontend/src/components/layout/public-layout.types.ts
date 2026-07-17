import type { ReactNode, RefObject } from "react";

export interface PublicNavigationItem {
  href: string;
  icon?: ReactNode;
  id: string;
  label: string;
}

export interface PublicFooterLink {
  href: string;
  id: string;
  label: string;
}

export interface PublicFooterGroup {
  id: string;
  label: string;
  links: PublicFooterLink[];
}

export interface PublicHeaderProps {
  actionSlot?: ReactNode;
  activeItemId?: string;
  brand: ReactNode;
  drawerCloseLabel: string;
  drawerOpen: boolean;
  menuButtonLabel: string;
  navigationItems: PublicNavigationItem[];
  navigationLabel: string;
  onDrawerClose: () => void;
  onDrawerOpen: () => void;
  utilitySlot?: ReactNode;
}

export interface PublicFooterProps {
  brand: ReactNode;
  groups: PublicFooterGroup[];
  legalSlot?: ReactNode;
  supportingSlot?: ReactNode;
}

export interface PublicNavigationDrawerProps {
  activeItemId?: string;
  closeLabel: string;
  items: PublicNavigationItem[];
  label: string;
  onClose: () => void;
  open: boolean;
  triggerRef: RefObject<HTMLButtonElement | null>;
}

export interface PublicShellProps {
  actionSlot?: ReactNode;
  activeItemId?: string;
  brand: ReactNode;
  children: ReactNode;
  drawerCloseLabel: string;
  footerGroups: PublicFooterGroup[];
  footerLegalSlot?: ReactNode;
  footerSupportingSlot?: ReactNode;
  menuButtonLabel: string;
  navigationItems: PublicNavigationItem[];
  navigationLabel: string;
  utilitySlot?: ReactNode;
}
