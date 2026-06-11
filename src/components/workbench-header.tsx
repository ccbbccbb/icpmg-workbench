"use client";

import { CalendarDays, LayoutDashboard } from "lucide-react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import FallbackAvatar from "@/components/ui/fallback-avatar";
import { useMockAuth } from "@/hooks/useMockAuth";

export function WorkbenchHeader() {
  const router = useRouter();
  const { user, signOut } = useMockAuth();

  return (
    <header className="flex flex-wrap items-center gap-x-2 gap-y-2 bg-background px-4 py-3 sm:flex-nowrap sm:gap-x-3 sm:px-6">
      <Image
        alt="KPMG"
        className="h-auto w-14 shrink-0 sm:w-[70px]"
        height={28}
        priority
        src="/assets/kpmg-blue.svg"
        width={70}
      />
      <span className="min-w-0 flex-1 font-semibold text-foreground text-sm leading-tight sm:text-lg">
        iCPMG Workbench
        <sup className="ml-1 font-normal text-[0.625rem] text-kpmgCobaltBlue uppercase tracking-wide sm:text-xs">
          alpha
        </sup>
      </span>

      <div className="ml-auto flex shrink-0 items-center gap-3 sm:gap-5">
        <button
          className="flex cursor-pointer items-center gap-2 text-kpmgGray1 text-sm hover:text-kpmgBlue"
          type="button"
        >
          <CalendarDays aria-hidden className="size-4" />
          <span className="hidden sm:inline">Schedule</span>
        </button>

        <DropdownMenu>
          <DropdownMenuTrigger className="cursor-pointer rounded-full outline-none focus-visible:ring-2 focus-visible:ring-ring">
            <FallbackAvatar name={user?.name ?? "Reviewer"} size={32} />
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuLabel>
              <span className="block">{user?.name ?? "Reviewer"}</span>
              <span className="block font-normal text-muted-foreground text-xs">{user?.email}</span>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem>
              <LayoutDashboard aria-hidden />
              Dashboard
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onSelect={() => {
                signOut();
                router.push("/");
              }}
              variant="destructive"
            >
              Sign out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
