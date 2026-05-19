import { useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { ActionMenu } from "./ActionMenu";
import { EmptyState } from "./EmptyState";
import { LoadingSkeleton } from "./LoadingSkeleton";
import { SearchInput } from "./SearchInput";
import { StatusBadge } from "./StatusBadge";
import { formatCurrency, formatDate, formatDateTime } from "../lib/format";

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
  error,
  onRetry,
  query: controlledQuery,
  onQueryChange,
  filterValue: controlledFilterValue,
  onFilterChange,
  sortValue: controlledSortValue,
  onSortChange,
  page: controlledPage,
  onPageChange,
  totalCount,
  pageSize = PAGE_SIZE,
  serverSide = false,
}) {
  const [query, setQuery] = useState("");
  const [filterValue, setFilterValue] = useState(filters[0]?.value ?? "all");
  const [sortValue, setSortValue] = useState(columns[0]?.key ?? "");
  const [page, setPage] = useState(1);
  const effectiveQuery = controlledQuery ?? query;
  const effectiveFilterValue = controlledFilterValue ?? filterValue;
  const effectiveSortValue = controlledSortValue ?? sortValue;
  const effectivePage = controlledPage ?? page;

  const processedRows = useMemo(() => {
    const normalizedQuery = effectiveQuery.trim().toLowerCase();

    const nextRows = rows
      .filter((row) => {
        if (serverSide || effectiveFilterValue === "all") {
          return true;
        }

        return String(row.status ?? row.type ?? row.transaction_type ?? "").toLowerCase() === effectiveFilterValue.toLowerCase();
      })
      .filter((row) =>
        serverSide || !normalizedQuery
          ? true
          : Object.values(row).some((value) => String(value).toLowerCase().includes(normalizedQuery))
      )
      .sort((left, right) => String(left[effectiveSortValue] ?? "").localeCompare(String(right[effectiveSortValue] ?? "")));

    return nextRows;
  }, [effectiveFilterValue, effectiveQuery, effectiveSortValue, rows, serverSide]);

  function updateQuery(value) {
    onQueryChange ? onQueryChange(value) : setQuery(value);
  }

  function updateFilter(value) {
    onFilterChange ? onFilterChange(value) : setFilterValue(value);
  }

  function updateSort(value) {
    onSortChange ? onSortChange(value) : setSortValue(value);
  }

  function updatePage(value) {
    onPageChange ? onPageChange(value) : setPage(value);
  }

  const totalPages = serverSide
    ? Math.max(1, Math.ceil((totalCount ?? rows.length) / pageSize))
    : Math.max(1, Math.ceil(processedRows.length / PAGE_SIZE));
  const currentPage = Math.min(effectivePage, totalPages);
  const visibleRows = serverSide
    ? processedRows
    : processedRows.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE);

  function renderCell(column, row) {
    const value = row[column.key];
    const detailLink = rowLink ? rowLink(row.id, row) : null;
    if (column.kind === "status") {
      return <StatusBadge value={value} />;
    }
    if (column.kind === "boolean") {
      return value ? "Yes" : "No";
    }
    if (column.kind === "currency") {
      return formatCurrency(value);
    }
    if (column.kind === "date") {
      return String(value ?? "").includes("T") ? formatDateTime(value) : formatDate(value);
    }
    if (column.render) {
      return column.render(value, row);
    }
    if (detailLink && column.key === columns[0].key) {
      return (
        <Link className="row-link" to={detailLink}>
          {value}
        </Link>
      );
    }
    return value ?? "—";
  }

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
          <select
            className="field-input compact-field"
            value={effectiveFilterValue}
            onChange={(event) => {
              updateFilter(event.target.value);
              updatePage(1);
            }}
          >
            {filters.map((filter) => (
              <option key={filter.value} value={filter.value}>
                {filter.label}
              </option>
            ))}
          </select>
        ) : null}

        <SearchInput
          value={effectiveQuery}
          onChange={(event) => {
            updateQuery(event.target.value);
            updatePage(1);
          }}
          placeholder={searchPlaceholder}
        />

        <select
          className="field-input compact-field"
          value={effectiveSortValue}
          onChange={(event) => {
            updateSort(event.target.value);
            updatePage(1);
          }}
        >
          {columns.map((column) => (
            <option key={column.key} value={column.key}>
              Sort by {column.label}
            </option>
          ))}
        </select>
      </div>

      {isLoading ? (
        <LoadingSkeleton rows={7} />
      ) : error ? (
        <EmptyState
          icon="alert"
          title="Unable to load table data"
          description={error}
          actionLabel={onRetry ? "Try Again" : undefined}
          onAction={onRetry}
          actionTone="ghost"
        />
      ) : processedRows.length ? (
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
                        {renderCell(column, row)}
                      </td>
                    ))}
                    <td>
                      <ActionMenu
                        items={[
                          ...(rowLink ? [{ label: "View details", to: rowLink(row.id, row) }] : []),
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
              <button
                className="ghost-button compact-button"
                type="button"
                onClick={() => updatePage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
              >
                Previous
              </button>
              <button
                className="ghost-button compact-button"
                type="button"
                onClick={() => updatePage(Math.min(totalPages, currentPage + 1))}
                disabled={currentPage === totalPages}
              >
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
