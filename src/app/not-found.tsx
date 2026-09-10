import Link from "next/link";
export default function NotFound() {
  return (
    <section className="subpage">
      <div className="page-heading">
        <div className="eyebrow">Page not found</div>
        <h1>This one is out of bounds.</h1>
        <p>
          The game or page at this address is not available. The current slate
          is a good place to start.
        </p>
        <Link className="button" href="/">
          Back to the slate
        </Link>
      </div>
    </section>
  );
}
