export interface JobListing {
  reqId: string;
  title: string;
  totalApplicants: number;
  newThisWeek: number;
  pipelineStage: "Screening" | "Shortlisting" | "Interviews" | "On Hold";
  /** The demo's featured roles — the only ones the reviewer can act on. */
  featured?: boolean;
}

export const JOB_LISTINGS: JobListing[] = [
  {
    reqId: "32538",
    title: "AI Builder - Senior Consultant",
    totalApplicants: 175,
    newThisWeek: 23,
    pipelineStage: "Screening",
    featured: true,
  },
  {
    reqId: "32544",
    title: "AI Builder - Manager",
    totalApplicants: 93,
    newThisWeek: 11,
    pipelineStage: "Screening",
    featured: true,
  },
  {
    reqId: "30989",
    title: "Data & AI Alliance Executive",
    totalApplicants: 42,
    newThisWeek: 4,
    pipelineStage: "Shortlisting",
    featured: true,
  },
  {
    reqId: "32088",
    title: "Manager, Data Analytics & Automation - AI Strategy",
    totalApplicants: 128,
    newThisWeek: 9,
    pipelineStage: "Interviews",
  },
  {
    reqId: "31963",
    title: "Manager, ML/AI Engineer, Data & AI",
    totalApplicants: 211,
    newThisWeek: 17,
    pipelineStage: "Screening",
  },
  {
    reqId: "31962",
    title: "Senior Consultant, ML/AI Engineer, Data & AI",
    totalApplicants: 246,
    newThisWeek: 21,
    pipelineStage: "Screening",
  },
  {
    reqId: "32101",
    title: "Senior Consultant, Data Analytics & Automation - AI Modernization",
    totalApplicants: 154,
    newThisWeek: 12,
    pipelineStage: "Shortlisting",
  },
  {
    reqId: "32359",
    title: "Senior Manager, Data Analytics & Automation-AI Strategy Modernization",
    totalApplicants: 87,
    newThisWeek: 6,
    pipelineStage: "Interviews",
  },
  {
    reqId: "32464",
    title: "Senior Manager, Data Platform(s) Architect, Data & AI",
    totalApplicants: 119,
    newThisWeek: 8,
    pipelineStage: "On Hold",
  },
  // TODO: replace with the remaining listing from the reference photo
  {
    reqId: "31210",
    title: "Director, Lighthouse - Data, AI & Emerging Technologies",
    totalApplicants: 64,
    newThisWeek: 3,
    pipelineStage: "On Hold",
  },
];

export function getJobByReqId(reqId: string): JobListing | undefined {
  return JOB_LISTINGS.find((job) => job.reqId === reqId);
}

/** Fake pagination totals shown in the (inactive) footer, per the iCIMS reference. */
export const JOB_PAGINATION = {
  pageSize: 10,
  rangeStart: 1,
  rangeEnd: 10,
  total: 411,
};
