from __future__ import annotations


def apply_living_os_theme() -> None:
    import streamlit as st

    st.markdown(
        """
        <style>
        :root {
          --los-bg:#050a12; --los-surface:#0a1320; --los-surface-2:#0d1928;
          --los-line:rgba(101,196,255,.16); --los-line-strong:rgba(91,210,255,.34);
          --los-text:#e9f5ff; --los-muted:#8298aa; --los-cyan:#55d9ff;
          --los-blue:#4d82ff; --los-good:#47e0b0; --los-warn:#ffc766; --los-danger:#ff718a;
          --los-radius:14px; --los-shadow:0 18px 55px rgba(0,0,0,.28);
        }
        .stApp { background:
          radial-gradient(circle at 72% -10%,rgba(38,103,180,.18),transparent 34rem),
          linear-gradient(180deg,#060c15 0%,var(--los-bg) 72%); color:var(--los-text); }
        .stApp::before { content:""; position:fixed; inset:0; pointer-events:none; opacity:.18;
          background-image:linear-gradient(rgba(83,194,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(83,194,255,.035) 1px,transparent 1px);
          background-size:40px 40px; mask-image:linear-gradient(to bottom,black,transparent 80%); }
        [data-testid="stHeader"] { background:rgba(5,10,18,.72); backdrop-filter:blur(14px); }
        [data-testid="stSidebar"] { background:linear-gradient(180deg,#08121f,#070e18); border-right:1px solid var(--los-line); }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1 { letter-spacing:.12em; font-size:1.1rem!important; }
        .block-container { max-width:1440px; padding-top:1.2rem; padding-bottom:5rem; }
        h1,h2,h3 { color:var(--los-text)!important; letter-spacing:-.025em; }
        p,.stCaption { color:var(--los-muted); }
        hr { border-color:var(--los-line)!important; }
        .los-system-banner { min-height:72px; display:flex; align-items:center; gap:14px; padding:12px 16px;
          border:1px solid var(--los-line); background:rgba(10,19,32,.78); border-radius:var(--los-radius); box-shadow:var(--los-shadow); }
        .los-orb { width:42px;height:42px;border:1px solid var(--los-line-strong);border-radius:50%;display:grid;place-items:center;box-shadow:0 0 24px rgba(85,217,255,.14) inset; }
        .los-orb span { width:15px;height:15px;border-radius:50%;background:var(--los-cyan);box-shadow:0 0 18px var(--los-cyan); }
        .los-wordmark { font-size:1.02rem;letter-spacing:.19em;color:var(--los-text); }.los-wordmark b{color:var(--los-cyan)}
        .los-system-banner small { color:var(--los-muted);letter-spacing:.1em;font-size:.65rem; }
        .los-system-state { margin-left:auto;display:flex;align-items:center;gap:9px;text-align:right}.los-system-state b{display:block;font-size:.75rem;letter-spacing:.12em}.los-system-state small{display:block;letter-spacing:0}
        .los-dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--los-blue);box-shadow:0 0 12px currentColor}.los-dot.good{background:var(--los-good)}.los-dot.warn{background:var(--los-warn)}.los-dot.danger{background:var(--los-danger)}
        .los-page-header { display:flex;justify-content:space-between;align-items:flex-end;gap:20px;padding:28px 2px 18px;border-bottom:1px solid var(--los-line);margin-bottom:20px; }
        .los-page-header h1 { font-size:clamp(2rem,4vw,3.25rem)!important;margin:.15rem 0 .3rem!important; }.los-page-header p{margin:0;max-width:760px}
        .los-eyebrow { color:var(--los-cyan);font-size:.69rem;font-weight:700;letter-spacing:.2em;text-transform:uppercase; }
        .los-badge { font-size:.68rem;letter-spacing:.1em;padding:7px 10px;border-radius:999px;border:1px solid var(--los-line-strong);color:var(--los-cyan); }.los-badge.good{color:var(--los-good)}.los-badge.warn{color:var(--los-warn)}.los-badge.danger{color:var(--los-danger)}
        [data-testid="stMetric"],.los-card { position:relative;overflow:hidden;background:linear-gradient(145deg,rgba(14,28,44,.94),rgba(8,17,29,.9));border:1px solid var(--los-line);border-radius:var(--los-radius);padding:17px;box-shadow:0 12px 35px rgba(0,0,0,.2); }
        [data-testid="stMetric"]::after,.los-card::after { content:"";position:absolute;inset:auto 12% 0;height:1px;background:linear-gradient(90deg,transparent,var(--los-cyan),transparent);opacity:.45 }
        [data-testid="stMetricValue"] { color:var(--los-text);font-weight:650; } [data-testid="stMetricLabel"]{color:var(--los-muted)}
        .los-kpi{min-height:128px}.los-kpi-label{color:var(--los-muted);font-size:.72rem;letter-spacing:.12em;text-transform:uppercase}.los-kpi-value{font-size:2rem;font-weight:650;margin:.55rem 0 .2rem}.los-kpi-detail{font-size:.78rem;color:var(--los-muted)}.los-kpi.good{border-top-color:rgba(71,224,176,.45)}.los-kpi.warn{border-top-color:rgba(255,199,102,.55)}.los-kpi.danger{border-top-color:rgba(255,113,138,.55)}
        .los-panel-header {display:flex;align-items:end;justify-content:space-between;margin:10px 0 12px}.los-panel-header h3{font-size:1rem;margin:0!important;letter-spacing:.02em}.los-panel-header p{font-size:.76rem;margin:.2rem 0 0}.los-panel-header>span{font-size:.68rem;color:var(--los-cyan);letter-spacing:.1em}
        .los-feed{border:1px solid var(--los-line);border-radius:var(--los-radius);padding:5px 16px;background:rgba(9,18,30,.75)}.los-activity{display:grid;grid-template-columns:12px 1fr auto;gap:10px;align-items:start;padding:14px 0;border-bottom:1px solid var(--los-line)}.los-activity:last-child{border:0}.los-activity-node{width:7px;height:7px;background:var(--los-cyan);border-radius:50%;margin-top:6px;box-shadow:0 0 9px rgba(85,217,255,.7)}.los-activity b{font-size:.86rem}.los-activity p{font-size:.75rem;margin:.2rem 0 0}.los-activity time{font-size:.68rem;color:var(--los-muted)}
        .los-health-row{display:grid;grid-template-columns:10px minmax(100px,.8fr) 1.5fr auto;gap:10px;align-items:center;padding:11px 4px;border-bottom:1px solid var(--los-line);font-size:.76rem}.los-health-row b{font-size:.78rem}.los-health-row span{color:var(--los-muted)}.los-health-row em{font-style:normal;font-size:.65rem;color:var(--los-cyan);letter-spacing:.1em}
        .los-empty{min-height:135px;display:grid;place-content:center;text-align:center;border:1px dashed var(--los-line-strong);border-radius:var(--los-radius);background:rgba(9,18,30,.5)}.los-empty b{font-size:.72rem;letter-spacing:.16em;color:var(--los-cyan)}.los-empty span{font-size:.8rem;color:var(--los-muted);margin-top:7px}
        .stButton>button,[data-testid="stFormSubmitButton"] button {border:1px solid var(--los-line-strong)!important;border-radius:9px!important;background:linear-gradient(180deg,rgba(25,65,94,.9),rgba(12,34,55,.9))!important;color:var(--los-text)!important;min-height:2.55rem;box-shadow:none!important}.stButton>button:hover{border-color:var(--los-cyan)!important;box-shadow:0 0 18px rgba(85,217,255,.12)!important}
        [data-baseweb="input"]>div,[data-baseweb="textarea"]>div,[data-baseweb="select"]>div {background:#091421!important;border-color:var(--los-line)!important;border-radius:9px!important}
        [data-testid="stDataFrame"],.stDataFrame{border:1px solid var(--los-line);border-radius:var(--los-radius);overflow:hidden}
        [data-baseweb="tab-list"]{gap:5px;border-bottom:1px solid var(--los-line)}[data-baseweb="tab"]{border-radius:8px 8px 0 0;color:var(--los-muted)}[aria-selected="true"]{color:var(--los-cyan)!important;background:rgba(85,217,255,.07)!important}
        [data-testid="stAlert"]{border-radius:var(--los-radius);border-color:var(--los-line)!important;background:rgba(12,28,44,.8)!important}
        @media(max-width:900px){.block-container{padding:1rem 1rem 4rem}.los-system-state small{display:none}.los-page-header{align-items:flex-start}.los-health-row{grid-template-columns:10px 1fr auto}.los-health-row>span:nth-of-type(2){display:none}div[data-testid="stHorizontalBlock"]:has(.los-kpi)>div[data-testid="stColumn"]{min-width:180px;flex:1 1 calc(33.333% - .7rem)!important}}
        @media(max-width:640px){.block-container{padding:.75rem .7rem 4.5rem}.los-system-banner{min-height:58px}.los-orb{width:34px;height:34px}.los-wordmark{font-size:.85rem}.los-system-banner>div:nth-child(2) small{display:none}.los-page-header{padding-top:20px}.los-page-header h1{font-size:2rem!important}.los-page-header p{font-size:.83rem}.los-badge{display:none}[data-testid="stHorizontalBlock"]{flex-wrap:wrap}.stButton button{width:100%}.los-kpi{min-height:105px}.los-kpi-value{font-size:1.55rem}}
        </style>
        """, unsafe_allow_html=True,
    )
