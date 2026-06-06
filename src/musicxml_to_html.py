#!/usr/bin/env python3
"""
MusicXML → Piano Guide HTML converter.
Parses homr OMR output and generates a beat-grid guide matching sample_output.html.

Usage:
    python src/musicxml_to_html.py assets/vetmua_page_1.musicxml [page_2.musicxml ...] -o output.html
    python src/musicxml_to_html.py assets/vetmua_page_1.musicxml assets/vetmua_page_2.musicxml \
        --title "Vết Mưa" --composer "Vũ Cát Tường" -o vetmua_guide.html
"""

import sys
import argparse
from pathlib import Path
from xml.etree import ElementTree as ET
from collections import defaultdict

NOTE_VN    = {'C': 'Đô', 'D': 'Rê', 'E': 'Mi', 'F': 'Fa', 'G': 'Sol', 'A': 'La', 'B': 'Si'}
NOTE_CLASS = {'C': 'do', 'D': 're', 'E': 'mi', 'F': 'fa', 'G': 'sol', 'A': 'la', 'B': 'si'}
PITCH_VAL  = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}

CSS = """
  @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;600;700;800;900&family=Playfair+Display:ital@1&display=swap');
  :root {
    --bg:#0e0d18; --card:#181726; --border:#252338;
    --rh:#38bdf8; --lh:#e879f9; --text:#eeeeff; --muted:#6b688f;
    --BEAT:64px;
    --do:#f87171; --re:#fb923c; --mi:#facc15;
    --fa:#4ade80; --sol:#38bdf8; --la:#a78bfa; --si:#f472b6;
  }
  *{margin:0;padding:0;box-sizing:border-box;}
  body{background:var(--bg);color:var(--text);font-family:'Be Vietnam Pro',sans-serif;padding:24px 14px 70px;}
  .guide-toolbar{position:sticky;top:0;z-index:50;max-width:980px;margin:0 auto 18px;
    display:flex;align-items:center;justify-content:space-between;gap:12px;
    background:rgba(14,13,24,.86);backdrop-filter:blur(14px);
    border:1px solid var(--border);border-radius:14px;padding:10px 12px;}
  .gt-title{display:flex;flex-direction:column;gap:2px;min-width:0;}
  .gt-title strong{font-size:.78rem;color:white;letter-spacing:.2px;}
  .gt-title span{font-size:.66rem;color:var(--muted);line-height:1.45;}
  .gt-link{flex-shrink:0;text-decoration:none;color:#0e0d18;background:linear-gradient(135deg,var(--rh),var(--lh));
    border-radius:999px;padding:8px 12px;font-size:.68rem;font-weight:900;}
  header{text-align:center;margin-bottom:20px;}
  header h1{font-family:'Playfair Display',serif;font-style:italic;font-size:2.2rem;
    background:linear-gradient(120deg,var(--rh),var(--lh));-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
  header p{color:var(--muted);font-size:.8rem;margin-top:4px;letter-spacing:.8px;}
  .timesig{display:flex;justify-content:center;margin-bottom:18px;}
  .tsbox{display:flex;align-items:center;gap:12px;background:rgba(255,255,255,.05);
    border:1px solid var(--border);border-radius:10px;padding:8px 18px;}
  .tsnum{display:flex;flex-direction:column;align-items:center;gap:2px;}
  .tsn{font-size:1.5rem;font-weight:900;color:white;line-height:1;}
  .tsbar{width:26px;height:2px;background:white;}
  .tsexp{font-size:.74rem;color:var(--muted);line-height:1.65;border-left:1px solid var(--border);padding-left:12px;}
  .tsexp strong{color:white;}
  .guide-help{max-width:980px;margin:0 auto 18px;background:rgba(255,255,255,.035);
    border:1px solid var(--border);border-radius:14px;padding:13px 14px;}
  .guide-help-title{font-size:.63rem;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin-bottom:10px;}
  .guide-help-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:9px;}
  .help-step{background:rgba(255,255,255,.035);border:1px solid rgba(255,255,255,.06);
    border-radius:10px;padding:10px 11px;line-height:1.65;}
  .help-step strong{display:block;color:white;font-size:.74rem;margin-bottom:2px;}
  .help-step span{color:var(--muted);font-size:.68rem;}
  .piano-section{max-width:980px;margin:0 auto 20px;background:var(--card);
    border:1px solid var(--border);border-radius:14px;padding:16px 18px;}
  .ps-title{font-size:.63rem;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin-bottom:10px;}
  .keyboard-wrap{overflow-x:auto;padding-bottom:4px;}
  .keyboard{display:flex;position:relative;height:110px;width:max-content;}
  .wk{width:30px;height:110px;flex-shrink:0;border:1.5px solid #555;border-top:none;
    border-radius:0 0 5px 5px;background:#f0eeec;position:relative;
    display:flex;flex-direction:column;align-items:center;justify-content:flex-end;
    padding-bottom:4px;margin-right:2px;}
  .bk{width:19px;height:68px;flex-shrink:0;background:#1a1a1a;
    border-radius:0 0 4px 4px;position:absolute;top:0;z-index:2;}
  .kl{font-size:.44rem;font-weight:800;color:rgba(0,0,0,.35);line-height:1;}
  .wk.rh-key{background:#bfefff;border-color:#38bdf8;}
  .wk.lh-key{background:#f3c6ff;border-color:#e879f9;}
  .wk.center{background:#ffe4b5;border:2px solid #f59e0b;}
  .kdot{width:18px;height:18px;border-radius:50%;display:flex;align-items:center;
    justify-content:center;font-size:.43rem;font-weight:900;color:rgba(0,0,0,.8);margin-bottom:2px;}
  .oct-row{display:flex;width:max-content;margin-top:6px;}
  .oct-item{display:flex;flex-direction:column;align-items:center;}
  .oct-bar{height:3px;border-radius:2px;margin-bottom:3px;width:100%;}
  .oct-txt{font-size:.54rem;font-weight:700;}
  .legend{display:flex;flex-wrap:wrap;gap:7px 16px;justify-content:center;margin-bottom:16px;}
  .leg{display:flex;align-items:center;gap:5px;font-size:.72rem;color:var(--muted);}
  .dot{width:10px;height:10px;border-radius:50%;}
  .measures{max-width:980px;margin:0 auto;display:flex;flex-direction:column;gap:14px;}
  .measure{background:var(--card);border:1px solid var(--border);border-radius:14px;overflow:hidden;}
  .mh{display:flex;align-items:center;gap:8px;padding:8px 14px;
    border-bottom:1px solid var(--border);background:rgba(255,255,255,.02);}
  .mn{background:linear-gradient(135deg,var(--rh),var(--lh));color:#0e0d18;
    width:22px;height:22px;border-radius:50%;display:flex;align-items:center;
    justify-content:center;font-size:.64rem;font-weight:900;flex-shrink:0;}
  .mlabel{font-size:.72rem;color:var(--muted);font-style:italic;flex:1;}
  .ctag{font-size:.6rem;font-weight:700;background:rgba(232,121,249,.12);
    color:var(--lh);border-radius:5px;padding:2px 8px;}
  .timeline{display:flex;flex-direction:column;padding:10px 12px;}
  .beat-ruler{display:flex;margin-bottom:5px;padding-left:78px;}
  .bn{width:var(--BEAT);text-align:center;font-size:.5rem;color:var(--muted);font-weight:700;flex-shrink:0;}
  .bn.s{color:rgba(255,255,255,.6);}
  .bn.grp{border-left:1px solid rgba(255,255,255,.15);}
  .trow{display:flex;align-items:stretch;margin-bottom:6px;min-height:70px;}
  .trow:last-child{margin-bottom:0;}
  .hlabel{width:72px;flex-shrink:0;display:flex;align-items:center;justify-content:center;
    font-size:.52rem;font-weight:800;letter-spacing:1.5px;text-transform:uppercase;
    padding:3px;border-radius:7px 0 0 7px;text-align:center;line-height:1.4;}
  .hlabel.rh{background:rgba(56,189,248,.12);color:var(--rh);}
  .hlabel.lh{background:rgba(232,121,249,.12);color:var(--lh);}
  .cells{display:flex;align-items:stretch;flex:1;border-left:2px solid var(--border);position:relative;}
  .cells::after{content:'';position:absolute;left:calc(var(--BEAT)*3);top:6px;bottom:6px;
    width:2px;background:rgba(255,255,255,.12);border-radius:2px;pointer-events:none;}
  .beat-col{width:var(--BEAT);flex-shrink:0;border-right:1px dashed rgba(255,255,255,.05);position:relative;}
  .beat-col:last-child{border-right:none;}
  .nb{position:absolute;left:3px;top:4px;bottom:4px;right:3px;border-radius:8px;
    display:flex;flex-direction:column;align-items:center;justify-content:center;
    padding:2px 4px;overflow:hidden;z-index:1;}
  .nb.s2{right:auto;width:calc(var(--BEAT)*2 - 6px);}
  .nb.s3{right:auto;width:calc(var(--BEAT)*3 - 6px);}
  .nn{font-size:.92rem;font-weight:900;color:rgba(0,0,0,.82);line-height:1;white-space:nowrap;}
  .ne{font-size:.5rem;font-weight:600;color:rgba(0,0,0,.45);margin-top:1px;}
  .rest{position:absolute;left:3px;top:4px;bottom:4px;right:3px;border-radius:8px;
    background:rgba(255,255,255,.025);display:flex;align-items:center;
    justify-content:center;font-size:.75rem;color:var(--muted);opacity:.4;}
  .do{background:var(--do);} .re{background:var(--re);} .mi{background:var(--mi);}
  .fa{background:var(--fa);} .sol{background:var(--sol);} .la{background:var(--la);}
  .si{background:var(--si);} .sib{background:linear-gradient(135deg,#f472b6,#a78bfa);}
  .cb{position:absolute;left:3px;top:4px;bottom:4px;border-radius:8px;
    display:flex;flex-direction:column;align-items:flex-start;justify-content:center;
    padding:4px 8px;overflow:hidden;z-index:1;background:rgba(255,255,255,.08);}
  .cb.s1{right:3px;}
  .cb.s2{width:calc(var(--BEAT)*2 - 6px);}
  .cb.s3{width:calc(var(--BEAT)*3 - 6px);}
  .cb.s4{width:calc(var(--BEAT)*4 - 6px);}
  .cb.s5{width:calc(var(--BEAT)*5 - 6px);}
  .cb.s6{width:calc(var(--BEAT)*6 - 6px);}
  .cn{font-size:.76rem;font-weight:900;color:rgba(255,255,255,.85);line-height:1;white-space:nowrap;}
  .ck{font-size:.55rem;font-weight:600;color:rgba(255,255,255,.55);margin-top:2px;white-space:nowrap;}
  .cf{font-size:.48rem;font-weight:700;color:rgba(255,255,255,.38);margin-top:1px;white-space:nowrap;}
  footer{text-align:center;margin-top:28px;color:var(--muted);font-size:.66rem;opacity:.35;}
  @media(max-width:720px){
    body{padding:14px 10px 56px;}
    .guide-toolbar{position:static;align-items:flex-start;border-radius:12px;}
    .guide-help-grid{grid-template-columns:1fr;}
    header h1{font-size:1.9rem;}
    .tsbox{align-items:flex-start;}
  }
"""

KEYBOARD_JS = """
(function(){
  const kb=document.getElementById('kb'),octRow=document.getElementById('oct-row');
  const W=['C','D','E','F','G','A','B'];
  const NC={C:'#f87171',D:'#fb923c',E:'#facc15',F:'#4ade80',G:'#38bdf8',A:'#a78bfa',B:'#f472b6'};
  const NV={C:'Đô',D:'Rê',E:'Mi',F:'Fa',G:'Sol',A:'La',B:'Si'};
  const octs=[1,2,3,4,5];const KW=30,GAP=2,OW=(KW+GAP)*7;
  octs.forEach(oct=>{W.forEach(n=>{
    const isRH=oct===4||(oct===5&&n==='C'),isLH=oct===3,isC=oct===4&&n==='C';
    const wk=document.createElement('div');
    wk.className='wk'+(isC?' center':isRH?' rh-key':isLH?' lh-key':'');
    if(isRH||isLH){const d=document.createElement('div');d.className='kdot';d.style.background=NC[n];d.textContent=NV[n];wk.appendChild(d);}
    const l=document.createElement('div');l.className='kl';l.textContent=n+oct;wk.appendChild(l);kb.appendChild(wk);
  });});
  const c6=document.createElement('div');c6.className='wk';const l6=document.createElement('div');l6.className='kl';l6.textContent='C6';c6.appendChild(l6);kb.appendChild(c6);
  [22,54,118,150,182].forEach(b=>octs.forEach(oct=>{const bk=document.createElement('div');bk.className='bk';bk.style.left=((oct-1)*OW+b)+'px';kb.appendChild(bk);}));
  ['#444','#444','#e879f9','#38bdf8','#444'].forEach((c,i)=>{
    const div=document.createElement('div');div.className='oct-item';div.style.width=OW+'px';
    const bar=document.createElement('div');bar.className='oct-bar';bar.style.background=c;
    const txt=document.createElement('div');txt.className='oct-txt';txt.style.color=c;
    txt.textContent=['Q8-1','Q8-2','🤚 Tay trái (C3)','🖐 Tay phải (C4)','Q8-5'][i];
    div.appendChild(bar);div.appendChild(txt);octRow.appendChild(div);
  });
})();
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def pitch_value(step, octave, alter=0):
    return octave * 12 + PITCH_VAL[step] + alter


def vn_name(step, alter=0):
    base = NOTE_VN[step]
    if alter == -1:
        return base + 'ᵇ'
    if alter == 1:
        return base + '♯'
    return base


def en_name(step, octave, alter=0):
    suffix = {-1: 'b', 1: '#'}.get(alter, '')
    return f"{step}{suffix}{octave}"


def css_class(step, alter=0):
    if step == 'B' and alter == -1:
        return 'sib'
    return NOTE_CLASS[step]


# ---------------------------------------------------------------------------
# MusicXML parsing
# ---------------------------------------------------------------------------

def parse_notes(measure_el):
    """
    Return list of note dicts with absolute start positions.
    Handles <backup> and <forward> correctly.
    """
    cursor = 0
    prev_start = 0
    notes = []

    for child in measure_el:
        if child.tag == 'note':
            is_chord = child.find('chord') is not None
            is_rest  = child.find('rest')  is not None
            is_grace = child.find('grace') is not None

            staff_el = child.find('staff')
            staff = int(staff_el.text) if staff_el is not None else 1

            voice_el = child.find('voice')
            voice = int(voice_el.text) if voice_el is not None else 1

            dur_el = child.find('duration')
            duration = int(dur_el.text) if (dur_el is not None and not is_grace) else 0

            pitch_el = child.find('pitch')
            if pitch_el is not None:
                step   = pitch_el.find('step').text
                octave = int(pitch_el.find('octave').text)
                al_el  = pitch_el.find('alter')
                alter  = int(float(al_el.text)) if al_el is not None else 0
            else:
                step = octave = alter = None

            start = prev_start if is_chord else cursor

            if not is_chord and not is_grace:
                prev_start = cursor
                cursor += duration

            if not is_grace:
                notes.append({
                    'start':    start,
                    'duration': duration,
                    'end':      start + duration,
                    'staff':    staff,
                    'voice':    voice,
                    'step':     step,
                    'octave':   octave,
                    'alter':    alter or 0,
                    'is_rest':  is_rest,
                })

        elif child.tag == 'backup':
            d = child.find('duration')
            if d is not None:
                cursor = max(0, cursor - int(d.text))
                prev_start = cursor

        elif child.tag == 'forward':
            d = child.find('duration')
            if d is not None:
                cursor += int(d.text)

    return notes


def get_attributes(measure_el):
    """Extract divisions, beats, beat_type from a measure's attributes if present."""
    result = {}
    for attr in measure_el.findall('attributes'):
        d = attr.find('divisions')
        if d is not None:
            result['divisions'] = int(d.text)
        t = attr.find('time')
        if t is not None:
            result['beats']     = int(t.find('beats').text)
            result['beat_type'] = int(t.find('beat-type').text)
    return result


# ---------------------------------------------------------------------------
# Beat assignment
# ---------------------------------------------------------------------------

def rh_per_beat(notes, beats, beat_divs):
    """
    One representative right-hand note per beat.
    Picks the note that starts earliest within the beat window (the on-beat note),
    preferring voice 1 / staff 1.
    """
    result = [None] * beats
    rh = [n for n in notes if n['staff'] == 1 and not n['is_rest'] and n['step'] is not None]

    for bi in range(beats):
        lo = bi * beat_divs
        hi = (bi + 1) * beat_divs

        # Notes starting exactly on the beat boundary — most reliable
        on_beat = [n for n in rh if n['start'] == lo]
        if on_beat:
            v1 = [n for n in on_beat if n['voice'] == 1]
            result[bi] = (v1 or on_beat)[0]
            continue

        # Any note starting within the beat window — take the earliest
        in_window = [n for n in rh if lo < n['start'] < hi]
        if in_window:
            v1 = [n for n in in_window if n['voice'] == 1]
            pool = v1 or in_window
            result[bi] = min(pool, key=lambda n: n['start'])
            continue

        # Sustained note from a previous beat
        sustained = [n for n in rh if n['start'] < lo and n['end'] > lo and n['voice'] == 1]
        if sustained:
            result[bi] = min(sustained, key=lambda n: n['start'])

    return result


def lh_chords(notes, beats, beat_divs):
    """
    Detect left-hand chord blocks.
    Returns list of dicts: {beat, span, notes}.
    """
    lh = [
        n for n in notes
        if n['staff'] == 2 and not n['is_rest'] and n['step'] is not None
    ]
    if not lh:
        return []

    by_start = defaultdict(list)
    for n in lh:
        by_start[n['start']].append(n)

    total_divs  = beats * beat_divs
    starts      = sorted(by_start)
    chords      = []

    for i, start in enumerate(starts):
        bi = start // beat_divs
        if bi >= beats:
            continue

        next_start  = starts[i + 1] if i + 1 < len(starts) else total_divs
        span_divs   = next_start - start
        span_beats  = max(1, round(span_divs / beat_divs))
        span_beats  = min(span_beats, beats - bi)

        chord_notes = sorted(by_start[start],
                             key=lambda n: pitch_value(n['step'], n['octave'], n['alter']))
        chords.append({'beat': bi, 'span': span_beats, 'notes': chord_notes})

    return chords


# ---------------------------------------------------------------------------
# HTML rendering
# ---------------------------------------------------------------------------

def render_note(note):
    cls = css_class(note['step'], note['alter'])
    vn  = vn_name(note['step'], note['alter'])
    en  = en_name(note['step'], note['octave'], note['alter'])
    return (
        f'<div class="nb {cls}">'
        f'<div class="nn">{vn}</div>'
        f'<div class="ne">{en}</div>'
        f'</div>'
    )


def render_chord(chord):
    span  = min(chord['span'], 6)
    notes = chord['notes']
    names = ' · '.join(vn_name(n['step'], n['alter']) for n in notes)
    keys  = ' · '.join(en_name(n['step'], n['octave'], n['alter']) for n in notes)
    span_lbl = 'Giữ cả nhịp' if span >= 6 else f'Giữ {span} phách'
    return (
        f'<div class="cb s{span}">'
        f'<div class="cn">{span_lbl}</div>'
        f'<div class="ck">{names}</div>'
        f'<div class="cf">{keys}</div>'
        f'</div>'
    )


def render_beat_ruler(beats):
    mid = beats // 2
    cols = []
    for i in range(beats):
        cls = 'bn'
        if i == 0:
            cls += ' s'
        if i == mid:
            cls += ' s grp'
        cols.append(f'<div class="{cls}">{i + 1}</div>')
    return ''.join(cols)


def render_measure(num, rh_beats, lh_chord_list, beats):
    ruler = render_beat_ruler(beats)

    # Right hand cells
    rh_cells = []
    for note in rh_beats:
        if note is None:
            rh_cells.append('<div class="beat-col"><div class="rest">—</div></div>')
        else:
            rh_cells.append(f'<div class="beat-col">{render_note(note)}</div>')

    # Left hand cells — build a beat→chord map
    chord_map = {c['beat']: c for c in lh_chord_list}
    lh_cells = []
    bi = 0
    while bi < beats:
        if bi in chord_map:
            chord = chord_map[bi]
            lh_cells.append(f'<div class="beat-col">{render_chord(chord)}</div>')
            for _ in range(chord['span'] - 1):
                lh_cells.append('<div class="beat-col"></div>')
            bi += chord['span']
        else:
            lh_cells.append('<div class="beat-col"><div class="rest">—</div></div>')
            bi += 1

    return f"""<div class="measure">
  <div class="mh">
    <div class="mn">{num}</div>
    <div class="mlabel">Nhịp {num}</div>
    <div class="ctag">—</div>
  </div>
  <div class="timeline">
    <div class="beat-ruler">{ruler}</div>
    <div class="trow">
      <div class="hlabel rh">TAY<br>PHẢI</div>
      <div class="cells">{''.join(rh_cells)}</div>
    </div>
    <div class="trow">
      <div class="hlabel lh">TAY<br>TRÁI</div>
      <div class="cells">{''.join(lh_cells)}</div>
    </div>
  </div>
</div>"""


def timesig_html(beats, beat_type):
    if beat_type == 8:
        exp = (
            f'<strong>Nhịp {beats}/{beat_type} — {beats} phách mỗi nhịp</strong><br>'
            f'Nhóm 2 cụm 3: <strong>●●● | ●●●</strong> &nbsp;·&nbsp; Nhấn phách 1 và 4'
        )
    else:
        exp = f'<strong>Nhịp {beats}/{beat_type}</strong>'

    return f"""<div class="timesig">
  <div class="tsbox">
    <div class="tsnum">
      <div class="tsn">{beats}</div>
      <div class="tsbar"></div>
      <div class="tsn">{beat_type}</div>
    </div>
    <div class="tsexp">{exp}</div>
  </div>
</div>"""


# ---------------------------------------------------------------------------
# Main converter
# ---------------------------------------------------------------------------

def convert(xml_paths, title='Bản nhạc', composer=''):
    divisions = 4
    beats     = 6
    beat_type = 8

    measures_html = []
    num = 0
    first_beats = beats
    first_beat_type = beat_type

    for xml_path in xml_paths:
        tree = ET.parse(xml_path)
        part = tree.getroot().find('.//part')
        if part is None:
            continue

        for meas in part.findall('measure'):
            attrs = get_attributes(meas)
            divisions = attrs.get('divisions', divisions)
            beats     = attrs.get('beats',     beats)
            beat_type = attrs.get('beat_type', beat_type)

            if num == 0:
                first_beats     = beats
                first_beat_type = beat_type

            beat_divs = divisions * 4 // beat_type
            notes     = parse_notes(meas)

            rh = rh_per_beat(notes, beats, beat_divs)
            lh = lh_chords(notes, beats, beat_divs)

            # Skip completely empty measures (all rests, no LH)
            if all(n is None for n in rh) and not lh:
                continue

            num += 1
            measures_html.append(render_measure(num, rh, lh, beats))

    ts_html = timesig_html(first_beats, first_beat_type)
    measures_body = '\n'.join(measures_html)

    page_title = f"{title} – Piano Guide"
    footer_txt = f"{title} · {composer}" if composer else title

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{page_title}</title>
<style>{CSS}</style>
</head>
<body>

<div class="guide-toolbar">
  <div class="gt-title">
    <strong>Piano Guide</strong>
    <span>Không cần đọc nhạc: đi từ vị trí phím → từng nhịp → ghép hai tay.</span>
  </div>
  <a class="gt-link" href="#measures">Bắt đầu chơi</a>
</div>

<header>
  <h1>{title}</h1>
  <p>{composer}</p>
</header>

{ts_html}

<div class="guide-help">
  <div class="guide-help-title">Cách đọc guide này</div>
  <div class="guide-help-grid">
    <div class="help-step"><strong>1. Nhìn vị trí phím</strong><span>Màu xanh là tay phải, màu hồng là tay trái, C4 là Đô giữa.</span></div>
    <div class="help-step"><strong>2. Chơi từng ô nhịp</strong><span>Đi từ trái sang phải. Mỗi ô là một phách cần bấm hoặc giữ.</span></div>
    <div class="help-step"><strong>3. Màu nốt</strong><span>Đỏ = Đô, Cam = Rê, Vàng = Mi, Xanh lá = Fa, Xanh dương = Sol, Tím = La, Hồng = Si.</span></div>
  </div>
</div>

<div class="piano-section">
  <div class="ps-title">🎹 Vị trí trên bàn phím</div>
  <div class="keyboard-wrap"><div class="keyboard" id="kb"></div></div>
  <div id="oct-row" class="oct-row"></div>
  <div style="display:flex;gap:14px;flex-wrap:wrap;margin-top:10px;">
    <div style="display:flex;align-items:center;gap:7px;font-size:.72rem;">
      <div style="width:20px;height:10px;background:#f3c6ff;border:1.5px solid #e879f9;border-radius:2px;"></div>
      <span style="color:var(--lh)">Tay trái C3</span>
    </div>
    <div style="display:flex;align-items:center;gap:7px;font-size:.72rem;">
      <div style="width:20px;height:10px;background:#bfefff;border:1.5px solid #38bdf8;border-radius:2px;"></div>
      <span style="color:var(--rh)">Tay phải C4–C5</span>
    </div>
    <div style="display:flex;align-items:center;gap:7px;font-size:.72rem;">
      <div style="width:20px;height:10px;background:#ffe4b5;border:2px solid #f59e0b;border-radius:2px;"></div>
      <span style="color:#f59e0b">C4 = Đô giữa</span>
    </div>
  </div>
</div>
<script>{KEYBOARD_JS}</script>

<div class="legend">
  <div class="leg"><div class="dot" style="background:var(--do)"></div>Đô</div>
  <div class="leg"><div class="dot" style="background:var(--re)"></div>Rê</div>
  <div class="leg"><div class="dot" style="background:var(--mi)"></div>Mi</div>
  <div class="leg"><div class="dot" style="background:var(--fa)"></div>Fa</div>
  <div class="leg"><div class="dot" style="background:var(--sol)"></div>Sol</div>
  <div class="leg"><div class="dot" style="background:var(--la)"></div>La</div>
  <div class="leg"><div class="dot" style="background:var(--si)"></div>Si / Siᵇ</div>
</div>

<div class="measures" id="measures">
{measures_body}
</div>

<footer><p>{footer_txt}</p></footer>
</body>
</html>"""


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MusicXML → Piano Guide HTML')
    parser.add_argument('inputs', nargs='+', help='MusicXML file(s) in order')
    parser.add_argument('-o', '--output', help='Output HTML file (default: stdout)')
    parser.add_argument('--title',    default='Bản nhạc', help='Song title')
    parser.add_argument('--composer', default='',         help='Composer / arranger line')
    args = parser.parse_args()

    html = convert(args.inputs, args.title, args.composer)

    if args.output:
        Path(args.output).write_text(html, encoding='utf-8')
        print(f"✓ Đã tạo: {args.output}  ({len(html):,} bytes)")
    else:
        sys.stdout.write(html)
