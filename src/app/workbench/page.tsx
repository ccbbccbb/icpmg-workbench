"use client";

import { ChevronDown, ChevronLeft, ChevronRight, Search, Sparkles } from "lucide-react";
import { useRouter } from "next/navigation";
import { type ReactNode, useEffect, useState } from "react";
import { AnimateSectionOnReveal } from "@/components/animate-section-on-reveal";
import { Button } from "@/components/ui/button";
import { RandomizedText } from "@/components/ui/randomized-text";
import { Spinner } from "@/components/ui/spinner";
import { WorkbenchHeader } from "@/components/workbench-header";
import { useCountUp } from "@/hooks/useCountUp";
import { useProximityScale } from "@/hooks/useProximityScale";
import { useUtcClock } from "@/hooks/useUtcClock";
import { JOB_LISTINGS, JOB_PAGINATION, type JobListing } from "@/lib/jobs-data";
import { cn } from "@/lib/utils/cn-util";

const TOTAL_CANDIDATES = JOB_LISTINGS.reduce((sum, job) => sum + job.totalApplicants, 0);
const TOTAL_NEW_THIS_WEEK = JOB_LISTINGS.reduce((sum, job) => sum + job.newThisWeek, 0);

export default function WorkbenchPage() {
  const utcTime = useUtcClock();
  const heroStatsRef = useProximityScale<HTMLDListElement>({
    axis: "x",
    maxBrightness: 1.0375,
    maxScale: 1.02,
  });
  const [liveAgents, setLiveAgents] = useState(3);

  // Count-up choreography: numbers climb as the hero section reveals.
  const candidatesCount = useCountUp(TOTAL_CANDIDATES, { delayMs: 150 });
  const weekCount = useCountUp(TOTAL_NEW_THIS_WEEK, { delayMs: 250 });
  const hoursSavedCount = useCountUp(2102, { delayMs: 350 });
  const avgShortlistHours = useCountUp(58, { delayMs: 450 });

  // Sync indicator: spin for 15s on load and again every 120s.
  const [isSyncing, setIsSyncing] = useState(true);
  useEffect(() => {
    let stopTimer: ReturnType<typeof setTimeout>;
    const startSpin = () => {
      setIsSyncing(true);
      stopTimer = globalThis.setTimeout(() => setIsSyncing(false), 15_000);
    };
    stopTimer = globalThis.setTimeout(() => setIsSyncing(false), 15_000);
    const intervalId = globalThis.setInterval(startSpin, 120_000);
    return () => {
      globalThis.clearInterval(intervalId);
      globalThis.clearTimeout(stopTimer);
    };
  }, []);

  // Drift the live-agent count randomly every 14-35s for ops-console feel.
  useEffect(() => {
    let timer: ReturnType<typeof setTimeout>;
    const schedule = () => {
      timer = globalThis.setTimeout(
        () => {
          setLiveAgents((prev) => {
            let next = prev;
            while (next === prev) {
              next = 2 + Math.floor(Math.random() * 5);
            }
            return next;
          });
          schedule();
        },
        14_000 + Math.random() * 21_000
      );
    };
    schedule();
    return () => globalThis.clearTimeout(timer);
  }, []);

  return (
    <div className="min-h-screen bg-kpmgGray6">
      <WorkbenchHeader />

      <AnimateSectionOnReveal index={0}>
        <div className="bg-gradient-to-r from-kpmgBlue via-kpmgCobaltBlue to-kpmgPacificBlue px-6 py-10 sm:px-0">
          <div className="mx-auto flex max-w-5xl flex-wrap items-end justify-between gap-8">
            <div>
              <h1 className="font-semibold text-2xl text-white">Open requisitions</h1>
              <p className="mt-1 flex items-center gap-2 text-sm text-white/60">
                <Spinner
                  className={cn("text-white/60", !isSyncing && "animate-none")}
                  size="sm"
                  speed="slow"
                />
                Intake pipeline &middot; last sync 2 min ago
              </p>
            </div>
            <dl className="flex flex-wrap items-end gap-8" ref={heroStatsRef}>
              <HeroStat label="Candidates" value={Math.round(candidatesCount).toLocaleString()} />
              <HeroStat label="This Week" value={String(Math.round(weekCount))} />
              <HeroStat
                label="Time Saved"
                value={`${Math.round(hoursSavedCount).toLocaleString()}h`}
              />
              <HeroStat
                label="Live Agents"
                value={
                  <RandomizedText delay={0} key={liveAgents} split="chars">
                    {String(liveAgents)}
                  </RandomizedText>
                }
              />
              <HeroStat
                label="Avg. Time-to-Shortlist"
                value={`${Math.round(avgShortlistHours)}h`}
              />
            </dl>
          </div>
        </div>
      </AnimateSectionOnReveal>

      <AnimateSectionOnReveal index={1}>
        <section className="border-kpmgGray45/60 border-b bg-background px-6 py-3 sm:px-0">
          <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-4">
            <div className="flex flex-wrap items-center gap-6 text-kpmgGray2 text-sm">
              <StatusItem color="bg-kpmgGreen" label="Pipeline healthy" />
              <StatusItem color="bg-kpmgPacificBlue" label={<LastAgentRun utcTime={utcTime} />} />
              <StatusItem color="bg-kpmgPink" label="4 candidates flagged for review" />
            </div>
            <div className="flex w-64 items-center gap-2 rounded-full border border-kpmgGray45 px-4 py-2">
              <Search aria-hidden className="size-4 text-kpmgGray3" />
              <input
                className="w-full bg-transparent text-sm outline-none placeholder:text-kpmgGray3"
                placeholder="Search"
                readOnly
              />
            </div>
          </div>
        </section>
      </AnimateSectionOnReveal>

      <AnimateSectionOnReveal index={2}>
        <main className="mx-auto max-w-5xl px-6 py-8 sm:px-0">
          <div className="mb-4 flex items-center justify-between text-sm">
            <span className="font-medium text-foreground">{JOB_PAGINATION.total} Results</span>
            <span className="flex items-center gap-2 text-kpmgGray2">
              Sort By
              <span className="flex items-center gap-1 text-foreground">
                Relevance
                <ChevronDown aria-hidden className="size-3.5" />
              </span>
            </span>
          </div>

          <div className="overflow-hidden rounded-2xl bg-background shadow-sm">
            <ul>
              {JOB_LISTINGS.map((job, index) => (
                <JobRow job={job} key={job.reqId} showDivider={index > 0} />
              ))}
            </ul>

            <footer className="flex items-center justify-end gap-8 border-kpmgGray45/60 border-t px-6 py-3 text-kpmgGray2 text-sm">
              <span className="flex items-center gap-2">
                Items per page
                <span className="flex items-center gap-1 font-medium text-foreground">
                  {JOB_PAGINATION.pageSize}
                  <ChevronDown aria-hidden className="size-4" />
                </span>
              </span>
              <span>
                {JOB_PAGINATION.rangeStart} &ndash; {JOB_PAGINATION.rangeEnd} of{" "}
                {JOB_PAGINATION.total}
              </span>
              <span className="flex items-center gap-4">
                <ChevronLeft aria-hidden className="size-5 text-kpmgGray4" />
                <ChevronRight aria-hidden className="size-5 text-kpmgGray1" />
              </span>
            </footer>
          </div>
        </main>
      </AnimateSectionOnReveal>
    </div>
  );
}

function HeroStat({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="border-white/20 border-l pl-4">
      <dt className="text-[0.65rem] text-white/60 uppercase tracking-widest">{label}</dt>
      <dd className="mt-1 font-semibold text-2xl text-white tabular-nums">{value}</dd>
    </div>
  );
}

function LastAgentRun({ utcTime }: { utcTime: string | null }) {
  const [hours, minutes] = (utcTime ?? "--:--").split(":");
  return (
    <span>
      Last agent run {hours}
      <span className="animate-[blink_1s_steps(1,end)_infinite]">:</span>
      {minutes} UTC &bull; 0 errors
    </span>
  );
}

function StatusItem({ color, label }: { color: string; label: ReactNode }) {
  return (
    <span className="flex items-center gap-2">
      <span aria-hidden className={cn("size-2 rounded-full", color)} />
      {label}
    </span>
  );
}

function JobRow({ job, showDivider }: { job: JobListing; showDivider: boolean }) {
  const locked = !job.featured;
  const router = useRouter();
  const openReview = () => {
    if (!locked) {
      router.push(`/workbench/${job.reqId}`);
    }
  };

  return (
    <li
      className={cn(
        "grid grid-cols-[2fr_repeat(3,minmax(0,9rem))_auto] items-start gap-6 px-6 py-6 transition-colors hover:bg-kpmgGray6/60",
        showDivider && "border-kpmgGray45/60 border-t",
        locked ? "cursor-not-allowed" : "cursor-pointer"
      )}
      onClick={openReview}
      onKeyDown={(event) => {
        if (event.key === "Enter") {
          openReview();
        }
      }}
    >
      <div className="flex items-start gap-3">
        <ChevronDown aria-hidden className="mt-1 size-4 shrink-0 text-kpmgGray1" />
        <div>
          <h2 className={cn("font-medium text-kpmgBlue", locked && "text-kpmgBlue/45")}>
            {job.title}
          </h2>
          <p className="mt-2 text-kpmgGray2 text-sm">Req ID: {job.reqId}</p>
        </div>
      </div>
      <JobMeta label="Candidates" value={String(job.totalApplicants)} />
      <JobMeta label="New This Week" value={`+${job.newThisWeek}`} />
      <JobMeta label="Pipeline Stage" value={job.pipelineStage} />
      <div className="flex flex-col items-stretch gap-2">
        <Button className="rounded-full px-6 hover:bg-black" disabled={locked}>
          Review Candidates
        </Button>
        <Button
          className="rounded-full px-6"
          disabled={locked}
          onClick={(event) => event.stopPropagation()}
          variant="outline"
        >
          <Sparkles aria-hidden />
          Run Screening Agent
        </Button>
      </div>
    </li>
  );
}

function JobMeta({ label, value }: { label: string; value: string }) {
  return (
    <div className="text-sm">
      <p className="text-kpmgGray3">{label}</p>
      <p className="mt-1 text-foreground">{value}</p>
    </div>
  );
}
