export function FormRow({ children, columns = 2 }) {
  return (
    <div className={`form-row columns-${columns}`}>
      {children}
    </div>
  );
}
