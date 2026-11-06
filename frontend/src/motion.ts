import { useEffect, type RefObject } from "react";
import { gsap } from "gsap";

/** A brief heading fade. Scientific values, charts and navigation never move. */
export function useWorkspaceMotion(root: RefObject<HTMLElement | null>, route: string) {
  useEffect(() => {
    if (!root.current || typeof window.matchMedia !== "function") return;
    const media = gsap.matchMedia();
    const context = gsap.context(() => {
      media.add("(prefers-reduced-motion: no-preference)", () => {
        gsap.fromTo(".page-heading h1", { opacity: 0.85 },
          { opacity: 1, duration: 0.16, ease: "none", clearProps: "opacity" });
      });
    }, root);
    return () => { media.revert(); context.revert(); };
  }, [root, route]);
}
