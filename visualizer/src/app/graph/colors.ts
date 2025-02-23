
const colors = {
  'red': [236, 84, 70],
  'orange': [242, 162, 60],
  'yellow': [249, 213, 74],
  'green': [107, 212, 96],
  'lightblue': [128, 209, 249],
  'darkblue': [55, 133, 247],
  'violet': [92, 96, 221],
  'mauve': [177, 100, 234],
  'redish': [235, 76, 100],
};

const colorsArray = Object.values(colors);

export const hexColors = colorsArray.map((color) => {
  const r = color[0].toString(16).padStart(2, '0');
  const g = color[1].toString(16).padStart(2, '0');
  const b = color[2].toString(16).padStart(2, '0');
  return `#${r}${g}${b}`;
});

export function lightenDarkenColor(css_color: string, amount: number): string {
  const color = parseInt(css_color.slice(1), 16);
  const r = Math.min(255, Math.max(0, ((color >> 16) & 0xff) + amount));
  const b = Math.min(255, Math.max(0, ((color >> 8) & 0xff) + amount));
  const g = Math.min(255, Math.max(0, (color & 0x0000ff) + amount));
  return '#' + (g | (b << 8) | (r << 16)).toString(16).padStart(6, '0');
}
