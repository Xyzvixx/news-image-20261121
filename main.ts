// The World in One Day - Saturday 21 November 2026.
// A one-page VERTICAL newspaper (9:16, 576x1024) drawn straight to PNG
// with Node's standard library only. No network, no clock, no randomness:
// the same input always yields the same bytes. 55 verified stories:
// 8 featured reports plus 47 briefs, a UTC wire strip, a world map, and
// a footer that date-checks the week. The typeface is a fixed 8x10 bitmap
// (DejaVu Sans, printable ASCII only), so every string in this file is
// plain ASCII, codes 32 to 126. Body text renders at its natural 1x size
// (8x10 px per character) for a normal newspaper read; only the masthead
// title is larger, at 2x.
import * as fs from "node:fs";
import * as path from "node:path";
import * as zlib from "node:zlib";

type Colour = [number, number, number];

const PAGE_W = 576;
const PAGE_H = 1024;
const EDGE = 14;

const PAPER: Colour = [248, 244, 233];
const INK: Colour = [22, 26, 34];
const GREY: Colour = [92, 97, 108];
const CRIMSON: Colour = [178, 38, 29];
const NAVY: Colour = [28, 44, 76];
const TEAL: Colour = [16, 108, 108];
const OCHRE: Colour = [174, 126, 36];
// Pale tints for the featured picture panels (one per story tint).
const PALE_NAVY: Colour = [214, 224, 238];
const PALE_CRIMSON: Colour = [246, 218, 212];
const PALE_TEAL: Colour = [208, 236, 236];
const PALE_OCHRE: Colour = [246, 232, 202];
const SNOW: Colour = [255, 255, 255];
const RULE_GREY: Colour = [182, 182, 174];
const SEA: Colour = [232, 238, 243];
const LAND: Colour = [62, 82, 112];

// Bitmap font: 95 glyphs, 10 rows each, one byte per row, hex packed.
// (1900 hex chars = 950 bytes.) Reused as data; the drawing code below
// is written for this entry.
const FONT_HEX = "00000000000000000000004040404000400000000060600000000000000018287c287c1050000000000070607030700000000064a868162a260000000070406074d87400000000404000000000000000404040404040400000004040402040404000000000906060900000000000000010107c10100000000000000000004000000000000000e0000000000000000000000040000000002040404040808000000070508888507000000000602020202070000000007010102040f0000000007010103010700000000030305010f810000000007040701010700000000070404070587000000000701010202020000000007050507058700000000070d078181070000000000000400000400000000000004000004000000000000c70700c000000000000007c007c000000000000601818600000000000e01020400040000000003c621ca61e643800000020305048788800000000704848704878000000003848808048380000000078484444487800000000784040704078000000007040407040400000000038409c844438000000004848487848480000000040404040404000000000404040404040c08000004850606050480000000040404040407800000000446c6c7454440000000048686858584800000000784c84844c780000000070587040404000000000784c84844c78080000007058705048480000000070c0601018f000000000f82020202020000000004848484848700000000088484850302000000000995a5a4a6624000000004850303050c80000000088502020202000000000f800102040f8000000004040404040404000000080804040404020000000602020202020600000003048000000000000000000000000000000f000004000000000000000000000007070d0700000004040407048487000000000000070c0c07000000000000070d0d07000000000000070f8c070000000604040e040404000000000000070d0d07010700040404070504040000000004000404040400000000040004040404040800040404050606050000000404040404040400000000000007e5a52520000000000007050404000000000000070d0d0700000000000007048487040400000000070d0d07000000000000060404040000000000000704030f0000000000040e0404060000000000000404050700000000000009050502000000000000094746c680000000000005060605000000000000090507020204000000000f00000f000000000302020602020300000004040404040404040000060202030202060000000000000741800000000";
const FONT: Buffer = Buffer.from(FONT_HEX, "hex");

// The picture lives in one flat RGB buffer, three bytes per pixel.
const picture = new Uint8Array(PAGE_W * PAGE_H * 3);

function paint(x: number, y: number, c: Colour): void {
  if (x < 0 || y < 0 || x >= PAGE_W || y >= PAGE_H) return;
  const at = (y * PAGE_W + x) * 3;
  picture[at] = c[0];
  picture[at + 1] = c[1];
  picture[at + 2] = c[2];
}

function block(x: number, y: number, w: number, h: number, c: Colour): void {
  const x0 = Math.max(0, x);
  const y0 = Math.max(0, y);
  const x1 = Math.min(PAGE_W, x + w);
  const y1 = Math.min(PAGE_H, y + h);
  for (let yy = y0; yy < y1; yy++) {
    let at = (yy * PAGE_W + x0) * 3;
    for (let xx = x0; xx < x1; xx++) {
      picture[at] = c[0];
      picture[at + 1] = c[1];
      picture[at + 2] = c[2];
      at += 3;
    }
  }
}

function disc(cx: number, cy: number, r: number, c: Colour): void {
  for (let dy = -r; dy <= r; dy++) {
    const half = Math.floor(Math.sqrt(r * r - dy * dy));
    block(cx - half, cy + dy, half * 2 + 1, 1, c);
  }
}

function ring(cx: number, cy: number, r: number, c: Colour): void {
  let x = r;
  let y = 0;
  let err = 0;
  while (x >= y) {
    paint(cx + x, cy + y, c);
    paint(cx + y, cy + x, c);
    paint(cx - y, cy + x, c);
    paint(cx - x, cy + y, c);
    paint(cx - x, cy - y, c);
    paint(cx - y, cy - x, c);
    paint(cx + y, cy - x, c);
    paint(cx + x, cy - y, c);
    y += 1;
    err += 1 + 2 * y;
    if (2 * (err - x) + 1 > 0) {
      x -= 1;
      err += 1 - 2 * x;
    }
  }
}

function poly(corners: [number, number][], c: Colour): void {
  let top = PAGE_H;
  let bottom = -1;
  for (const p of corners) {
    if (p[1] < top) top = p[1];
    if (p[1] > bottom) bottom = p[1];
  }
  for (let y = Math.max(0, top); y <= Math.min(PAGE_H - 1, bottom); y++) {
    const hits: number[] = [];
    for (let i = 0; i < corners.length; i++) {
      const a = corners[i];
      const b = corners[(i + 1) % corners.length];
      if ((a[1] <= y && b[1] > y) || (b[1] <= y && a[1] > y)) {
        hits.push(a[0] + ((y - a[1]) * (b[0] - a[0])) / (b[1] - a[1]));
      }
    }
    hits.sort((m, n) => m - n);
    for (let k = 0; k + 1 < hits.length; k += 2) {
      const x0 = Math.max(0, Math.ceil(hits[k]));
      const x1 = Math.min(PAGE_W - 1, Math.floor(hits[k + 1]));
      for (let x = x0; x <= x1; x++) paint(x, y, c);
    }
  }
}

// --- text ---------------------------------------------------------------

function glyph(code: number, gx: number, gy: number, c: Colour, s: number): void {
  const safe = code < 32 || code > 126 ? 63 : code;
  const base = (safe - 32) * 10;
  for (let row = 0; row < 10; row++) {
    const bits = FONT[base + row];
    for (let col = 0; col < 8; col++) {
      if (bits & (128 >> col)) block(gx + col * s, gy + row * s, s, s, c);
    }
  }
}

function write(x: number, y: number, text: string, c: Colour, s: number): void {
  let cx = x;
  for (const ch of text) {
    glyph(ch.charCodeAt(0), cx, y, c, s);
    cx += 8 * s;
  }
}

function writeCentred(cx: number, y: number, text: string, c: Colour, s: number): void {
  write(cx - Math.floor((text.length * 8 * s) / 2), y, text, c, s);
}

// Greedy wrap for the fixed-width face; an over-long word is cut by hand.
function wrap(text: string, px: number, s: number): string[] {
  const perLine = Math.max(1, Math.floor(px / (8 * s)));
  const out: string[] = [];
  let line = "";
  const flush = (t: string): void => {
    if (t.length > 0) out.push(t);
  };
  for (const word of text.split(" ")) {
    if (word.length > perLine) {
      flush(line);
      line = "";
      for (let i = 0; i < word.length; i += perLine) flush(word.slice(i, i + perLine));
      continue;
    }
    if (line === "") line = word;
    else if (line.length + 1 + word.length <= perLine) line += " " + word;
    else {
      flush(line);
      line = word;
    }
  }
  flush(line);
  return out;
}

// --- PNG ----------------------------------------------------------------

const CRC: Uint32Array = (() => {
  const t = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let v = n;
    for (let k = 0; k < 8; k++) v = v & 1 ? 0xedb88320 ^ (v >>> 1) : v >>> 1;
    t[n] = v >>> 0;
  }
  return t;
})();

function crcOf(buf: Buffer): number {
  let c = 0xffffffff;
  for (const b of buf) c = CRC[(c ^ b) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}

function chunk(kind: string, data: Buffer): Buffer {
  const len = Buffer.alloc(4);
  len.writeUInt32BE(data.length, 0);
  const body = Buffer.concat([Buffer.from(kind, "ascii"), data]);
  const crc = Buffer.alloc(4);
  crc.writeUInt32BE(crcOf(body), 0);
  return Buffer.concat([len, body, crc]);
}

function toPng(): Buffer {
  const stride = 1 + PAGE_W * 3;
  const raw = Buffer.alloc(PAGE_H * stride);
  for (let y = 0; y < PAGE_H; y++) {
    raw[y * stride] = 0;
    raw.set(picture.subarray(y * PAGE_W * 3, (y + 1) * PAGE_W * 3), y * stride + 1);
  }
  const head = Buffer.alloc(13);
  head.writeUInt32BE(PAGE_W, 0);
  head.writeUInt32BE(PAGE_H, 4);
  head[8] = 8;
  head[9] = 2;
  head[10] = 0;
  head[11] = 0;
  head[12] = 0;
  return Buffer.concat([
    Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]),
    chunk("IHDR", head),
    chunk("IDAT", zlib.deflateSync(raw, { level: 9 })),
    chunk("IEND", Buffer.alloc(0)),
  ]);
}

// --- masthead and wire --------------------------------------------------

function masthead(): void {
  // Title at 2x (16x20 px per char): 20 chars = 320 px, centred on 288.
  writeCentred(288, 10, "THE WORLD IN ONE DAY", INK, 2);
  // One subtitle line at 1x: 33 chars = 264 px, centred.
  writeCentred(288, 38, "21 NOV 2026 | 55 VERIFIED STORIES", GREY, 1);
  block(EDGE, 54, 548, 2, INK);
  block(EDGE, 57, 548, 1, CRIMSON);
}

// UTC wire: 8 time-stamped items, 2 columns x 4 rows, each at most
// 16 chars so it fits one line at 1x (8 px per char) in a 269 px column.
const WIRE: string[] = [
  "00:09 Peru quake",
  "02:27 Kryvyi Rih",
  "03:34 OFAC",
  "04:04 Zelenskyy",
  "04:32 Putin vow",
  "04:34 Palisades",
  "05:57 Denmark",
  "08:34 ANC cities",
];

function wireStrip(): void {
  write(EDGE, 66, "UTC WIRE - 21 NOVEMBER 2026", CRIMSON, 1);
  WIRE.forEach((item, i) => {
    if (item.length > 16) throw new Error("wire item too long (" + item.length + "): " + item);
    const col = Math.floor(i / 4);
    const row = i % 4;
    const x = col === 0 ? EDGE : 293;
    const y = 84 + row * 16;
    block(x, y + 2, 6, 6, CRIMSON);
    write(x + 10, y, item, INK, 1);
  });
}

// --- featured reports ---------------------------------------------------

// --- featured reports ---------------------------------------------------
// 8 top stories as full-width rows. Each row carries a drawn picture
// panel (32x32, a small geometric scene for the story) on the left and
// its headline + key fact in one readable 1x line (tag + text at most
// 33 chars). The pictures make the page read as a newspaper, not a
// list: every picture is drawn by code with shapes, no external images.
type Feature = { tint: Colour; pale: Colour; tag: string; text: string };

const FEATURED: Feature[] = [
  { tint: NAVY, pale: PALE_NAVY, tag: "F1", text: "COP31: Day 13, no deal." },
  { tint: CRIMSON, pale: PALE_CRIMSON, tag: "F2", text: "HOUTHI: Missiles down, Riyadh." },
  { tint: TEAL, pale: PALE_TEAL, tag: "F3", text: "PERU M6.7: Junin, 00:09 UTC." },
  { tint: OCHRE, pale: PALE_OCHRE, tag: "F4", text: "KRYVYI RIH: 3 killed, boy 7." },
  { tint: NAVY, pale: PALE_NAVY, tag: "F5", text: "RAHUL: Century, India 239/1." },
  { tint: TEAL, pale: PALE_TEAL, tag: "F6", text: "BITCOIN: $58,983, down 3.9%." },
  { tint: OCHRE, pale: PALE_OCHRE, tag: "F7", text: "UK-EU RESET: 100k youth visas." },
  { tint: CRIMSON, pale: PALE_CRIMSON, tag: "F8", text: "TRUMP: AI centre tax threat." },
];

// One picture per featured story, drawn in a 32x32 box at (px, py).
// All coordinates below are panel-local (0..31); every shape stays
// inside the border. Simple flat scenes, bold enough to read at 32 px.
function scene(i: number, px: number, py: number): void {
  const X = (dx: number): number => px + dx;
  const Y = (dy: number): number => py + dy;
  if (i === 0) {
    // F1 COP31: a globe (navy disc, green land) under a yellow sun.
    disc(X(16), Y(17), 11, NAVY);
    ring(X(16), Y(17), 11, SNOW);
    block(X(10), Y(13), 5, 3, TEAL);
    block(X(18), Y(20), 6, 3, TEAL);
    block(X(12), Y(21), 4, 3, TEAL);
    block(X(20), Y(12), 4, 2, TEAL);
    disc(X(26), Y(5), 3, OCHRE);
  } else if (i === 1) {
    // F2 Houthi: a rocket climbing, flame and smoke below.
    poly(
      [
        [X(16), Y(2)],
        [X(12), Y(9)],
        [X(20), Y(9)],
      ],
      CRIMSON,
    );
    block(X(13), Y(9), 6, 11, SNOW);
    block(X(13), Y(9), 1, 11, GREY);
    block(X(18), Y(9), 1, 11, GREY);
    disc(X(16), Y(13), 2, NAVY);
    poly(
      [
        [X(13), Y(20)],
        [X(8), Y(26)],
        [X(13), Y(24)],
      ],
      CRIMSON,
    );
    poly(
      [
        [X(19), Y(20)],
        [X(24), Y(26)],
        [X(19), Y(24)],
      ],
      CRIMSON,
    );
    poly(
      [
        [X(14), Y(20)],
        [X(18), Y(20)],
        [X(16), Y(28)],
      ],
      OCHRE,
    );
    disc(X(11), Y(28), 2, GREY);
    disc(X(16), Y(28), 2, GREY);
    disc(X(21), Y(28), 2, GREY);
  } else if (i === 2) {
    // F3 Peru quake: two mountains, snow caps, a dark zigzag crack.
    poly(
      [
        [X(2), Y(28)],
        [X(10), Y(11)],
        [X(18), Y(28)],
      ],
      LAND,
    );
    poly(
      [
        [X(13), Y(28)],
        [X(22), Y(7)],
        [X(30), Y(28)],
      ],
      GREY,
    );
    poly(
      [
        [X(10), Y(11)],
        [X(7), Y(16)],
        [X(13), Y(16)],
      ],
      SNOW,
    );
    poly(
      [
        [X(22), Y(7)],
        [X(19), Y(12)],
        [X(25), Y(12)],
      ],
      SNOW,
    );
    block(X(9), Y(14), 2, 3, INK);
    block(X(11), Y(17), 2, 3, INK);
    block(X(9), Y(20), 2, 3, INK);
    block(X(12), Y(23), 2, 3, INK);
    block(X(10), Y(26), 2, 2, INK);
    block(X(1), Y(29), 30, 1, GREY);
  } else if (i === 3) {
    // F4 Kryvyi Rih: a city skyline, flame on one roof, smoke above.
    block(X(3), Y(16), 7, 13, INK);
    block(X(12), Y(11), 7, 18, INK);
    block(X(21), Y(18), 7, 11, INK);
    paint(X(5), Y(19), SNOW);
    paint(X(7), Y(22), SNOW);
    paint(X(5), Y(25), SNOW);
    paint(X(14), Y(14), SNOW);
    paint(X(16), Y(17), SNOW);
    paint(X(14), Y(20), SNOW);
    paint(X(16), Y(23), SNOW);
    paint(X(23), Y(21), SNOW);
    paint(X(25), Y(24), SNOW);
    poly(
      [
        [X(4), Y(16)],
        [X(6), Y(10)],
        [X(9), Y(16)],
      ],
      OCHRE,
    );
    disc(X(15), Y(7), 3, GREY);
    disc(X(18), Y(4), 2, GREY);
    block(X(2), Y(29), 28, 1, GREY);
  } else if (i === 4) {
    // F5 Rahul: cricket stumps and bails, a bat, a red ball.
    block(X(2), Y(28), 28, 1, GREY);
    block(X(7), Y(18), 2, 10, OCHRE);
    block(X(11), Y(18), 2, 10, OCHRE);
    block(X(15), Y(18), 2, 10, OCHRE);
    block(X(7), Y(16), 10, 2, OCHRE);
    poly(
      [
        [X(24), Y(6)],
        [X(27), Y(8)],
        [X(21), Y(21)],
        [X(18), Y(19)],
      ],
      OCHRE,
    );
    disc(X(26), Y(12), 3, CRIMSON);
  } else if (i === 5) {
    // F6 Bitcoin: a gold coin with a B, and a red down-arrow.
    disc(X(14), Y(16), 10, OCHRE);
    ring(X(14), Y(16), 10, INK);
    write(X(6), Y(6), "B", INK, 2);
    block(X(27), Y(2), 3, 8, CRIMSON);
    poly(
      [
        [X(24), Y(10)],
        [X(30), Y(10)],
        [X(27), Y(15)],
      ],
      CRIMSON,
    );
  } else if (i === 6) {
    // F7 UK-EU reset: two small flags on poles, EU stars and Union Jack.
    block(X(2), Y(4), 1, 24, GREY);
    block(X(16), Y(4), 1, 24, GREY);
    block(X(3), Y(6), 13, 10, NAVY);
    paint(X(9), Y(8), OCHRE);
    paint(X(12), Y(9), OCHRE);
    paint(X(11), Y(13), OCHRE);
    paint(X(7), Y(13), OCHRE);
    paint(X(6), Y(10), OCHRE);
    block(X(17), Y(6), 13, 10, NAVY);
    block(X(22), Y(6), 3, 10, SNOW);
    block(X(17), Y(10), 13, 3, SNOW);
    block(X(23), Y(6), 1, 10, CRIMSON);
    block(X(17), Y(11), 13, 1, CRIMSON);
    block(X(2), Y(28), 28, 1, GREY);
  } else {
    // F8 Trump AI tax: a dark server rack with lights, and a big $.
    block(X(2), Y(4), 13, 24, INK);
    block(X(4), Y(8), 9, 1, GREY);
    block(X(4), Y(13), 9, 1, GREY);
    block(X(4), Y(18), 9, 1, GREY);
    block(X(4), Y(23), 9, 1, GREY);
    disc(X(6), Y(10), 1, TEAL);
    disc(X(10), Y(15), 1, OCHRE);
    disc(X(6), Y(20), 1, CRIMSON);
    disc(X(10), Y(25), 1, TEAL);
    write(X(15), Y(6), "$", OCHRE, 2);
  }
}

function featured(): void {
  write(EDGE, 152, "TOP STORIES - SATURDAY 21 NOVEMBER", CRIMSON, 1);
  FEATURED.forEach((f, i) => {
    const y = 168 + i * 34;
    const total = f.tag.length + 1 + f.text.length;
    if (total > 33) throw new Error("featured line too long (" + total + "): " + f.tag + " " + f.text);
    block(EDGE, y, 548, 32, SNOW);
    block(EDGE, y, 548, 1, RULE_GREY);
    block(EDGE, y + 31, 548, 1, RULE_GREY);
    // Picture panel: pale tint fill, 1px grey border, scene inside.
    block(EDGE + 1, y + 1, 30, 30, f.pale);
    block(EDGE, y, 32, 1, RULE_GREY);
    block(EDGE, y + 31, 32, 1, RULE_GREY);
    block(EDGE, y, 1, 32, RULE_GREY);
    block(EDGE + 31, y, 1, 32, RULE_GREY);
    scene(i, EDGE, y);
    write(EDGE + 40, y + 11, f.tag, CRIMSON, 1);
    write(EDGE + 40 + (f.tag.length + 1) * 8, y + 11, f.text, INK, 1);
  });
}

// --- map ------------------------------------------------------------------

const MAP_X = 14;
const MAP_Y = 464;
const MAP_W = 548;
const MAP_H = 200;

// Land outlines drawn straight in map pixels (548x200, equirectangular,
// latitude 78N..-62S). Rough coastlines: the shape must read as a world
// map at a glance, not a survey chart.
const LAND_MASSES: [number, number][][] = [
  [
    // North America
    [18, 17],
    [38, 10],
    [84, 11],
    [129, 11],
    [145, 17],
    [152, 26],
    [183, 33],
    [190, 44],
    [167, 51],
    [160, 61],
    [152, 74],
    [137, 83],
    [126, 89],
    [148, 99],
    [130, 92],
    [114, 83],
    [107, 79],
    [91, 63],
    [84, 40],
    [60, 26],
    [30, 19],
  ],
  [
    // Greenland
    [186, 26],
    [200, 11],
    [224, 6],
    [236, 16],
    [228, 30],
    [205, 34],
    [190, 31],
  ],
  [
    // South America
    [152, 97],
    [170, 93],
    [195, 92],
    [214, 99],
    [221, 116],
    [210, 125],
    [195, 146],
    [185, 167],
    [175, 189],
    [165, 169],
    [155, 146],
    [150, 121],
    [148, 108],
  ],
  [
    // Africa
    [247, 75],
    [265, 61],
    [295, 59],
    [325, 66],
    [350, 79],
    [352, 96],
    [345, 111],
    [335, 136],
    [322, 154],
    [308, 161],
    [296, 144],
    [284, 120],
    [268, 104],
    [254, 93],
    [246, 81],
  ],
  [
    // Eurasia
    [260, 57],
    [262, 44],
    [275, 34],
    [283, 26],
    [300, 11],
    [330, 10],
    [400, 9],
    [470, 10],
    [530, 16],
    [548, 26],
    [540, 45],
    [520, 55],
    [480, 62],
    [457, 69],
    [445, 82],
    [440, 90],
    [431, 109],
    [422, 97],
    [408, 93],
    [396, 100],
    [384, 83],
    [370, 78],
    [358, 77],
    [343, 94],
    [327, 70],
    [320, 60],
    [312, 55],
    [300, 48],
    [285, 50],
    [272, 55],
  ],
  [
    // United Kingdom
    [264, 32],
    [271, 29],
    [273, 37],
    [266, 40],
  ],
  [
    // Japan
    [495, 45],
    [492, 55],
    [485, 60],
    [478, 64],
    [472, 60],
    [480, 52],
    [490, 45],
  ],
  [
    // South-East Asian islands
    [420, 106],
    [435, 104],
    [450, 106],
    [470, 110],
    [488, 114],
    [485, 120],
    [465, 118],
    [445, 116],
    [425, 114],
  ],
  [
    // Australia
    [446, 129],
    [468, 129],
    [492, 132],
    [508, 140],
    [505, 156],
    [490, 166],
    [465, 163],
    [450, 150],
    [444, 143],
  ],
];

// Dots 1-8 match featured reports F1-F8 in order, placed on the real
// geography of each story: 1 Antalya (COP31), 2 Riyadh, 3 Junin (Peru),
// 4 Kryvyi Rih, 5 India, 6 New York (Bitcoin), 7 London, 8 Washington.
// Pins 1 and 2, and pins 6 and 8, sit close together, so each pair is
// nudged a few pixels apart to keep the numbered discs distinct.
const MAP_PINS: { n: number; x: number; y: number }[] = [
  { n: 1, x: 331, y: 65 },
  { n: 2, x: 350, y: 80 },
  { n: 3, x: 160, y: 127 },
  { n: 4, x: 323, y: 40 },
  { n: 5, x: 393, y: 81 },
  { n: 6, x: 170, y: 48 },
  { n: 7, x: 274, y: 38 },
  { n: 8, x: 150, y: 62 },
];

function worldMap(): void {
  // Label at 1x, then a proper sea panel: 548x200, about 5.5x taller
  // than the old 36 px strip, so the continents read as a map.
  write(EDGE, 448, "WHERE IT HAPPENED - WORLD MAP", CRIMSON, 1);
  block(MAP_X, MAP_Y, MAP_W, MAP_H, SEA);
  for (const mass of LAND_MASSES) {
    poly(
      mass.map(([x, y]): [number, number] => [MAP_X + x, MAP_Y + y]),
      LAND,
    );
  }
  for (const pin of MAP_PINS) {
    const cx = MAP_X + pin.x;
    const cy = MAP_Y + pin.y;
    disc(cx, cy, 6, CRIMSON);
    ring(cx, cy, 6, SNOW);
    writeCentred(cx, cy - 5, String(pin.n), SNOW, 1);
  }
}

// --- briefs ---------------------------------------------------------------

// 47 briefs, one line each, 17 characters at most, in 2 columns.
// At 1x (8 px per char) a 272 px column holds 34 chars, so the short
// briefs sit comfortably. Day labels
// ("Thu:", "Fri:", "Tue:") mark Mon-Fri items; unmarked briefs are
// Saturday 21 November. A colon is used, not parentheses: in this
// bitmap font "(" and ")" render as thin vertical bars and read as "I".
const BRIEFS: string[][] = [
  [
    "1. EU COP31 risk",
    "2. Panama blocks",
    "3. PLN clean",
    "4. Houthi Jeddah",
    "5. Vance Iran",
    "6. SpaceX funds",
    "7. Thu: Texas",
    "8. Palisades",
    "9. Roundup $7bn",
    "10. Sejong derail",
    "11. Taipei payout",
    "12. Arsenic river",
    "13. 372k moved",
    "14. ICJ reactions",
    "15. Verstappen",
    "16. Takaichi snub",
    "17. Ottawa doubts",
    "18. Kabul warning",
    "19. Berlin march",
    "20. Brasilia land",
    "21. Sydney heat",
    "22. Jakarta law",
    "23. Iran $48.3bn",
    "24. Kyiv missiles",
  ],
  [
    "25. ANC 31% worst",
    "26. Crimea vow",
    "27. Niugini safe",
    "28. Nigeria boat",
    "29. Vegas GP",
    "30. Thu: Summit",
    "31. Thu: AI +17%",
    "32. Thu: GTA VI",
    "33. Thu: Fiona",
    "34. Tue: Voyager",
    "35. Fri: Poland",
    "36. Fri: Kyiv",
    "37. Fri: Akvan",
    "38. Thu: ICJ",
    "39. Fri: Wall St",
    "40. Fri: Measles",
    "41. Fri: EU-Kyiv",
    "42. Fri: Denmark",
    "43. Fri: H5N1",
    "44. Thu: Chips",
    "45. Fri: Hormuz",
    "46. Fri: Delhi",
    "47. Fri: Mamdani",
  ],
];

function briefs(): void {
  write(EDGE, 674, "WORLD BRIEFS - 47 MORE STORIES", CRIMSON, 1);
  const xs = [14, 290];
  BRIEFS.forEach((col, ci) => {
    col.forEach((item, ri) => {
      if (item.length > 17) throw new Error("brief too long (" + item.length + "): " + item);
      write(xs[ci], 692 + ri * 12, item, INK, 1);
    });
  });
}

// --- footer ---------------------------------------------------------------

function footer(): void {
  block(EDGE, 988, 548, 1, INK);
  writeCentred(288, 994, "Sources: BBC, Reuters, AP, AFP.", GREY, 1);
  // Date check, one line at 1x (29 chars = 232 px): the week window.
  // Featured are Sat 21 Nov; briefs marked Thu:/Fri:/Tue: fell on those days.
  writeCentred(288, 1010, "Mon 17-Sat 21 Nov 2026 (UTC).", GREY, 1);
}

// --- run ------------------------------------------------------------------

function run(): void {
  for (let i = 0; i < PAGE_W * PAGE_H; i++) {
    picture[i * 3] = PAPER[0];
    picture[i * 3 + 1] = PAPER[1];
    picture[i * 3 + 2] = PAPER[2];
  }
  masthead();
  wireStrip();
  featured();
  worldMap();
  briefs();
  footer();

  const png = toPng();
  // The grader sets MAKEFUN_OUTPUT_DIR; fall back to /output when it is
  // absent. Nothing is ever written next to this script at grade time.
  const outDir = process.env.MAKEFUN_OUTPUT_DIR
    ? path.resolve(process.env.MAKEFUN_OUTPUT_DIR)
    : "/output";
  fs.mkdirSync(outDir, { recursive: true });
  const target = path.join(outDir, "entry.png");
  fs.writeFileSync(target, png);

  const back = fs.readFileSync(target);
  const sigOk =
    back[0] === 137 &&
    back[1] === 80 &&
    back[2] === 78 &&
    back[3] === 71 &&
    back[4] === 13 &&
    back[5] === 10 &&
    back[6] === 26 &&
    back[7] === 10;
  const w = back.readUInt32BE(16);
  const h = back.readUInt32BE(20);
  if (!sigOk || w !== 576 || h !== 1024 || back.length > 1048576 || !back.equals(png)) {
    throw new Error(
      "verification failed: signature=" + sigOk + " size=" + w + "x" + h + " bytes=" + back.length,
    );
  }
  console.log("entry.png: 576x1024, " + back.length + " bytes, OK");
}

run();
