import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { useParams } from "react-router-dom";

import { api } from "../../lib/api";
import { useToast } from "../../components/ToastProvider";

type ReportSummary = {
  status?: string;
  legal_name?: string;
  document?: string;
  snapshot_at?: string;
  source?: string;
};

export default function TargetDetailPage() {
  const { id } = useParams();
  const targetId = Number(id);
  const queryClient = useQueryClient();
  const [checkError, setCheckError] = useState<string | null>(null);
  const { showToast } = useToast();

  const reportQuery = useQuery({
    queryKey: ["reports", targetId],
    queryFn: () => api.getLatestReport(targetId),
    enabled: Number.isFinite(targetId),
    retry: false,
  });

  const checkMutation = useMutation({
    mutationFn: () => api.runCheck(targetId),
    onSuccess: () => {
      setCheckError(null);
      queryClient.invalidateQueries({ queryKey: ["reports", targetId] });
      showToast({ tone: "success", message: "Verificação executada." });
    },
    onError: (err) => {
      setCheckError(err instanceof Error ? err.message : "Falha ao gerar relatorio");
      showToast({ tone: "error", message: "Falha ao executar verificação." });
    },
  });

  const summary: ReportSummary | undefined = useMemo(
    () => reportQuery.data?.summary_json as ReportSummary | undefined,
    [reportQuery.data]
  );

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-cloud/50">Target</p>
          <h1 className="mt-3 font-display text-3xl font-semibold text-white">Consulta e relatório</h1>
        </div>
        <button
          onClick={() => checkMutation.mutate()}
          className="rounded-full bg-accent px-5 py-2 text-sm font-semibold text-ink shadow-lg"
          disabled={!Number.isFinite(targetId) || checkMutation.isPending}
        >
          {checkMutation.isPending ? "Executando..." : "Rodar verificação"}
        </button>
      </header>

      <section className="glass-panel p-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-lg font-semibold text-white">Relatório atual</h2>
          {summary?.status ? (
            <span className="pill border-white/20 bg-white/5 text-white">
              Status: {summary.status}
            </span>
          ) : null}
        </div>

        {checkError ? (
          <div className="mt-4 rounded-2xl border border-red-400/40 bg-red-500/10 px-4 py-3 text-xs text-red-200">
            {checkError}
          </div>
        ) : null}

        {reportQuery.isLoading ? (
          <div className="mt-4 space-y-2">
            <div className="h-4 w-1/3 animate-pulse rounded bg-white/10" />
            <div className="h-32 animate-pulse rounded-xl bg-white/5" />
          </div>
        ) : summary ? (
          <div className="mt-4 space-y-3">
            <div className="grid gap-3 md:grid-cols-2">
              <DetailCard label="Razão social" value={summary.legal_name || "—"} />
              <DetailCard label="CNPJ" value={summary.document || "—"} />
              <DetailCard label="Fonte" value={summary.source || "—"} />
              <DetailCard label="Snapshot em" value={summary.snapshot_at || "—"} />
            </div>
            <div className="rounded-2xl border border-white/10 bg-black/40 p-4">
              <p className="text-xs uppercase text-cloud/50">Detalhes brutos</p>
              <pre className="mt-2 max-h-[320px] overflow-auto whitespace-pre-wrap text-xs text-cloud">
                {JSON.stringify(reportQuery.data?.summary_json, null, 2)}
              </pre>
            </div>
          </div>
        ) : reportQuery.isError ? (
          <p className="mt-4 text-sm text-red-200">
            {reportQuery.error instanceof Error
              ? reportQuery.error.message
              : "Falha ao carregar relatorio"}
          </p>
        ) : (
          <p className="mt-4 text-sm text-cloud/70">Nenhum relatorio disponivel ainda.</p>
        )}
      </section>
    </div>
  );
}

function DetailCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
      <p className="text-xs uppercase tracking-[0.2em] text-cloud/60">{label}</p>
      <p className="mt-2 text-sm text-white">{value}</p>
    </div>
  );
}
