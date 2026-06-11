"use client";

import { motion } from "framer-motion";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { UI_SLIDE_REVEAL_MS } from "@/components/animate-section-on-reveal";
import { GoogleIcon } from "@/components/auth/google-icon";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import FallbackAvatar from "@/components/ui/fallback-avatar";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { Spinner } from "@/components/ui/spinner";
import { useMockAuth } from "@/hooks/useMockAuth";
import { cn } from "@/lib/utils/cn-util";

export default function Home() {
  const { user, isHydrated, isPending, signIn, signOut } = useMockAuth();

  return (
    <main className="flex min-h-screen animate-[gradient-move_20s_ease_infinite] items-center justify-center bg-[length:200%_200%] bg-gradient-to-br from-kpmgDarkBlue via-kpmgBlue to-kpmgCobaltBlue p-6">
      <motion.div
        animate={{ opacity: 1, y: 0 }}
        className="flex w-full flex-col items-center gap-10"
        initial={{ opacity: 0, y: 12 }}
        transition={{ duration: UI_SLIDE_REVEAL_MS / 1000, ease: "easeOut" }}
      >
        <Image alt="KPMG" height={44} priority src="/assets/kpmg-white.svg" width={110} />
        <div className="w-full max-w-sm rounded-xl bg-background p-8 text-center shadow-2xl">
          <h1 className="font-semibold text-2xl text-foreground">
            iCPMG Workbench
            <sup className="ml-1.5 font-normal text-kpmgCobaltBlue text-xs uppercase tracking-wide">
              alpha
            </sup>
          </h1>
          <p className="mt-1 text-muted-foreground text-sm">
            KPMG&apos;s candidate intelligence layer for iCIMS.
          </p>

          <div className="mt-8">
            {!isHydrated ? (
              <Skeleton className="h-10 w-full" />
            ) : user ? (
              <SignedIn email={user.email} name={user.name} onSignOut={signOut} />
            ) : (
              <Button
                className="w-full"
                disabled={isPending}
                onClick={signIn}
                size="lg"
                variant="outline"
              >
                {isPending ? <Spinner size="sm" /> : <GoogleIcon />}
                {isPending ? "Redirecting…" : "Continue with Google"}
              </Button>
            )}
          </div>

          <Separator className="my-6" />
          <Image
            alt="iCIMS"
            className="mx-auto"
            height={17}
            src="/assets/icims-black.svg"
            width={100}
          />
        </div>
      </motion.div>
    </main>
  );
}

function SignedIn({
  name,
  email,
  onSignOut,
}: {
  name: string;
  email: string;
  onSignOut: () => void;
}) {
  const router = useRouter();

  return (
    <div className="flex flex-col items-center gap-3">
      <DropdownMenu>
        <DropdownMenuTrigger
          className={cn(
            "flex items-center gap-3 rounded-md p-1 pr-3 outline-none",
            "hover:bg-accent focus-visible:ring-2 focus-visible:ring-ring"
          )}
        >
          <FallbackAvatar name={name} size={36} />
          <span className="text-left">
            <span className="block font-medium text-foreground text-sm">{name}</span>
            <span className="block text-muted-foreground text-xs">{email}</span>
          </span>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start">
          <DropdownMenuLabel>Mock session</DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem onSelect={onSignOut} variant="destructive">
            Sign out
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
      <Button className="mt-2 hover:bg-black" onClick={() => router.push("/workbench")}>
        Enter
      </Button>
    </div>
  );
}
