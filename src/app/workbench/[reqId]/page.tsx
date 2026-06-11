"use client";

import { notFound, useParams } from "next/navigation";
import { WorkbenchHeader } from "@/components/workbench-header";
import { getJobByReqId } from "@/lib/jobs-data";

export default function RequisitionPage() {
  const { reqId } = useParams<{ reqId: string }>();
  const job = getJobByReqId(reqId);

  if (!job?.featured) {
    notFound();
  }

  return (
    <div className="min-h-screen bg-kpmgGray6">
      <WorkbenchHeader />

      <div className="bg-gradient-to-r from-kpmgBlue via-kpmgCobaltBlue to-kpmgPacificBlue px-6 py-12">
        <div className="mx-auto max-w-5xl">
          <h1 className="font-semibold text-2xl text-white">{job.title}</h1>
          <p className="mt-2 text-sm text-white/70">Req ID: {job.reqId}</p>
        </div>
      </div>

      <main className="mx-auto max-w-5xl px-6 py-8">
        <div className="grid grid-cols-3 gap-4">
          <StatCard label="Total Applicants" value={String(job.totalApplicants)} />
          <StatCard label="New This Week" value={`+${job.newThisWeek}`} />
          <StatCard label="Pipeline Stage" value={job.pipelineStage} />
        </div>

        <div className="mt-6 flex min-h-80 items-center justify-center rounded-2xl bg-background shadow-sm">
          <p className="text-kpmgGray3 text-sm">Candidate analysis workspace — coming soon.</p>
        </div>
      </main>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl bg-background p-6 shadow-sm">
      <p className="text-kpmgGray3 text-sm">{label}</p>
      <p className="mt-2 font-semibold text-2xl text-foreground">{value}</p>
    </div>
  );
}
