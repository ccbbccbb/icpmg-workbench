"use client";

import { useCallback, useEffect, useState } from "react";

const SESSION_STORAGE_KEY = "mock-sso-session";
/** Long enough to read as a real OAuth redirect, short enough not to bore a demo audience. */
const FAKE_REDIRECT_MS = 900;

export interface MockUser {
  id: string;
  name: string;
  email: string;
  provider: "google";
}

const DEMO_USER: MockUser = {
  id: "usr_demo_reviewer",
  name: "FM & AI Innovation + Data Team",
  email: "CA-FMAIInnovation@kpmg.ca",
  provider: "google",
};

export interface UseMockAuthResult {
  /** null until signed in; undefined-free after hydration */
  user: MockUser | null;
  /** false until the stored session has been read on the client */
  isHydrated: boolean;
  /** true during the fake OAuth redirect delay */
  isPending: boolean;
  signIn: () => void;
  signOut: () => void;
}

/**
 * Demo-only SSO stand-in: no backend, no DB. The "session" lives in
 * localStorage and sign-in is a timed delay that mimics an OAuth redirect.
 * Swap for WorkOS AuthKit (or similar) behind the same interface for real auth.
 */
export function useMockAuth(): UseMockAuthResult {
  const [user, setUser] = useState<MockUser | null>(null);
  const [isHydrated, setIsHydrated] = useState(false);
  const [isPending, setIsPending] = useState(false);

  useEffect(() => {
    const raw = localStorage.getItem(SESSION_STORAGE_KEY);
    if (raw) {
      try {
        setUser(JSON.parse(raw) as MockUser);
      } catch {
        localStorage.removeItem(SESSION_STORAGE_KEY);
      }
    }
    setIsHydrated(true);
  }, []);

  const signIn = useCallback(() => {
    setIsPending(true);
    globalThis.setTimeout(() => {
      localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(DEMO_USER));
      setUser(DEMO_USER);
      setIsPending(false);
    }, FAKE_REDIRECT_MS);
  }, []);

  const signOut = useCallback(() => {
    localStorage.removeItem(SESSION_STORAGE_KEY);
    setUser(null);
  }, []);

  return { user, isHydrated, isPending, signIn, signOut };
}
