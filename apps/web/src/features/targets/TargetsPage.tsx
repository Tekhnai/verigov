import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { api } from "../../lib/api";

export default function TargetsPage() {
  const queryClient = useQueryClient();
  const [document, setDocument] = useState("");
  const [nameHint, setNameHint] = useState("");

  const targetsQuery = useQuery({
    queryKey: ["targets"],
    queryFn: api.listTargets,
  });

  const createMutation = useMutation({
    mutationFn: () => api.createTarget(document, nameHint || undefined),
    onSuccess: () => {
      setDocument("");
      setNameHint("");
      queryClient.invalidateQueries({ queryKey: ["targets"] });
    },
  });

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-cloud/50">Targets</p>
          <h1 className="mt-3 font-display text-3xl font-semibold text-white">Empresas alvo</h1>
        </div>
        <div className="rounded-full bg-white/10 px-4 py-2 text-xs text-cloud/60">
          Multi-tenant ativo
        </div>
      </header>

      <section className="rounded-3xl bg-white/5 p-6">
        <h2 className="text-lg font-semibold text-white">Cadastrar novo CNPJ</h2>
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
            className="rounded-xl bg-accent px-4 py-3 text-sm font-semibold text-ink"
            disabled={!document || createMutation.isPending}
          >
            Criar
          </button>
        </div>
      </section>

      <section className="rounded-3xl bg-white/5 p-6">
        <h2 className="text-lg font-semibold text-white">Lista de targets</h2>
        {targetsQuery.isLoading ? (
          <p className="mt-4 text-sm text-cloud/70">Carregando...</p>
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
          <p className="mt-4 text-sm text-cloud/70">Nenhum target cadastrado ainda.</p>
        )}
      </section>
    </div>
  );
}
