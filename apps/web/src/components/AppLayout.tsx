import { NavLink, Outlet } from "react-router-dom";

const navItems = [
  { label: "Dashboard", to: "/dashboard" },
  { label: "Targets", to: "/targets" },
];

export default function AppLayout() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-ink via-slate to-steel text-cloud">
      <div className="mx-auto flex min-h-screen max-w-6xl gap-6 px-6 py-8">
        <aside className="w-60 rounded-3xl bg-black/30 p-6 backdrop-blur">
          <div className="text-xl font-semibold tracking-tight text-white">
            <span className="font-display">VeriGov</span>
          </div>
          <p className="mt-2 text-sm text-cloud/70">Compliance automatizado</p>
          <nav className="mt-8 flex flex-col gap-2">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  [
                    "rounded-xl px-4 py-2 text-sm font-medium transition",
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
        </aside>
        <main className="flex-1">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
