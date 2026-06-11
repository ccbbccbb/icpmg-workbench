import snapshotData from "../../data/workbench_candidate_snapshots.json";

export interface CandidateHighlight {
  label: string;
  priority: "critical" | "strong" | "supporting";
  matchedTerms: string[];
  evidence: string[];
}

export interface CandidateSnapshot {
  candidateId: string;
  candidateName: string;
  appliedJobId: string;
  recommendedJobId: string;
  recommendedRole: string;
  score: number;
  scoreBeforePenalty: number;
  reviewBand: "Strong match" | "Review" | "Partial match" | "Low alignment";
  isCrossRoleRecommendation: boolean;
  crossRoleDelta: number;
  profileImagePath: string;
  resumePath: string;
  yearsReason: string;
  titleMatches: string[];
  prototypePortfolio: string | null;
  highlights: CandidateHighlight[];
  missingCritical: string[];
  missingStrong: string[];
  riskFlags: string[];
  scoresByJob: Record<string, number>;
}

interface CandidateSnapshotPayload {
  schemaVersion: string;
  generatedFrom: {
    rankings: string;
    manifest: string;
  };
  jobs: Record<string, CandidateSnapshot[]>;
}

const CANDIDATE_SNAPSHOTS = snapshotData as CandidateSnapshotPayload;

export function getCandidatesByReqId(reqId: string): CandidateSnapshot[] {
  return CANDIDATE_SNAPSHOTS.jobs[reqId] ?? [];
}

export function getCandidateCountsByReqId(reqId: string) {
  const candidates = getCandidatesByReqId(reqId);
  return {
    total: candidates.length,
    strong: candidates.filter((candidate) => candidate.reviewBand === "Strong match").length,
    review: candidates.filter((candidate) => candidate.reviewBand === "Review").length,
    partial: candidates.filter((candidate) => candidate.reviewBand === "Partial match").length,
    low: candidates.filter((candidate) => candidate.reviewBand === "Low alignment").length,
    crossRole: candidates.filter((candidate) => candidate.isCrossRoleRecommendation).length,
    flagged: candidates.filter((candidate) => candidate.riskFlags.length > 0).length,
  };
}

export function getTopCandidateByReqId(reqId: string): CandidateSnapshot | undefined {
  return getCandidatesByReqId(reqId)[0];
}
