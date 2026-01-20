import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useNavigate } from "react-router-dom";

import { api } from "../../lib/api";
import { clearTokens, isAuthenticated, setTokens } from "../../lib/auth";

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8).max(72),
});

type LoginForm = z.infer<typeof loginSchema>;

const registerSchema = loginSchema.extend({
  tenantName: z.string().min(2),
});

type RegisterForm = z.infer<typeof registerSchema>;

export default function LoginPage() {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const loginForm = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  });

  const registerForm = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
  });

  const handleLogin = loginForm.handleSubmit(async (values) => {
    setError(null);
    try {
      const data = await api.login(values.email, values.password);
      setTokens(data.access_token, data.refresh_token);
      navigate("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Falha ao entrar");
    }
  });

  const handleRegister = registerForm.handleSubmit(async (values) => {
    setError(null);
    try {
      const data = await api.register(values.email, values.password, values.tenantName);
      setTokens(data.access_token, data.refresh_token);
      navigate("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Falha ao registrar");
    }
  });

  const handleClearSession = () => {
    clearTokens();
    setError("Sessao limpa. Entre novamente.");
  };

  useEffect(() => {
    if (isAuthenticated()) {
      navigate("/dashboard", { replace: true });
    }
  }, [navigate]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-ink via-slate to-steel text-cloud">
      <div className="mx-auto flex min-h-screen max-w-5xl items-center px-6">
        <div className="grid w-full gap-8 md:grid-cols-[1.2fr_0.8fr]">
          <div>
            <p className="text-sm uppercase tracking-[0.3em] text-cloud/60">VeriGov</p>
            <h1 className="mt-4 font-display text-4xl font-semibold leading-tight text-white md:text-5xl">
              Compliance automatizado com foco em CNPJ, pronto para auditorias.
            </h1>
            <p className="mt-6 max-w-xl text-base text-cloud/70">
              Monte seu fluxo de consulta em menos de 60 segundos. Tenancy nativo, relatorios claros e
              integracoes governamentais com fallback inteligente.
            </p>
            <div className="mt-8 flex gap-3">
              <button
                type="button"
                onClick={() => setMode("login")}
                className={
                  mode === "login"
                    ? "rounded-full bg-accent px-5 py-2 text-sm font-semibold text-ink"
                    : "rounded-full border border-white/20 px-5 py-2 text-sm text-cloud/70"
                }
              >
                Entrar
              </button>
              <button
                type="button"
                onClick={() => setMode("register")}
                className={
                  mode === "register"
                    ? "rounded-full bg-accent px-5 py-2 text-sm font-semibold text-ink"
                    : "rounded-full border border-white/20 px-5 py-2 text-sm text-cloud/70"
                }
              >
                Criar conta
              </button>
            </div>
          </div>

          <div className="rounded-3xl bg-white/5 p-8 shadow-xl backdrop-blur">
            {error ? (
              <div className="mb-4 rounded-2xl border border-red-400/40 bg-red-500/10 px-4 py-3 text-xs text-red-200">
                {error}
              </div>
            ) : null}
            {mode === "login" ? (
              <form onSubmit={handleLogin} className="space-y-4">
                <h2 className="text-xl font-semibold text-white">Acesse sua conta</h2>
                <div>
                  <label className="text-xs uppercase text-cloud/60">Email</label>
                  <input
                    className="mt-2 w-full rounded-xl border border-white/10 bg-black/40 px-4 py-3 text-sm text-white"
                    type="email"
                    {...loginForm.register("email")}
                  />
                </div>
                <div>
                  <label className="text-xs uppercase text-cloud/60">Senha (8-72 caracteres)</label>
                  <input
                    className="mt-2 w-full rounded-xl border border-white/10 bg-black/40 px-4 py-3 text-sm text-white"
                    type="password"
                    {...loginForm.register("password")}
                  />
                </div>
                <button
                  type="submit"
                  className="w-full rounded-xl bg-accent px-4 py-3 text-sm font-semibold text-ink"
                  disabled={loginForm.formState.isSubmitting}
                >
                  Entrar
                </button>
              </form>
            ) : (
              <form onSubmit={handleRegister} className="space-y-4">
                <h2 className="text-xl font-semibold text-white">Criar tenant</h2>
                <div>
                  <label className="text-xs uppercase text-cloud/60">Nome do tenant</label>
                  <input
                    className="mt-2 w-full rounded-xl border border-white/10 bg-black/40 px-4 py-3 text-sm text-white"
                    type="text"
                    {...registerForm.register("tenantName")}
                  />
                </div>
                <div>
                  <label className="text-xs uppercase text-cloud/60">Email</label>
                  <input
                    className="mt-2 w-full rounded-xl border border-white/10 bg-black/40 px-4 py-3 text-sm text-white"
                    type="email"
                    {...registerForm.register("email")}
                  />
                </div>
                <div>
                  <label className="text-xs uppercase text-cloud/60">Senha (8-72 caracteres)</label>
                  <input
                    className="mt-2 w-full rounded-xl border border-white/10 bg-black/40 px-4 py-3 text-sm text-white"
                    type="password"
                    {...registerForm.register("password")}
                  />
                </div>
                <button
                  type="submit"
                  className="w-full rounded-xl bg-accent px-4 py-3 text-sm font-semibold text-ink"
                  disabled={registerForm.formState.isSubmitting}
                >
                  Criar conta
                </button>
              </form>
            )}
            <button
              type="button"
              onClick={handleClearSession}
              className="mt-4 w-full rounded-xl border border-white/20 px-4 py-2 text-xs uppercase tracking-wide text-cloud/70"
            >
              Limpar sessao
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
