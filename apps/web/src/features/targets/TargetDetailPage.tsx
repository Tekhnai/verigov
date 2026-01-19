import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams } from "react-router-dom";

import { api } from "../../lib/api";

export default function TargetDetailPage() {
  const { id } = useParams();
  const targetId = Number(id);
  const queryClient = useQueryClient();

  const reportQuery = useQuery({
    queryKey: ["reports", targetId],
    queryFn: () => api.getLatestReport(targetId),
    enabled: Number.isFinite(targetId),
  });

  const checkMutation = useMutation({
    mutationFn: () => api.runCheck(targetId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reports", targetId] });
    },
  });

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-cloud/50">Target</p>
          <h1 className="mt-3 font-display text-3xl font-semibold text-white">Consulta e relatorio</h1>
        </div>
        <button
          onClick={() => checkMutation.mutate()}
          className="rounded-full bg-accent px-5 py-2 text-sm font-semibold text-ink"
          disabled={!Number.isFinite(targetId) || checkMutation.isPending}
        >
          Rodar verificacao
        </button>
      </header>

      <section className="rounded-3xl bg-white/5 p-6">
        <h2 className="text-lg font-semibold text-white">Relatorio atual</h2>
        {reportQuery.isLoading ? (
          <p className="mt-4 text-sm text-cloud/70">Carregando relatorio...</p>
        ) : reportQuery.data ? (
          <pre className="mt-4 whitespace-pre-wrap rounded-2xl bg-black/40 p-4 text-xs text-cloud">
            {JSON.stringify(reportQuery.data.summary_json, null, 2)}
          </pre>
        ) : (
          <p className="mt-4 text-sm text-cloud/70">Nenhum relatorio disponivel ainda.</p>
        )}
      </section>
    </div>
  );
}
