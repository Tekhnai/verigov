const kpis = [
  { label: "Consultas hoje", value: "0", hint: "Checks de CNPJ executados" },
  { label: "Targets ativos", value: "0", hint: "Empresas monitoradas" },
  { label: "Checks com alerta", value: "0", hint: "Falhas ou inconsistências" },
];

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-cloud/50">Dashboard</p>
          <h1 className="mt-3 font-display text-4xl font-semibold text-white">
            Painel de confiança
          </h1>
          <p className="mt-2 text-sm text-cloud/70">
            Acompanhe sessões, consultas e status em tempo real para seu tenant.
          </p>
        </div>
      </header>

      <section className="grid gap-4 md:grid-cols-3">
        {kpis.map((kpi) => (
          <div key={kpi.label} className="glass-panel p-5">
            <p className="text-xs uppercase tracking-[0.2em] text-cloud/60">{kpi.label}</p>
            <p className="mt-3 text-3xl font-semibold text-white">{kpi.value}</p>
            <p className="mt-2 text-xs text-cloud/60">{kpi.hint}</p>
          </div>
        ))}
      </section>

      <section className="glass-panel p-6">
        <h2 className="text-lg font-semibold text-white">Próximos passos</h2>
        <p className="mt-2 text-sm text-cloud/70">
          Cadastre um CNPJ, execute o check e visualize o relatório. Configure alertas e integrações em
          seguida para manter sua operação segura.
        </p>
      </section>
    </div>
  );
}
