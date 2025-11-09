#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math, sys, os, io, re, time, base64, logging, threading, random
from pathlib import Path
from itertools import permutations
from typing import List, Tuple, Dict

import numpy as np
import webview

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

logging.getLogger('pywebview').setLevel(logging.CRITICAL)
if sys.platform == 'win32':
    os.environ['PYTHONWARNINGS'] = 'ignore'

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR   = (SCRIPT_DIR.parent / "data").resolve()
INPUT_DIR  = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"
MAXRECT_DIR = DATA_DIR / "maxrect"
INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
MAXRECT_DIR.mkdir(parents=True, exist_ok=True)

PLACA_LARGURA = 300
PLACA_ALTURA  = 300
MARGEM        = 10
LASER_CUSTO_POR_CM = 0.01
PLACA_CUSTO        = 1000.0

pagina_html = r"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Corte de Placas</title>
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:linear-gradient(135deg,#f5f7fa,#c3cfe2);min-height:100vh;padding-top:70px}
  .navbar{position:fixed;top:0;left:0;right:0;background:#fff;box-shadow:0 2px 8px rgba(0,0,0,.1);z-index:1000;height:70px;display:flex;align-items:center;justify-content:center;gap:1rem;padding:0 2rem}
  .nav-btn{background:#fff;border:2px solid #3b82f6;color:#3b82f6;padding:.75rem 2rem;border-radius:8px;font-weight:600;cursor:pointer;transition:.2s}
  .nav-btn:hover{background:#eff6ff;transform:translateY(-2px);box-shadow:0 4px 12px rgba(59,130,246,.2)}
  .nav-btn-active{background:#3b82f6;color:#fff}
  .screen{display:none;max-width:1800px;margin:2rem auto;padding:2rem}
  .screen-active{display:block;animation:fade .3s ease forwards}
  @keyframes fade{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
  .sections-container{display:flex;gap:1.5rem;align-items:stretch;height:calc(100vh - 160px)}
  .section{background:#fff;border-radius:12px;padding:1.5rem;box-shadow:0 4px 6px rgba(0,0,0,.07);flex:1;min-width:0;display:flex;flex-direction:column}
  .section-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:1rem;padding-bottom:.6rem;border-bottom:3px solid #3b82f6}
  .section-title{font-size:1.15rem;font-weight:800;color:#1e293b}
  .head-actions{display:flex;align-items:center;gap:.5rem}
  .icon-btn{border:1px solid #cbd5e1;background:#fff;border-radius:8px;padding:.35rem .6rem;cursor:pointer;font-weight:700}
  .icon-btn:hover{background:#f1f5f9}
  .counter{min-width:58px;text-align:center;font-weight:700;color:#334155}
  .btn{padding:.75rem 1.5rem;border:none;border-radius:8px;font-weight:700;cursor:pointer;transition:.2s;box-shadow:0 2px 4px rgba(0,0,0,.1);white-space:nowrap}
  .btn-primary{background:#3b82f6;color:#fff}.btn-primary:hover{background:#2563eb;transform:translateY(-2px)}
  .btn-secondary{background:#10b981;color:#fff}.btn-secondary:hover{background:#059669;transform:translateY(-2px)}
  .input-container{display:flex;flex-direction:column;gap:1rem;flex-grow:1}
  .image-preview{background:#f8fafc;border:2px solid #e2e8f0;border-radius:8px;padding:1rem;min-height:300px;display:flex;align-items:center;justify-content:center;overflow:auto;flex-grow:1;position:relative}
  .image-preview img{max-width:100%;max-height:100%;object-fit:contain;border-radius:8px}
  .image-preview-empty{color:#94a3b8;font-style:italic}
  .gallery{background:#f8fafc;border:2px solid #e2e8f0;border-radius:10px;padding:1rem;min-height:420px;display:flex;align-items:center;justify-content:center;overflow:auto}
  .gallery img{max-width:100%;max-height:100%;object-fit:contain;border-radius:8px}
  .info-card{margin-top:12px;background:#f8fafc;border:2px dashed #cbd5e1;border-radius:10px;padding:18px;text-align:center;color:#334155;font-weight:700}
  @media (max-width:1200px){.sections-container{flex-direction:column;height:auto}.section{min-height:auto}}
  #txtChooser{display:none}

  .spinner{display:inline-block;width:1.2rem;height:1.2rem;border:.18rem solid #93c5fd;border-top-color:#1d4ed8;border-radius:50%;animation:spin .8s linear infinite;margin-left:.5rem;vertical-align:middle}
  .spinner.sm{width:.9rem;height:.9rem;border-width:.16rem;margin-left:.35rem}
  @keyframes spin{to{transform:rotate(360deg)}}

  .timer{font-weight:700;color:#475569;font-variant-numeric:tabular-nums}
  .meta{display:flex;align-items:center;gap:.35rem}
  .meta .label{font-weight:700;color:#1f2937}

  /* MaxRect layout: 40% + 60% */
  #screen-heurmax .sections-container .section:nth-child(1){flex:0 0 40%}
  #screen-heurmax .sections-container .section:nth-child(2){flex:1 1 60%}
</style>
</head>
<body>
  <nav class="navbar">
    <button class="nav-btn nav-btn-active" onclick="switchScreen('bruto', event)">Bruto</button>
    <button class="nav-btn" onclick="switchScreen('bnb', event)">Branch and Bound</button>
    <button class="nav-btn" onclick="switchScreen('heurmax', event)">Heurística (MaxRect)</button>
  </nav>

  <input id="txtChooser" type="file" accept=".txt">

  <!-- BRUTO -->
  <div id="screen-bruto" class="screen screen-active">
    <div class="sections-container">
      <div class="section">
        <div class="section-head">
          <div class="section-title">Entrada e Processamento</div>
          <div class="head-actions">
            <span class="meta"><span class="label">⏱</span><span id="ticEntrada" class="timer">00:00</span><span id="spinEntrada" class="spinner sm" style="visibility:hidden"></span></span>
            <button class="icon-btn" onclick="prevEntrada()">◀</button>
            <span id="counterEntrada" class="counter">0/0</span>
            <button class="icon-btn" onclick="nextEntrada()">▶</button>
          </div>
        </div>
        <div class="action-buttons" style="display:flex;flex-direction:column;gap:.75rem;margin-bottom:1rem">
          <div><button id="btnCarregar" class="btn btn-primary" onclick="selecionarTXT()">📁 Carregar Arquivo TXT</button></div>
          <div>
            <button id="btnProcessar" class="btn btn-secondary" onclick="processarBruto()">▶️ Processar (Bruto)</button>
            <span id="procStatus" style="margin-left:.5rem;color:#334155;font-weight:600"></span>
          </div>
        </div>
        <div class="input-container">
          <div class="image-preview">
            <span id="placeholderBruto" class="image-preview-empty">Nenhuma peça carregada</span>
            <img id="imgBruto" alt="Peça" style="display:none">
          </div>
        </div>
      </div>

      <div class="section">
        <div class="section-head">
          <div class="section-title">Solução Atual</div>
          <div class="head-actions">
            <span class="meta"><span class="label">⏱</span><span id="ticAtual" class="timer">00:00</span><span id="spinAtual" class="spinner sm" style="visibility:hidden"></span></span>
            <button class="icon-btn" onclick="prevImage('atual')">◀</button>
            <span id="counterAtual" class="counter">0/0</span>
            <button class="icon-btn" onclick="nextImage('atual')">▶</button>
          </div>
        </div>
        <div id="galeriaAtual" class="gallery"><em style="color:#94a3b8">Sem resultados ainda</em></div>
        <div id="infoAtual" class="info-card">—</div>
      </div>

      <div class="section">
        <div class="section-head">
          <div class="section-title">Solução Anterior</div>
          <div class="head-actions">
            <span class="meta"><span class="label">⏱</span><span id="ticAntiga" class="timer">00:00</span><span id="spinAntiga" class="spinner sm" style="visibility:hidden"></span></span>
            <button class="icon-btn" onclick="prevImage('antiga')">◀</button>
            <span id="counterAntiga" class="counter">0/0</span>
            <button class="icon-btn" onclick="nextImage('antiga')">▶</button>
          </div>
        </div>
        <div id="galeriaAntiga" class="gallery"><em style="color:#94a3b8">Sem resultados ainda</em></div>
        <div id="infoAntiga" class="info-card">—</div>
      </div>
    </div>
  </div>

  <!-- BNB placeholder -->
  <div id="screen-bnb" class="screen">
    <div class="sections-container">
      <div class="section"><div class="section-head"><div class="section-title">Branch and Bound</div></div><div style="padding:2rem;text-align:center;color:#64748b">Em desenvolvimento...</div></div>
    </div>
  </div>

  <!-- HEURÍSTICA (MAXRECT) — DUAS DIVS -->
  <div id="screen-heurmax" class="screen">
    <div class="sections-container">

      <!-- (1) Entrada / Execução (40%) -->
      <div class="section">
        <div class="section-head">
          <div class="section-title">Heurística (MaxRect) — Entrada e Execução</div>
          <div class="head-actions">
            <span class="meta"><span class="label">⏱</span><span id="ticMRin" class="timer">00:00</span><span id="spinMRin" class="spinner sm" style="visibility:hidden"></span></span>
            <button class="icon-btn" onclick="prevEntrada()">◀</button>
            <span class="counter" id="counterMRin">0/0</span>
            <button class="icon-btn" onclick="nextEntrada()">▶</button>
          </div>
        </div>

        <div class="action-buttons" style="display:flex;flex-direction:column;gap:.75rem;margin-bottom:1rem">
          <div><button class="btn btn-primary" onclick="selecionarTXT()">📁 Carregar Arquivo TXT</button></div>
          <div>
            <button id="btnMR" class="btn btn-secondary" onclick="processarMaxRect()">▶️ Rodar MaxRect</button>
            <span id="mrStatus" style="margin-left:.5rem;color:#334155;font-weight:600"></span>
          </div>
        </div>

        <div class="input-container">
          <div class="image-preview">
            <span id="placeholderMRin" class="image-preview-empty">Nenhuma peça carregada</span>
            <img id="imgMRin" alt="Peça" style="display:none">
          </div>
        </div>
      </div>

      <!-- (2) Progresso auto (60%) -->
      <div class="section">
        <div class="section-head">
          <div class="section-title">MaxRect — Progresso (auto)</div>
          <div class="head-actions">
            <span class="meta"><span class="label">⏱</span><span id="ticMRprog" class="timer">00:00</span><span id="spinMRprog" class="spinner sm" style="visibility:hidden"></span></span>
            <span id="counterMRprog" class="counter">0/0</span>
          </div>
        </div>
        <div id="galMRprog" class="gallery"><em style="color:#94a3b8">Aguardando execução…</em></div>
        <div id="infoMRprog" class="info-card">—</div>
      </div>

    </div>
  </div>

<script>
  function switchScreen(name, ev){
    document.querySelectorAll('.screen').forEach(s=>s.classList.remove('screen-active'));
    document.querySelectorAll('.nav-btn').forEach(b=>b.classList.remove('nav-btn-active'));
    document.getElementById('screen-'+name).classList.add('screen-active');
    if(ev) ev.target.classList.add('nav-btn-active');
  }

  // ---------------- cronômetros ----------------
  let tEntrada=0, tAtual=0, tAntiga=0, tMRin=0, tMRprog=0;
  function fmt(t){const h=Math.floor(t/3600),m=Math.floor((t%3600)/60),s=t%60;return (h>0?`${String(h).padStart(2,'0')}:`:'')+`${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;}
  function tick(){tEntrada++;tAtual++;tAntiga++;tMRin++;tMRprog++;
    document.getElementById('ticEntrada').textContent=fmt(tEntrada);
    document.getElementById('ticAtual').textContent=fmt(tAtual);
    document.getElementById('ticAntiga').textContent=fmt(tAntiga);
    document.getElementById('ticMRin').textContent=fmt(tMRin);
    document.getElementById('ticMRprog').textContent=fmt(tMRprog);
  }
  setInterval(tick,1000);
  function resetTimer(w){({entrada:()=>tEntrada=0,atual:()=>tAtual=0,antiga:()=>tAntiga=0,mrin:()=>tMRin=0,mrprog:()=>tMRprog=0}[w]||(()=>{}))();}
  function setProcessingUI(on){
    const vis=on?'visible':'hidden';
    ['spinEntrada','spinAtual','spinAntiga','spinMRin','spinMRprog'].forEach(id=>{const el=document.getElementById(id); if(el) el.style.visibility=vis;});
  }

  // -------- previews entrada (compartilhado)
  const entrada={images:[],idx:0};
  function selecionarTXT(){document.getElementById('txtChooser').value='';document.getElementById('txtChooser').click();}
  document.getElementById('txtChooser').addEventListener('change', async (ev)=>{
    const f=ev.target.files&&ev.target.files[0]; if(!f) return;
    try{
      const text=await f.text(); const res=await window.pywebview.api.carregar_entrada_texto(text);
      if(res?.error){alert('Erro: '+res.error);return;}
      entrada.images=Array.isArray(res?.images)?res.images:[]; entrada.idx=0; resetTimer('entrada'); resetTimer('mrin'); renderEntrada(); renderEntradaMR();
    }catch(e){console.error(e); alert('Erro ao ler o arquivo.');}
  });
  function _renderPrev(imgId,phId,ctrId){
    const img=document.getElementById(imgId), ph=document.getElementById(phId), ctr=document.getElementById(ctrId);
    if(!entrada.images.length){img.style.display='none';img.removeAttribute('src');ph.style.display='block';ctr.textContent='0/0';return;}
    entrada.idx=Math.max(0,Math.min(entrada.idx,entrada.images.length-1));
    img.src=entrada.images[entrada.idx]; img.style.display='block'; ph.style.display='none'; ctr.textContent=`${entrada.idx+1}/${entrada.images.length}`;
  }
  function renderEntrada(){_renderPrev('imgBruto','placeholderBruto','counterEntrada');}
  function renderEntradaMR(){_renderPrev('imgMRin','placeholderMRin','counterMRin');}
  function nextEntrada(){entrada.idx++; renderEntrada(); renderEntradaMR();}
  function prevEntrada(){entrada.idx--; renderEntrada(); renderEntradaMR();}

  // -------- BRUTO watcher --------
  const state={atual:{images:[],idx:0,infoText:''},antiga:{images:[],idx:0,infoText:''}};
  let lastAtualInfo='', lastAntigaInfo='';
  function cap(s){return s.charAt(0).toUpperCase()+s.slice(1);}
  function renderInfo(txt){
    if(!txt||typeof txt!=='string') return '—';
    const custo=(txt.match(/Custo:\s*R\$?\s*([0-9.,]+)/i)||[])[1];
    const tempo=(txt.match(/Tempo:\s*([0-9.,]+)s?/i)||[])[1];
    const placas=(txt.match(/Placas:\s*(\d+)/i)||[])[1];
    const parts=[]; if(placas)parts.push(`Placas: <strong>${placas}</strong>`); if(custo)parts.push(`Custo: <strong>R$ ${custo}</strong>`); if(tempo)parts.push(`Tempo: <strong>${tempo}s</strong>`);
    let html = parts.length?`<div>${parts.join(' &nbsp;•&nbsp; ')}</div>`:'';
    let stripped=txt.replace(/^.*Placas:.*\n?/gmi,'').replace(/^.*Custo:.*\n?/gmi,'').replace(/^.*Tempo:.*\n?/gmi,'');
    if(stripped.trim()) html+=`<hr style="margin:8px 0;border:none;border-top:1px dashed #cbd5e1"><pre style="white-space:pre-wrap;text-align:left">${stripped}</pre>`;
    return html||`<pre style="white-space:pre-wrap;text-align:left">${txt}</pre>`;
  }
  function setGallery(which){
    const gal=document.getElementById('galeria'+cap(which));
    const ctr=document.getElementById('counter'+cap(which));
    const info=document.getElementById('info'+cap(which));
    const s=state[which];
    if(!s.images.length){gal.innerHTML='<em style="color:#94a3b8">Sem resultados ainda</em>'; ctr.textContent='0/0'; info.textContent='—'; return;}
    if(s.idx<0)s.idx=0; if(s.idx>=s.images.length)s.idx=s.images.length-1;
    gal.innerHTML=`<img src="${s.images[s.idx]}">`; ctr.textContent=`${s.idx+1}/${s.images.length}`; info.innerHTML=renderInfo(s.infoText);
  }
  function nextImage(w){state[w].idx++; setGallery(w);} function prevImage(w){state[w].idx--; setGallery(w);}

  let pollingHandle=null;
  async function processarBruto(){
    const btn=document.getElementById('btnProcessar'); const status=document.getElementById('procStatus');
    btn.disabled=true; status.innerHTML='Processando<span class="spinner"></span>'; setProcessingUI(true);
    try{window.pywebview.api.forca_bruta();}catch(e){console.error(e);}
    if(!pollingHandle){pollingHandle=setInterval(fetchSolucoes,1500);}
  }
  async function fetchSolucoes(){
    try{
      const res=await window.pywebview.api.get_solutions();
      if(typeof res?.processing==='boolean'){
        setProcessingUI(res.processing);
        if(!res.processing){document.getElementById('btnProcessar').disabled=false; document.getElementById('procStatus').textContent='';}
      }
      if(res?.atual){
        state.atual.images=res.atual.images||[]; state.atual.infoText=res.atual.info_text||''; if(state.atual.idx>=state.atual.images.length) state.atual.idx=0;
        if(res.atual.info_text!==lastAtualInfo){resetTimer('atual'); lastAtualInfo=res.atual.info_text;} setGallery('atual');
      }
      if(res?.antiga){
        state.antiga.images=res.antiga.images||[]; state.antiga.infoText=res.antiga.info_text||''; if(state.antiga.idx>=state.antiga.images.length) state.antiga.idx=0;
        if(res.antiga.info_text!==lastAntigaInfo){resetTimer('antiga'); lastAntigaInfo=res.antiga.info_text;} setGallery('antiga');
      }
    }catch(e){console.error(e);}
  }

  // -------- MAXRECT — auto play (lê TODOS PNGs ordenados) --------
  const mr={images:[], idx:-1, info:'', running:false};
  let mrPolling=null, mrAuto=null;

  function startAuto(){
    if(mrAuto) return;
    mrAuto = setInterval(()=>{
      if(mr.images.length===0) return;
      if(mr.idx < mr.images.length-1){ mr.idx++; renderMR(); }
      else { if(!mr.running) stopAuto(); }
    }, 700);
  }
  function stopAuto(){ if(mrAuto){clearInterval(mrAuto); mrAuto=null;} }

  function renderMR(){
    const gal=document.getElementById('galMRprog');
    const ctr=document.getElementById('counterMRprog');
    const info=document.getElementById('infoMRprog');
    if(!mr.images.length){ gal.innerHTML='<em style="color:#94a3b8">Sem imagens ainda</em>'; ctr.textContent='0/0'; info.textContent='—'; return; }
    if(mr.idx<0) mr.idx=0; if(mr.idx>=mr.images.length) mr.idx=mr.images.length-1;
    gal.innerHTML=`<img src="${mr.images[mr.idx]}">`;
    ctr.textContent=`${mr.idx+1}/${mr.images.length}`;
    info.innerHTML=renderInfo(mr.info);
  }

  async function processarMaxRect(){
    const btn=document.getElementById('btnMR'); const st=document.getElementById('mrStatus');
    btn.disabled=true; st.innerHTML='Processando<span class="spinner"></span>';
    document.getElementById('spinMRin').style.visibility='visible';
    document.getElementById('spinMRprog').style.visibility='visible';
    resetTimer('mrprog'); mr.idx=-1; mr.images=[]; renderMR();
    try{ await window.pywebview.api.maxrect(); }catch(e){ console.error(e); }
    if(!mrPolling){ mrPolling=setInterval(fetchMaxRect, 1000); }
    startAuto();
  }

  async function fetchMaxRect(){
    try{
      const res = await window.pywebview.api.get_maxrect();
      if(!res) return;
      mr.running = !!res.processing;
      document.getElementById('btnMR').disabled = mr.running;
      document.getElementById('mrStatus').textContent = mr.running ? 'Processando…' : '';
      document.getElementById('spinMRin').style.visibility = mr.running ? 'visible':'hidden';
      document.getElementById('spinMRprog').style.visibility = mr.running ? 'visible':'hidden';
// Se está processando e, por algum motivo, o auto-play não está ligado, liga de novo
     if (mr.running && !mrAuto) {
       startAuto();
     }

      if(res.after){
        const prevLen = mr.images.length;
        mr.images = res.after.images || [];
        mr.info   = res.after.info_text || '';
        // Chegaram novos frames? garante auto ligado
       if(mr.images.length > prevLen){ startAuto(); }
        if(mr.idx < 0 && mr.images.length>0){ mr.idx = 0; }
        renderMR();
      }

// Se terminou, só para quando já estiver no último frame
if(!mr.running && mr.idx >= mr.images.length - 1)
{ stopAuto();
}
    }catch(e){ console.error(e); }
  }

  window.addEventListener('DOMContentLoaded', ()=>{
    setProcessingUI(false);
    if(!pollingHandle) pollingHandle=setInterval(fetchSolucoes,1500);
    if(!mrPolling) mrPolling=setInterval(fetchMaxRect,700);
  });
</script>
</body>
</html>
"""

# --------------- helpers preview ---------------
def _fig_to_data_uri(fig)->str:
    buf=io.BytesIO(); fig.savefig(buf, format='png', dpi=150, bbox_inches='tight'); plt.close(fig)
    b64=base64.b64encode(buf.getvalue()).decode('ascii'); return f"data:image/png;base64,{b64}"

def _desenhar_peca_preview(w:int,h:int,pid:int)->str:
    PAD=20; max_side=max(w,h)
    fig,ax=plt.subplots(figsize=(6,6))
    ax.set_xlim(0,max_side+2*PAD); ax.set_ylim(0,max_side+2*PAD); ax.set_aspect('equal'); ax.axis('off')
    x=PAD+(max_side-w)/2; y=PAD+(max_side-h)/2
    ax.add_patch(patches.Rectangle((x,y),w,h,linewidth=2,edgecolor='black',facecolor='#a7f3d0',alpha=0.9))
    ax.text(x+w/2,y+h/2,f"P{pid}\n{w}×{h} cm",ha='center',va='center',fontsize=14,fontweight='bold',color='#111827')
    ax.set_title(f"Peça {pid} — {w}×{h} cm",fontsize=14,fontweight='bold')
    return _fig_to_data_uri(fig)

# --------------- parsing TXT ---------------
_last_txt_path: Path = INPUT_DIR / "entrada.txt"
_last_txt_lock = threading.Lock()

def _save_latest_txt(content:str)->Path:
    with _last_txt_lock:
        _last_txt_path.write_text(content, encoding='utf-8'); return _last_txt_path

def _parse_txt_content(content:str)->List[Tuple[int,int]]:
    linhas=[ln.strip() for ln in content.splitlines() if ln.strip()]
    if not linhas: raise ValueError("Arquivo vazio")
    try: n=int(linhas[0])
    except: raise ValueError("Primeira linha deve ser um inteiro")
    if n<=0: raise ValueError("Número de peças deve ser positivo")
    if len(linhas)<1+n: raise ValueError(f"Declaradas {n} peças, mas só há {len(linhas)-1}")
    pares=[]
    for i in range(n):
        w_h=linhas[1+i].split()
        if len(w_h)!=2: raise ValueError(f"Linha {i+2} inválida: '{linhas[1+i]}'")
        w,h=map(int,w_h)
        if w<=0 or h<=0: raise ValueError(f"Linha {i+2}: dimensões devem ser positivas")
        pares.append((w,h))
    return pares

# ============================================================
# ========================  BRUTO  ===========================
# ============================================================
class Peca:
    def __init__(self, largura:int, altura:int, pid:int):
        self.largura=largura; self.altura=altura; self.id=pid; self.x=0; self.y=0

class Placa:
    def __init__(self):
        self.largura=PLACA_LARGURA; self.altura=PLACA_ALTURA
        self.ocupacao=[[False]*self.largura for _ in range(self.altura)]
        self.pecas:List[Peca]=[]
        self.laser_corte=0.0

    def verificar_espaco(self,x:int,y:int,w:int,h:int)->bool:
        x_min=MARGEM; y_min=MARGEM; x_max=self.largura-MARGEM; y_max=self.altura-MARGEM
        if x<x_min or y<y_min or x+w>x_max or y+h>y_max: return False
        for yy in range(y,y+h):
            row=self.ocupacao[yy]
            for xx in range(x,x+w):
                if row[xx]: return False
        return True

    def ocupar_espaco(self,x:int,y:int,w:int,h:int):
        for yy in range(y,y+h):
            row=self.ocupacao[yy]
            for xx in range(x,x+w):
                row[xx]=True

    def _corte_compartilhado(self,x:int,y:int,w:int,h:int)->int:
        comp=0
        if y>0:
            row=self.ocupacao[y-1]
            for xx in range(x,x+w):
                if row[xx]: comp+=1
        if y+h<self.altura:
            row=self.ocupacao[y+h]
            for xx in range(x,x+w):
                if row[xx]: comp+=1
        if x>0:
            for yy in range(y,y+h):
                if self.ocupacao[yy][x-1]: comp+=1
        if x+w<self.largura:
            for yy in range(y,y+h):
                if self.ocupacao[yy][x+w]: comp+=1
        return comp

    def custo_posicao(self,x:int,y:int,w:int,h:int)->float:
        perimetro=2*(w+h); compartilhado=self._corte_compartilhado(x,y,w,h)
        return (perimetro-compartilhado)*LASER_CUSTO_POR_CM

    def melhor_posicao(self,p:Peca)->Tuple[float,int,int]:
        best=(float('inf'),-1,-1)
        for yy in range(MARGEM,self.altura-MARGEM-p.altura+1):
            for xx in range(MARGEM,self.largura-MARGEM-p.largura+1):
                if self.verificar_espaco(xx,yy,p.largura,p.altura):
                    c=self.custo_posicao(xx,yy,p.largura,p.altura)
                    if c<best[0]: best=(c,xx,yy)
        return best

    def colocar(self,p:Peca,x:int,y:int,custo_laser_incremental:float=0.0):
        p.x,p.y=x,y; self.ocupar_espaco(x,y,p.largura,p.altura); self.pecas.append(p)
        self.laser_corte+=float(custo_laser_incremental)

def _desenhar_placa_png(placa:Placa, idx:int, destino:Path):
    fig,ax=plt.subplots(1,1,figsize=(8,6))
    ax.set_xlim(0,PLACA_LARGURA); ax.set_ylim(0,PLACA_ALTURA); ax.set_aspect('equal'); ax.grid(True,alpha=0.25)
    ax.set_title(f'Placa {idx}',fontsize=14,fontweight='bold')
    ax.set_xlabel('Largura (cm)'); ax.set_ylabel('Altura (cm)')
    ax.add_patch(patches.Rectangle((0,0),PLACA_LARGURA,PLACA_ALTURA,linewidth=2.5,edgecolor='black',facecolor='lightgray',alpha=0.25))
    ax.add_patch(patches.Rectangle((MARGEM,MARGEM),PLACA_LARGURA-2*MARGEM,PLACA_ALTURA-2*MARGEM,linewidth=1.5,edgecolor='#6b7280',facecolor='none',linestyle='--'))
    cmap=matplotlib.colormaps['Set3'].colors
    for p in placa.pecas:
        color=cmap[(p.id)%len(cmap)]
        ax.add_patch(patches.Rectangle((p.x,p.y),p.largura,p.altura,linewidth=2,edgecolor='black',facecolor=color,alpha=0.8))
        ax.text(p.x+p.largura/2,p.y+p.altura/2,f"P{p.id}\n{p.largura}×{p.altura}",ha='center',va='center',fontsize=10,fontweight='bold',color='#111827')
    destino.parent.mkdir(parents=True,exist_ok=True); plt.tight_layout(); fig.savefig(str(destino),dpi=150,bbox_inches='tight'); plt.close(fig)

def _calcular_solucao(pecas_ordenadas:List[Peca])->Tuple[List[Placa],float]:
    placas=[Placa()]; custo_total=PLACA_CUSTO
    for p in pecas_ordenadas:
        melhor_c,best_idx,bx,by=float('inf'),None,-1,-1
        for i,pl in enumerate(placas):
            c,x,y=pl.melhor_posicao(p)
            if c<melhor_c: melhor_c,best_idx,bx,by=c,i,x,y
        pl_nova=Placa(); c_n,x_n,y_n=pl_nova.melhor_posicao(p)
        custo_nova=(PLACA_CUSTO+c_n) if c_n!=float('inf') else float('inf')
        if custo_nova<melhor_c:
            pl=Placa(); pl.colocar(p,x_n,y_n,custo_laser_incremental=c_n); placas.append(pl); custo_total+=PLACA_CUSTO+c_n
        else:
            if best_idx is None: return [], float('inf')
            placas[best_idx].colocar(p,bx,by,custo_laser_incremental=melhor_c); custo_total+=melhor_c
    return placas, custo_total

def _salvar_solucao(out_dir:Path, placas:List[Placa], custo_total:float, tempo:float):
    out_dir.mkdir(parents=True,exist_ok=True)
    for i,pl in enumerate(placas, start=1): _desenhar_placa_png(pl,i,out_dir/f"placa_{i:02d}.png")
    linhas=[f"Placas: {len(placas)}",f"Custo: R${custo_total:.2f}",f"Tempo: {tempo:.3f}s","", "[Por placa]"]
    for i,pl in enumerate(placas,start=1):
        linhas.append(f"Placa {i:02d}: Chapa R${PLACA_CUSTO:.2f} | Laser R${pl.laser_corte:.2f} | Total R${(PLACA_CUSTO+pl.laser_corte):.2f}")
    (out_dir/"info.txt").write_text("\n".join(linhas)+"\n",encoding='utf-8')

def _next_solution_index()->int:
    rx=re.compile(r"solucao\s*#\s*(\d+)$",re.I); nums=[]
    for p in OUTPUT_DIR.glob("solucao # *"):
        m=rx.search(p.name)
        if m: nums.append(int(m.group(1)))
    return (max(nums)+1) if nums else 1

def forca_bruta_total(caminho_txt:Path):
    pares=_parse_txt_content(caminho_txt.read_text(encoding='utf-8'))
    pecas=[(w,h,i+1) for i,(w,h) in enumerate(pares)]
    melhor_custo=float('inf'); melhor_placas=[]; t0=time.time(); serial=_next_solution_index()-1
    for _,ordem in enumerate(permutations(range(len(pecas))), start=1):
        ord_pecas=[Peca(*pecas[i]) for i in ordem]
        placas,custo=_calcular_solucao(ord_pecas)
        if custo<melhor_custo:
            melhor_custo=custo; melhor_placas=placas; serial+=1
            _salvar_solucao(OUTPUT_DIR/f"solucao # {serial}",melhor_placas,melhor_custo,time.time()-t0)
    if melhor_placas: _salvar_solucao(OUTPUT_DIR/"solucao final",melhor_placas,melhor_custo,time.time()-t0)

# watcher BRUTO
_cache_lock=threading.Lock()
_cache:Dict[Path,Dict]={}
def _dir_latest_mtime(p:Path)->float:
    mt=p.stat().st_mtime
    for c in p.glob("*"):
        try: mt=max(mt,c.stat().st_mtime)
        except: pass
    return mt
def _load_solution_dir(p:Path)->Dict:
    with _cache_lock:
        mt=_dir_latest_mtime(p); entry=_cache.get(p)
        if entry and abs(entry['mt']-mt)<1e-6: return entry
    imgs=[]
    for f in sorted(p.glob("*.png")):
        b64=base64.b64encode(f.read_bytes()).decode('ascii'); imgs.append(f"data:image/png;base64,{b64}")
    info=(p/"info.txt").read_text(encoding='utf-8') if (p/"info.txt").exists() else ""
    data={'mt':mt,'images':imgs,'info':info}
    with _cache_lock: _cache[p]=data
    return data
def _pick_last_two()->Tuple[Path,Path]:
    rx=re.compile(r"solucao\s*#\s*(\d+)$",re.I); nums=[]
    for p in OUTPUT_DIR.glob("solucao # *"):
        m=rx.search(p.name)
        if m: nums.append((int(m.group(1)),p))
    if not nums: return (None,None)
    nums.sort(key=lambda t:t[0],reverse=True); return nums[0][1], (nums[1][1] if len(nums)>1 else None)

# ============================================================
# ==============  MAXRECT (HEURÍSTICA)  ======================
# ============================================================
THIN_GAP_CM=6
THIN_PENAL=0.25
RAND_RESTARTS=4

class MRPiece:
    def __init__(self,w:int,h:int,pid:int):
        self.w=w; self.h=h; self.id=pid; self.x=0; self.y=0; self.plate_index=0

class MRFreeRect:
    def __init__(self,x:int,y:int,w:int,h:int):
        self.x=x; self.y=y; self.w=w; self.h=h
    def fits(self,w:int,h:int)->bool: return (w<=self.w) and (h<=self.h)
    def as_tup(self): return (self.x,self.y,self.w,self.h)

def _intersect(a:MRFreeRect,b:MRFreeRect)->bool:
    return not (a.x+a.w<=b.x or b.x+b.w<=a.x or a.y+a.h<=b.y or b.y+b.h<=a.y)

class MRPlate:
    def __init__(self,idx:int):
        self.idx=idx; self.W=PLACA_LARGURA; self.H=PLACA_ALTURA
        usable=MRFreeRect(MARGEM,MARGEM,self.W-2*MARGEM,self.H-2*MARGEM)
        self.free=[usable]; self.placed:List[MRPiece]=[]
        self.grid=[[False]*self.W for _ in range(self.H)]
        self.laser_cost=0.0

    def _mark_grid(self,x:int,y:int,w:int,h:int,val=True):
        for yy in range(y,y+h):
            row=self.grid[yy]
            for xx in range(x,x+w): row[xx]=val

    def _shared_border(self,x:int,y:int,w:int,h:int)->int:
        comp=0
        if y>0:
            row=self.grid[y-1]
            for xx in range(x,x+w):
                if row[xx]: comp+=1
        if y+h<self.H:
            row=self.grid[y+h]
            for xx in range(x,x+w):
                if row[xx]: comp+=1
        if x>0:
            for yy in range(y,y+h):
                if self.grid[yy][x-1]: comp+=1
        if x+w<self.W:
            for yy in range(y,y+h):
                if self.grid[yy][x+w]: comp+=1
        return comp

    def _wall_contact(self,x:int,y:int,w:int,h:int)->int:
        c=0
        if y==MARGEM: c+=w
        if y+h==self.H-MARGEM: c+=w
        if x==MARGEM: c+=h
        if x+w==self.W-MARGEM: c+=h
        return c

    def _split_free_rectangles(self, placed:MRFreeRect):
        out=[]
        for fr in self.free:
            if not _intersect(fr,placed): out.append(fr); continue
            if placed.x>fr.x: out.append(MRFreeRect(fr.x,fr.y,placed.x-fr.x,fr.h))
            if placed.x+placed.w<fr.x+fr.w:
                out.append(MRFreeRect(placed.x+placed.w,fr.y,fr.x+fr.w-(placed.x+placed.w),fr.h))
            if placed.y>fr.y: out.append(MRFreeRect(fr.x,fr.y,fr.w,placed.y-fr.y))
            if placed.y+placed.h<fr.y+fr.h:
                out.append(MRFreeRect(fr.x,placed.y+placed.h,fr.w,fr.y+fr.h-(placed.y+placed.h)))
        # prune contidos
        pruned=[]
        for i,r in enumerate(out):
            contained=False
            for j,s in enumerate(out):
                if i==j: continue
                if (r.x>=s.x and r.y>=s.y and r.x+r.w<=s.x+s.w and r.y+r.h<=s.y+s.h): contained=True; break
            if not contained and r.w>0 and r.h>0: pruned.append(r)
        self.free=pruned

    def _thin_penalty(self,leftover_h:int,leftover_v:int)->float:
        pen=0.0
        if leftover_h<THIN_GAP_CM: pen+=(THIN_GAP_CM-leftover_h)*THIN_PENAL
        if leftover_v<THIN_GAP_CM: pen+=(THIN_GAP_CM-leftover_v)*THIN_PENAL
        return pen

    def best_position(self, piece:MRPiece):
        best_score=None; best=(float('inf'),-1,-1,-1,None)
        for k,fr in enumerate(self.free):
            if not fr.fits(piece.w,piece.h): continue
            x,y=fr.x,fr.y
            leftover_h=fr.w-piece.w; leftover_v=fr.h-piece.h
            short_fit=min(leftover_h,leftover_v); long_fit=max(leftover_h,leftover_v)
            shared=self._shared_border(x,y,piece.w,piece.h); walls=self._wall_contact(x,y,piece.w,piece.h)
            contact=shared+walls
            perim=2*(piece.w+piece.h); laser=(perim-shared)*LASER_CUSTO_POR_CM
            thin=self._thin_penalty(leftover_h,leftover_v)
            score=(short_fit,long_fit,thin,-contact,laser)
            if (best_score is None) or (score<best_score):
                best_score=score; best=(laser,x,y,k,score)
        return best

    def place_and_get_deltas(self, piece:MRPiece, x:int,y:int,free_idx:int, laser_inc:float):
        # captura antes
        old_free=[MRFreeRect(r.x,r.y,r.w,r.h) for r in self.free]
        # coloca
        piece.x,piece.y=x,y; piece.plate_index=self.idx
        self.placed.append(piece); self._mark_grid(x,y,piece.w,piece.h,True)
        placed_rect=MRFreeRect(x,y,piece.w,piece.h)
        self._split_free_rectangles(placed_rect)
        self.laser_cost+=float(laser_inc)
        new_free=[MRFreeRect(r.x,r.y,r.w,r.h) for r in self.free]
        return placed_rect, old_free, new_free

# --------- desenho DEBUG forte (pre/split/after) ----------
def _draw_cuts(ax, placed:MRFreeRect, fr_list:List[MRFreeRect]):
    # desenha linhas laranja nas bordas do 'placed' dentro das interseções
    for fr in fr_list:
        if not _intersect(fr, placed): continue
        # verticals
        x1=placed.x; x2=placed.x+placed.w
        y_low=max(fr.y, placed.y); y_high=min(fr.y+fr.h, placed.y+placed.h)
        ax.plot([x1,x1],[y_low,y_high], linewidth=2.0, color='#f97316')
        ax.plot([x2,x2],[y_low,y_high], linewidth=2.0, color='#f97316')
        # horizontals
        y1=placed.y; y2=placed.y+placed.h
        x_low=max(fr.x, placed.x); x_high=min(fr.x+fr.w, placed.x+placed.w)
        ax.plot([x_low,x_high],[y1,y1], linewidth=2.0, color='#f97316')
        ax.plot([x_low,x_high],[y2,y2], linewidth=2.0, color='#f97316')

def _set_base(ax, titulo):
    ax.set_xlim(0, PLACA_LARGURA); ax.set_ylim(0, PLACA_ALTURA)
    ax.set_aspect('equal'); ax.grid(True, alpha=0.25)
    ax.set_title(titulo, fontsize=12, fontweight='bold')
    ax.add_patch(patches.Rectangle((0,0), PLACA_LARGURA, PLACA_ALTURA, linewidth=2, edgecolor='black', facecolor='lightgray', alpha=0.2))
    ax.add_patch(patches.Rectangle((MARGEM,MARGEM), PLACA_LARGURA-2*MARGEM, PLACA_ALTURA-2*MARGEM, linewidth=1.5, edgecolor='#6b7280', facecolor='none', linestyle='--'))

def _mr_draw_stage(plates:List[MRPlate], plate_idx:int, stage:str, destino:Path,
                   placed:MRFreeRect=None, old_free:List[MRFreeRect]=None, new_free:List[MRFreeRect]=None):
    # stage in {"pre","split","after"}
    cols = len(plates)
    fig, axes = plt.subplots(1, cols, figsize=(8*cols, 6))
    if not isinstance(axes, (list, np.ndarray)): axes=[axes]
    cmap=matplotlib.colormaps['Set3'].colors

    for i,pl in enumerate(plates):
        ax=axes[i]; _set_base(ax, f"Placa {i+1} — {stage.upper()}")
        # peças já colocadas (pre/split não “preenchem” a nova peça)
        for p in pl.placed:
            ax.add_patch(patches.Rectangle((p.x,p.y), p.w, p.h, linewidth=2, edgecolor='black', facecolor=cmap[(p.id)%len(cmap)], alpha=0.85))
            ax.text(p.x+p.w/2, p.y+p.h/2, f"P{p.id}", ha='center', va='center', fontsize=10, fontweight='bold')

        # livres default (azul)
        for fr in pl.free:
            ax.add_patch(patches.Rectangle((fr.x,fr.y),fr.w,fr.h,linewidth=1.2,edgecolor='#0284c7',facecolor='none',linestyle=':'))

        if i==plate_idx:
            if stage=='pre':
                # antigos livres em azul mais forte e cortes
                if old_free:
                    for fr in old_free:
                        ax.add_patch(patches.Rectangle((fr.x,fr.y),fr.w,fr.h,linewidth=1.8,edgecolor='#0369a1',facecolor='none',linestyle='--'))
                if placed:
                    # contorno da peça a entrar (vermelho)
                    ax.add_patch(patches.Rectangle((placed.x,placed.y),placed.w,placed.h,linewidth=3,edgecolor='#ef4444',facecolor='none'))
                    # linhas de corte (laranja)
                    _draw_cuts(ax, placed, old_free or [])
            elif stage=='split':
                # destaca deltas: removidos (magenta), novos (verde)
                old_set = set(fr.as_tup() for fr in (old_free or []))
                new_set = set(fr.as_tup() for fr in (new_free or []))
                removed = old_set - new_set
                added   = new_set - old_set
                for (x,y,w,h) in removed:
                    ax.add_patch(patches.Rectangle((x,y),w,h,linewidth=2.2,edgecolor='#d946ef',facecolor='none',linestyle='-'))
                for (x,y,w,h) in added:
                    ax.add_patch(patches.Rectangle((x,y),w,h,linewidth=2.2,edgecolor='#22c55e',facecolor='none',linestyle='-'))
                if placed:
                    ax.add_patch(patches.Rectangle((placed.x,placed.y),placed.w,placed.h,linewidth=2.5,edgecolor='#ef4444',facecolor='none'))
            elif stage=='after':
                # nada extra além do estado atual: peça já está desenhada em pl.placed
                pass

    destino.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout(); fig.savefig(str(destino), dpi=150, bbox_inches='tight'); plt.close(fig)

def _mr_info_lines(plates: List[MRPlate], elapsed: float)->str:
    total=len(plates)*PLACA_CUSTO + sum(p.laser_cost for p in plates)
    linhas=[f"Placas: {len(plates)}", f"Custo: R${total:.2f}", f"Tempo: {elapsed:.3f}s", "", "[Por placa]"]
    for i,pl in enumerate(plates, start=1):
        linhas.append(f"Placa {i:02d}: Chapa R${PLACA_CUSTO:.2f} | Laser R${pl.laser_cost:.2f} | Total R${PLACA_CUSTO+pl.laser_cost:.2f}")
    return "\n".join(linhas)+"\n"

def _mr_build_orders(pairs:List[Tuple[int,int]])->List[List[Tuple[int,int,int]]]:
    base=[(w,h,i+1) for i,(w,h) in enumerate(pairs)]
    orders=[]
    orders.append(sorted(base, key=lambda t:t[0]*t[1], reverse=True))
    orders.append(sorted(base, key=lambda t:max(t[0],t[1]), reverse=True))
    orders.append(sorted(base, key=lambda t:t[1], reverse=True))
    orders.append(sorted(base, key=lambda t:t[0], reverse=True))
    orders.append(sorted(base, key=lambda t:2*(t[0]+t[1]), reverse=True))
    for _ in range(RAND_RESTARTS):
        tmp=base[:]; random.shuffle(tmp); orders.append(tmp)
    return orders

def _mr_run(order:List[Tuple[int,int,int]], draw_steps:bool)->Tuple[List[MRPlate],float]:
    plates=[MRPlate(0)]; t0=time.time(); step=0
    for (w,h,pid) in order:
        piece=MRPiece(w,h,pid)
        # best em existentes
        best_tuple=(None, float('inf'), -1,-1, -1, -1)  # (score, laser, x,y,k, plate_idx)
        target_plate=-1
        for pid_plate,pl in enumerate(plates):
            laser,x,y,k,score=pl.best_position(piece)
            if score is None: continue
            if (best_tuple[0] is None) or (score<best_tuple[0]):
                best_tuple=(score,laser,x,y,k,pid_plate); target_plate=pid_plate
        # nova
        new_pl=MRPlate(len(plates))
        laser2,x2,y2,k2,score2=new_pl.best_position(piece)
        delta_exist = best_tuple[1] if best_tuple[0] is not None else float('inf')
        delta_new   = (laser2 + PLACA_CUSTO) if score2 is not None else float('inf')
        use_new = (delta_new < delta_exist) or (math.isfinite(delta_exist) and math.isfinite(delta_new) and abs(delta_new-delta_exist)<1e-9 and (score2 is not None and (best_tuple[0] is None or score2<best_tuple[0])))

        if use_new:
            plates.append(new_pl); target_plate=len(plates)-1
            # PRE: antes de colocar na nova, livres são da nova placa (1 retângulo)
            if draw_steps:
                placed_rect=MRFreeRect(x2,y2,w,h)
                _mr_draw_stage(plates, target_plate, "pre",   MAXRECT_DIR/f"step_{step:03d}_pre.png",   placed=placed_rect, old_free=[MRFreeRect(MARGEM,MARGEM, new_pl.W-2*MARGEM, new_pl.H-2*MARGEM)])
            placed, old_free, new_free = new_pl.place_and_get_deltas(piece, x2,y2,k2, laser_inc=laser2)
            if draw_steps:
                _mr_draw_stage(plates, target_plate, "split", MAXRECT_DIR/f"step_{step:03d}_split.png", placed=placed, old_free=old_free, new_free=new_free)
                _mr_draw_stage(plates, target_plate, "after", MAXRECT_DIR/f"step_{step:03d}_after.png")
        else:
            if best_tuple[2] < 0:  # não coube (deveria ser raro)
                continue
            pid_pl = best_tuple[5]; pl = plates[pid_pl]
            placed_rect=MRFreeRect(best_tuple[2],best_tuple[3],w,h)
            if draw_steps:
                _mr_draw_stage(plates, pid_pl, "pre", MAXRECT_DIR/f"step_{step:03d}_pre.png", placed=placed_rect, old_free=[MRFreeRect(r.x,r.y,r.w,r.h) for r in pl.free])
            placed, old_free, new_free = pl.place_and_get_deltas(piece, best_tuple[2], best_tuple[3], best_tuple[4], laser_inc=best_tuple[1])
            if draw_steps:
                _mr_draw_stage(plates, pid_pl, "split", MAXRECT_DIR/f"step_{step:03d}_split.png", placed=placed, old_free=old_free, new_free=new_free)
                _mr_draw_stage(plates, pid_pl, "after", MAXRECT_DIR/f"step_{step:03d}_after.png")
        step+=1

    total_cost=len(plates)*PLACA_CUSTO + sum(p.laser_cost for p in plates)
    elapsed=time.time()-t0
    if draw_steps:
        (MAXRECT_DIR/"info.txt").write_text(_mr_info_lines(plates, elapsed), encoding='utf-8')
    return plates, total_cost

def maxrect_process(caminho_txt:Path):
    # limpa frames
    for f in MAXRECT_DIR.glob("*.png"):
        try: f.unlink()
        except: pass
    pares=_parse_txt_content(caminho_txt.read_text(encoding='utf-8'))
    orders=_mr_build_orders(pares)
    # escolhe melhor ordem sem desenhar
    best_cost=float('inf'); best_order=None
    for order in orders:
        plates,cost=_mr_run(order, draw_steps=False)
        if cost<best_cost: best_cost=cost; best_order=order
    # roda melhor ordem com desenho detalhado
    if best_order is not None: _mr_run(best_order, draw_steps=True)

# ============================================================
# API
# ============================================================
class Api:
    def __init__(self):
        self.window=None
        self._proc_lock=threading.Lock(); self._proc_running=False
        self._mr_lock=threading.Lock();   self._mr_running=False

    def carregar_entrada_texto(self, conteudo:str):
        try:
            pares=_parse_txt_content(conteudo)
            previews=[_desenhar_peca_preview(w,h,i+1) for i,(w,h) in enumerate(pares)]
            _save_latest_txt(conteudo); return {"images":previews}
        except Exception as e:
            return {"images":[], "error":str(e)}

    def forca_bruta(self):
        def _run():
            with self._proc_lock:
                if self._proc_running: return
                self._proc_running=True
            try:
                if not _last_txt_path.exists(): return
                forca_bruta_total(_last_txt_path)
            except Exception as e:
                print("[PROCESSAR] erro:", e)
            finally:
                self._proc_running=False
        threading.Thread(target=_run,daemon=True).start()
        return {"status":"started"}

    def get_solutions(self):
        last,pen=_pick_last_two()
        out={"processing":self._proc_running}
        if last and last.exists():
            d=_load_solution_dir(last); out['atual']={"images":d['images'],"info_text":d['info']}
        if pen and pen.exists():
            d=_load_solution_dir(pen);  out['antiga']={"images":d['images'],"info_text":d['info']}
        return out

    def maxrect(self):
        def _run():
            with self._mr_lock:
                if self._mr_running: return
                self._mr_running=True
            try:
                if not _last_txt_path.exists(): return
                maxrect_process(_last_txt_path)
            except Exception as e:
                print("[MAXRECT] erro:", e)
            finally:
                self._mr_running=False
        threading.Thread(target=_run,daemon=True).start()
        return {"status":"started"}

    def get_maxrect(self):
        # lê TODOS PNGs (pre/split/after/final) ordenados por nome
        files=sorted(MAXRECT_DIR.glob("*.png"))
        imgs=[]
        for f in files:
            try:
                b64=base64.b64encode(f.read_bytes()).decode('ascii')
                imgs.append(f"data:image/png;base64,{b64}")
            except: pass
        info=(MAXRECT_DIR/"info.txt").read_text(encoding='utf-8') if (MAXRECT_DIR/"info.txt").exists() else ""
        return {"processing":self._mr_running, "after":{"images":imgs,"info_text":info}}

# ============================================================
if __name__=="__main__":
    api=Api()
    win=webview.create_window("Corte de Placas - Interface", html=pagina_html, width=1920, height=1080, js_api=api)
    api.window=win
    webview.start(gui='edgechromium', debug=False)
