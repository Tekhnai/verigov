import { createContext, ReactNode, useCallback, useContext, useMemo, useState } from "react";

type Toast = {
  id: string;
  title?: string;
  message: string;
  tone?: "success" | "error" | "info";
};

type ToastContextValue = {
  showToast: (toast: Omit<Toast, "id">) => void;
};

const ToastContext = createContext<ToastContextValue | undefined>(undefined);

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const showToast = useCallback((toast: Omit<Toast, "id">) => {
    const id = crypto.randomUUID();
    setToasts((prev) => [...prev, { ...toast, id }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  }, []);

  const value = useMemo(() => ({ showToast }), [showToast]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="fixed bottom-6 right-6 z-50 space-y-3">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={[
              "min-w-[280px] rounded-2xl border px-4 py-3 shadow-lg backdrop-blur",
              toast.tone === "error"
                ? "border-red-400/40 bg-red-500/10 text-red-100"
                : toast.tone === "success"
                  ? "border-emerald-400/40 bg-emerald-500/10 text-emerald-100"
                  : "border-white/20 bg-black/50 text-white",
            ].join(" ")}
          >
            {toast.title ? <p className="text-sm font-semibold">{toast.title}</p> : null}
            <p className="text-sm">{toast.message}</p>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) {
    throw new Error("useToast must be used within ToastProvider");
  }
  return ctx;
}
