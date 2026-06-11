import Image from "next/image";

export function WorkbenchHeader() {
  return (
    <header className="flex items-center gap-3 bg-background px-6 py-3">
      <Image alt="KPMG" height={28} priority src="/assets/kpmg-blue.svg" width={70} />
      <span className="font-semibold text-foreground text-lg">
        iCPMG Workbench
        <sup className="ml-1 font-normal text-kpmgCobaltBlue text-xs uppercase tracking-wide">
          alpha
        </sup>
      </span>
    </header>
  );
}
