const kpis = [
  { label: "Consultas hoje", value: "0" },
  { label: "Targets ativos", value: "0" },
  { label: "Checks com alerta", value: "0" },
];

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <header>
        <p className="text-sm uppercase tracking-[0.3em] text-cloud/50">Dashboard</p>
        <h1 className="mt-3 font-display text-3xl font-semibold text-white">
          Visao geral do seu tenant
        </h1>
      </header>

      <section className="grid gap-4 md:grid-cols-3">
        {kpis.map((kpi) => (
          <div key={kpi.label} className="rounded-2xl bg-white/5 p-5 shadow-xl">
            <p className="text-xs uppercase text-cloud/50">{kpi.label}</p>
            <p className="mt-3 text-3xl font-semibold text-white">{kpi.value}</p>
          </div>
        ))}
      </section>

      <section className="rounded-3xl bg-white/5 p-6">
        <h2 className="text-lg font-semibold text-white">Proximas acoes</h2>
        <p className="mt-2 text-sm text-cloud/70">
          Crie um target e rode o primeiro check para gerar um relatorio simples.
        </p>
      </section>
    </div>
  );
}
