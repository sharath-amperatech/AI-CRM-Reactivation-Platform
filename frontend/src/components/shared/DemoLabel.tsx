export default function DemoLabel({ label = 'Demo Data' }: { label?: string }) {
  return (
    <span className="inline-flex items-center gap-1 text-[10px] font-medium text-muted-foreground/60 uppercase tracking-wide">
      <span className="w-1.5 h-1.5 rounded-full bg-muted-foreground/40 inline-block" />
      {label}
    </span>
  )
}
