"use client";
export default function ErrorPage({ reset }: { reset: () => void }) {
  return (
    <section className="subpage">
      <div className="page-heading">
        <h1>The analysis could not load.</h1>
        <p>Please try loading this page again.</p>
        <button className="button" onClick={reset}>
          Try again
        </button>
      </div>
    </section>
  );
}
