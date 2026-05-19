export function LoadingSkeleton({ rows = 4 }) {
  return (
    <div className="loading-skeleton" role="status" aria-live="polite" aria-label="Loading content">
      {Array.from({ length: rows }).map((_, index) => (
        <span key={index} className="loading-skeleton-line" />
      ))}
    </div>
  );
}
