"use client";

import {
  AlertTriangle,
  ArrowLeft,
  BriefcaseBusiness,
  CheckCircle2,
  ExternalLink,
  Mail,
  Phone,
  Search,
  Sparkles,
  UserRound,
} from "lucide-react";
import Image from "next/image";
import { notFound, useParams, useRouter } from "next/navigation";
import { useMemo, useState } from "react";
import { AnimateSectionOnReveal } from "@/components/animate-section-on-reveal";
import { LinkedinIcon } from "@/components/icons/linkedin-icon";
import { Button } from "@/components/ui/button";
import { WorkbenchHeader } from "@/components/workbench-header";
import { useProximityScale } from "@/hooks/useProximityScale";
import {
  type CandidateSnapshot,
  getCandidateCountsByReqId,
  getCandidatesByReqId,
} from "@/lib/candidate-snapshots";
import { getJobByReqId, JOB_LISTINGS } from "@/lib/jobs-data";
import { cn } from "@/lib/utils/cn-util";

const FEATURED_JOB_IDS = new Set(["32538", "32544", "30989"]);
const CANDIDATE_IMAGE_VERSION = "seed-refresh-2026-06-11";

function candidateImageSrc(profileImagePath: string) {
  return `/candidates/${profileImagePath}?v=${CANDIDATE_IMAGE_VERSION}`;
}

export default function RequisitionPage() {
  const { reqId } = useParams<{ reqId: string }>();
  const router = useRouter();
  const job = getJobByReqId(reqId);
  const candidates = useMemo(() => getCandidatesByReqId(reqId), [reqId]);
  const counts = useMemo(() => getCandidateCountsByReqId(reqId), [reqId]);
  const [selectedCandidateId, setSelectedCandidateId] = useState(candidates[0]?.candidateId);

  if (!(job?.featured && FEATURED_JOB_IDS.has(reqId))) {
    notFound();
  }

  const selectedCandidate =
    candidates.find((candidate) => candidate.candidateId === selectedCandidateId) ?? candidates[0];
  const shortlistCandidates = candidates.filter(
    (candidate) => candidate.reviewBand === "Strong match"
  );

  return (
    <div className="min-h-screen bg-kpmgGray6">
      <WorkbenchHeader />

      <AnimateSectionOnReveal index={0}>
        <div className="bg-gradient-to-r from-kpmgBlue via-kpmgCobaltBlue to-kpmgPacificBlue px-6 py-8">
          <div className="mx-auto max-w-7xl">
            <Button
              className="mb-7 border border-white/20 bg-kpmgBlue/50 text-white hover:bg-kpmgBlue/65 hover:text-white"
              onClick={() => router.push("/workbench")}
              size="sm"
              variant="ghost"
            >
              <ArrowLeft aria-hidden />
              Requisitions
            </Button>

            <div className="flex flex-wrap items-end justify-between gap-8">
              <div>
                <h1 className="font-semibold text-2xl text-white">{job.title}</h1>
                <p className="mt-2 text-sm text-white/70">Req ID: {job.reqId}</p>
              </div>
              <dl className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                <HeroMetric label="Applicants" value={String(counts.total)} />
                <HeroMetric label="Strong" value={String(counts.strong)} />
                <HeroMetric label="Review" value={String(counts.review)} />
                <HeroMetric label="Flagged" value={String(counts.flagged)} />
              </dl>
            </div>
          </div>
        </div>
      </AnimateSectionOnReveal>

      <AnimateSectionOnReveal index={1}>
        <section className="border-kpmgGray45/60 border-b bg-background px-6 py-3">
          <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 text-sm">
            <div className="flex flex-wrap items-center gap-5 text-kpmgGray2">
              <StatusPill tone="green" value={`${shortlistCandidates.length} shortlist-ready`} />
              <StatusPill tone="blue" value={`${counts.crossRole} cross-role recommendations`} />
              <StatusPill tone="pink" value={`${counts.low} low alignment`} />
            </div>
            <div className="flex w-72 items-center gap-2 rounded-full border border-kpmgGray45 px-4 py-2">
              <Search aria-hidden className="size-4 text-kpmgGray3" />
              <input
                className="w-full bg-transparent text-sm outline-none placeholder:text-kpmgGray3"
                placeholder="Search candidates"
                readOnly
              />
            </div>
          </div>
        </section>
      </AnimateSectionOnReveal>

      <AnimateSectionOnReveal index={2}>
        <main className="mx-auto grid max-w-7xl gap-6 px-6 py-8 lg:grid-cols-[24rem_minmax(0,1fr)]">
          <CandidateRail
            candidates={candidates}
            onSelect={setSelectedCandidateId}
            selectedCandidateId={selectedCandidate?.candidateId}
          />

          {selectedCandidate ? (
            <CandidateSnapshotPanel candidate={selectedCandidate} currentReqId={job.reqId} />
          ) : (
            <EmptyState />
          )}
        </main>
      </AnimateSectionOnReveal>
    </div>
  );
}

function HeroMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-28 border-white/20 border-l pl-4">
      <dt className="text-[0.65rem] text-white/60 uppercase tracking-widest">{label}</dt>
      <dd className="mt-1 font-semibold text-2xl text-white tabular-nums">{value}</dd>
    </div>
  );
}

function StatusPill({ tone, value }: { tone: "green" | "blue" | "pink"; value: string }) {
  const color = {
    green: "bg-kpmgGreen",
    blue: "bg-kpmgPacificBlue",
    pink: "bg-kpmgPink",
  }[tone];

  return (
    <span className="flex items-center gap-2">
      <span aria-hidden className={cn("size-2 rounded-full", color)} />
      {value}
    </span>
  );
}

function CandidateRail({
  candidates,
  selectedCandidateId,
  onSelect,
}: {
  candidates: CandidateSnapshot[];
  selectedCandidateId?: string;
  onSelect: (candidateId: string) => void;
}) {
  const railRef = useProximityScale<HTMLDivElement>({
    axis: "y",
    maxBrightness: 1.0075,
    maxScale: 1.01,
    radius: 110,
    transformOrigin: "left center",
  });

  return (
    <aside className="flex min-h-0 flex-col self-stretch overflow-hidden rounded-2xl bg-background shadow-sm">
      <div className="shrink-0 border-kpmgGray45/60 border-b px-5 py-4">
        <p className="font-medium text-foreground">Ranked candidates</p>
        <p className="mt-1 text-kpmgGray2 text-sm">Sorted by applied-role match score</p>
      </div>
      <div className="relative min-h-96 flex-1">
        <div className="absolute inset-0 overflow-y-auto overflow-x-hidden" ref={railRef}>
          {candidates.map((candidate, index) => (
            <button
              className={cn(
                "flex w-full items-start gap-3 border-kpmgGray45/60 border-b px-4 py-4 text-left transition-colors hover:bg-kpmgGray6",
                selectedCandidateId === candidate.candidateId && "bg-muted"
              )}
              key={candidate.candidateId}
              onClick={() => onSelect(candidate.candidateId)}
              type="button"
            >
              <span className="mt-1 w-8 shrink-0 text-center font-semibold text-kpmgGray3 text-sm tabular-nums">
                {index + 1}
              </span>
              <Image
                alt=""
                className="size-22 rounded-full object-cover"
                height={88}
                src={candidateImageSrc(candidate.profileImagePath)}
                width={88}
              />
              <span className="min-w-0 flex-1">
                <span className="flex items-start justify-between gap-2">
                  <span className="truncate font-medium text-foreground text-sm">
                    {candidate.candidateName}
                  </span>
                  <ScoreBadge score={candidate.score} />
                </span>
                <span className="mt-1 block text-kpmgGray2 text-xs">{candidate.reviewBand}</span>
                <span className="mt-2 block truncate text-kpmgGray3 text-xs">
                  {candidate.highlights[0]?.label ?? "No strong evidence matched"}
                </span>
              </span>
            </button>
          ))}
        </div>
      </div>
    </aside>
  );
}

function CandidateSnapshotPanel({
  candidate,
  currentReqId,
}: {
  candidate: CandidateSnapshot;
  currentReqId: string;
}) {
  return (
    <section className="space-y-6">
      <div className="rounded-2xl bg-background shadow-sm">
        <div className="grid gap-x-6 gap-y-2 p-4 md:grid-cols-[auto_minmax(0,1fr)_auto]">
          <Image
            alt=""
            className="size-24 rounded-2xl object-cover"
            height={96}
            priority
            src={candidateImageSrc(candidate.profileImagePath)}
            width={96}
          />
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="font-semibold text-2xl text-foreground">{candidate.candidateName}</h2>
              <ReviewBandBadge band={candidate.reviewBand} />
            </div>
            <div className="mt-2 flex flex-wrap items-center gap-2">
              <a
                className="flex items-center gap-1 rounded-full bg-kpmgGray6 px-3 py-1 font-medium text-kpmgGray2 text-xs transition-colors hover:bg-kpmgGray5"
                href={`/candidates/${candidate.resumePath}`}
                rel="noreferrer"
                target="_blank"
              >
                <ExternalLink aria-hidden className="size-3" />
                Resume
              </a>
              <button
                className="flex cursor-pointer items-center gap-1 rounded-full bg-kpmgGray6 px-3 py-1 font-medium text-kpmgGray2 text-xs transition-colors hover:bg-kpmgGray5"
                type="button"
              >
                <LinkedinIcon className="size-3" />
                LinkedIn
              </button>
            </div>
            <p className="mt-2 text-kpmgGray2 text-sm">{candidate.yearsReason}</p>
          </div>
          <div className="flex flex-col items-stretch gap-2 md:w-44">
            <div className="flex flex-col justify-center rounded-xl bg-kpmgBlue px-4 py-3 text-center text-white">
              <p className="text-white/65 text-xs uppercase tracking-widest">Match score</p>
              <p className="mt-1 font-extrabold text-3xl tabular-nums">{candidate.score}</p>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2 md:col-span-full">
            {candidate.titleMatches.slice(0, 3).map((title) => (
              <span
                className="rounded-full bg-kpmgGray6 px-3 py-1 text-kpmgGray2 text-xs lowercase"
                key={title}
              >
                {title}
              </span>
            ))}
            {candidate.prototypePortfolio ? (
              <span className="rounded-full bg-kpmgCobaltBlue/10 px-3 py-1 text-kpmgBlue text-xs lowercase">
                Prototype portfolio
              </span>
            ) : null}
            <span className="ml-auto flex gap-2">
              <button
                aria-label="Email candidate"
                className="flex size-7 cursor-pointer items-center justify-center rounded-full bg-kpmgGray6 text-kpmgGray2 transition-colors hover:bg-kpmgGray5"
                type="button"
              >
                <Mail aria-hidden className="size-3.5" />
              </button>
              <button
                aria-label="Call candidate"
                className="flex size-7 cursor-pointer items-center justify-center rounded-full bg-kpmgGray6 text-kpmgGray2 transition-colors hover:bg-kpmgGray5"
                type="button"
              >
                <Phone aria-hidden className="size-3.5" />
              </button>
            </span>
          </div>
        </div>

        {candidate.isCrossRoleRecommendation ? (
          <div className="border-kpmgLightPink/50 border-t bg-kpmgLightPink/10 px-6 py-3 text-kpmgGray1 text-sm">
            <AlertTriangle aria-hidden className="mr-2 inline size-4 text-kpmgPink" />
            Stronger fit detected for {candidate.recommendedRole} by {candidate.crossRoleDelta}{" "}
            points.
          </div>
        ) : null}
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <ScoreComparison candidate={candidate} currentReqId={currentReqId} />
        <GapsPanel candidate={candidate} />
      </div>

      <EvidencePanel candidate={candidate} />
    </section>
  );
}

function EvidencePanel({ candidate }: { candidate: CandidateSnapshot }) {
  return (
    <div className="rounded-2xl bg-background p-4 shadow-sm">
      <div className="mb-4 flex items-center gap-2">
        <Sparkles aria-hidden className="size-5 text-kpmgCobaltBlue" />
        <h3 className="font-semibold text-foreground">Evidence highlights</h3>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        {candidate.highlights.map((highlight) => (
          <article className="rounded-xl border border-kpmgGray45/70 p-4" key={highlight.label}>
            <div className="flex items-center gap-2">
              <CheckCircle2 aria-hidden className="size-4 shrink-0 text-kpmgGreen" />
              <span className="font-medium text-kpmgGray3 text-xs capitalize">
                {highlight.priority}
              </span>
            </div>
            <p className="mt-1 font-medium text-foreground text-sm">{highlight.label}</p>
            <p className="mt-3 line-clamp-3 text-kpmgGray2 text-sm">
              {highlight.evidence[0] ?? highlight.matchedTerms.join(", ")}
            </p>
            <div className="mt-3 flex flex-wrap gap-1.5">
              {highlight.matchedTerms.slice(0, 4).map((term) => (
                <span
                  className="rounded-full bg-kpmgGray6 px-2 py-1 text-kpmgGray2 text-xs"
                  key={term}
                >
                  {term}
                </span>
              ))}
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}

function GapsPanel({ candidate }: { candidate: CandidateSnapshot }) {
  const hasGaps =
    candidate.missingCritical.length > 0 ||
    candidate.missingStrong.length > 0 ||
    candidate.riskFlags.length > 0;

  return (
    <div className="rounded-2xl bg-background p-4 shadow-sm">
      <div className="mb-4 flex items-center gap-2">
        <AlertTriangle aria-hidden className="size-5 text-kpmgPink" />
        <h3 className="font-semibold text-foreground">Gaps and flags</h3>
      </div>
      {hasGaps ? (
        <div className="grid gap-4 md:grid-cols-3">
          <GapList items={candidate.missingCritical} label="Missing critical" />
          <GapList items={candidate.missingStrong} label="Missing strong" />
          <GapList items={candidate.riskFlags} label="Risk flags" />
        </div>
      ) : (
        <p className="text-kpmgGray2 text-sm">No critical gaps or risk flags surfaced.</p>
      )}
    </div>
  );
}

function GapList({ label, items }: { label: string; items: string[] }) {
  return (
    <div>
      <p className="font-medium text-foreground text-sm">{label}</p>
      {items.length > 0 ? (
        <ul className="mt-2 space-y-2">
          {items.slice(0, 5).map((item) => (
            <li className="text-kpmgGray2 text-sm" key={item}>
              {item}
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-2 text-kpmgGray3 text-sm">None</p>
      )}
    </div>
  );
}

function ScoreComparison({
  candidate,
  currentReqId,
}: {
  candidate: CandidateSnapshot;
  currentReqId: string;
}) {
  // Only the requisition being reviewed; other roles stay out of this view.
  const scores = Object.entries(candidate.scoresByJob).filter(([jobId]) => jobId === currentReqId);

  return (
    <aside className="rounded-2xl bg-background p-4 shadow-sm">
      <div className="mb-4 flex items-center gap-2">
        <BriefcaseBusiness aria-hidden className="size-5 text-kpmgCobaltBlue" />
        <h3 className="font-semibold text-foreground">Role fit</h3>
      </div>
      <div className="space-y-4">
        {scores.map(([jobId, score]) => {
          const job = JOB_LISTINGS.find((listing) => listing.reqId === jobId);
          return (
            <div key={jobId}>
              <div className="mb-1 flex items-center justify-between gap-3 text-sm">
                <span className="font-medium text-foreground">{job?.title ?? jobId}</span>
                <span className="text-kpmgGray2 tabular-nums">{score}</span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-kpmgGray5">
                <div
                  className={cn(
                    "h-full rounded-full",
                    jobId === currentReqId ? "bg-kpmgBlue" : "bg-kpmgPacificBlue"
                  )}
                  style={{ width: `${Math.min(100, Math.max(0, score))}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </aside>
  );
}

function ScoreBadge({ score }: { score: number }) {
  return (
    <span
      className={cn(
        "rounded-full px-2 py-0.5 font-medium text-xs tabular-nums",
        score >= 85 && "bg-kpmgGreen/10 text-kpmgGreen",
        score < 85 && score >= 65 && "bg-kpmgPacificBlue/10 text-kpmgBlue",
        score < 65 && score >= 40 && "bg-kpmgPurple/10 text-kpmgPurple",
        score < 40 && "bg-kpmgGray6 text-kpmgGray2"
      )}
    >
      {score}
    </span>
  );
}

function ReviewBandBadge({ band }: { band: CandidateSnapshot["reviewBand"] }) {
  return (
    <span
      className={cn(
        "rounded-full px-3 py-1 font-medium text-xs",
        band === "Strong match" && "bg-kpmgGreen/10 text-kpmgGreen",
        band === "Review" && "bg-kpmgPacificBlue/10 text-kpmgBlue",
        band === "Partial match" && "bg-kpmgPurple/10 text-kpmgPurple",
        band === "Low alignment" && "bg-kpmgGray6 text-kpmgGray2"
      )}
    >
      {band}
    </span>
  );
}

function EmptyState() {
  return (
    <div className="flex min-h-96 items-center justify-center rounded-2xl bg-background shadow-sm">
      <div className="text-center">
        <UserRound aria-hidden className="mx-auto size-8 text-kpmgGray3" />
        <p className="mt-3 text-kpmgGray2 text-sm">No candidates found for this requisition.</p>
      </div>
    </div>
  );
}
