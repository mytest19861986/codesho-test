"use client";

import { useEffect, useRef } from "react";
import { createPortal } from "react-dom";

import type { PublicNavigationDrawerProps } from "./public-layout.types";
import styles from "./public-shell.module.css";

export function PublicNavigationDrawer({ activeItemId, closeLabel, items, label, onClose, open, triggerRef }: PublicNavigationDrawerProps) {
  const dialogRef = useRef<HTMLDivElement>(null);
  const layerRef = useRef<HTMLDivElement>(null);
  const wasOpen = useRef(false);

  useEffect(() => {
    if (!open) {
      if (wasOpen.current) {
        wasOpen.current = false;
        triggerRef.current?.focus();
      }
      return undefined;
    }

    wasOpen.current = true;
    const dialog = dialogRef.current;
    const bodyOverflow = document.body.style.overflow;
    const documentOverflow = document.documentElement.style.overflow;
    const backgroundTargets = Array.from(document.body.children)
      .filter((element): element is HTMLElement => element instanceof HTMLElement && element !== layerRef.current)
      .map((element) => ({
        ariaHidden: element.getAttribute("aria-hidden"),
        element,
        inert: element.inert,
      }));
    backgroundTargets.forEach(({ element }) => {
      element.inert = true;
      element.setAttribute("aria-hidden", "true");
    });
    document.body.style.overflow = "hidden";
    document.documentElement.style.overflow = "hidden";
    const focusFrame = window.requestAnimationFrame(() => {
      dialog?.querySelector<HTMLButtonElement>("[data-public-drawer-close]")?.focus();
    });

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        event.preventDefault();
        onClose();
        return;
      }
      if (event.key !== "Tab" || !dialog) return;
      const focusable = Array.from(dialog.querySelectorAll<HTMLElement>(
        "button, a[href], [tabindex]:not([tabindex='-1'])",
      )).filter((element) => !element.hasAttribute("disabled"));
      if (focusable.length === 0) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }

    dialog?.addEventListener("keydown", handleKeyDown);
    return () => {
      window.cancelAnimationFrame(focusFrame);
      dialog?.removeEventListener("keydown", handleKeyDown);
      backgroundTargets.forEach(({ ariaHidden, element, inert }) => {
        element.inert = inert;
        if (ariaHidden === null) {
          element.removeAttribute("aria-hidden");
        } else {
          element.setAttribute("aria-hidden", ariaHidden);
        }
      });
      document.body.style.overflow = bodyOverflow;
      document.documentElement.style.overflow = documentOverflow;
    };
  }, [onClose, open, triggerRef]);

  if (!open) return null;

  return createPortal(
    <div className={styles.drawerLayer} ref={layerRef}>
      <button aria-label={closeLabel} className={styles.drawerOverlay} onClick={onClose} type="button" />
      <div aria-label={label} aria-modal="true" className={styles.drawer} id="codesho-public-navigation-drawer" ref={dialogRef} role="dialog">
        <div className={styles.drawerHeader}>
          <span className={styles.drawerTitle}>{label}</span>
          <button aria-label={closeLabel} className={styles.drawerClose} data-public-drawer-close onClick={onClose} type="button">
            <span aria-hidden="true" className={styles.closeIcon} />
          </button>
        </div>
        <nav aria-label={label}>
          <ul className={styles.drawerNavigationList}>
            {items.map((item) => (
              <li key={item.id}>
                <a aria-current={item.id === activeItemId ? "page" : undefined} className={`${styles.drawerNavigationLink} ${item.id === activeItemId ? styles.drawerNavigationLinkActive : ""}`} href={item.href} onClick={onClose}>
                  {item.icon ? <span aria-hidden="true" className={styles.navigationIcon}>{item.icon}</span> : null}
                  <span>{item.label}</span>
                </a>
              </li>
            ))}
          </ul>
        </nav>
      </div>
    </div>,
    document.body,
  );
}
