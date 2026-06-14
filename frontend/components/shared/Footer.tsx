export function Footer() {
  return (
    <footer className="border-t bg-muted/50 py-8">
      <div className="mx-auto max-w-6xl px-4">
        <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
          <div>
            <span className="font-bold text-amber-600">NyayaSetu</span>
            <p className="text-xs text-muted-foreground">
              Legal intelligence grounded in BNS, BNSS & BSA
            </p>
          </div>
          <p className="text-xs text-muted-foreground">
            NyayaSetu is not a law firm and does not provide legal advice. All
            information is for educational purposes only.
          </p>
        </div>
      </div>
    </footer>
  );
}
