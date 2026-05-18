import { useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { ActionMenu } from "./ActionMenu";
import { EmptyState } from "./EmptyState";
import { LoadingSkeleton } from "./LoadingSkeleton";
import { SearchInput } from "./SearchInput";
import { StatusBadge } from "./StatusBadge";

const PAGE_SIZE = 6;

export function DataTable({
  title,
  description,
  rows,
  columns,
  filters = [],
  createLabel,
  createTo,
  searchPlaceholder,
  emptyState,
  rowLink,
  isLoading = false,
  sourceNote,
}) {
  const [query, setQuery] = useState("");
  const [filterValue, setFilterValue] = useState(filters[0]?.value ?? "all");
  const [sortValue, setSortValue] = useState(columns[0]?.key ?? "");
  const [page, setPage] = useState(1);

  const filteredRows = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();

    return rows
      .filter((row) => {
        if (filterValue === "all") {
          return true;
        }

        return String(row.status ?? row.type ?? "").toLowerCase() === filterValue.toLowerCase();
      })
      .filter((row) =>
        normalizedQuery
          ? Object.values(row).some((value) => String(value).toLowerCase().includes(normalizedQuery))
          : true,
      )
      .sort((left, right) => String(left[sortValue] ?? "").localeCompare(String(right[sortValue] ?? "")));
  }, [filterValue, query, rows, sortValue]);

  const totalPages = Math.max(1, Math.ceil(filteredRows.length / PAGE_SIZE));
  const currentPage = Math.min(page, totalPages);
  const visibleRows = filteredRows.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE);

  return (
    <section className="table-shell">
      <header className="table-header">
        <div>
          <h2>{title}</h2>
          {description ? <p>{description}</p> : null}
          {sourceNote ? <span className="helper-note">{sourceNote}</span> : null}
        </div>

        <div className="table-header-actions">
          {createLabel && createTo ? (
            <Link className="button button-primary" to={createTo}>
              {createLabel}
            </Link>
          ) : null}
        </div>
      </header>

      <div className="table-toolbar">
        {filters.length ? (
          <select value={filterValue} onChange={(event) => setFilterValue(event.target.value)}>
            {filters.map((filter) => (
              <option key={filter.value} value={filter.value}>
                {filter.label}
              </option>
            ))}
          </select>
        ) : null}

        <SearchInput
          value={query}
          onChange={(event) => {
            setQuery(event.target.value);
            setPage(1);
          }}
          placeholder={searchPlaceholder}
        />

        <select value={sortValue} onChange={(event) => setSortValue(event.target.value)}>
          {columns.map((column) => (
            <option key={column.key} value={column.key}>
              Sort by {column.label}
            </option>
          ))}
        </select>
      </div>

      {isLoading ? (
        <LoadingSkeleton rows={7} />
      ) : filteredRows.length ? (
        <>
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  {columns.map((column) => (
                    <th key={column.key}>{column.label}</th>
                  ))}
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {visibleRows.map((row) => (
                  <tr key={row.id}>
                    {columns.map((column) => (
                      <td key={column.key}>
                        {column.key === "status" ? (
                          <StatusBadge status={row[column.key]} />
                        ) : column.render ? (
                          column.render(row[column.key], row)
                        ) : rowLink && column.key === columns[0].key ? (
                          <Link className="row-link" to={rowLink(row)}>
                            {row[column.key]}
                          </Link>
                        ) : (
                          row[column.key]
                        )}
                      </td>
                    ))}
                    <td>
                      <ActionMenu
                        items={[
                          ...(rowLink ? [{ label: "View details", to: rowLink(row) }] : []),
                          ...(createTo ? [{ label: "Create similar", to: createTo }] : []),
                        ]}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="table-pagination">
            <span>
              Page {currentPage} of {totalPages}
            </span>
            <div className="pagination-actions">
              <button type="button" onClick={() => setPage((value) => Math.max(1, value - 1))}>
                Previous
              </button>
              <button type="button" onClick={() => setPage((value) => Math.min(totalPages, value + 1))}>
                Next
              </button>
            </div>
          </div>
        </>
      ) : (
        <EmptyState {...emptyState} />
      )}
    </section>
  );
}
