from __future__ import annotations


def apply_living_os_theme() -> None:
    import streamlit as st

    st.markdown(
        """
        <style>
        :root {
          --los-bg:#050609; --los-bg-2:#0a0c12; --los-surface:rgba(16,18,24,.78);
          --los-surface-2:rgba(22,25,33,.68); --los-line:rgba(255,255,255,.075);
          --los-line-strong:rgba(100,221,255,.30); --los-text:#f4f7fa; --los-muted:#8a929e;
          --los-cyan:#64dcff; --los-blue:#5b8cff; --los-purple:#8875d8;
          --los-good:#64dcff; --los-warn:#c8a76a; --los-danger:#c87888;
          --los-radius:16px; --los-radius-sm:10px; --los-shadow:0 12px 36px rgba(0,0,0,.18);
          --los-glow:0 0 0 1px rgba(255,255,255,.018),0 10px 30px rgba(0,0,0,.14);
        }
        html,body,[class*="css"] { font-family:Inter,"Segoe UI",system-ui,sans-serif; }
        .stApp { color:var(--los-text); background:
          radial-gradient(circle at 72% -12%,rgba(64,126,190,.13),transparent 36rem),
          radial-gradient(circle at 12% 38%,rgba(105,82,150,.045),transparent 32rem),
          linear-gradient(155deg,#090c13 0%,var(--los-bg) 52%,#07080c 100%); }
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
        [data-testid="stSidebar"] { width:290px!important;background:linear-gradient(180deg,rgba(12,14,20,.97),rgba(7,8,12,.99));border-right:1px solid var(--los-line);box-shadow:none; }
        [data-testid="stSidebarContent"] { padding:1rem .7rem 2rem; }
        [data-testid="stSidebar"] h1 { font-size:1.08rem!important;letter-spacing:.2em!important;margin-bottom:.05rem!important;color:var(--los-text)!important; }
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] { font-size:.61rem;letter-spacing:.13em;text-transform:uppercase;margin-bottom:.05rem; }
        [data-testid="stSidebar"] div[role="radiogroup"] { gap:2px;padding-top:.75rem; }
        [data-testid="stSidebar"] div[role="radiogroup"]>label { position:relative;min-height:38px;padding:7px 10px;border:1px solid transparent;border-radius:10px;color:#a9bdcd;transition:background .16s,border-color .16s,color .16s; }
        [data-testid="stSidebar"] div[role="radiogroup"]>label:hover { background:rgba(255,255,255,.045);border-color:rgba(255,255,255,.075);color:var(--los-text);transform:translateX(2px); }
        [data-testid="stSidebar"] div[role="radiogroup"]>label:active { transform:translateX(2px) scale(.985); }
        [data-testid="stSidebar"] div[role="radiogroup"]>label:has(input:checked) { color:var(--los-text);background:linear-gradient(90deg,rgba(100,220,255,.14),rgba(255,255,255,.025));border-color:rgba(100,220,255,.20);box-shadow:inset 2px 0 0 var(--los-cyan); }
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
        [data-testid="stSidebar"] div[role="radiogroup"]>label:nth-child(1)::before { content:"CORE"; }
        [data-testid="stSidebar"] div[role="radiogroup"]>label:nth-child(2)::before { content:"JOURNAL & INSIGHT"; }
        [data-testid="stSidebar"] div[role="radiogroup"]>label:nth-child(10)::before { content:"LIFE SYSTEMS"; }
        [data-testid="stSidebar"] div[role="radiogroup"]>label:nth-child(21)::before { content:"WORKSPACES"; }
        [data-testid="stSidebar"] div[role="radiogroup"]>label:nth-child(27)::before { content:"SYSTEM"; }

        /* Command shell */
        .los-system-banner { min-height:72px;display:flex;align-items:center;gap:15px;padding:12px 17px;border:1px solid var(--los-line);background:linear-gradient(110deg,rgba(20,24,33,.78),rgba(10,12,18,.72));backdrop-filter:blur(22px);border-radius:var(--los-radius);box-shadow:var(--los-shadow);position:relative;overflow:hidden; }
        .los-system-banner::after { content:"";position:absolute;right:17%;top:0;width:22%;height:1px;background:linear-gradient(90deg,transparent,var(--los-cyan),transparent);opacity:.75; }
        .los-orb { width:44px;height:44px;border:1px solid var(--los-line-strong);border-radius:50%;display:grid;place-items:center;background:radial-gradient(circle,rgba(98,227,255,.12),transparent 66%);box-shadow:0 0 28px rgba(65,183,255,.13),inset 0 0 20px rgba(98,227,255,.08); }
        .los-orb span { width:13px;height:13px;border-radius:50%;background:var(--los-cyan);box-shadow:0 0 8px var(--los-cyan),0 0 24px rgba(98,227,255,.75); }
        .los-wordmark { font-size:1.04rem;letter-spacing:.22em;color:var(--los-text); }.los-wordmark b{color:var(--los-cyan)}
        .los-system-banner small { color:var(--los-muted);letter-spacing:.11em;font-size:.62rem; }
        .los-system-state { margin-left:auto;display:flex;align-items:center;gap:10px;text-align:right;padding:8px 11px;border:1px solid rgba(83,230,181,.12);border-radius:11px;background:rgba(83,230,181,.035); }
        .los-system-state b{display:block;font-size:.7rem;letter-spacing:.15em}.los-system-state small{display:block;letter-spacing:0;margin-top:2px}
        .los-dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--los-blue);box-shadow:0 0 13px currentColor}.los-dot.good{background:var(--los-good)}.los-dot.warn{background:var(--los-warn)}.los-dot.danger{background:var(--los-danger)}
        .los-page-header { display:flex;justify-content:space-between;align-items:flex-end;gap:24px;padding:38px 4px 24px;border-bottom:1px solid var(--los-line);margin-bottom:20px;position:relative; }
        .los-page-header::after { content:"";position:absolute;left:0;bottom:-1px;width:90px;height:1px;background:linear-gradient(90deg,var(--los-cyan),transparent);box-shadow:0 0 13px rgba(98,227,255,.5); }
        .los-page-header h1 { font-size:clamp(2.25rem,3.4vw,3.8rem)!important;line-height:1.02;margin:.22rem 0 .45rem!important;text-shadow:0 0 32px rgba(91,175,255,.09); }
        .los-page-header p{margin:0;max-width:780px;font-size:.94rem;line-height:1.55}.los-eyebrow{color:var(--los-cyan);font-size:.66rem;font-weight:750;letter-spacing:.22em;text-transform:uppercase}
        .los-badge { font-size:.65rem;font-weight:750;letter-spacing:.14em;padding:8px 12px;border-radius:999px;border:1px solid var(--los-line-strong);color:var(--los-cyan);background:rgba(98,227,255,.045);box-shadow:0 0 22px rgba(98,227,255,.07); }.los-badge.good{color:var(--los-good);border-color:rgba(83,230,181,.28)}.los-badge.warn{color:var(--los-warn);border-color:rgba(255,202,114,.3)}.los-badge.danger{color:var(--los-danger);border-color:rgba(255,120,148,.3)}
        .st-key-home_orbit{position:relative;min-height:740px;margin-top:4px;isolation:isolate;overflow:hidden;border-radius:32px}
        .st-key-home_orbit::before{content:"";position:absolute;inset:3% 8%;border-radius:50%;background:radial-gradient(circle,rgba(100,220,255,.065),transparent 58%);filter:blur(18px);pointer-events:none}
        .los-core-stage{position:absolute;inset:0;display:grid;place-items:center;pointer-events:none}
        .los-core-rings,.los-core-rings i{position:absolute;inset:50% auto auto 50%;translate:-50% -50%;border:1px solid rgba(100,220,255,.09);border-radius:50%;pointer-events:none}
        .los-core-rings{width:650px;height:650px;border-style:dashed;animation:los-orbit-spin 55s linear infinite}
        .los-core-rings i:nth-child(1){width:540px;height:540px;border-color:rgba(100,220,255,.12)}
        .los-core-rings i:nth-child(2){width:438px;height:438px;border-color:rgba(136,117,216,.10);border-style:dashed;animation:los-orbit-reverse 38s linear infinite}
        .los-core-rings i:nth-child(3){width:326px;height:326px;border-color:rgba(100,220,255,.16);box-shadow:0 0 48px rgba(100,220,255,.035)}
        .los-core{box-sizing:border-box;position:relative;width:min(600px,64vw);min-height:500px;padding:62px 50px 42px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;border:1px solid rgba(100,220,255,.16);border-radius:48% 52% 46% 54% / 52% 45% 55% 48%;background:radial-gradient(circle at 50% 20%,rgba(100,220,255,.065),transparent 42%),linear-gradient(155deg,rgba(18,22,31,.82),rgba(7,9,14,.74));backdrop-filter:blur(28px);box-shadow:inset 0 0 60px rgba(100,220,255,.025),0 0 80px rgba(21,104,155,.06);pointer-events:auto}
        .los-core::before{content:"";position:absolute;inset:13px;border:1px solid rgba(255,255,255,.035);border-radius:inherit;pointer-events:none}.los-core::after{content:"";position:absolute;top:4%;width:88px;height:2px;background:linear-gradient(90deg,transparent,var(--los-cyan),transparent);box-shadow:0 0 18px var(--los-cyan)}
        .los-core-kicker{display:flex;align-items:center;gap:10px;color:var(--los-cyan);font-size:.59rem;font-weight:750;letter-spacing:.24em}.los-core-kicker span{width:20px;height:1px;background:linear-gradient(90deg,transparent,var(--los-cyan))}.los-core-kicker span:last-child{transform:scaleX(-1)}
        .los-core h1{font-size:clamp(3rem,4.5vw,4.6rem)!important;line-height:.96;margin:1.05rem 0 .7rem!important;letter-spacing:-.06em;text-shadow:0 0 38px rgba(100,220,255,.08);white-space:nowrap}
        .los-core time{font-size:.7rem;color:var(--los-muted);letter-spacing:.08em}.los-core-summary{margin:1.15rem 0 0;color:#c0c6ce;font-size:.98rem;letter-spacing:-.01em}
        .los-core-brief{width:100%;margin:1.8rem 0 1.45rem;padding:15px 0;border-top:1px solid rgba(100,220,255,.10);border-bottom:1px solid rgba(100,220,255,.10)}.los-core-brief b{display:block;color:var(--los-cyan);font-size:.58rem;letter-spacing:.2em}.los-core-brief p{margin:.5rem 0 0;font-size:.78rem;color:var(--los-muted)}
        .los-core-signals{width:100%;display:grid;grid-template-columns:repeat(3,1fr);gap:0}.los-core-signals>div{padding:0 12px}.los-core-signals>div+div{border-left:1px solid var(--los-line)}.los-core-signals span{display:block;color:var(--los-muted);font-size:.54rem;font-weight:700;letter-spacing:.17em}.los-core-signals b{display:block;margin-top:.45rem;font-size:.7rem;font-weight:620;letter-spacing:.015em}
        .st-key-home_orbit_finance,.st-key-home_orbit_health,.st-key-home_orbit_vehicle,.st-key-home_orbit_learning,.st-key-home_orbit_knowledge,.st-key-home_orbit_routine{position:absolute;z-index:4;width:144px;animation:los-float 5.8s ease-in-out infinite}
        .st-key-home_orbit_finance{left:5%;top:16%}.st-key-home_orbit_health{right:5%;top:16%;animation-delay:-1.2s}.st-key-home_orbit_vehicle{left:1%;top:48%;animation-delay:-2.4s}.st-key-home_orbit_learning{right:1%;top:48%;animation-delay:-3.6s}.st-key-home_orbit_knowledge{left:13%;bottom:8%;animation-delay:-4.4s}.st-key-home_orbit_routine{right:13%;bottom:8%;animation-delay:-.7s}
        .st-key-home_orbit .stButton>button{width:100%;min-height:48px!important;border-radius:999px!important;justify-content:center!important;padding:0 16px!important;border:1px solid rgba(100,220,255,.14)!important;background:linear-gradient(150deg,rgba(20,25,34,.82),rgba(8,11,17,.76))!important;backdrop-filter:blur(18px);box-shadow:0 10px 28px rgba(0,0,0,.18),inset 0 0 18px rgba(100,220,255,.025)!important;color:#cbd3dc!important;font-size:.71rem!important;letter-spacing:.035em}
        .st-key-home_orbit .stButton>button:hover{transform:scale(1.035);border-color:rgba(100,220,255,.38)!important;color:var(--los-text)!important;box-shadow:0 0 28px rgba(100,220,255,.10)!important}
        @keyframes los-orbit-spin{to{transform:rotate(360deg)}}@keyframes los-orbit-reverse{to{transform:rotate(-360deg)}}@keyframes los-float{0%,100%{translate:0 0}50%{translate:0 -7px}}

        @media(min-width:1201px){.block-container:has(.st-key-home_orbit){box-sizing:border-box!important;width:calc(100vw - 500px)!important;max-width:calc(100vw - 500px)!important;margin-left:0!important;margin-right:0!important;transform:translateX(-150px)}}
        @media(min-width:761px) and (max-width:1200px){.block-container:has(.st-key-home_orbit){box-sizing:border-box!important;width:calc(100vw - 390px)!important;max-width:calc(100vw - 390px)!important;margin-left:0!important;margin-right:0!important;transform:translateX(-80px)}}

        /* Cards, panels, and shared states */
        [data-testid="stMetric"],.los-card { position:relative;overflow:hidden;background:linear-gradient(145deg,rgba(24,27,36,.78),rgba(11,13,19,.76));border:1px solid var(--los-line);border-radius:var(--los-radius);padding:19px;box-shadow:var(--los-glow);backdrop-filter:blur(18px); }
        [data-testid="stMetric"]::before,.los-card::before { content:"";position:absolute;inset:0;background:radial-gradient(circle at 90% 0,rgba(67,136,255,.10),transparent 45%);pointer-events:none; }
        [data-testid="stMetric"]::after,.los-card::after { content:"";position:absolute;inset:auto 11% 0;height:1px;background:linear-gradient(90deg,transparent,var(--los-cyan),transparent);opacity:.52 }
        [data-testid="stMetricValue"] { color:var(--los-text);font-weight:670;font-size:1.75rem; } [data-testid="stMetricLabel"]{color:var(--los-muted);font-size:.78rem;letter-spacing:.04em}
        .los-kpi{min-height:142px;padding:21px;transition:transform .18s ease,border-color .18s ease,background .18s ease}.los-kpi:hover{transform:translateY(-2px);border-color:rgba(100,220,255,.22);background:linear-gradient(145deg,rgba(28,32,42,.84),rgba(13,15,22,.8))}.los-kpi:active{transform:translateY(0) scale(.99)}
        .los-kpi-label{color:var(--los-muted);font-size:.67rem;font-weight:700;letter-spacing:.15em;text-transform:uppercase}.los-kpi-value{font-size:2.45rem;line-height:1;font-weight:680;margin:1rem 0 .45rem;letter-spacing:-.04em}.los-kpi-detail{font-size:.76rem;color:var(--los-muted)}.los-kpi.good{border-top-color:rgba(83,230,181,.45)}.los-kpi.warn{border-top-color:rgba(255,202,114,.56)}.los-kpi.danger{border-top-color:rgba(255,120,148,.56)}
        .los-panel-header {display:flex;align-items:end;justify-content:space-between;margin:14px 2px 13px}.los-panel-header h3{font-size:1.05rem;margin:0!important;letter-spacing:.01em}.los-panel-header p{font-size:.74rem;margin:.25rem 0 0}.los-panel-header>span{font-size:.61rem;font-weight:750;color:var(--los-cyan);letter-spacing:.15em;padding:5px 8px;border:1px solid rgba(98,227,255,.12);border-radius:7px;background:rgba(98,227,255,.025)}
        div[data-testid="stColumn"]:has(.los-feed),div[data-testid="stColumn"]:has(.los-health-row){padding:3px 16px 16px;border:1px solid var(--los-line);border-radius:var(--los-radius);background:linear-gradient(145deg,rgba(20,23,31,.68),rgba(9,11,16,.62));box-shadow:var(--los-glow);backdrop-filter:blur(18px)}
        div[data-testid="stColumn"]:has(.los-health-row){background:radial-gradient(circle at 100% 0,rgba(100,220,255,.045),transparent 42%),linear-gradient(145deg,rgba(20,23,31,.72),rgba(9,11,16,.66))}
        .los-feed{border:0;padding:2px 4px;background:transparent}.los-activity{display:grid;grid-template-columns:12px 1fr auto;gap:11px;align-items:start;padding:15px 2px;border-bottom:1px solid var(--los-line)}.los-activity:last-child{border:0}.los-activity-node{width:7px;height:7px;background:var(--los-cyan);border-radius:50%;margin-top:6px;box-shadow:0 0 10px rgba(98,227,255,.75)}.los-activity b{font-size:.84rem}.los-activity p{font-size:.74rem;margin:.2rem 0 0}.los-activity time{font-size:.65rem;color:var(--los-muted)}
        .los-health-row{display:grid;grid-template-columns:10px minmax(90px,.75fr) 1.45fr auto;gap:10px;align-items:center;padding:14px 3px;border-bottom:1px solid var(--los-line);font-size:.74rem}.los-health-row:last-child{border:0}.los-health-row b{font-size:.78rem}.los-health-row span{color:var(--los-muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.los-health-row em{font-style:normal;font-size:.59rem;font-weight:750;color:var(--los-cyan);letter-spacing:.12em}
        .los-empty{min-height:174px;display:grid;place-content:center;text-align:center;border:1px dashed rgba(98,227,255,.26);border-radius:14px;background:radial-gradient(circle at 50% 25%,rgba(67,136,255,.08),transparent 55%),rgba(7,17,31,.34);position:relative}.los-empty::before{content:"◇";font-size:1.5rem;color:rgba(98,227,255,.48);margin-bottom:.6rem;text-shadow:0 0 20px rgba(98,227,255,.32)}.los-empty b{font-size:.66rem;letter-spacing:.18em;color:var(--los-cyan)}.los-empty span{font-size:.77rem;color:var(--los-muted);margin-top:8px;max-width:350px}.los-empty.danger{border-color:rgba(255,120,148,.32)}

        /* Native controls */
        .stButton>button,[data-testid="stFormSubmitButton"] button,[data-testid="baseButton-secondary"] {border:1px solid var(--los-line-strong)!important;border-radius:var(--los-radius-sm)!important;background:linear-gradient(180deg,rgba(24,68,102,.88),rgba(10,32,54,.92))!important;color:var(--los-text)!important;min-height:2.65rem;font-weight:620!important;letter-spacing:.015em;box-shadow:0 10px 24px rgba(0,0,0,.16)!important;transition:transform .15s,border-color .15s,box-shadow .15s!important}
        .stButton>button:hover,[data-testid="stFormSubmitButton"] button:hover{transform:translateY(-1px);border-color:var(--los-cyan)!important;box-shadow:0 0 24px rgba(98,227,255,.12)!important}
        .stButton>button:active,[data-testid="stFormSubmitButton"] button:active{transform:translateY(0) scale(.985)!important}
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
        [data-testid="stVegaLiteChart"],[data-testid="stArrowVegaLiteChart"],[data-testid="stPlotlyChart"]{border:1px solid var(--los-line);border-radius:var(--los-radius);background:rgba(12,14,20,.48);padding:8px;overflow:hidden}
        [data-testid="stVegaLiteChart"] .mark-rule.role-axis-grid line,[data-testid="stArrowVegaLiteChart"] .mark-rule.role-axis-grid line{stroke:rgba(255,255,255,.055)!important}
        .los-system-banner,.los-page-header,.los-core-stage,.los-kpi,.los-feed,.los-health-row,[data-testid="stDataFrame"]{animation:los-enter .4s cubic-bezier(.2,.75,.25,1) both}
        @keyframes los-enter{from{opacity:0;transform:translateY(5px)}to{opacity:1;transform:translateY(0)}}
        @media(prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important;scroll-behavior:auto!important}}

        @media(max-width:1100px){
          .block-container{padding:1.1rem 1.35rem 4rem}.los-kpi{min-height:135px;padding:18px}.los-kpi-value{font-size:2rem}
          div[data-testid="stHorizontalBlock"]:has(.los-kpi){flex-wrap:wrap}
          div[data-testid="stHorizontalBlock"]:has(.los-kpi)>div[data-testid="stColumn"]{min-width:190px;flex:1 1 calc(33.333% - .75rem)!important}
          .st-key-home_orbit{min-height:0;overflow:visible}.los-core-stage{position:relative;height:590px}.los-core{width:100%;min-height:480px;padding:54px 38px 38px}.los-core-rings{width:min(590px,96%);height:auto;aspect-ratio:1}.los-core-rings i:nth-child(1){width:84%;height:84%}
          .st-key-home_orbit_finance,.st-key-home_orbit_health,.st-key-home_orbit_vehicle,.st-key-home_orbit_learning,.st-key-home_orbit_knowledge,.st-key-home_orbit_routine{position:static;display:inline-block;width:calc(50% - 12px);animation:none;margin:5px;vertical-align:top}
          .los-health-row{grid-template-columns:10px 1fr auto}.los-health-row>span:nth-of-type(2){display:none}
        }
        @media(max-width:760px){
          html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{max-width:100vw!important;overflow-x:hidden!important}
          [data-testid="stSidebar"]{width:min(86vw,290px)!important}.block-container{padding:.9rem .85rem 4.25rem;max-width:100%;overflow-x:hidden}
          .block-container:has(.st-key-home_orbit){box-sizing:border-box!important;width:100vw!important;max-width:100vw!important;margin:0!important;transform:none!important}
          .los-system-banner{min-height:62px;padding:10px 12px}.los-orb{width:36px;height:36px}.los-system-state small{display:none}.los-system-state{padding:7px 9px}
          .los-page-header{align-items:flex-start;padding:25px 2px 18px}.los-page-header h1{font-size:2.25rem!important}.los-page-header p{font-size:.84rem}.los-badge{margin-top:3px}
          div[data-testid="stHorizontalBlock"]{flex-wrap:wrap;gap:.65rem!important}
          div[data-testid="stHorizontalBlock"]>div[data-testid="stColumn"]{min-width:min(100%,260px)!important;flex:1 1 calc(50% - .65rem)!important}
          div[data-testid="stColumn"]:has(.los-feed),div[data-testid="stColumn"]:has(.los-health-row){padding:2px 12px 12px}
          [data-testid="stDataFrame"]{max-width:100%;overflow:auto}.stButton button{width:100%}
          .st-key-home_orbit{min-height:0;overflow:visible}.los-core-stage{position:relative;height:580px}.los-core{width:min(500px,92vw);min-height:480px;padding:54px 38px 38px}.los-core-rings{width:530px;height:530px}.los-core-rings i:nth-child(1){width:450px;height:450px}.los-core-rings i:nth-child(2){width:370px;height:370px}.los-core-rings i:nth-child(3){width:290px;height:290px}
          .st-key-home_orbit_finance,.st-key-home_orbit_health,.st-key-home_orbit_vehicle,.st-key-home_orbit_learning,.st-key-home_orbit_knowledge,.st-key-home_orbit_routine{display:block;width:100%;margin:5px 0}
        }
        @media(max-width:480px){
          .block-container{padding:.7rem .62rem 4.5rem}.los-system-banner>div:nth-child(2) small{display:none}.los-wordmark{font-size:.82rem}.los-orb{width:32px;height:32px}.los-orb span{width:10px;height:10px}
          .los-page-header{display:block}.los-page-header h1{font-size:2rem!important}.los-badge{display:inline-block;margin-top:14px}
          div[data-testid="stHorizontalBlock"]>div[data-testid="stColumn"],div[data-testid="stHorizontalBlock"]:has(.los-kpi)>div[data-testid="stColumn"]{min-width:100%!important;flex-basis:100%!important}
          .los-kpi{min-height:116px}.los-kpi-value{font-size:1.8rem;margin:.7rem 0 .32rem}.los-empty{min-height:145px}
          .los-activity{grid-template-columns:10px 1fr}.los-activity time{grid-column:2}.los-health-row{grid-template-columns:9px 1fr auto}
          [data-testid="stForm"]{padding:.9rem!important}[data-baseweb="tab-list"]{overflow-x:auto;scrollbar-width:none}
          .los-core-stage{height:530px}.los-core{width:100%;min-height:455px;padding:48px 22px 32px;border-radius:34% 66% 40% 60% / 55% 42% 58% 45%}.los-core h1{font-size:2.7rem!important;white-space:normal}.los-core-kicker{font-size:.52rem;letter-spacing:.16em}.los-core-summary{font-size:.88rem}.los-core-brief{margin:1.4rem 0 1.15rem}.los-core-signals{width:90%}.los-core-signals>div{padding:0 6px}.los-core-signals span{font-size:.48rem}.los-core-signals b{font-size:.61rem}.los-core-rings{width:100%;height:auto;aspect-ratio:1}.los-core-rings i:nth-child(1){width:86%;height:86%}.los-core-rings i:nth-child(2){width:72%;height:72%}.los-core-rings i:nth-child(3){width:58%;height:58%}
        }
        </style>
        """, unsafe_allow_html=True,
    )
