import { createGameStore, renderGame } from '@1game/engine-bundle/runtime/worker';

type GameState = {
  clicks: number;
  color: string;
};

const SCENE_WIDTH = 1280;
const SCENE_HEIGHT = 720;

const { store, commitChange, bindStore } = createGameStore({
  clicks: 0,
  color: '#2563eb',
} satisfies GameState);

function Game() {
  return (
    <scene
      name="main"
      width={SCENE_WIDTH}
      height={SCENE_HEIGHT}
      backgroundColor="#0f172a"
    >
      <node
        x={0}
        y={0}
        width={SCENE_WIDTH}
        height={SCENE_HEIGHT}
        clickable
        backgroundColor={store.color}
        onPointerDown={() => {
          commitChange('click', (draft: GameState) => {
            draft.clicks += 1;
            draft.color = draft.clicks % 2 === 1 ? '#f97316' : '#2563eb';
          });
        }}
      />
      <text
        x={48}
        y={48}
        width={600}
        height={48}
        text={`clicks:${store.clicks}`}
        textColor="#f8fafc"
        textSize="32"
      />
    </scene>
  );
}

renderGame(() => <Game />, { bindStore });
