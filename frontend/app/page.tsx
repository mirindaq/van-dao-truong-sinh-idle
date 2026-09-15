import { GameHome } from "@/components/game-home";
import { getGameState } from "@/lib/api";

export default async function Home() {
  const state = await getGameState();
  return <GameHome state={state} />;
}

