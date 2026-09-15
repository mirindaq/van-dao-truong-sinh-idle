import { Clock, Gem, Heart, Leaf, Mountain, PawPrint, Sparkles, Swords } from "lucide-react";

import type { GameState } from "@/lib/types";
import { assetPath } from "@/lib/assets";

type Props = {
  state: GameState | null;
};

export function GameHome({ state }: Props) {
  if (!state) {
    return (
      <main className="min-h-screen px-4 py-6 text-parchment">
        <section className="mx-auto flex max-w-5xl flex-col gap-4 rounded border border-gold/30 bg-ink/80 p-5">
          <h1 className="font-display text-3xl text-gold">Vạn Đạo Trường Sinh</h1>
          <p className="text-sm text-moon">
            Backend chưa sẵn sàng. Hãy chạy API tại cổng 8000 rồi tải lại trang.
          </p>
        </section>
      </main>
    );
  }

  const progress = Math.min(
    100,
    Math.round((state.cultivation.current_exp / state.cultivation.required_exp) * 100)
  );

  return (
    <main className="min-h-screen px-4 py-6">
      <section className="mx-auto grid max-w-6xl gap-5 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="overflow-hidden rounded border border-gold/25 bg-ink/85 shadow-2xl">
          <div
            className="min-h-[18rem] bg-cover bg-center p-5"
            style={{ backgroundImage: `linear-gradient(rgba(16,19,18,.72), rgba(16,19,18,.88)), url(${assetPath("maps/qingyun_mountain")})` }}
          >
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <p className="text-sm uppercase tracking-[0.18em] text-moon">Thanh Vân Sơn</p>
                <h1 className="mt-2 font-display text-4xl text-gold">{state.player.name}</h1>
                <p className="mt-1 text-lg text-parchment">
                  {state.realm.name} tầng {state.realm.stage}
                </p>
              </div>
              <div className="rounded border border-jade/60 bg-ink/70 px-3 py-2 text-sm text-moon">
                {formatActivity(state.player.current_activity)}
              </div>
            </div>

            <div className="mt-8">
              <div className="flex justify-between text-sm text-moon">
                <span>Tu vi</span>
                <span>
                  {Math.floor(state.cultivation.current_exp)} / {state.cultivation.required_exp}
                </span>
              </div>
              <div className="mt-2 h-3 rounded bg-black/50">
                <div className="h-3 rounded bg-gradient-to-r from-jade to-gold" style={{ width: `${progress}%` }} />
              </div>
            </div>

            <div className="mt-6 grid gap-3 sm:grid-cols-3">
              <Metric icon={<Leaf size={18} />} label="Tu vi/phút" value={state.cultivation.rate_per_minute.toFixed(2)} />
              <Metric icon={<Clock size={18} />} label="Tới tầng sau" value={formatDuration(state.cultivation.seconds_until_next_stage)} />
              <Metric icon={<Gem size={18} />} label="Linh thạch" value={String(state.player.spirit_stones)} />
            </div>
          </div>

          <div className="grid gap-3 border-t border-gold/20 p-5 sm:grid-cols-3">
            <Action label="Tu luyện" primary />
            <Action label="Thám hiểm" />
            <Action label="Luyện đan" />
          </div>
        </div>

        <aside className="grid gap-4">
          <Panel title="Căn cốt">
            <Metric icon={<Sparkles size={18} />} label="Linh căn" value={state.spiritual_root.name} />
            <Metric icon={<Swords size={18} />} label="Chiến lực" value={String(state.player.combat_power)} />
            <Metric icon={<PawPrint size={18} />} label="Linh thú" value={state.active_pet ?? "Chưa có"} />
            <Metric icon={<Heart size={18} />} label="Đạo lữ" value={state.dao_partner ?? "Chưa có"} />
          </Panel>

          <Panel title="Gần đây">
            <div className="space-y-3">
              {state.recent_logs.map((log) => (
                <div key={log.id} className="border-l border-gold/50 pl-3 text-sm text-parchment">
                  {log.message}
                </div>
              ))}
              {state.recent_logs.length === 0 && (
                <div className="text-sm text-moon">Chưa có ghi chép.</div>
              )}
            </div>
          </Panel>
        </aside>
      </section>
    </main>
  );
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="rounded border border-gold/25 bg-ink/80 p-5">
      <h2 className="mb-4 flex items-center gap-2 font-display text-xl text-gold">
        <Mountain size={18} />
        {title}
      </h2>
      <div className="grid gap-3">{children}</div>
    </section>
  );
}

function Metric({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="rounded border border-white/10 bg-black/25 p-3">
      <div className="flex items-center gap-2 text-xs uppercase tracking-[0.12em] text-moon">
        {icon}
        {label}
      </div>
      <div className="mt-2 text-lg text-parchment">{value}</div>
    </div>
  );
}

function Action({ label, primary = false }: { label: string; primary?: boolean }) {
  return (
    <button
      className={[
        "h-11 rounded border px-4 text-sm font-semibold transition",
        primary
          ? "border-gold bg-gold text-ink hover:bg-parchment"
          : "border-jade/70 bg-jade/20 text-parchment hover:bg-jade/35"
      ].join(" ")}
    >
      {label}
    </button>
  );
}

function formatDuration(seconds: number | null) {
  if (seconds === null) return "Không rõ";
  if (seconds === 0) return "Sẵn sàng";
  const minutes = Math.ceil(seconds / 60);
  if (minutes < 60) return `${minutes} phút`;
  const hours = Math.floor(minutes / 60);
  const rest = minutes % 60;
  return rest ? `${hours} giờ ${rest} phút` : `${hours} giờ`;
}

function formatActivity(activity: string) {
  const labels: Record<string, string> = {
    cultivating: "Đang tu luyện"
  };

  return labels[activity] ?? activity;
}
