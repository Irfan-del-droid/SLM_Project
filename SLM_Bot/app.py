import streamlit as st
import ollama
import re
import zipfile
import io
import time
from datetime import datetime
from complexity import analyze_complexity
from detector import detect_language, detect_project_type

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="NEXUS · Code Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
#  FULL CSS INJECTION
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(r"""
<style>

/* ─── FONTS ─────────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@100;200;300;400;500;600;700;800;900&family=Orbitron:wght@400;500;600;700;800;900&family=Share+Tech+Mono&family=Syne+Mono&display=swap');

/* ─── CSS VARIABLES ─────────────────────────────────────────────────────── */
:root {
  --neon-cyan:     #00f5ff;
  --neon-blue:     #0080ff;
  --neon-teal:     #00ffcc;
  --neon-violet:   #7b2fff;
  --neon-orange:   #ff6b35;
  --neon-red:      #ff2255;
  --dark-void:     #01030a;
  --dark-deep:     #020610;
  --dark-mid:      #050e20;
  --dark-surface:  #081428;
  --dark-raised:   #0b1d38;
  --glass-bg:      rgba(8, 20, 40, 0.7);
  --glass-border:  rgba(0, 245, 255, 0.12);
  --text-primary:  #cce8ff;
  --text-secondary:#5a8aaa;
  --text-dim:      #2a4a6a;
  --font-display:  'Orbitron', monospace;
  --font-body:     'Exo 2', sans-serif;
  --font-mono:     'Share Tech Mono', monospace;
  --font-code:     'Syne Mono', monospace;
}

/* ─── GLOBAL RESET ──────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }
html, body {
  font-family: var(--font-body);
  background: var(--dark-void);
  color: var(--text-primary);
  overflow-x: hidden;
}

/* ─── APP BASE ──────────────────────────────────────────────────────────── */
.stApp {
  background: var(--dark-void) !important;
  min-height: 100vh;
  position: relative;
  overflow: hidden;
}

/* ─── LAYER 1: Aurora / Blob Gradients ─────────────────────────────────── */
.stApp::before {
  content: "";
  position: fixed;
  inset: 0;
  z-index: 0;
  background:
    radial-gradient(ellipse 70vw 50vh at -5% 5%,
      rgba(0, 180, 255, 0.09) 0%, transparent 70%),
    radial-gradient(ellipse 55vw 65vh at 108% 30%,
      rgba(0, 70, 255, 0.08) 0%, transparent 70%),
    radial-gradient(ellipse 80vw 40vh at 25% 105%,
      rgba(0, 255, 180, 0.07) 0%, transparent 70%),
    radial-gradient(ellipse 45vw 55vh at 92% -8%,
      rgba(110, 0, 255, 0.05) 0%, transparent 70%),
    radial-gradient(ellipse 100% 80% at 50% 0%,
      rgba(0, 25, 70, 0.5) 0%, var(--dark-void) 100%);
  animation: aurora-drift 22s ease-in-out infinite alternate;
  pointer-events: none;
}
@keyframes aurora-drift {
  0%   { opacity: 1;    transform: scale(1)    translateY(0px); }
  33%  { opacity: 0.85; transform: scale(1.04) translateY(-8px); }
  66%  { opacity: 1;    transform: scale(0.97) translateY(5px); }
  100% { opacity: 0.9;  transform: scale(1.02) translateY(-3px); }
}

/* ─── LAYER 2: Grid Lines ───────────────────────────────────────────────── */
.stApp::after {
  content: "";
  position: fixed;
  inset: 0;
  z-index: 0;
  background-image:
    repeating-linear-gradient(0deg,
      transparent 0px, transparent 59px,
      rgba(0, 200, 255, 0.035) 59px, rgba(0, 200, 255, 0.035) 60px),
    repeating-linear-gradient(90deg,
      transparent 0px, transparent 59px,
      rgba(0, 200, 255, 0.035) 59px, rgba(0, 200, 255, 0.035) 60px);
  animation: grid-breathe 9s ease-in-out infinite;
  pointer-events: none;
}
@keyframes grid-breathe {
  0%,100% { opacity: 0.5; }
  50%     { opacity: 1.0; }
}

/* ─── FLOATING ORB ELEMENTS (injected in HTML) ──────────────────────────── */
.orb {
  position: fixed;
  border-radius: 50%;
  filter: blur(90px);
  pointer-events: none;
  z-index: 0;
  will-change: transform;
}
.orb-1 {
  width: 700px; height: 700px;
  top: -250px; left: -250px;
  background: radial-gradient(circle, rgba(0,210,255,0.07) 0%, transparent 70%);
  animation: orb1 28s ease-in-out infinite;
}
.orb-2 {
  width: 550px; height: 550px;
  bottom: -180px; right: -180px;
  background: radial-gradient(circle, rgba(0,90,255,0.08) 0%, transparent 70%);
  animation: orb2 34s ease-in-out infinite;
}
.orb-3 {
  width: 450px; height: 450px;
  top: 38%; left: 55%;
  background: radial-gradient(circle, rgba(0,255,180,0.045) 0%, transparent 70%);
  animation: orb3 22s ease-in-out infinite;
}
.orb-4 {
  width: 350px; height: 350px;
  top: 18%; left: 25%;
  background: radial-gradient(circle, rgba(120,0,255,0.04) 0%, transparent 70%);
  animation: orb4 40s ease-in-out infinite;
}
.orb-5 {
  width: 250px; height: 250px;
  top: 65%; left: 10%;
  background: radial-gradient(circle, rgba(0,180,255,0.05) 0%, transparent 70%);
  animation: orb5 18s ease-in-out infinite;
}
@keyframes orb1 {
  0%,100%{ transform:translate(0,0)   scale(1);   }
  25%    { transform:translate(90px,70px) scale(1.1);  }
  50%    { transform:translate(-50px,130px) scale(0.9); }
  75%    { transform:translate(70px,-50px) scale(1.05); }
}
@keyframes orb2 {
  0%,100%{ transform:translate(0,0)     scale(1);   }
  33%    { transform:translate(-110px,-70px) scale(1.15); }
  66%    { transform:translate(60px,90px)  scale(0.88); }
}
@keyframes orb3 {
  0%,100%{ transform:translate(0,0)    scale(1);  }
  50%    { transform:translate(-90px,70px) scale(1.2); }
}
@keyframes orb4 {
  0%,100%{ transform:translate(0,0)   scale(1);   }
  40%    { transform:translate(70px,-90px) scale(0.85); }
  80%    { transform:translate(-35px,50px) scale(1.1); }
}
@keyframes orb5 {
  0%,100%{ transform:translate(0,0)   scale(1);  }
  50%    { transform:translate(60px,-40px) scale(1.15); }
}

/* ─── SCANLINES ─────────────────────────────────────────────────────────── */
.scanlines {
  position: fixed; inset: 0; z-index: 1;
  background: repeating-linear-gradient(
    0deg, transparent 0px, transparent 3px,
    rgba(0,245,255,0.007) 3px, rgba(0,245,255,0.007) 4px
  );
  pointer-events: none;
}

/* ─── MOVING SCAN BEAM ──────────────────────────────────────────────────── */
.scan-beam {
  position: fixed; left: 0; right: 0; height: 2px;
  z-index: 2;
  background: linear-gradient(90deg,
    transparent, rgba(0,245,255,0.12),
    rgba(0,245,255,0.35),
    rgba(0,245,255,0.12), transparent);
  animation: beam-sweep 10s linear infinite;
  pointer-events: none;
  filter: blur(1px);
}
@keyframes beam-sweep {
  0%   { top: -2px;  opacity: 0; }
  4%   { opacity: 1; }
  96%  { opacity: 0.25; }
  100% { top: 100vh; opacity: 0; }
}

/* ─── VIGNETTE ──────────────────────────────────────────────────────────── */
.vignette {
  position: fixed; inset: 0; z-index: 2;
  background: radial-gradient(ellipse 130% 130% at 50% 50%,
    transparent 35%, rgba(1,3,10,0.7) 100%);
  pointer-events: none;
}

/* ─── CORNER DECORATIONS ────────────────────────────────────────────────── */
.corner { position: fixed; width: 100px; height: 100px; z-index: 3; pointer-events: none; }
.corner::before, .corner::after {
  content: "";
  position: absolute;
  background: rgba(0,245,255,0.3);
}
.corner-tl { top:0; left:0; }
.corner-tl::before { top:0;left:0; width:2px; height:50px; }
.corner-tl::after  { top:0;left:0; width:50px; height:2px; }
.corner-tr { top:0; right:0; }
.corner-tr::before { top:0;right:0; width:2px; height:50px; }
.corner-tr::after  { top:0;right:0; width:50px; height:2px; }
.corner-bl { bottom:0; left:0; }
.corner-bl::before { bottom:0;left:0; width:2px; height:50px; }
.corner-bl::after  { bottom:0;left:0; width:50px; height:2px; }
.corner-br { bottom:0; right:0; }
.corner-br::before { bottom:0;right:0; width:2px; height:50px; }
.corner-br::after  { bottom:0;right:0; width:50px; height:2px; }

/* Corner inner dots */
.corner-tl::before { box-shadow: 8px 8px 0 rgba(0,245,255,0.15); }
.corner-br::before { box-shadow: -8px -8px 0 rgba(0,245,255,0.15); }

/* ─── MAIN CONTENT ──────────────────────────────────────────────────────── */
.main .block-container {
  position: relative;
  z-index: 10;
  padding-top: 0.5rem !important;
  padding-bottom: 7rem !important;
  max-width: 1050px !important;
}

/* ─── SIDEBAR ────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
  background: rgba(2, 6, 16, 0.98) !important;
  border-right: 1px solid rgba(0,245,255,0.09) !important;
  backdrop-filter: blur(25px);
  z-index: 20 !important;
  box-shadow: 6px 0 50px rgba(0,0,0,0.9), inset -1px 0 0 rgba(0,245,255,0.04);
}
[data-testid="stSidebar"]::before {
  content: "";
  position: absolute; inset: 0;
  background: repeating-linear-gradient(
    0deg, transparent 0px, transparent 39px,
    rgba(0,245,255,0.015) 39px, rgba(0,245,255,0.015) 40px
  );
  pointer-events: none;
}
[data-testid="stSidebar"] * { color: var(--text-primary) !important; }

/* ─── HEADER ─────────────────────────────────────────────────────────────── */
.nexus-header-wrap {
  text-align: center;
  padding: 1.8rem 0 1rem;
  position: relative;
  width: 100%;
  display: block;
  margin: 0 auto;
}

.nexus-logo-text {
  font-family: var(--font-display);
  font-size: clamp(2.4rem, 5.5vw, 3.8rem);
  font-weight: 900;
  letter-spacing: 0.22em;
  background: linear-gradient(135deg,
    #ffffff 0%,
    var(--neon-cyan) 25%,
    #5de8ff 50%,
    var(--neon-teal) 75%,
    var(--neon-blue) 100%
  );
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  filter: drop-shadow(0 0 25px rgba(0,245,255,0.55))
          drop-shadow(0 0 70px rgba(0,245,255,0.18));
  display: inline-block;
  animation: logo-flicker 8s ease-in-out infinite;
}
@keyframes logo-flicker {
  0%,89%,100% {
    filter: drop-shadow(0 0 25px rgba(0,245,255,0.55))
            drop-shadow(0 0 70px rgba(0,245,255,0.18));
  }
  90% {
    filter: drop-shadow(0 0 5px rgba(0,245,255,0.2))
            drop-shadow(0 0 12px rgba(0,245,255,0.08));
  }
  91% {
    filter: drop-shadow(0 0 25px rgba(0,245,255,0.55))
            drop-shadow(0 0 70px rgba(0,245,255,0.18));
  }
  93% {
    filter: drop-shadow(0 0 8px rgba(0,245,255,0.25))
            drop-shadow(0 0 20px rgba(0,245,255,0.1));
  }
  94% {
    filter: drop-shadow(0 0 25px rgba(0,245,255,0.55))
            drop-shadow(0 0 70px rgba(0,245,255,0.18));
  }
}
.nexus-bolt {
  display: inline-block;
  margin-right: 0.2em;
  filter: drop-shadow(0 0 18px rgba(0,245,255,0.9));
  animation: bolt-pulse 3s ease-in-out infinite;
}
@keyframes bolt-pulse {
  0%,100% { transform: scale(1) rotate(0deg);   }
  50%     { transform: scale(1.18) rotate(6deg); }
}
.nexus-tagline {
  font-family: var(--font-mono);
  font-size: 0.66rem;
  color: var(--neon-cyan);
  letter-spacing: 0.5em;
  opacity: 0.55;
  margin-top: 0.3rem;
  text-transform: uppercase;
}

/* ─── NEON RULE ─────────────────────────────────────────────────────────── */
.neon-rule {
  position: relative;
  height: 1px;
  margin: 0.8rem 0 1rem;
  background: linear-gradient(90deg,
    transparent 0%,
    rgba(0,245,255,0.08) 8%,
    rgba(0,245,255,0.5) 30%,
    var(--neon-cyan) 50%,
    rgba(0,245,255,0.5) 70%,
    rgba(0,245,255,0.08) 92%,
    transparent 100%
  );
  box-shadow: 0 0 14px rgba(0,245,255,0.35), 0 0 40px rgba(0,245,255,0.08);
  animation: rule-pulse 4s ease-in-out infinite;
}
@keyframes rule-pulse {
  0%,100% { opacity: 0.75; }
  50%     { opacity: 1; box-shadow: 0 0 22px rgba(0,245,255,0.5), 0 0 60px rgba(0,245,255,0.12); }
}
.neon-rule::before {
  content: "◆";
  position: absolute; left: 50%; top: 50%;
  transform: translate(-50%, -50%);
  font-size: 0.38rem;
  color: var(--neon-cyan);
  text-shadow: 0 0 8px var(--neon-cyan);
  background: var(--dark-void);
  padding: 0 4px;
}

/* ─── SIDEBAR HEADER ────────────────────────────────────────────────────── */
.sidebar-header {
  background: linear-gradient(180deg, rgba(0,245,255,0.04) 0%, transparent 100%);
  border-bottom: 1px solid rgba(0,245,255,0.08);
  padding: 1.4rem 1rem 0.9rem;
  text-align: center;
}
.sidebar-logo {
  font-family: var(--font-display);
  font-size: 1.05rem;
  font-weight: 900;
  letter-spacing: 0.35em;
  background: linear-gradient(135deg, var(--neon-cyan), var(--neon-teal));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  filter: drop-shadow(0 0 8px rgba(0,245,255,0.4));
}
.sidebar-version {
  font-family: var(--font-mono);
  font-size: 0.55rem;
  color: var(--text-dim);
  letter-spacing: 0.3em;
  margin-top: 3px;
}

/* ─── STATUS BAR ─────────────────────────────────────────────────────────── */
.status-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(0,255,180,0.04);
  border: 1px solid rgba(0,255,180,0.1);
  border-radius: 7px;
  padding: 0.45rem 0.8rem;
  margin: 0.7rem 0;
  font-family: var(--font-mono);
  font-size: 0.67rem;
  color: var(--neon-teal);
  letter-spacing: 0.08em;
}
.status-dot {
  width: 7px; height: 7px;
  border-radius: 50%;
  background: var(--neon-teal);
  box-shadow: 0 0 10px var(--neon-teal), 0 0 25px rgba(0,255,180,0.4);
  flex-shrink: 0;
  animation: heartbeat 2.2s ease-in-out infinite;
}
@keyframes heartbeat {
  0%,100%{ transform:scale(1);   opacity:1;   }
  25%    { transform:scale(1.5); opacity:0.75; }
  55%    { transform:scale(1);   opacity:1;   }
  75%    { transform:scale(1.25);opacity:0.85; }
}

/* ─── SIDEBAR SECTION LABELS ────────────────────────────────────────────── */
.sbl {
  font-family: var(--font-display);
  font-size: 0.52rem;
  letter-spacing: 0.35em;
  color: var(--text-dim);
  text-transform: uppercase;
  margin: 1.1rem 0 0.45rem;
  padding-bottom: 4px;
  border-bottom: 1px solid rgba(0,245,255,0.05);
  display: flex; align-items: center; gap: 6px;
}
.sbl::before {
  content: "";
  display: inline-block;
  width: 14px; height: 1px;
  background: linear-gradient(90deg, var(--neon-cyan), transparent);
}

/* ─── STAT ROWS ──────────────────────────────────────────────────────────── */
.stat-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 0.42rem 0;
  border-bottom: 1px solid rgba(0,245,255,0.03);
  font-family: var(--font-mono);
  font-size: 0.68rem;
}
.stat-label { color: var(--text-dim); letter-spacing: 0.04em; }
.stat-value {
  color: var(--neon-cyan);
  font-weight: 600;
  text-shadow: 0 0 10px rgba(0,245,255,0.35);
}

/* ─── ANALYSIS PANEL ─────────────────────────────────────────────────────── */
.analysis-panel {
  background: rgba(0,8,25,0.6);
  border: 1px solid rgba(0,245,255,0.09);
  border-radius: 10px;
  overflow: hidden;
  margin: 0.5rem 0;
}
.ap-header {
  background: linear-gradient(90deg, rgba(0,245,255,0.07), transparent);
  border-bottom: 1px solid rgba(0,245,255,0.07);
  padding: 0.45rem 0.8rem;
  font-family: var(--font-display);
  font-size: 0.52rem;
  letter-spacing: 0.3em;
  color: var(--neon-cyan);
  display: flex; align-items: center; gap: 6px;
}
.ap-row {
  padding: 0.42rem 0.8rem;
  border-bottom: 1px solid rgba(0,245,255,0.03);
  display: flex; justify-content: space-between; align-items: center;
}
.ap-row:last-child { border-bottom: none; }
.ap-key  { font-family:var(--font-mono);font-size:0.6rem;color:var(--text-dim);letter-spacing:0.06em; }
.ap-val  { font-family:var(--font-mono);font-size:0.68rem;color:var(--text-primary);font-weight:600; }

/* ─── COMPLEXITY METER ───────────────────────────────────────────────────── */
.cx-meter { padding: 0.55rem 0.8rem; background: rgba(0,4,12,0.5); }
.cx-bar-bg {
  height: 3px; background: rgba(0,245,255,0.07);
  border-radius: 2px; overflow: hidden; margin-top: 7px;
}
.cx-bar { height: 100%; border-radius: 2px; }
.cx-bar.beginner     { background:linear-gradient(90deg,#00ffcc,#00e0aa);width:22%;box-shadow:0 0 6px rgba(0,255,204,0.5); }
.cx-bar.intermediate { background:linear-gradient(90deg,#00b4ff,#0055ff);width:58%;box-shadow:0 0 6px rgba(0,180,255,0.5); }
.cx-bar.advanced     { background:linear-gradient(90deg,#ff6b35,#ff2255);width:94%;box-shadow:0 0 6px rgba(255,107,53,0.5); }

/* ─── MODE CARD ──────────────────────────────────────────────────────────── */
.mode-card {
  position: relative;
  border-radius: 9px;
  padding: 0.65rem 1rem;
  margin: 0.4rem 0;
  overflow: hidden;
  font-family: var(--font-mono);
  font-size: 0.7rem;
  letter-spacing: 0.07em;
  display: flex; align-items: center; gap: 8px;
  border: 1px solid;
  transition: all 0.3s;
}
.mode-card::before {
  content: "";
  position: absolute; inset: 0;
  opacity: 0.05;
  background: currentColor;
}
.mode-generate   { color:var(--neon-teal);  border-color:rgba(0,255,180,0.2);  background:rgba(0,255,180,0.04); }
.mode-debug      { color:var(--neon-orange); border-color:rgba(255,107,53,0.2); background:rgba(255,107,53,0.04); }
.mode-optimize   { color:var(--neon-cyan);   border-color:rgba(0,245,255,0.2);  background:rgba(0,245,255,0.04); }
.mode-explain    { color:#c084fc;            border-color:rgba(192,132,252,0.2);background:rgba(192,132,252,0.04); }
.mode-enterprise { color:#ffd700;            border-color:rgba(255,215,0,0.2);  background:rgba(255,215,0,0.04); }

/* ─── CHAT MESSAGES ──────────────────────────────────────────────────────── */
[data-testid="stChatMessage"] {
  position: relative;
  background: rgba(6,16,38,0.72) !important;
  border: 1px solid rgba(0,245,255,0.1) !important;
  border-radius: 14px !important;
  margin-bottom: 1.1rem !important;
  padding: 1.1rem !important;
  backdrop-filter: blur(18px) !important;
  box-shadow:
    0 4px 28px rgba(0,0,0,0.55),
    inset 0 1px 0 rgba(0,245,255,0.07),
    inset 0 -1px 0 rgba(0,0,0,0.3) !important;
  transition: border-color 0.3s, box-shadow 0.3s;
  overflow: hidden;
}
[data-testid="stChatMessage"]::before {
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent 5%, rgba(0,245,255,0.25) 50%, transparent 95%);
}
[data-testid="stChatMessage"]:hover {
  border-color: rgba(0,245,255,0.2) !important;
  box-shadow:
    0 6px 40px rgba(0,0,0,0.65),
    0 0 0 1px rgba(0,245,255,0.04),
    inset 0 1px 0 rgba(0,245,255,0.1) !important;
}

/* ─── CODE BLOCKS ────────────────────────────────────────────────────────── */
code:not(pre code) {
  font-family: var(--font-code) !important;
  font-size: 0.84em !important;
  background: rgba(0,245,255,0.055) !important;
  border: 1px solid rgba(0,245,255,0.14) !important;
  border-radius: 4px !important;
  padding: 0.08em 0.4em !important;
  color: var(--neon-cyan) !important;
}
pre {
  font-family: var(--font-code) !important;
  background: rgba(1,4,12,0.97) !important;
  border: 1px solid rgba(0,245,255,0.14) !important;
  border-radius: 12px !important;
  box-shadow:
    0 0 0 1px rgba(0,0,0,0.6),
    0 8px 35px rgba(0,0,0,0.7),
    inset 0 1px 0 rgba(0,245,255,0.07),
    0 0 50px rgba(0,245,255,0.025) !important;
  position: relative;
  overflow: hidden !important;
}
pre::before {
  content: "";
  position: absolute; top:0;left:0;right:0; height:2px;
  background: linear-gradient(90deg,
    var(--neon-violet), var(--neon-blue), var(--neon-cyan), var(--neon-teal));
  opacity: 0.75;
}
pre code {
  font-family: var(--font-code) !important;
  background: transparent !important;
  border: none !important;
  color: #9dd9ff !important;
  font-size: 0.82rem !important;
  line-height: 1.7 !important;
}

/* ─── CHAT INPUT ─────────────────────────────────────────────────────────── */
[data-testid="stChatInputContainer"] {
  position: fixed !important;
  bottom: 0 !important; left: 0 !important; right: 0 !important;
  z-index: 100 !important;
  background: rgba(1,3,10,0.94) !important;
  backdrop-filter: blur(35px) !important;
  border-top: 1px solid rgba(0,245,255,0.09) !important;
  padding: 0.9rem 2.5rem 1.1rem !important;
  box-shadow: 0 -25px 70px rgba(0,0,0,0.85) !important;
}
[data-testid="stChatInputContainer"]::before {
  content: "";
  position: absolute; top:0;left:0;right:0;height:1px;
  background: linear-gradient(90deg,
    transparent, rgba(0,245,255,0.45), rgba(0,100,255,0.35), transparent);
}
[data-testid="stChatInput"] {
  background: rgba(3,10,28,0.97) !important;
  border: 1px solid rgba(0,245,255,0.18) !important;
  border-radius: 12px !important;
  color: var(--text-primary) !important;
  font-family: var(--font-body) !important;
  font-size: 0.93rem !important;
  transition: all 0.3s !important;
  box-shadow: inset 0 2px 10px rgba(0,0,0,0.5) !important;
}
[data-testid="stChatInput"]:focus-within {
  border-color: rgba(0,245,255,0.45) !important;
  box-shadow:
    inset 0 2px 10px rgba(0,0,0,0.5),
    0 0 0 3px rgba(0,245,255,0.055),
    0 0 25px rgba(0,245,255,0.08) !important;
}
[data-testid="stChatInput"] button {
  background: linear-gradient(135deg,rgba(0,80,200,0.55),rgba(0,200,255,0.3)) !important;
  border: 1px solid rgba(0,245,255,0.28) !important;
  border-radius: 8px !important;
  transition: all 0.2s !important;
}
[data-testid="stChatInput"] button:hover {
  background: linear-gradient(135deg,rgba(0,120,255,0.75),rgba(0,245,255,0.45)) !important;
  box-shadow: 0 0 18px rgba(0,245,255,0.3) !important;
  transform: scale(1.06) !important;
}

/* ─── BUTTONS ────────────────────────────────────────────────────────────── */
.stButton > button {
  position: relative;
  font-family: var(--font-mono) !important;
  font-size: 0.7rem !important;
  letter-spacing: 0.12em !important;
  background: linear-gradient(135deg,rgba(0,40,110,0.55),rgba(0,90,190,0.3)) !important;
  border: 1px solid rgba(0,245,255,0.22) !important;
  color: var(--neon-cyan) !important;
  border-radius: 8px !important;
  padding: 0.5rem 1rem !important;
  transition: all 0.25s !important;
  overflow: hidden !important;
}
.stButton > button:hover {
  border-color: rgba(0,245,255,0.55) !important;
  box-shadow: 0 0 22px rgba(0,245,255,0.18), inset 0 1px 0 rgba(0,245,255,0.18) !important;
  transform: translateY(-1px) !important;
  color: #fff !important;
}
.stButton > button:active { transform: translateY(0) !important; }

.stDownloadButton > button {
  font-family: var(--font-mono) !important;
  font-size: 0.7rem !important;
  letter-spacing: 0.12em !important;
  background: linear-gradient(135deg,rgba(0,15,50,0.75),rgba(0,50,140,0.4)) !important;
  border: 1px solid rgba(0,245,255,0.18) !important;
  color: var(--neon-cyan) !important;
  border-radius: 8px !important;
  transition: all 0.25s !important;
}
.stDownloadButton > button:hover {
  background: linear-gradient(135deg,rgba(0,50,140,0.75),rgba(0,120,255,0.4)) !important;
  border-color: rgba(0,245,255,0.5) !important;
  box-shadow: 0 0 20px rgba(0,245,255,0.16) !important;
  transform: translateY(-1px) !important;
  color: #fff !important;
}

/* danger button wrapper */
.danger-btn .stButton > button {
  background: linear-gradient(135deg,rgba(70,0,15,0.55),rgba(140,0,35,0.3)) !important;
  border-color: rgba(255,34,85,0.22) !important;
  color: rgba(255,100,130,0.9) !important;
}
.danger-btn .stButton > button:hover {
  border-color: rgba(255,34,85,0.55) !important;
  box-shadow: 0 0 18px rgba(255,34,85,0.18) !important;
  color: #ff4466 !important;
}

/* ─── SELECTBOX ──────────────────────────────────────────────────────────── */
[data-testid="stSelectbox"] > div > div {
  background: rgba(3,10,28,0.97) !important;
  border: 1px solid rgba(0,245,255,0.16) !important;
  border-radius: 9px !important;
  color: var(--text-primary) !important;
  font-family: var(--font-body) !important;
  font-size: 0.87rem !important;
}
[data-testid="stSelectbox"] > div > div:hover {
  border-color: rgba(0,245,255,0.38) !important;
}

/* ─── BADGES ─────────────────────────────────────────────────────────────── */
.badge {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 0.18em 0.7em;
  border-radius: 20px;
  font-family: var(--font-mono);
  font-size: 0.68rem;
  letter-spacing: 0.05em;
  border: 1px solid;
  transition: all 0.2s;
}
.badge:hover { filter: brightness(1.25); transform: translateY(-1px); }
.badge-lang  { color:#00ffcc;border-color:rgba(0,255,204,0.3);background:rgba(0,255,204,0.06); }
.badge-type  { color:#00b4ff;border-color:rgba(0,180,255,0.3);background:rgba(0,180,255,0.06); }
.badge-begin { color:#00ffcc;border-color:rgba(0,255,204,0.3);background:rgba(0,255,204,0.06); }
.badge-inter { color:#00b4ff;border-color:rgba(0,180,255,0.3);background:rgba(0,180,255,0.06); }
.badge-adv   { color:#ff2255;border-color:rgba(255,34,85,0.3); background:rgba(255,34,85,0.06); }

/* ─── THINKING / DOTS ────────────────────────────────────────────────────── */
.thinking-box {
  display: flex; align-items: center; gap: 10px;
  padding: 0.75rem 1rem;
  background: rgba(0,5,20,0.55);
  border: 1px solid rgba(0,245,255,0.09);
  border-radius: 10px;
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: var(--text-secondary);
  letter-spacing: 0.08em;
}
.thinking-dots { display: flex; gap: 4px; }
.thinking-dots span {
  width: 5px; height: 5px; border-radius: 50%;
  background: var(--neon-cyan);
  animation: dot-bounce 1.4s ease-in-out infinite both;
}
.thinking-dots span:nth-child(2) { animation-delay: 0.2s; }
.thinking-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes dot-bounce {
  0%,80%,100% { transform: translateY(0);  opacity: 0.35; }
  40%         { transform: translateY(-7px);opacity: 1; }
}

/* ─── WELCOME CARDS ──────────────────────────────────────────────────────── */
.welcome-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.7rem;
  margin: 1.3rem 0;
}
.wcard {
  position: relative;
  background: rgba(4,12,30,0.72);
  border: 1px solid rgba(0,245,255,0.08);
  border-radius: 12px;
  padding: 1rem 1.1rem;
  transition: all 0.3s;
  overflow: hidden;
}
.wcard::after {
  content: "";
  position: absolute; top:0;left:0;right:0;height:1px;
  background: linear-gradient(90deg, transparent, rgba(0,245,255,0.18), transparent);
  opacity: 0;
  transition: opacity 0.3s;
}
.wcard:hover {
  border-color: rgba(0,245,255,0.22);
  transform: translateY(-3px);
  box-shadow: 0 12px 35px rgba(0,0,0,0.45), 0 0 25px rgba(0,245,255,0.04);
}
.wcard:hover::after { opacity: 1; }
.wcard-icon  { font-size: 1.4rem; margin-bottom: 0.35rem; display: block; }
.wcard-title {
  font-family: var(--font-display);
  font-size: 0.68rem; letter-spacing: 0.1em;
  color: var(--neon-cyan); margin-bottom: 0.25rem;
}
.wcard-desc  { font-family:var(--font-body);font-size:0.76rem;color:var(--text-dim);line-height:1.4; }

/* ─── SCROLLBAR ──────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 3px; height: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(0,245,255,0.18); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,245,255,0.45); }

/* ─── CURSOR ─────────────────────────────────────────────────────────────── */
* { cursor: crosshair !important; }
input, textarea { cursor: text !important; }
button, [role="button"], a, select { cursor: pointer !important; }

/* ─── MISC OVERRIDES ─────────────────────────────────────────────────────── */
.stApp > header,
[data-testid="stHeader"],
[data-testid="stToolbar"] { background: transparent !important; box-shadow: none !important; }
.element-container { background: transparent !important; }
hr {
  border: none !important; height: 1px !important;
  background: linear-gradient(90deg, transparent, rgba(0,245,255,0.18), transparent) !important;
  margin: 0.9rem 0 !important;
}
::selection { background: rgba(0,245,255,0.18); color: #fff; }

/* Avatar */
[data-testid^="chatAvatarIcon"] {
  background: rgba(0,25,65,0.85) !important;
  border: 1px solid rgba(0,245,255,0.2) !important;
  box-shadow: 0 0 12px rgba(0,245,255,0.08) !important;
}

</style>

<!-- Atmosphere layers -->
<div class="orb orb-1"></div>
<div class="orb orb-2"></div>
<div class="orb orb-3"></div>
<div class="orb orb-4"></div>
<div class="orb orb-5"></div>
<div class="scanlines"></div>
<div class="scan-beam"></div>
<div class="vignette"></div>
<div class="corner corner-tl"></div>
<div class="corner corner-tr"></div>
<div class="corner corner-bl"></div>
<div class="corner corner-br"></div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════
MODEL = "hf.co/Maziyarpanahi/codegemma-2b-GGUF:Q4_K_M"

SYSTEM_PROMPT = """You are NEXUS, an elite AI Software Engineering Engine.
You are not a chatbot — you are a professional full-stack development system.
Your mission: Generate production-ready, clean, well-commented code.

RULES:
- Auto-detect language and project type from the request.
- Generate COMPLETE, runnable code — never partial snippets.
- Always include proper imports, error handling, and inline comments.
- Follow language best practices (PEP8, etc.).
- Wrap ALL code in proper markdown code blocks with language tags.
- Briefly state: Language, Project Type, and what you built — then show code.
- Never truncate mid-function. Production-grade always.
"""

MODE_CONFIG = {
    "Code Generation": {
        "icon": "⚡", "class": "mode-generate",
        "hint": "Describe what you want to build...",
        "prefix": "",
    },
    "Debug & Fix": {
        "icon": "🔬", "class": "mode-debug",
        "hint": "Paste your buggy code here...",
        "prefix": "[DEBUG] Find ALL bugs, explain each fix precisely, then output corrected complete code: ",
    },
    "Optimize": {
        "icon": "🚀", "class": "mode-optimize",
        "hint": "Paste code to optimize...",
        "prefix": "[OPTIMIZE] Improve performance, structure, and readability. Show what changed and why: ",
    },
    "Explain Code": {
        "icon": "📡", "class": "mode-explain",
        "hint": "Paste code to explain...",
        "prefix": "[EXPLAIN] Break down this code step-by-step in clear detail: ",
    },
    "Enterprise Mode": {
        "icon": "🏛️", "class": "mode-enterprise",
        "hint": "Describe your enterprise system...",
        "prefix": "[ENTERPRISE] Generate scalable, modular, production-grade architecture with full structure: ",
    },
}

EXT_MAP = {
    "python":"py","py":"py","javascript":"js","js":"js","typescript":"ts",
    "ts":"ts","html":"html","css":"css","java":"java","cpp":"cpp","c":"c",
    "go":"go","rust":"rs","bash":"sh","shell":"sh","sql":"sql","r":"r",
    "kotlin":"kt","swift":"swift","php":"php","ruby":"rb","dart":"dart",
    "json":"json","yaml":"yml","toml":"toml","md":"md","markdown":"md",
}

# ══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
def init_state():
    defaults = {
        "messages":      [{"role": "system", "content": SYSTEM_PROMPT}],
        "stats":         {"prompts": 0, "blocks": 0, "tokens": 0},
        "last_analysis": None,
        "mode":          "Code Generation",
        "boot_time":     datetime.now().strftime("%H:%M:%S"),
        "auto_prompt":   None,   # set by quick-start cards
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def extract_code_blocks(text):
    return re.findall(r"```(\w+)?\n([\s\S]*?)```", text)

def build_zip(blocks):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for i, (lang, code) in enumerate(blocks):
            ext  = EXT_MAP.get((lang or "").lower(), "txt")
            name = f"nexus_{i+1}.{ext}" if len(blocks) > 1 else f"nexus_output.{ext}"
            zf.writestr(name, code.strip())
        zf.writestr("README.md",
            f"# NEXUS Generated Code\n\n"
            f"Generated : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Files     : {len(blocks)}\n"
            f"Model     : {MODEL}\n"
        )
    buf.seek(0)
    return buf

def cx_badge(level):
    l = level.lower()
    if l == "beginner":     return "badge-begin"
    if l == "advanced":     return "badge-adv"
    return "badge-inter"

def cx_bar(level):
    return level.lower()  # matches CSS class names

# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
      <div class="sidebar-logo">⚡ NEXUS</div>
      <div class="sidebar-version">CODE ENGINE · v2.1 · ELITE</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="status-bar">
      <div class="status-dot"></div>
      ENGINE ONLINE · NOMINAL
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sbl">OPERATING MODE</div>', unsafe_allow_html=True)
    mode = st.selectbox(
        "", list(MODE_CONFIG.keys()),
        index=list(MODE_CONFIG.keys()).index(st.session_state.mode),
        label_visibility="collapsed", key="mode_select",
    )
    st.session_state.mode = mode
    cfg = MODE_CONFIG[mode]
    st.markdown(f'<div class="mode-card {cfg["class"]}">{cfg["icon"]} &nbsp; {mode.upper()}</div>',
                unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # Stats
    s = st.session_state.stats
    st.markdown('<div class="sbl">SESSION TELEMETRY</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="stat-row"><span class="stat-label">BOOT TIME</span>
      <span class="stat-value">{st.session_state.boot_time}</span></div>
    <div class="stat-row"><span class="stat-label">PROMPTS</span>
      <span class="stat-value">{s['prompts']}</span></div>
    <div class="stat-row"><span class="stat-label">CODE BLOCKS</span>
      <span class="stat-value">{s['blocks']}</span></div>
    <div class="stat-row"><span class="stat-label">EST. TOKENS</span>
      <span class="stat-value">{s['tokens']:,}</span></div>
    <div class="stat-row"><span class="stat-label">MODEL</span>
      <span class="stat-value" style="font-size:0.56rem;">CODEGEMMA-2B Q4</span></div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # Analysis
    if st.session_state.last_analysis:
        a   = st.session_state.last_analysis
        lvl = a["level"]
        st.markdown('<div class="sbl">LAST CODE ANALYSIS</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="analysis-panel">
          <div class="ap-header">◈ &nbsp; DETECTION REPORT</div>
          <div class="ap-row"><span class="ap-key">LANGUAGE</span>
            <span class="ap-val">{a['language']}</span></div>
          <div class="ap-row"><span class="ap-key">PROJECT</span>
            <span class="ap-val">{a['project_type']}</span></div>
          <div class="ap-row"><span class="ap-key">FUNCTIONS</span>
            <span class="ap-val">{a['functions']}</span></div>
          <div class="ap-row"><span class="ap-key">LOOPS</span>
            <span class="ap-val">{a['loops']}</span></div>
          <div class="ap-row"><span class="ap-key">CONDITIONS</span>
            <span class="ap-val">{a['conditions']}</span></div>
          <div class="ap-row"><span class="ap-key">LOC</span>
            <span class="ap-val">{a['loc']}</span></div>
          <div class="cx-meter">
            <div style="display:flex;justify-content:space-between;align-items:center;">
              <span class="ap-key">COMPLEXITY</span>
              <span class="badge {cx_badge(lvl)}">{lvl.upper()}</span>
            </div>
            <div class="cx-bar-bg">
              <div class="cx-bar {cx_bar(lvl)}"></div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

    # Controls
    st.markdown('<div class="sbl">CONTROLS</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="danger-btn">', unsafe_allow_html=True)
        if st.button("⟳  CLEAR SESSION", use_container_width=True, key="clear_btn"):
            for k in ["messages","stats","last_analysis"]:
                del st.session_state[k]
            init_state()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top:1.4rem;padding-top:0.7rem;text-align:center;
                font-family:'Share Tech Mono',monospace;font-size:0.56rem;
                color:rgba(0,245,255,0.13);letter-spacing:0.14em;
                border-top:1px solid rgba(0,245,255,0.04);">
      NEXUS · OLLAMA · CODEGEMMA-2B-Q4_K_M<br>
      <span style="opacity:0.6;">STREAMLIT · PYTHON</span>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  MAIN HEADER — centered, fixed position
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="nexus-header-wrap">
  <div class="nexus-logo-text">
    <span class="nexus-bolt">⚡</span>NEXUS
  </div>
  <div class="nexus-tagline">Advanced AI Software Engineering Engine</div>
</div>
<div class="neon-rule"></div>
""", unsafe_allow_html=True)

# Mode pill
mc_map = {
    "Code Generation":("var(--neon-teal)","rgba(0,255,180,0.07)","rgba(0,255,180,0.22)"),
    "Debug & Fix":    ("var(--neon-orange)","rgba(255,107,53,0.07)","rgba(255,107,53,0.22)"),
    "Optimize":       ("var(--neon-cyan)","rgba(0,245,255,0.07)","rgba(0,245,255,0.22)"),
    "Explain Code":   ("#c084fc","rgba(192,132,252,0.07)","rgba(192,132,252,0.22)"),
    "Enterprise Mode":("#ffd700","rgba(255,215,0,0.07)","rgba(255,215,0,0.22)"),
}
mc, mb, mbd = mc_map.get(mode, ("var(--neon-cyan)","rgba(0,245,255,0.07)","rgba(0,245,255,0.22)"))
st.markdown(f"""
<div style="text-align:center;margin-bottom:1.1rem;">
  <span style="display:inline-flex;align-items:center;gap:8px;padding:0.32em 1.4em;
               border-radius:25px;font-family:'Share Tech Mono',monospace;
               font-size:0.71rem;letter-spacing:0.13em;border:1px solid {mbd};
               color:{mc};background:{mb};
               box-shadow:0 0 22px {mb},inset 0 1px 0 {mbd};">
    {cfg["icon"]} &nbsp; {mode.upper()} &nbsp; ACTIVE
  </span>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  EMPTY STATE — QUICK-START CARDS (functional buttons)
# ══════════════════════════════════════════════════════════════════════════════
visible_msgs = [m for m in st.session_state.messages if m["role"] != "system"]
if not visible_msgs:
    st.markdown("""
    <div style="text-align:center;margin:0.8rem 0 0.5rem;">
      <p style="font-family:'Share Tech Mono',monospace;font-size:0.72rem;
                color:rgba(0,245,255,0.35);letter-spacing:0.22em;">
        // NEXUS READY · AWAITING INSTRUCTIONS
      </p>
    </div>
    """, unsafe_allow_html=True)

    # CSS for the quick-start buttons to look like wcard panels
    st.markdown("""
    <style>
    /* Quick-start card buttons */
    div[data-testid="stHorizontalBlock"] .stButton > button {
      width: 100% !important;
      min-height: 110px !important;
      height: auto !important;
      text-align: left !important;
      white-space: normal !important;
      word-wrap: break-word !important;
      padding: 1rem 1.1rem !important;
      background: rgba(4,12,30,0.75) !important;
      border: 1px solid rgba(0,245,255,0.1) !important;
      border-radius: 13px !important;
      color: var(--text-primary) !important;
      font-family: 'Exo 2', sans-serif !important;
      font-size: 0.85rem !important;
      letter-spacing: 0.02em !important;
      line-height: 1.55 !important;
      transition: all 0.28s ease !important;
      box-shadow: 0 4px 20px rgba(0,0,0,0.4),
                  inset 0 1px 0 rgba(0,245,255,0.06) !important;
      display: flex !important;
      flex-direction: column !important;
      align-items: flex-start !important;
      cursor: pointer !important;
    }
    div[data-testid="stHorizontalBlock"] .stButton > button:hover {
      border-color: rgba(0,245,255,0.3) !important;
      background: rgba(6,20,50,0.85) !important;
      box-shadow: 0 8px 30px rgba(0,0,0,0.5),
                  0 0 25px rgba(0,245,255,0.06),
                  inset 0 1px 0 rgba(0,245,255,0.12) !important;
      transform: translateY(-3px) !important;
      color: #e8f4ff !important;
    }
    div[data-testid="stHorizontalBlock"] .stButton > button:active {
      transform: translateY(-1px) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Card definitions: (icon, title, desc, prompt)
    QUICK_CARDS = [
        ("🐍", "REST API",     "FastAPI with auth, routes, models",
         "Build a complete REST API using FastAPI with JWT authentication, CRUD routes, Pydantic models, and error handling."),
        ("🌐", "WEB APP",      "Full-stack with modern UI",
         "Build a full-stack web application with a Python Flask backend and a responsive HTML/CSS/JS frontend with a modern dark UI."),
        ("🤖", "ML PIPELINE",  "Data processing → model training",
         "Build a complete machine learning pipeline in Python with data loading, preprocessing, feature engineering, model training with scikit-learn, evaluation metrics, and model saving."),
        ("⚙️", "CLI TOOL",     "Powerful command-line utilities",
         "Build a professional Python CLI tool using Click with multiple commands, colored output, progress bars, config file support, and error handling."),
    ]

    col1, col2 = st.columns(2)
    for idx, (icon, title, desc, prompt_text) in enumerate(QUICK_CARDS):
        col = col1 if idx % 2 == 0 else col2
        with col:
            label = f"{icon}  {title}\n{desc}"
            if st.button(label, key=f"qs_{idx}", use_container_width=True):
                st.session_state.auto_prompt = prompt_text
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  CHAT HISTORY
# ══════════════════════════════════════════════════════════════════════════════
for i, message in enumerate(st.session_state.messages):
    if message["role"] == "system":
        continue
    with st.chat_message(message["role"]):
        content = message["content"]
        blocks  = extract_code_blocks(content)

        if message["role"] == "assistant" and blocks:
            prose = re.sub(r"```(\w+)?\n[\s\S]*?```", "", content).strip()
            if prose:
                st.markdown(prose)
            for lang, code in blocks:
                st.code(code.strip(), language=lang if lang else None)

            first_lang, first_code = blocks[0]
            ext = EXT_MAP.get((first_lang or "").lower(), "txt")
            ts  = int(time.time() * 1000) + i

            c1, c2, c3 = st.columns([1.3, 1.3, 3])
            with c1:
                st.download_button("⬇ DOWNLOAD", first_code.strip(),
                                   file_name=f"nexus_output.{ext}", mime="text/plain",
                                   key=f"dl_{ts}", use_container_width=True)
            with c2:
                zb = build_zip(blocks)
                st.download_button("📦 ZIP", zb,
                                   file_name="nexus_project.zip", mime="application/zip",
                                   key=f"zip_{ts}", use_container_width=True)
            with c3:
                if st.session_state.last_analysis and i == len(st.session_state.messages) - 1:
                    a   = st.session_state.last_analysis
                    lvl = a["level"]
                    st.markdown(f"""
                    <div style="display:flex;align-items:center;gap:5px;padding-top:5px;flex-wrap:wrap;">
                      <span class="badge badge-lang">⬡ {a['language']}</span>
                      <span class="badge badge-type">◈ {a['project_type']}</span>
                      <span class="badge {cx_badge(lvl)}">◉ {lvl}</span>
                    </div>""", unsafe_allow_html=True)
        else:
            st.markdown(content)

# ══════════════════════════════════════════════════════════════════════════════
#  PROMPT PROCESSING  (auto_prompt from cards OR typed chat input)
# ══════════════════════════════════════════════════════════════════════════════

# Pull prompt from quick-start card click OR typed input
typed_prompt = st.chat_input(cfg["hint"])
prompt = st.session_state.pop("auto_prompt", None) or typed_prompt

if prompt:
    full_prompt = cfg["prefix"] + prompt

    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": full_prompt})
    st.session_state.stats["prompts"] += 1

    with st.chat_message("assistant"):
        thinking_ph = st.empty()
        thinking_ph.markdown("""
        <div class="thinking-box">
          <div class="thinking-dots">
            <span></span><span></span><span></span>
          </div>
          NEXUS PROCESSING · GENERATING CODE
        </div>""", unsafe_allow_html=True)

        msg_ph        = st.empty()
        full_response = ""

        try:
            stream = ollama.chat(
                model=MODEL,
                messages=st.session_state.messages,
                stream=True,
            )
            thinking_ph.empty()
            for chunk in stream:
                full_response += chunk["message"]["content"]
                msg_ph.markdown(full_response + "▊")
            msg_ph.markdown(full_response)

        except Exception as e:
            thinking_ph.empty()
            full_response = (
                f"⚠️ **NEXUS ENGINE ERROR**\n\n```\n{e}\n```\n\n"
                f"**Resolution:**\n"
                f"1. Start Ollama: `ollama serve`\n"
                f"2. Pull model:\n```bash\nollama pull {MODEL}\n```"
            )
            msg_ph.markdown(full_response)

        # Post-response analysis + downloads
        blocks = extract_code_blocks(full_response)
        if blocks:
            first_lang, first_code = blocks[0]
            analysis = analyze_complexity(first_code)
            analysis["language"]     = detect_language(first_code, first_lang or "")
            analysis["project_type"] = detect_project_type(full_response, first_code)
            st.session_state.last_analysis = analysis
            st.session_state.stats["blocks"] += len(blocks)
            st.session_state.stats["tokens"] += len(full_response.split())

            ext = EXT_MAP.get((first_lang or "").lower(), "txt")
            c1, c2, c3 = st.columns([1.3, 1.3, 3])
            with c1:
                st.download_button("⬇ DOWNLOAD", first_code.strip(),
                                   file_name=f"nexus_output.{ext}", mime="text/plain",
                                   key="live_dl", use_container_width=True)
            with c2:
                zb = build_zip(blocks)
                st.download_button("📦 ZIP", zb,
                                   file_name="nexus_project.zip", mime="application/zip",
                                   key="live_zip", use_container_width=True)
            with c3:
                lvl = analysis["level"]
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:5px;padding-top:5px;flex-wrap:wrap;">
                  <span class="badge badge-lang">⬡ {analysis['language']}</span>
                  <span class="badge badge-type">◈ {analysis['project_type']}</span>
                  <span class="badge {cx_badge(lvl)}">◉ {lvl}</span>
                </div>""", unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.rerun()