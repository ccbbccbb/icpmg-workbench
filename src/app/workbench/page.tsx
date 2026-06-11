"use client";

import {
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  MapPin,
  Search,
  SlidersHorizontal,
  Sparkles,
} from "lucide-react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { WorkbenchHeader } from "@/components/workbench-header";
import { JOB_LISTINGS, JOB_PAGINATION, type JobListing } from "@/lib/jobs-data";
import { cn } from "@/lib/utils/cn-util";

const TOTAL_CANDIDATES = JOB_LISTINGS.reduce((sum, job) => sum + job.totalApplicants, 0);
const TOTAL_NEW_THIS_WEEK = JOB_LISTINGS.reduce((sum, job) => sum + job.newThisWeek, 0);

export default function WorkbenchPage() {
  return (
    <div className="min-h-screen bg-kpmgGray6">
      <WorkbenchHeader />

      <div className="bg-gradient-to-r from-kpmgBlue via-kpmgCobaltBlue to-kpmgPacificBlue px-6 py-10">
        <div className="mx-auto flex max-w-5xl flex-wrap items-end justify-between gap-8">
          <div>
            <h1 className="font-semibold text-2xl text-white">Open requisitions</h1>
            <p className="mt-1 text-sm text-white/60">
              Intake pipeline &middot; last sync 2 min ago
            </p>
          </div>
          <dl className="flex flex-wrap items-end gap-8">
            <HeroStat label="Total Candidates" value={TOTAL_CANDIDATES.toLocaleString()} />
            <HeroStat label="New This Week" value={`+${TOTAL_NEW_THIS_WEEK}`} />
            <HeroStat label="CVs Parsed" value="9,482" />
            <HeroStat label="Agents Active" value="3" />
            <HeroStat label="Avg. Time-to-Shortlist" value="2.4d" />
          </dl>
        </div>
      </div>

      <section className="border-kpmgGray45/60 border-b bg-background px-6 py-6">
        <div className="mx-auto flex max-w-5xl flex-wrap items-center gap-3">
          <div className="flex min-w-64 flex-1 items-center gap-2 rounded-full border border-kpmgGray45 px-4 py-2.5">
            <Search aria-hidden className="size-4 text-kpmgGray3" />
            <input
              className="w-full bg-transparent text-sm outline-none placeholder:text-kpmgGray3"
              placeholder="Search roles"
              readOnly
              value="ai"
            />
          </div>
          <div className="flex min-w-56 items-center gap-2 rounded-full border border-kpmgGray45 px-4 py-2.5">
            <MapPin aria-hidden className="size-4 text-kpmgGray3" />
            <input
              className="w-full bg-transparent text-sm outline-none placeholder:text-kpmgGray3"
              placeholder="Search Location"
              readOnly
            />
            <span className="flex shrink-0 items-center gap-1 text-kpmgGray2 text-sm">
              10 KM
              <ChevronDown aria-hidden className="size-3.5" />
            </span>
          </div>
          <Button className="rounded-full" size="icon" variant="default">
            <Search aria-hidden />
          </Button>
        </div>

        <div className="mx-auto mt-4 flex max-w-5xl items-center gap-5 text-kpmgGray1 text-sm">
          <span className="flex items-center gap-2">
            <SlidersHorizontal aria-hidden className="size-4" />
            Filters
          </span>
          <FilterChip label="Locations" />
          <FilterChip label="Career Areas" />
          <FilterChip label="Position Type" />
        </div>
      </section>

      <main className="mx-auto max-w-5xl px-6 py-8">
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
    </div>
  );
}

function HeroStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="border-white/20 border-l pl-4">
      <dt className="text-[0.65rem] text-white/60 uppercase tracking-widest">{label}</dt>
      <dd className="mt-1 font-semibold text-2xl text-white tabular-nums">{value}</dd>
    </div>
  );
}

function FilterChip({ label }: { label: string }) {
  return (
    <span className="flex items-center gap-1.5">
      {label}
      <ChevronDown aria-hidden className="size-3.5" />
    </span>
  );
}

function JobRow({ job, showDivider }: { job: JobListing; showDivider: boolean }) {
  const locked = !job.featured;
  const router = useRouter();

  return (
    <li
      className={cn(
        "grid grid-cols-[1.4fr_repeat(3,minmax(0,10rem))_auto] items-start gap-6 px-6 py-6 transition-colors hover:bg-kpmgGray6/60",
        showDivider && "border-kpmgGray45/60 border-t",
        locked && "cursor-not-allowed"
      )}
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
      <JobMeta label="Total Applicants" value={String(job.totalApplicants)} />
      <JobMeta label="New This Week" value={`+${job.newThisWeek}`} />
      <JobMeta label="Pipeline Stage" value={job.pipelineStage} />
      <div className="flex flex-col items-stretch gap-2">
        <Button
          className="rounded-full px-6 hover:bg-black"
          disabled={locked}
          onClick={() => router.push(`/workbench/${job.reqId}`)}
        >
          Analyze Candidates
        </Button>
        <Button className="rounded-full px-6" disabled={locked} variant="outline">
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
