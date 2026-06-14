import { QueryInput } from "@/components/query/QueryInput";

export default function HomePage() {
  return (
    <div className="mx-auto max-w-4xl px-4 py-16">
      <div className="mb-12 text-center">
        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
          Know Your Rights.{" "}
          <span className="text-amber-600">Instantly.</span>
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-lg text-muted-foreground">
          Describe your legal situation in plain language — Hindi, English, or
          Hinglish. NyayaSetu maps it to the exact clauses in BNS, BNSS &amp;
          BSA that apply to your case.
        </p>
      </div>

      <QueryInput />

      <div className="mt-16 grid gap-8 sm:grid-cols-3">
        <div className="text-center">
          <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-amber-100 text-amber-700">
            1
          </div>
          <h3 className="font-semibold">Describe</h3>
          <p className="mt-1 text-sm text-muted-foreground">
            Tell us what happened in your own words
          </p>
        </div>
        <div className="text-center">
          <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-amber-100 text-amber-700">
            2
          </div>
          <h3 className="font-semibold">Analyze</h3>
          <p className="mt-1 text-sm text-muted-foreground">
            AI identifies relevant legal provisions
          </p>
        </div>
        <div className="text-center">
          <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-amber-100 text-amber-700">
            3
          </div>
          <h3 className="font-semibold">Understand</h3>
          <p className="mt-1 text-sm text-muted-foreground">
            Get plain-language explanations of your rights
          </p>
        </div>
      </div>
    </div>
  );
}
