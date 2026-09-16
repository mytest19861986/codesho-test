import type { ReactNode } from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout";
import { studentAlphaContent as copy } from "@/content/fa/student.alpha";

interface StudentLayoutProps {
  children: ReactNode;
}

export default function StudentLayout({ children }: StudentLayoutProps) {
  const navigationItems = copy.navigation.map((item) => ({
    id: item.id,
    label: item.label,
    href: item.href,
    icon: <span aria-hidden="true">{copy.indicators.bullet}</span>,
  }));

  return (
    <AppShell
      activeItemId="dashboard"
      brand={<Link href="/student" style={{ color: "inherit", textDecoration: "none" }}>{copy.brand}</Link>}
      bottomNavigationItems={navigationItems}
      drawerCloseLabel={copy.shell.drawerCloseLabel}
      menuButtonLabel={copy.shell.menuButtonLabel}
      navigationItems={navigationItems}
      navigationLabel={copy.shell.navigationLabel}
      profileSlot={<span style={{ padding: "0 0.5rem" }}>{copy.shell.roleLabel}</span>}
      tone="learner"
    >
      {children}
    </AppShell>
  );
}
