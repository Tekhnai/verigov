import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate } from "react-router-dom";

import { api } from "../../lib/api";
import { useToast } from "../../components/ToastProvider";

export default function TargetsPage() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const [document, setDocument] = useState("");
  const [nameHint, setNameHint] = useState("");
  const [error, setError] = useState<string | null>(null);
  const { showToast } = useToast();

  const targetsQuery = useQuery({
    queryKey: ["targets"],
    queryFn: api.listTargets,
  });

  const createMutation = useMutation({
    mutationFn: () => api.createTarget(document, nameHint || undefined),
    onSuccess: async (data) => {
      setError(null);
      setDocument("");
      setNameHint("");
      queryClient.invalidateQueries({ queryKey: ["targets"] });
      try {
        await api.runCheck(data.id);
        queryClient.invalidateQueries({ queryKey: ["reports", data.id] });
        showToast({ tone: "success", message: "Target criado e verificação iniciada." });
      } catch (err) {
        setError(err instanceof Error ? err.message : "Falha ao gerar relatorio");
        showToast({ tone: "error", message: "Falha ao gerar relatorio" });
      }
      navigate(`/targets/${data.id}`);
    },
    onError: (err) => {
      setError(err instanceof Error ? err.message : "Falha ao criar target");
      showToast({ tone: "error", message: "Falha ao criar target" });
    },
  });

  const isLoadingList = targetsQuery.isLoading;
  const skeletons = useMemo(() => Array.from({ length: 3 }, (_, i) => i), []);

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-cloud/50">Targets</p>
          <h1 className="mt-3 font-display text-3xl font-semibold text-white">Empresas alvo</h1>
          <p className="text-sm text-cloud/70">Cadastre CNPJ e gere relatórios confiáveis.</p>
        </div>
        <div className="flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs text-cloud/60">
          <span className="h-2 w-2 rounded-full bg-emerald-400" /> Multi-tenant ativo
        </div>
      </header>

      <section className="glass-panel p-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-lg font-semibold text-white">Cadastrar novo CNPJ</h2>
            <p className="text-sm text-cloud/70">Validação e formatação automática.</p>
          </div>
          <div className="pill border-white/20 text-cloud/70">Segurança ativa</div>
        </div>
        {error ? (
          <div className="mt-4 rounded-2xl border border-red-400/40 bg-red-500/10 px-4 py-3 text-xs text-red-200">
            {error}
          </div>
        ) : null}
        <div className="mt-4 grid gap-3 md:grid-cols-[1.2fr_1.2fr_0.6fr]">
          <input
            className="rounded-xl border border-white/10 bg-black/40 px-4 py-3 text-sm text-white"
            placeholder="CNPJ (somente numeros)"
            value={document}
            onChange={(event) => setDocument(event.target.value)}
          />
          <input
            className="rounded-xl border border-white/10 bg-black/40 px-4 py-3 text-sm text-white"
            placeholder="Nome fantasia (opcional)"
            value={nameHint}
            onChange={(event) => setNameHint(event.target.value)}
          />
          <button
            onClick={() => createMutation.mutate()}
            className="rounded-xl bg-accent px-4 py-3 text-sm font-semibold text-ink shadow-lg"
            disabled={!document || createMutation.isPending}
          >
            {createMutation.isPending ? "Processando..." : "Criar"}
          </button>
        </div>
      </section>

      <section className="glass-panel p-6">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-white">Lista de targets</h2>
          <span className="text-xs text-cloud/60">
            {targetsQuery.data ? `${targetsQuery.data.length} registrados` : ""}
          </span>
        </div>
        {isLoadingList ? (
          <div className="mt-4 space-y-3">
            {skeletons.map((idx) => (
              <div
                key={idx}
                className="h-14 animate-pulse rounded-2xl border border-white/10 bg-white/5"
              />
            ))}
          </div>
        ) : targetsQuery.data && targetsQuery.data.length > 0 ? (
          <div className="mt-4 space-y-3">
            {targetsQuery.data.map((target) => (
              <Link
                key={target.id}
                to={`/targets/${target.id}`}
                className="flex items-center justify-between rounded-2xl border border-white/10 bg-black/30 px-4 py-3"
              >
                <div>
                  <p className="text-sm text-white">{target.document}</p>
                  <p className="text-xs text-cloud/60">{target.name_hint || "Sem nome"}</p>
                </div>
                <span className="text-xs text-cloud/50">Ver detalhes</span>
              </Link>
            ))}
          </div>
        ) : (
          <div className="mt-4 rounded-2xl border border-dashed border-white/15 bg-black/30 p-4 text-sm text-cloud/70">
            Nenhum target cadastrado ainda. Cadastre um CNPJ para iniciar um check.
          </div>
        )}
      </section>
    </div>
  );
}
