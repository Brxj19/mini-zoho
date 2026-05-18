import { Link } from "react-router-dom";

import { PageHeader } from "../components/PageHeader";
import { reportGroups } from "../lib/demoData";

export function ReportsPage() {
  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Analytics"
        title="Reports"
        description="Grouped report catalog for inventory, sales, purchases, and activity reporting workflows."
      />

      <div className="report-groups">
        {reportGroups.map((group) => (
          <section className="report-group-card" key={group.title}>
            <h2>{group.title}</h2>
            <div className="report-card-grid">
              {group.reports.map((report) => (
                <Link key={report.key} className="report-card" to={`/reports/${report.key}`}>
                  <strong>{report.title}</strong>
                  <p>{report.description}</p>
                  <span>Open report</span>
                </Link>
              ))}
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}
