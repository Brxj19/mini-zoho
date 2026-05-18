import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import api from "../lib/api";
import { PageHeader } from "../components/PageHeader";

export function ReportsPage() {
  const [groups, setGroups] = useState([]);

  useEffect(() => {
    api.get("/app/reports/catalog").then(({ data }) => setGroups(data.groups ?? []));
  }, []);

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Analytics"
        title="Reports"
        description="Grouped report catalog connected to backend report definitions."
      />

      <div className="report-groups">
        {groups.map((group) => (
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
