import type { GameState } from "@/lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function getGameState(): Promise<GameState | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/game/state`, {
      cache: "no-store"
    });

    if (!response.ok) {
      return null;
    }

    return (await response.json()) as GameState;
  } catch {
    return null;
  }
}

