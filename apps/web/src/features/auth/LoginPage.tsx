import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useNavigate } from "react-router-dom";

import { api } from "../../lib/api";
import { clearTokens, isAuthenticated, setTokens } from "../../lib/auth";
import { useToast } from "../../components/ToastProvider";

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
  const { showToast } = useToast();

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
      showToast({ tone: "success", message: "Login realizado com sucesso." });
      navigate("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Falha ao entrar");
      showToast({ tone: "error", message: "Falha ao entrar" });
    }
  });

  const handleRegister = registerForm.handleSubmit(async (values) => {
    setError(null);
    try {
      const data = await api.register(values.email, values.password, values.tenantName);
      setTokens(data.access_token, data.refresh_token);
      showToast({ tone: "success", message: "Conta criada e sessão iniciada." });
      navigate("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Falha ao registrar");
      showToast({ tone: "error", message: "Falha ao registrar" });
    }
  });

  const handleClearSession = () => {
    clearTokens();
    setError("Sessao limpa. Entre novamente.");
    showToast({ tone: "info", message: "Sessão limpa. Faça login novamente." });
  };

  useEffect(() => {
    if (isAuthenticated()) {
      navigate("/dashboard", { replace: true });
    }
  }, [navigate]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0d16] via-[#0f1627] to-[#0f1f35] text-cloud">
      <div className="mx-auto flex min-h-screen max-w-6xl items-center px-6 py-12">
        <div className="grid w-full gap-10 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="space-y-6">
            <span className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/5 px-4 py-2 text-xs uppercase tracking-[0.25em] text-cloud/70">
              VeriGov • SaaS
            </span>
            <h1 className="font-display text-4xl font-semibold leading-tight text-white md:text-5xl">
              Compliance automatizado com foco em CNPJ, pronto para auditorias.
            </h1>
            <p className="max-w-xl text-base text-cloud/70">
              Monte seu fluxo de consulta em menos de 60 segundos. Tenancy nativo, relatórios claros e
              integrações governamentais com fallback inteligente.
            </p>
            <div className="grid gap-3 sm:grid-cols-3">
              {[
                "Multi-tenant isolado",
                "Tokens com refresh",
                "Logs e métricas prontas",
              ].map((item) => (
                <div key={item} className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-cloud/80">
                  {item}
                </div>
              ))}
            </div>
            <div className="flex gap-3">
              <button
                type="button"
                onClick={() => setMode("login")}
                className={
                  mode === "login"
                    ? "rounded-full bg-accent px-5 py-2 text-sm font-semibold text-ink shadow-lg"
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
                    ? "rounded-full bg-white/10 px-5 py-2 text-sm font-semibold text-white"
                    : "rounded-full border border-white/20 px-5 py-2 text-sm text-cloud/70"
                }
              >
                Criar conta
              </button>
            </div>
          </div>

          <div className="glass-panel p-8">
            {error ? (
              <div className="mb-4 rounded-2xl border border-red-400/40 bg-red-500/10 px-4 py-3 text-xs text-red-200">
                {error}
              </div>
            ) : null}
            {mode === "login" ? (
              <form onSubmit={handleLogin} className="space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-semibold text-white">Acesse sua conta</h2>
                  <span className="pill border-white/20 text-cloud/60">Tenant já criado</span>
                </div>
                <div>
                  <label className="text-xs uppercase text-cloud/60">Email</label>
                  <input
                    className="mt-2 w-full rounded-xl border border-white/10 bg-black/40 px-4 py-3 text-sm text-white"
                    type="email"
                    placeholder="voce@empresa.com"
                    {...loginForm.register("email")}
                  />
                </div>
                <div>
                  <label className="text-xs uppercase text-cloud/60">Senha (8-72 caracteres)</label>
                  <input
                    className="mt-2 w-full rounded-xl border border-white/10 bg-black/40 px-4 py-3 text-sm text-white"
                    type="password"
                    placeholder="********"
                    {...loginForm.register("password")}
                  />
                </div>
                <button
                  type="submit"
                  className="w-full rounded-xl bg-accent px-4 py-3 text-sm font-semibold text-ink shadow-lg"
                  disabled={loginForm.formState.isSubmitting}
                >
                  Entrar
                </button>
              </form>
            ) : (
              <form onSubmit={handleRegister} className="space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-semibold text-white">Criar tenant</h2>
                  <span className="pill border-white/20 text-cloud/60">Novo cliente</span>
                </div>
                <div>
                  <label className="text-xs uppercase text-cloud/60">Nome do tenant</label>
                  <input
                    className="mt-2 w-full rounded-xl border border-white/10 bg-black/40 px-4 py-3 text-sm text-white"
                    type="text"
                    placeholder="Empresa X"
                    {...registerForm.register("tenantName")}
                  />
                </div>
                <div className="grid gap-3 md:grid-cols-2">
                  <div>
                    <label className="text-xs uppercase text-cloud/60">Email</label>
                    <input
                      className="mt-2 w-full rounded-xl border border-white/10 bg-black/40 px-4 py-3 text-sm text-white"
                      type="email"
                      placeholder="contato@empresa.com"
                      {...registerForm.register("email")}
                    />
                  </div>
                  <div>
                    <label className="text-xs uppercase text-cloud/60">Senha (8-72 caracteres)</label>
                    <input
                      className="mt-2 w-full rounded-xl border border-white/10 bg-black/40 px-4 py-3 text-sm text-white"
                      type="password"
                      placeholder="********"
                      {...registerForm.register("password")}
                    />
                  </div>
                </div>
                <button
                  type="submit"
                  className="w-full rounded-xl bg-accent px-4 py-3 text-sm font-semibold text-ink shadow-lg"
                  disabled={registerForm.formState.isSubmitting}
                >
                  Criar conta
                </button>
              </form>
            )}
            <button
              type="button"
              onClick={handleClearSession}
              className="mt-4 w-full rounded-xl border border-white/20 px-4 py-2 text-xs uppercase tracking-wide text-cloud/70 hover:border-white/40"
            >
              Limpar sessao
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
