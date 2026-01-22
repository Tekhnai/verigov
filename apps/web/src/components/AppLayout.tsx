import { NavLink, Outlet, useNavigate } from "react-router-dom";

import { clearTokens } from "../lib/auth";
import { useEffect, useState } from "react";
import { useToast } from "./ToastProvider";

const navItems = [
  { label: "Dashboard", to: "/dashboard" },
  { label: "Targets", to: "/targets" },
];

export default function AppLayout() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [sessionExpired, setSessionExpired] = useState(false);

  const handleLogout = () => {
    clearTokens();
    navigate("/login");
  };

  useEffect(() => {
    const listener = () => {
      setSessionExpired(true);
      showToast({ tone: "error", message: "Sessao expirada. Faça login novamente." });
    };
    window.addEventListener("session-expired", listener);
    return () => window.removeEventListener("session-expired", listener);
  }, [showToast]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0d16] via-[#0e1322] to-[#0f1a33] text-cloud">
      <div className="mx-auto flex min-h-screen max-w-6xl gap-6 px-6 py-8">
        <aside className="w-64 rounded-3xl border border-white/10 bg-white/5 p-6 shadow-2xl backdrop-blur">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-accent text-ink font-display text-lg shadow-lg">
              V
            </div>
            <div>
              <div className="text-xl font-semibold tracking-tight text-white">
                <span className="font-display">VeriGov</span>
              </div>
              <p className="text-[11px] uppercase tracking-[0.25em] text-cloud/60">Trusted SaaS</p>
            </div>
          </div>
          <nav className="mt-8 flex flex-col gap-2">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  [
                    "flex items-center justify-between rounded-xl px-4 py-3 text-sm font-medium transition",
                    isActive
                      ? "bg-accent text-ink shadow-glow"
                      : "text-cloud/80 hover:bg-white/10",
                  ].join(" ")
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
          <div className="mt-6 rounded-2xl border border-white/10 bg-black/30 p-4 text-xs text-cloud/70">
            <p className="font-semibold text-white">Status</p>
            <p className="mt-2 text-cloud/60">Sessões ativas e checks seguros para seu tenant.</p>
          </div>
          <button
            type="button"
            onClick={handleLogout}
            className="mt-6 w-full rounded-xl border border-white/20 px-4 py-2 text-xs uppercase tracking-wide text-cloud/70 hover:border-white/40"
          >
            Sair
          </button>
        </aside>
        <main className="flex-1">
          {sessionExpired ? (
            <div className="mb-4 rounded-2xl border border-amber-400/40 bg-amber-500/10 px-4 py-3 text-xs text-amber-100">
              Sessão expirada. Faça login novamente.
            </div>
          ) : null}
          <Outlet />
        </main>
      </div>
    </div>
  );
}
