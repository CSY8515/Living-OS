from __future__ import annotations


def apply_living_os_theme() -> None:
    import streamlit as st

    st.markdown(
        """
        <style>
        :root {
          --los-bg:#030712; --los-bg-2:#07101d; --los-surface:rgba(10,22,38,.82);
          --los-surface-2:rgba(14,30,50,.72); --los-line:rgba(111,202,255,.14);
          --los-line-strong:rgba(89,218,255,.38); --los-text:#edf8ff; --los-muted:#8299ae;
          --los-cyan:#62e3ff; --los-blue:#4388ff; --los-purple:#9b78ff;
          --los-good:#53e6b5; --los-warn:#ffca72; --los-danger:#ff7894;
          --los-radius:18px; --los-radius-sm:11px; --los-shadow:0 24px 70px rgba(0,0,0,.32);
          --los-glow:0 0 0 1px rgba(98,227,255,.04),0 18px 55px rgba(0,0,0,.24);
        }
        html,body,[class*="css"] { font-family:Inter,"Segoe UI",system-ui,sans-serif; }
        .stApp { color:var(--los-text); background:
          radial-gradient(circle at 76% -8%,rgba(48,112,232,.20),transparent 34rem),
          radial-gradient(circle at 15% 32%,rgba(108,66,188,.08),transparent 31rem),
          linear-gradient(155deg,#050c18 0%,var(--los-bg) 48%,#040916 100%); }
        .stApp::before { content:"";position:fixed;inset:0;pointer-events:none;opacity:.22;
          background-image:linear-gradient(rgba(93,200,255,.028) 1px,transparent 1px),linear-gradient(90deg,rgba(93,200,255,.028) 1px,transparent 1px);
          background-size:48px 48px;mask-image:linear-gradient(to bottom,black,transparent 88%); }
        [data-testid="stHeader"] { background:rgba(3,7,18,.62);backdrop-filter:blur(20px);border-bottom:1px solid rgba(98,227,255,.05); }
        [data-testid="stToolbar"] { right:.7rem; }
        .block-container { max-width:1640px;padding:1.35rem 2.35rem 5rem; }
        h1,h2,h3,h4 { color:var(--los-text)!important;letter-spacing:-.028em;font-weight:650!important; }
        p,.stCaption,[data-testid="stCaptionContainer"] { color:var(--los-muted); }
        hr { border-color:var(--los-line)!important;margin:1.6rem 0!important; }

        /* Navigation rail */
        [data-testid="stSidebar"] { width:290px!important;background:linear-gradient(180deg,rgba(8,20,35,.98),rgba(4,10,20,.99));border-right:1px solid var(--los-line);box-shadow:18px 0 60px rgba(0,0,0,.20); }
        [data-testid="stSidebarContent"] { padding:1rem .7rem 2rem; }
        [data-testid="stSidebar"] h1 { font-size:1.08rem!important;letter-spacing:.2em!important;margin-bottom:.05rem!important;color:var(--los-text)!important; }
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] { font-size:.61rem;letter-spacing:.13em;text-transform:uppercase;margin-bottom:.05rem; }
        [data-testid="stSidebar"] div[role="radiogroup"] { gap:2px;padding-top:.75rem; }
        [data-testid="stSidebar"] div[role="radiogroup"]>label { position:relative;min-height:38px;padding:7px 10px;border:1px solid transparent;border-radius:10px;color:#a9bdcd;transition:background .16s,border-color .16s,color .16s; }
        [data-testid="stSidebar"] div[role="radiogroup"]>label:hover { background:rgba(98,227,255,.055);border-color:rgba(98,227,255,.10);color:var(--los-text); }
        [data-testid="stSidebar"] div[role="radiogroup"]>label:has(input:checked) { color:var(--los-text);background:linear-gradient(90deg,rgba(44,129,201,.25),rgba(33,71,132,.10));border-color:rgba(98,227,255,.25);box-shadow:inset 3px 0 0 var(--los-cyan),0 0 22px rgba(60,154,235,.07); }
        [data-testid="stSidebar"] div[role="radiogroup"]>label p { color:#9eb3c5!important;font-size:.82rem;font-weight:520;letter-spacing:.01em; }
        [data-testid="stSidebar"] div[role="radiogroup"]>label:hover p,[data-testid="stSidebar"] div[role="radiogroup"]>label:has(input:checked) p { color:var(--los-text)!important; }
        [data-testid="stSidebar"] div[role="radiogroup"]>label>div:first-child { display:none; }
        [data-testid="stSidebar"] [data-testid="stRadioOption"]>div>div>div:first-child { display:none; }
        [data-testid="stSidebar"] [data-testid="stRadioOption"]>div>div { gap:0!important; }
        [data-testid="stSidebar"] div[role="radiogroup"]>label:nth-child(1)::before,
        [data-testid="stSidebar"] div[role="radiogroup"]>label:nth-child(2)::before,
        [data-testid="stSidebar"] div[role="radiogroup"]>label:nth-child(10)::before,
        [data-testid="stSidebar"] div[role="radiogroup"]>label:nth-child(21)::before,
        [data-testid="stSidebar"] div[role="radiogroup"]>label:nth-child(27)::before { display:block;position:absolute;left:7px;bottom:calc(100% + 9px);font-size:.59rem;font-weight:700;letter-spacing:.18em;color:#6f879b;white-space:nowrap; }
        [data-testid="stSidebar"] div[role="radiogroup"]>label:nth-child(1),
        [data-testid="stSidebar"] div[role="radiogroup"]>label:nth-child(2),
        [data-testid="stSidebar"] div[role="radiogroup"]>label:nth-child(10),
        [data-testid="stSidebar"] div[role="radiogroup"]>label:nth-child(21),
        [data-testid="stSidebar"] div[role="radiogroup"]>label:nth-child(27) { margin-top:34px; }
        [data-testid="stSidebar"] div[role="radiogroup"]>label:nth-child(1)::before { content:"OVERVIEW"; }
        [data-testid="stSidebar"] div[role="radiogroup"]>label:nth-child(2)::before { content:"CAPTURE & INSIGHT"; }
        [data-testid="stSidebar"] div[role="radiogroup"]>label:nth-child(10)::before { content:"LIFE SYSTEMS"; }
        [data-testid="stSidebar"] div[role="radiogroup"]>label:nth-child(21)::before { content:"MANAGEMENT"; }
        [data-testid="stSidebar"] div[role="radiogroup"]>label:nth-child(27)::before { content:"SYSTEM"; }

        /* Command shell */
        .los-system-banner { min-height:78px;display:flex;align-items:center;gap:15px;padding:13px 18px;border:1px solid var(--los-line);background:linear-gradient(110deg,rgba(12,28,47,.88),rgba(7,16,30,.78));backdrop-filter:blur(18px);border-radius:var(--los-radius);box-shadow:var(--los-shadow);position:relative;overflow:hidden; }
        .los-system-banner::after { content:"";position:absolute;right:17%;top:0;width:22%;height:1px;background:linear-gradient(90deg,transparent,var(--los-cyan),transparent);opacity:.75; }
        .los-orb { width:44px;height:44px;border:1px solid var(--los-line-strong);border-radius:50%;display:grid;place-items:center;background:radial-gradient(circle,rgba(98,227,255,.12),transparent 66%);box-shadow:0 0 28px rgba(65,183,255,.13),inset 0 0 20px rgba(98,227,255,.08); }
        .los-orb span { width:13px;height:13px;border-radius:50%;background:var(--los-cyan);box-shadow:0 0 8px var(--los-cyan),0 0 24px rgba(98,227,255,.75); }
        .los-wordmark { font-size:1.04rem;letter-spacing:.22em;color:var(--los-text); }.los-wordmark b{color:var(--los-cyan)}
        .los-system-banner small { color:var(--los-muted);letter-spacing:.11em;font-size:.62rem; }
        .los-system-state { margin-left:auto;display:flex;align-items:center;gap:10px;text-align:right;padding:8px 11px;border:1px solid rgba(83,230,181,.12);border-radius:11px;background:rgba(83,230,181,.035); }
        .los-system-state b{display:block;font-size:.7rem;letter-spacing:.15em}.los-system-state small{display:block;letter-spacing:0;margin-top:2px}
        .los-dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--los-blue);box-shadow:0 0 13px currentColor}.los-dot.good{background:var(--los-good)}.los-dot.warn{background:var(--los-warn)}.los-dot.danger{background:var(--los-danger)}
        .los-page-header { display:flex;justify-content:space-between;align-items:flex-end;gap:24px;padding:34px 4px 22px;border-bottom:1px solid var(--los-line);margin-bottom:24px;position:relative; }
        .los-page-header::after { content:"";position:absolute;left:0;bottom:-1px;width:90px;height:1px;background:linear-gradient(90deg,var(--los-cyan),transparent);box-shadow:0 0 13px rgba(98,227,255,.5); }
        .los-page-header h1 { font-size:clamp(2.25rem,3.4vw,3.8rem)!important;line-height:1.02;margin:.22rem 0 .45rem!important;text-shadow:0 0 32px rgba(91,175,255,.09); }
        .los-page-header p{margin:0;max-width:780px;font-size:.94rem;line-height:1.55}.los-eyebrow{color:var(--los-cyan);font-size:.66rem;font-weight:750;letter-spacing:.22em;text-transform:uppercase}
        .los-badge { font-size:.65rem;font-weight:750;letter-spacing:.14em;padding:8px 12px;border-radius:999px;border:1px solid var(--los-line-strong);color:var(--los-cyan);background:rgba(98,227,255,.045);box-shadow:0 0 22px rgba(98,227,255,.07); }.los-badge.good{color:var(--los-good);border-color:rgba(83,230,181,.28)}.los-badge.warn{color:var(--los-warn);border-color:rgba(255,202,114,.3)}.los-badge.danger{color:var(--los-danger);border-color:rgba(255,120,148,.3)}

        /* Cards, panels, and shared states */
        [data-testid="stMetric"],.los-card { position:relative;overflow:hidden;background:linear-gradient(145deg,rgba(16,35,57,.92),rgba(7,16,30,.88));border:1px solid var(--los-line);border-radius:var(--los-radius);padding:19px;box-shadow:var(--los-glow);backdrop-filter:blur(14px); }
        [data-testid="stMetric"]::before,.los-card::before { content:"";position:absolute;inset:0;background:radial-gradient(circle at 90% 0,rgba(67,136,255,.10),transparent 45%);pointer-events:none; }
        [data-testid="stMetric"]::after,.los-card::after { content:"";position:absolute;inset:auto 11% 0;height:1px;background:linear-gradient(90deg,transparent,var(--los-cyan),transparent);opacity:.52 }
        [data-testid="stMetricValue"] { color:var(--los-text);font-weight:670;font-size:1.75rem; } [data-testid="stMetricLabel"]{color:var(--los-muted);font-size:.78rem;letter-spacing:.04em}
        .los-kpi{min-height:154px;padding:22px;transition:transform .16s,border-color .16s,box-shadow .16s}.los-kpi:hover{transform:translateY(-2px);border-color:rgba(98,227,255,.28);box-shadow:0 22px 60px rgba(0,0,0,.3),0 0 24px rgba(67,136,255,.07)}
        .los-kpi-label{color:var(--los-muted);font-size:.67rem;font-weight:700;letter-spacing:.15em;text-transform:uppercase}.los-kpi-value{font-size:2.45rem;line-height:1;font-weight:680;margin:1rem 0 .45rem;letter-spacing:-.04em}.los-kpi-detail{font-size:.76rem;color:var(--los-muted)}.los-kpi.good{border-top-color:rgba(83,230,181,.45)}.los-kpi.warn{border-top-color:rgba(255,202,114,.56)}.los-kpi.danger{border-top-color:rgba(255,120,148,.56)}
        .los-panel-header {display:flex;align-items:end;justify-content:space-between;margin:14px 2px 13px}.los-panel-header h3{font-size:1.05rem;margin:0!important;letter-spacing:.01em}.los-panel-header p{font-size:.74rem;margin:.25rem 0 0}.los-panel-header>span{font-size:.61rem;font-weight:750;color:var(--los-cyan);letter-spacing:.15em;padding:5px 8px;border:1px solid rgba(98,227,255,.12);border-radius:7px;background:rgba(98,227,255,.025)}
        div[data-testid="stColumn"]:has(.los-feed),div[data-testid="stColumn"]:has(.los-health-row){padding:3px 16px 16px;border:1px solid var(--los-line);border-radius:var(--los-radius);background:linear-gradient(145deg,rgba(11,25,42,.72),rgba(6,14,26,.62));box-shadow:var(--los-glow)}
        div[data-testid="stColumn"]:has(.los-health-row){border-color:rgba(83,230,181,.17);background:radial-gradient(circle at 100% 0,rgba(83,230,181,.07),transparent 42%),linear-gradient(145deg,rgba(11,28,42,.76),rgba(6,14,26,.7))}
        .los-feed{border:0;padding:2px 4px;background:transparent}.los-activity{display:grid;grid-template-columns:12px 1fr auto;gap:11px;align-items:start;padding:15px 2px;border-bottom:1px solid var(--los-line)}.los-activity:last-child{border:0}.los-activity-node{width:7px;height:7px;background:var(--los-cyan);border-radius:50%;margin-top:6px;box-shadow:0 0 10px rgba(98,227,255,.75)}.los-activity b{font-size:.84rem}.los-activity p{font-size:.74rem;margin:.2rem 0 0}.los-activity time{font-size:.65rem;color:var(--los-muted)}
        .los-health-row{display:grid;grid-template-columns:10px minmax(90px,.75fr) 1.45fr auto;gap:10px;align-items:center;padding:14px 3px;border-bottom:1px solid var(--los-line);font-size:.74rem}.los-health-row:last-child{border:0}.los-health-row b{font-size:.78rem}.los-health-row span{color:var(--los-muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.los-health-row em{font-style:normal;font-size:.59rem;font-weight:750;color:var(--los-cyan);letter-spacing:.12em}
        .los-empty{min-height:174px;display:grid;place-content:center;text-align:center;border:1px dashed rgba(98,227,255,.26);border-radius:14px;background:radial-gradient(circle at 50% 25%,rgba(67,136,255,.08),transparent 55%),rgba(7,17,31,.34);position:relative}.los-empty::before{content:"◇";font-size:1.5rem;color:rgba(98,227,255,.48);margin-bottom:.6rem;text-shadow:0 0 20px rgba(98,227,255,.32)}.los-empty b{font-size:.66rem;letter-spacing:.18em;color:var(--los-cyan)}.los-empty span{font-size:.77rem;color:var(--los-muted);margin-top:8px;max-width:350px}.los-empty.danger{border-color:rgba(255,120,148,.32)}

        /* Native controls */
        .stButton>button,[data-testid="stFormSubmitButton"] button,[data-testid="baseButton-secondary"] {border:1px solid var(--los-line-strong)!important;border-radius:var(--los-radius-sm)!important;background:linear-gradient(180deg,rgba(24,68,102,.88),rgba(10,32,54,.92))!important;color:var(--los-text)!important;min-height:2.65rem;font-weight:620!important;letter-spacing:.015em;box-shadow:0 10px 24px rgba(0,0,0,.16)!important;transition:transform .15s,border-color .15s,box-shadow .15s!important}
        .stButton>button:hover,[data-testid="stFormSubmitButton"] button:hover{transform:translateY(-1px);border-color:var(--los-cyan)!important;box-shadow:0 0 24px rgba(98,227,255,.12)!important}
        .stButton>button:focus-visible{outline:2px solid var(--los-cyan)!important;outline-offset:2px}
        [data-baseweb="input"]>div,[data-baseweb="textarea"]>div,[data-baseweb="select"]>div,[data-baseweb="base-input"] {background:rgba(7,18,32,.88)!important;border-color:var(--los-line)!important;border-radius:var(--los-radius-sm)!important;transition:border-color .15s,box-shadow .15s}
        [data-baseweb="input"]>div:focus-within,[data-baseweb="textarea"]>div:focus-within,[data-baseweb="select"]>div:focus-within{border-color:rgba(98,227,255,.48)!important;box-shadow:0 0 0 3px rgba(98,227,255,.06)!important}
        [data-testid="stForm"] {border:1px solid var(--los-line)!important;border-radius:var(--los-radius)!important;background:rgba(8,19,33,.48);padding:1.25rem!important}
        [data-testid="stDataFrame"],.stDataFrame{border:1px solid var(--los-line);border-radius:var(--los-radius);overflow:hidden;box-shadow:var(--los-glow);background:rgba(7,17,30,.7)}
        [data-testid="stExpander"]{border:1px solid var(--los-line)!important;border-radius:var(--los-radius-sm)!important;background:rgba(8,19,33,.52)!important;overflow:hidden}
        [data-baseweb="tab-list"]{gap:5px;border-bottom:1px solid var(--los-line)}[data-baseweb="tab"]{border-radius:9px 9px 0 0;color:var(--los-muted);padding-left:1rem!important;padding-right:1rem!important}[aria-selected="true"]{color:var(--los-cyan)!important;background:rgba(98,227,255,.065)!important}
        [data-testid="stAlert"]{border-radius:var(--los-radius-sm);border:1px solid var(--los-line)!important;background:rgba(12,30,48,.82)!important;box-shadow:0 12px 30px rgba(0,0,0,.12)}
        [data-testid="stProgress"]>div>div{background:linear-gradient(90deg,var(--los-blue),var(--los-cyan))!important;box-shadow:0 0 12px rgba(98,227,255,.35)}
        [data-testid="stSpinner"]{color:var(--los-cyan)!important}

        @media(max-width:1100px){
          .block-container{padding:1.1rem 1.35rem 4rem}.los-kpi{min-height:135px;padding:18px}.los-kpi-value{font-size:2rem}
          div[data-testid="stHorizontalBlock"]:has(.los-kpi){flex-wrap:wrap}
          div[data-testid="stHorizontalBlock"]:has(.los-kpi)>div[data-testid="stColumn"]{min-width:190px;flex:1 1 calc(33.333% - .75rem)!important}
          .los-health-row{grid-template-columns:10px 1fr auto}.los-health-row>span:nth-of-type(2){display:none}
        }
        @media(max-width:760px){
          [data-testid="stSidebar"]{width:min(86vw,290px)!important}.block-container{padding:.9rem .85rem 4.25rem;max-width:100%;overflow-x:hidden}
          .los-system-banner{min-height:62px;padding:10px 12px}.los-orb{width:36px;height:36px}.los-system-state small{display:none}.los-system-state{padding:7px 9px}
          .los-page-header{align-items:flex-start;padding:25px 2px 18px}.los-page-header h1{font-size:2.25rem!important}.los-page-header p{font-size:.84rem}.los-badge{margin-top:3px}
          div[data-testid="stHorizontalBlock"]{flex-wrap:wrap;gap:.65rem!important}
          div[data-testid="stHorizontalBlock"]>div[data-testid="stColumn"]{min-width:min(100%,260px)!important;flex:1 1 calc(50% - .65rem)!important}
          div[data-testid="stColumn"]:has(.los-feed),div[data-testid="stColumn"]:has(.los-health-row){padding:2px 12px 12px}
          [data-testid="stDataFrame"]{max-width:100%;overflow:auto}.stButton button{width:100%}
        }
        @media(max-width:480px){
          .block-container{padding:.7rem .62rem 4.5rem}.los-system-banner>div:nth-child(2) small{display:none}.los-wordmark{font-size:.82rem}.los-orb{width:32px;height:32px}.los-orb span{width:10px;height:10px}
          .los-page-header{display:block}.los-page-header h1{font-size:2rem!important}.los-badge{display:inline-block;margin-top:14px}
          div[data-testid="stHorizontalBlock"]>div[data-testid="stColumn"],div[data-testid="stHorizontalBlock"]:has(.los-kpi)>div[data-testid="stColumn"]{min-width:100%!important;flex-basis:100%!important}
          .los-kpi{min-height:116px}.los-kpi-value{font-size:1.8rem;margin:.7rem 0 .32rem}.los-empty{min-height:145px}
          .los-activity{grid-template-columns:10px 1fr}.los-activity time{grid-column:2}.los-health-row{grid-template-columns:9px 1fr auto}
          [data-testid="stForm"]{padding:.9rem!important}[data-baseweb="tab-list"]{overflow-x:auto;scrollbar-width:none}
        }
        </style>
        """, unsafe_allow_html=True,
    )
