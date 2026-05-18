export function LoadingSkeleton({ rows = 4 }) {
  return (
    <div className="loading-skeleton" aria-hidden="true">
      {Array.from({ length: rows }).map((_, index) => (
        <span key={index} className="loading-skeleton-line" />
      ))}
    </div>
  );
}
