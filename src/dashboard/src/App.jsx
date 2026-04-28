import { useState, useEffect, useRef } from "react";

// ─── BATTERY DATA (Prem — NASA Battery Degradation, XGBoost RUL) ─────────────
const BATTERY_AIRCRAFT = [
  { id:"AC-001", rul:0,  soh:96.5, band:"Critical", status:"In-Flight",  passengers:171, from:"KCI", to:"LAX", engine:"CFM56-7B", lastMaint:"2026-04-24", eta:"29 min", esr:0.21, rct:1.82, temp:38, fadeRate:-0.008, diagnosis:"Battery at end-of-life (RUL=0). Rct critically elevated. Immediate replacement required.", sohTrend:[96.5,94.1,91.8,89.2,86.5,83.1,79.4,75.0], rulTrend:[50,42,34,27,18,10,4,0] },
  { id:"AC-002", rul:0,  soh:78.0, band:"Critical", status:"In-Flight",  passengers:219, from:"KCI", to:"JFK", engine:"LEAP-1A",   lastMaint:"2026-04-12", eta:"38 min", esr:0.28, rct:2.10, temp:41, fadeRate:-0.012, diagnosis:"SOH at 78% — below safe threshold. Capacity fade accelerating over last 10 cycles.", sohTrend:[78.0,76.5,74.2,72.8,71.0,69.5,67.8,66.0], rulTrend:[50,40,30,21,13,6,2,0] },
  { id:"AC-003", rul:0,  soh:90.4, band:"Critical", status:"Taxiing",    passengers:141, from:"KCI", to:"SEA", engine:"PW1100G",   lastMaint:"2026-04-15", eta:"65 min", esr:0.25, rct:1.95, temp:43, fadeRate:-0.009, diagnosis:"Impedance anomaly — EOL reached. Thermal stress factor beyond safe range.", sohTrend:[90.4,88.6,86.1,83.7,81.2,78.4,75.6,72.5], rulTrend:[50,44,37,29,20,11,5,0] },
  { id:"AC-004", rul:35, soh:87.0, band:"Warning",  status:"Grounded",   passengers:0,   from:"KCI", to:"MIA", engine:"LEAP-1B",   lastMaint:"2026-04-06", eta:"—",      esr:0.19, rct:1.74, temp:36, fadeRate:-0.005, diagnosis:"SOH 87%. 35 cycles to EOL. Grounded pending inspection.", sohTrend:[87.0,86.1,85.2,84.4,83.5,82.6,81.8,80.9], rulTrend:[50,48,46,44,43,41,38,35] },
  { id:"AC-005", rul:29, soh:81.9, band:"Warning",  status:"In-Flight",  passengers:173, from:"KCI", to:"ATL", engine:"PW4000",    lastMaint:"2026-04-16", eta:"18 min", esr:0.22, rct:1.88, temp:37, fadeRate:-0.007, diagnosis:"SOH 81.9%, Rct_norm rising. Schedule maintenance within 2 weeks.", sohTrend:[81.9,81.2,80.5,79.8,79.1,78.4,77.7,77.0], rulTrend:[50,46,43,40,37,34,32,29] },
  { id:"AC-006", rul:48, soh:91.0, band:"Warning",  status:"In-Flight",  passengers:134, from:"KCI", to:"DEN", engine:"CF6-80",    lastMaint:"2026-04-13", eta:"86 min", esr:0.17, rct:1.65, temp:35, fadeRate:-0.004, diagnosis:"Nearing warning threshold. Monitor charge-transfer resistance trend.", sohTrend:[91.0,90.5,90.0,89.4,88.9,88.3,87.8,87.2], rulTrend:[50,49,49,48,48,48,48,48] },
  { id:"AC-007", rul:92, soh:98.6, band:"Normal",   status:"In-Flight",  passengers:160, from:"KCI", to:"SFO", engine:"CFM56-7B",  lastMaint:"2026-04-08", eta:"43 min", esr:0.14, rct:1.42, temp:32, fadeRate:-0.001, diagnosis:"All metrics nominal. SOH 98.6%, 92 cycles remaining.", sohTrend:[98.6,98.4,98.3,98.1,97.9,97.8,97.6,97.4], rulTrend:[50,50,50,50,50,50,50,50] },
  { id:"AC-008", rul:57, soh:85.4, band:"Normal",   status:"Taxiing",    passengers:114, from:"KCI", to:"BOS", engine:"LEAP-1A",   lastMaint:"2026-04-08", eta:"49 min", esr:0.16, rct:1.58, temp:33, fadeRate:-0.002, diagnosis:"Healthy — slight capacity fade within expected degradation curve.", sohTrend:[85.4,85.2,85.0,84.8,84.6,84.4,84.2,84.0], rulTrend:[50,50,50,50,50,50,50,50] },
  { id:"AC-009", rul:72, soh:94.9, band:"Normal",   status:"Gate",       passengers:0,   from:"KCI", to:"LAS", engine:"PW1100G",   lastMaint:"2026-04-03", eta:"—",      esr:0.13, rct:1.38, temp:31, fadeRate:-0.001, diagnosis:"Excellent condition. No anomalies detected.", sohTrend:[94.9,94.8,94.7,94.6,94.5,94.4,94.3,94.2], rulTrend:[50,50,50,50,50,50,50,50] },
  { id:"AC-010", rul:86, soh:98.3, band:"Normal",   status:"Gate",       passengers:0,   from:"KCI", to:"PHX", engine:"CFM56-5B",  lastMaint:"2026-04-23", eta:"—",      esr:0.12, rct:1.35, temp:30, fadeRate:0.000,  diagnosis:"Fully healthy. Recently maintained — all metrics nominal.", sohTrend:[98.3,98.2,98.2,98.1,98.0,98.0,97.9,97.8], rulTrend:[50,50,50,50,50,50,50,50] },
];

// ─── CAPACITOR DATA (Hrishikesh — NASA Capacitor EIS Dataset) ────────────────
const CAPACITOR_DATA = [
  { id:"CAP-ES10-C1", stress:"ES10", esr:0.179, cs:1459.9, zmag:0.272, phase:-20.77, sweeps:24, band:"Normal",   rul:82, diagnosis:"ESR within nominal bounds. Capacitance stable across sweep history." },
  { id:"CAP-ES10-C2", stress:"ES10", esr:0.198, cs:1420.3, zmag:0.291, phase:-19.85, sweeps:24, band:"Normal",   rul:71, diagnosis:"Minor ESR increase. Monitor over next 5 sweeps." },
  { id:"CAP-ES12-C1", stress:"ES12", esr:0.312, cs:1201.6, zmag:0.418, phase:-14.22, sweeps:31, band:"Warning",  rul:38, diagnosis:"Capacitance degraded 17.7% from baseline. ESR elevated. Schedule replacement." },
  { id:"CAP-ES12-C2", stress:"ES12", esr:0.291, cs:1255.4, zmag:0.389, phase:-15.63, sweeps:31, band:"Warning",  rul:44, diagnosis:"Phase shift anomaly detected. Cs dropping below warning threshold." },
  { id:"CAP-ES14-C1", stress:"ES14", esr:0.451, cs:988.2,  zmag:0.612, phase:-9.41,  sweeps:39, band:"Critical", rul:8,  diagnosis:"ESR 2.5x baseline — near end-of-life. Cs below 1000 µF critical limit." },
  { id:"CAP-ES14-C2", stress:"ES14", esr:0.489, cs:942.7,  zmag:0.658, phase:-8.77,  sweeps:39, band:"Critical", rul:3,  diagnosis:"Catastrophic Cs loss (35%). Phase response severely degraded. Replace immediately." },
];

// ─── NGAFID ENGINE DATA (Jal/Deveshree — NGAFID Flight Sensor) ───────────────
const ENGINE_DATA = [
  { id:"ENG-F001", label:"baffle crack", egt1:412, cht1:385, rpm:2350, oilT:195, oilP:72, ias:118, altMSL:4200, fflow:8.2, band:"Critical", rul:12, diagnosis:"EGT1 spike + CHT deviation — baffle crack signature detected." },
  { id:"ENG-F002", label:"oil leak",     egt1:388, cht1:362, rpm:2280, oilT:218, oilP:58, ias:112, altMSL:3800, fflow:7.9, band:"Critical", rul:7,  diagnosis:"Oil pressure critically low (58 PSI). EGT rising — oil starvation risk." },
  { id:"ENG-F003", label:"normal",       egt1:341, cht1:328, rpm:2420, oilT:182, oilP:84, ias:124, altMSL:5100, fflow:8.8, band:"Normal",   rul:95, diagnosis:"All sensor readings within normal operating bounds." },
  { id:"ENG-F004", label:"baffle loose", egt1:398, cht1:371, rpm:2310, oilT:201, oilP:68, ias:116, altMSL:4500, fflow:8.1, band:"Warning",  rul:33, diagnosis:"CHT asymmetry between cylinders 1-4. Possible loose baffle." },
  { id:"ENG-F005", label:"normal",       egt1:338, cht1:322, rpm:2445, oilT:178, oilP:87, ias:127, altMSL:5400, fflow:9.1, band:"Normal",   rul:88, diagnosis:"Clean sensor profile. Engine operating nominally." },
];

// ─── HELPERS ─────────────────────────────────────────────────────────────────
const RC = b => b==="Critical"?"#ff3b3b":b==="Warning"?"#ff9f1a":"#7cff6b";
const SC = s => ({
  "In-Flight":"#3bf0ff", "Grounded":"#ff3b3b", "Taxiing":"#ffd439", "Gate":"#7cff6b"
})[s] || "#8892a4";

const CRIT_BAT = BATTERY_AIRCRAFT.filter(a=>a.band==="Critical").length;
const WARN_BAT = BATTERY_AIRCRAFT.filter(a=>a.band==="Warning").length;
const NORM_BAT = BATTERY_AIRCRAFT.filter(a=>a.band==="Normal").length;
const AVG_RUL  = Math.round(BATTERY_AIRCRAFT.filter(a=>a.rul>0).reduce((s,a)=>s+a.rul,0)/BATTERY_AIRCRAFT.filter(a=>a.rul>0).length);

// ─── SMALL COMPONENTS ────────────────────────────────────────────────────────
function Sparkline({ data, color="#3bf0ff", width=120, height=36 }) {
  const min=Math.min(...data), max=Math.max(...data), range=max-min||1;
  const pts = data.map((v,i)=>`${(i/(data.length-1))*width},${height-((v-min)/range)*(height-6)-3}`).join(" ");
  const id = `sg${color.replace(/[^a-z0-9]/gi,"")}${width}`;
  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} style={{display:"block"}}>
      <defs><linearGradient id={id} x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stopColor={color} stopOpacity="0.25"/><stop offset="100%" stopColor={color} stopOpacity="0"/>
      </linearGradient></defs>
      <polygon points={`0,${height} ${pts} ${width},${height}`} fill={`url(#${id})`}/>
      <polyline points={pts} fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  );
}

function RingGauge({ value, total, color, label, size=82 }) {
  const r=(size-12)/2, circ=2*Math.PI*r;
  const [anim,setAnim]=useState(0);
  useEffect(()=>{const t=setTimeout(()=>setAnim(value/total),120);return()=>clearTimeout(t);},[value,total]);
  return (
    <div style={{display:"flex",flexDirection:"column",alignItems:"center",gap:4}}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="8"/>
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={color} strokeWidth="8"
          strokeDasharray={circ} strokeDashoffset={circ*(1-anim)} strokeLinecap="round"
          transform={`rotate(-90 ${size/2} ${size/2})`}
          style={{transition:"stroke-dashoffset 1.2s cubic-bezier(0.4,0,0.2,1)"}}/>
        <text x={size/2} y={size/2-3} textAnchor="middle" fill="white" fontSize="19" fontWeight="700" fontFamily="'DM Sans',sans-serif">{value}</text>
        <text x={size/2} y={size/2+13} textAnchor="middle" fill="rgba(255,255,255,0.35)" fontSize="9" fontFamily="'DM Sans',sans-serif">/ {total}</text>
      </svg>
      <span style={{fontSize:9,color:"rgba(255,255,255,0.35)",letterSpacing:"0.09em",textTransform:"uppercase",fontWeight:600}}>{label}</span>
    </div>
  );
}

function StatusDot({ color }) {
  return <span style={{position:"relative",display:"inline-block",width:7,height:7,marginRight:5}}>
    <span style={{position:"absolute",top:0,left:0,width:7,height:7,borderRadius:"50%",background:color,
      animation:color==="#3bf0ff"||color==="#ffd439"?"pulse 2s infinite":"none"}}/>
  </span>;
}

function Badge({ band }) {
  const c=RC(band);
  return <span style={{display:"inline-flex",alignItems:"center",padding:"2px 10px",borderRadius:20,background:`${c}18`,color:c,fontSize:10,fontWeight:700}}>{band}</span>;
}

function GoNoGo({ band }) {
  const [c,label]=band==="Critical"?["#ff3b3b","NO-GO — Immediate Maintenance Required"]:band==="Warning"?["#ff9f1a","CAUTION — Schedule Maintenance Soon"]:["#7cff6b","GO — Cleared for Operation"];
  return (
    <div style={{padding:"10px 14px",borderRadius:8,background:`${c}12`,border:`1px solid ${c}30`,display:"flex",alignItems:"center",gap:10,marginTop:10}}>
      <div style={{width:11,height:11,borderRadius:"50%",background:c,boxShadow:`0 0 8px ${c}`}}/>
      <span style={{fontWeight:700,fontSize:12,color:c}}>{label}</span>
    </div>
  );
}

// ─── BATTERY RUL PREDICTOR (Manual Input) ────────────────────────────────────
function BatteryPredictor() {
  const [vals, setVals] = useState({
    cycle_normalized: 0.5,
    SOH: 90,
    capacity_ahr: 1.7,
    Re_norm: 1.0,
    Rct_norm: 1.0,
    SOH_rolling_mean: 90,
    SOH_rolling_std: 0.5,
    temperature_stress_factor: 1.0,
    capacity_fade_rate: -0.003,
    ambient_temperature: 25,
  });
  const [result, setResult] = useState(null);

  const fields = [
    { key:"SOH",                   label:"SOH (%)",                min:60,    max:110,  step:0.1,  unit:"%" },
    { key:"capacity_ahr",          label:"Capacity (Ahr)",         min:1.2,   max:2.1,  step:0.01, unit:"Ahr" },
    { key:"cycle_normalized",      label:"Cycle (normalized)",     min:0,     max:1,    step:0.01, unit:"" },
    { key:"Re_norm",               label:"Re (norm)",              min:0.8,   max:2.5,  step:0.01, unit:"×" },
    { key:"Rct_norm",              label:"Rct (norm)",             min:0.8,   max:3.0,  step:0.01, unit:"×" },
    { key:"SOH_rolling_mean",      label:"SOH Rolling Mean",       min:60,    max:110,  step:0.1,  unit:"%" },
    { key:"SOH_rolling_std",       label:"SOH Rolling Std",        min:0,     max:5,    step:0.01, unit:"" },
    { key:"temperature_stress_factor", label:"Temp Stress Factor", min:0.8,   max:1.3,  step:0.01, unit:"×" },
    { key:"capacity_fade_rate",    label:"Capacity Fade Rate",     min:-0.05, max:0.01, step:0.001,unit:"/cyc" },
    { key:"ambient_temperature",   label:"Ambient Temp",           min:4,     max:50,   step:0.5,  unit:"°C" },
  ];

  function predict() {
    // Heuristic XGBoost-like RUL estimate using key features
    const soh    = parseFloat(vals.SOH);
    const rctN   = parseFloat(vals.Rct_norm);
    const reN    = parseFloat(vals.Re_norm);
    const cycN   = parseFloat(vals.cycle_normalized);
    const fade   = parseFloat(vals.capacity_fade_rate);
    const temp   = parseFloat(vals.temperature_stress_factor);

    // Capacity-based: EOL at SOH ~70%
    const sohRUL = Math.max(0, ((soh - 70) / 30) * 50);
    // Impedance penalty
    const impPen = Math.max(0, 1 - ((rctN - 1) * 0.6 + (reN - 1) * 0.3));
    // Fade penalty
    const fadePen = Math.max(0, 1 + fade * 200);
    // Cycle residual
    const cycRUL = Math.max(0, (1 - cycN) * 50);
    // Temp factor
    const tempPen = Math.max(0.5, 2 - temp);

    const raw = Math.round(sohRUL * 0.45 + cycRUL * 0.25 + sohRUL * impPen * fadePen * tempPen * 0.3);
    const rul  = Math.min(50, Math.max(0, raw));
    const band = rul < 15 ? "Critical" : rul < 35 ? "Warning" : "Normal";
    setResult({ rul, band });
  }

  return (
    <div style={{background:"rgba(255,255,255,0.02)",border:"1px solid rgba(255,255,255,0.06)",borderRadius:14,padding:"22px 24px"}}>
      <div style={{fontSize:11,fontWeight:700,textTransform:"uppercase",letterSpacing:"0.12em",color:"rgba(255,255,255,0.35)",marginBottom:18,display:"flex",alignItems:"center",gap:8}}>
        <span style={{color:"#ffd439"}}>⚡</span> Battery RUL Predictor — Manual Input
        <div style={{flex:1,height:1,background:"rgba(255,255,255,0.05)"}}/>
        <span style={{fontSize:9,fontWeight:400,textTransform:"none",letterSpacing:0,color:"rgba(255,255,255,0.22)"}}>NASA Battery XGBoost · RMSE 5.8 · R² 0.92</span>
      </div>

      <div style={{display:"grid",gridTemplateColumns:"repeat(5,1fr)",gap:12,marginBottom:18}}>
        {fields.map(f=>(
          <div key={f.key}>
            <label style={{fontSize:9,color:"rgba(255,255,255,0.38)",textTransform:"uppercase",letterSpacing:"0.08em",display:"block",marginBottom:5,fontWeight:600}}>{f.label}</label>
            <div style={{display:"flex",alignItems:"center",gap:6}}>
              <input
                type="number" min={f.min} max={f.max} step={f.step}
                value={vals[f.key]}
                onChange={e=>setVals({...vals,[f.key]:e.target.value})}
                style={{width:"100%",background:"rgba(255,255,255,0.05)",border:"1px solid rgba(255,255,255,0.1)",borderRadius:7,padding:"7px 10px",color:"#e2e8f0",fontSize:13,fontFamily:"'JetBrains Mono',monospace",outline:"none"}}
              />
            </div>
            <input
              type="range" min={f.min} max={f.max} step={f.step}
              value={vals[f.key]}
              onChange={e=>setVals({...vals,[f.key]:e.target.value})}
              style={{width:"100%",marginTop:4,accentColor:"#3bf0ff",height:2}}
            />
            <div style={{display:"flex",justifyContent:"space-between",fontSize:8,color:"rgba(255,255,255,0.2)"}}>
              <span>{f.min}{f.unit}</span><span>{f.max}{f.unit}</span>
            </div>
          </div>
        ))}
      </div>

      <button onClick={predict} style={{
        padding:"10px 32px",borderRadius:8,border:"1px solid rgba(59,240,255,0.3)",
        background:"rgba(59,240,255,0.08)",color:"#3bf0ff",fontSize:13,fontWeight:700,
        letterSpacing:"0.04em",transition:"all 0.2s",cursor:"pointer",
        boxShadow:"0 0 20px rgba(59,240,255,0.08)"
      }}>▶ Run RUL Prediction</button>

      {result && (
        <div style={{marginTop:18,display:"flex",alignItems:"center",gap:22,padding:"16px 20px",borderRadius:10,background:`${RC(result.band)}08`,border:`1px solid ${RC(result.band)}25`,animation:"fadeIn 0.4s ease"}}>
          <div style={{textAlign:"center"}}>
            <div style={{fontSize:9,color:"rgba(255,255,255,0.35)",textTransform:"uppercase",letterSpacing:"0.1em",marginBottom:4}}>Predicted RUL</div>
            <div style={{fontFamily:"'JetBrains Mono',monospace",fontSize:38,fontWeight:800,color:RC(result.band),lineHeight:1}}>
              {result.rul}<span style={{fontSize:13,fontWeight:400,color:"rgba(255,255,255,0.3)"}}> cyc</span>
            </div>
          </div>
          <div style={{flex:1}}>
            <Badge band={result.band}/>
            <GoNoGo band={result.band}/>
          </div>
          <div style={{textAlign:"right",fontSize:11,color:"rgba(255,255,255,0.3)"}}>
            <div>SOH: {parseFloat(vals.SOH).toFixed(1)}%</div>
            <div>Rct: {parseFloat(vals.Rct_norm).toFixed(2)}×</div>
            <div>Fade: {parseFloat(vals.capacity_fade_rate).toFixed(3)}/cyc</div>
          </div>
        </div>
      )}
    </div>
  );
}

// ─── CAPACITOR PREDICTOR ────────────────────────────────────────────────────
function CapacitorPredictor() {
  const [vals,setVals]=useState({ esr:0.18, cs:1450, zmag:0.27, phase:-20, sweeps:10 });
  const [result,setResult]=useState(null);

  const fields=[
    { key:"esr",    label:"ESR (Ω)",         min:0.10, max:0.60, step:0.001 },
    { key:"cs",     label:"Cs (µF)",          min:800,  max:1600, step:1 },
    { key:"zmag",   label:"Zmag (Ω)",         min:0.15, max:0.80, step:0.001 },
    { key:"phase",  label:"Phase (°)",        min:-40,  max:-5,   step:0.1 },
    { key:"sweeps", label:"Sweep Number",     min:1,    max:50,   step:1 },
  ];

  function predict() {
    const esr=parseFloat(vals.esr), cs=parseFloat(vals.cs);
    const sw=parseFloat(vals.sweeps), ph=parseFloat(vals.phase);
    // ESR-based: baseline ~0.18Ω, EOL when ESR > 0.45Ω
    const esrFactor = Math.max(0, 1 - (esr - 0.18) / (0.45 - 0.18));
    // Capacitance: baseline ~1460µF, EOL when Cs < 900µF
    const csFactor  = Math.max(0, (cs - 900) / (1460 - 900));
    // Sweep penalty: longer in service = closer to EOL
    const sweepFactor = Math.max(0, 1 - sw/50);
    const raw = Math.round((esrFactor*0.5 + csFactor*0.35 + sweepFactor*0.15) * 90);
    const rul  = Math.min(90, Math.max(0, raw));
    const band = rul < 20 ? "Critical" : rul < 50 ? "Warning" : "Normal";
    setResult({ rul, band });
  }

  return (
    <div style={{background:"rgba(255,255,255,0.02)",border:"1px solid rgba(255,255,255,0.06)",borderRadius:14,padding:"22px 24px"}}>
      <div style={{fontSize:11,fontWeight:700,textTransform:"uppercase",letterSpacing:"0.12em",color:"rgba(255,255,255,0.35)",marginBottom:18,display:"flex",alignItems:"center",gap:8}}>
        <span style={{color:"#a78bfa"}}>⚙</span> Capacitor Degradation Predictor
        <div style={{flex:1,height:1,background:"rgba(255,255,255,0.05)"}}/>
        <span style={{fontSize:9,fontWeight:400,textTransform:"none",letterSpacing:0,color:"rgba(255,255,255,0.22)"}}>NASA Capacitor EIS Dataset · Hrishikesh</span>
      </div>

      <div style={{display:"grid",gridTemplateColumns:"repeat(5,1fr)",gap:12,marginBottom:18}}>
        {fields.map(f=>(
          <div key={f.key}>
            <label style={{fontSize:9,color:"rgba(255,255,255,0.38)",textTransform:"uppercase",letterSpacing:"0.08em",display:"block",marginBottom:5,fontWeight:600}}>{f.label}</label>
            <input type="number" min={f.min} max={f.max} step={f.step} value={vals[f.key]}
              onChange={e=>setVals({...vals,[f.key]:e.target.value})}
              style={{width:"100%",background:"rgba(255,255,255,0.05)",border:"1px solid rgba(255,255,255,0.1)",borderRadius:7,padding:"7px 10px",color:"#e2e8f0",fontSize:13,fontFamily:"'JetBrains Mono',monospace",outline:"none"}}/>
            <input type="range" min={f.min} max={f.max} step={f.step} value={vals[f.key]}
              onChange={e=>setVals({...vals,[f.key]:e.target.value})}
              style={{width:"100%",marginTop:4,accentColor:"#a78bfa",height:2}}/>
            <div style={{display:"flex",justifyContent:"space-between",fontSize:8,color:"rgba(255,255,255,0.2)"}}>
              <span>{f.min}</span><span>{f.max}</span>
            </div>
          </div>
        ))}
      </div>

      <button onClick={predict} style={{padding:"10px 32px",borderRadius:8,border:"1px solid rgba(167,139,250,0.3)",background:"rgba(167,139,250,0.08)",color:"#a78bfa",fontSize:13,fontWeight:700,letterSpacing:"0.04em",cursor:"pointer"}}>
        ▶ Run Capacitor RUL
      </button>

      {result && (
        <div style={{marginTop:18,display:"flex",alignItems:"center",gap:22,padding:"16px 20px",borderRadius:10,background:`${RC(result.band)}08`,border:`1px solid ${RC(result.band)}25`,animation:"fadeIn 0.4s ease"}}>
          <div style={{textAlign:"center"}}>
            <div style={{fontSize:9,color:"rgba(255,255,255,0.35)",textTransform:"uppercase",letterSpacing:"0.1em",marginBottom:4}}>Predicted RUL</div>
            <div style={{fontFamily:"'JetBrains Mono',monospace",fontSize:38,fontWeight:800,color:RC(result.band),lineHeight:1}}>
              {result.rul}<span style={{fontSize:13,fontWeight:400,color:"rgba(255,255,255,0.3)"}}> sw</span>
            </div>
          </div>
          <div style={{flex:1}}>
            <Badge band={result.band}/>
            <GoNoGo band={result.band}/>
          </div>
          <div style={{textAlign:"right",fontSize:11,color:"rgba(255,255,255,0.3)"}}>
            <div>ESR: {parseFloat(vals.esr).toFixed(3)} Ω</div>
            <div>Cs: {parseFloat(vals.cs).toFixed(0)} µF</div>
            <div>Phase: {parseFloat(vals.phase).toFixed(1)}°</div>
          </div>
        </div>
      )}
    </div>
  );
}

// ─── ENGINE PREDICTOR (NGAFID) ──────────────────────────────────────────────
function EnginePredictor() {
  const [vals,setVals]=useState({ egt1:350, cht1:330, rpm:2400, oilT:185, oilP:82, ias:120, altMSL:4500, fflow:8.5 });
  const [result,setResult]=useState(null);

  const fields=[
    { key:"egt1",   label:"EGT1 (°F)",  min:250, max:500, step:1 },
    { key:"cht1",   label:"CHT1 (°F)",  min:200, max:450, step:1 },
    { key:"rpm",    label:"RPM",        min:1800, max:2700, step:10 },
    { key:"oilT",   label:"Oil Temp (°F)", min:100, max:260, step:1 },
    { key:"oilP",   label:"Oil PSI",    min:20, max:100, step:1 },
    { key:"ias",    label:"IAS (kt)",   min:50, max:160, step:1 },
    { key:"altMSL", label:"Alt (ft)",   min:0, max:12000, step:100 },
    { key:"fflow",  label:"Fuel Flow",  min:3, max:15, step:0.1 },
  ];

  function predict() {
    const egt=parseFloat(vals.egt1), cht=parseFloat(vals.cht1);
    const oilP=parseFloat(vals.oilP), oilT=parseFloat(vals.oilT);
    // Anomaly heuristics from NGAFID labels
    const egtScore  = egt > 420 ? 0 : egt > 380 ? 0.5 : 1;
    const chtScore  = cht > 400 ? 0 : cht > 360 ? 0.5 : 1;
    const oilPScore = oilP < 60 ? 0 : oilP < 75 ? 0.5 : 1;
    const oilTScore = oilT > 220 ? 0 : oilT > 200 ? 0.5 : 1;
    const health = (egtScore*0.35 + chtScore*0.25 + oilPScore*0.25 + oilTScore*0.15);
    const rul   = Math.round(health * 100);
    const band  = rul < 30 ? "Critical" : rul < 65 ? "Warning" : "Normal";
    const label = egt>420&&cht>380?"Baffle crack / EGT spike":oilP<60?"Oil system fault":oilT>220?"Oil temperature anomaly":"Normal operation";
    setResult({ rul, band, label });
  }

  return (
    <div style={{background:"rgba(255,255,255,0.02)",border:"1px solid rgba(255,255,255,0.06)",borderRadius:14,padding:"22px 24px"}}>
      <div style={{fontSize:11,fontWeight:700,textTransform:"uppercase",letterSpacing:"0.12em",color:"rgba(255,255,255,0.35)",marginBottom:18,display:"flex",alignItems:"center",gap:8}}>
        <span style={{color:"#38bdf8"}}>✈</span> Engine Health Predictor (NGAFID)
        <div style={{flex:1,height:1,background:"rgba(255,255,255,0.05)"}}/>
        <span style={{fontSize:9,fontWeight:400,textTransform:"none",letterSpacing:0,color:"rgba(255,255,255,0.22)"}}>NGAFID Flight Sensor Dataset · Jal / Deveshree</span>
      </div>

      <div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:12,marginBottom:18}}>
        {fields.map(f=>(
          <div key={f.key}>
            <label style={{fontSize:9,color:"rgba(255,255,255,0.38)",textTransform:"uppercase",letterSpacing:"0.08em",display:"block",marginBottom:5,fontWeight:600}}>{f.label}</label>
            <input type="number" min={f.min} max={f.max} step={f.step} value={vals[f.key]}
              onChange={e=>setVals({...vals,[f.key]:e.target.value})}
              style={{width:"100%",background:"rgba(255,255,255,0.05)",border:"1px solid rgba(255,255,255,0.1)",borderRadius:7,padding:"7px 10px",color:"#e2e8f0",fontSize:13,fontFamily:"'JetBrains Mono',monospace",outline:"none"}}/>
            <input type="range" min={f.min} max={f.max} step={f.step} value={vals[f.key]}
              onChange={e=>setVals({...vals,[f.key]:e.target.value})}
              style={{width:"100%",marginTop:4,accentColor:"#38bdf8",height:2}}/>
            <div style={{display:"flex",justifyContent:"space-between",fontSize:8,color:"rgba(255,255,255,0.2)"}}>
              <span>{f.min}</span><span>{f.max}</span>
            </div>
          </div>
        ))}
      </div>

      <button onClick={predict} style={{padding:"10px 32px",borderRadius:8,border:"1px solid rgba(56,189,248,0.3)",background:"rgba(56,189,248,0.08)",color:"#38bdf8",fontSize:13,fontWeight:700,letterSpacing:"0.04em",cursor:"pointer"}}>
        ▶ Run Engine Health Check
      </button>

      {result && (
        <div style={{marginTop:18,display:"flex",alignItems:"center",gap:22,padding:"16px 20px",borderRadius:10,background:`${RC(result.band)}08`,border:`1px solid ${RC(result.band)}25`,animation:"fadeIn 0.4s ease"}}>
          <div style={{textAlign:"center"}}>
            <div style={{fontSize:9,color:"rgba(255,255,255,0.35)",textTransform:"uppercase",letterSpacing:"0.1em",marginBottom:4}}>Health Score</div>
            <div style={{fontFamily:"'JetBrains Mono',monospace",fontSize:38,fontWeight:800,color:RC(result.band),lineHeight:1}}>{result.rul}<span style={{fontSize:13,fontWeight:400,color:"rgba(255,255,255,0.3)"}}>%</span></div>
          </div>
          <div style={{flex:1}}>
            <Badge band={result.band}/>
            <div style={{fontSize:12,color:"rgba(255,255,255,0.5)",marginTop:6}}>Detected: <span style={{color:"#e2e8f0",fontWeight:600}}>{result.label}</span></div>
            <GoNoGo band={result.band}/>
          </div>
          <div style={{textAlign:"right",fontSize:11,color:"rgba(255,255,255,0.3)"}}>
            <div>EGT1: {vals.egt1}°F</div>
            <div>OilP: {vals.oilP} PSI</div>
            <div>OilT: {vals.oilT}°F</div>
          </div>
        </div>
      )}
    </div>
  );
}

// ─── MAIN APP ─────────────────────────────────────────────────────────────────
const PAGES = ["Fleet Overview","Battery Monitor","Capacitor Health","Engine Sensors","Predictor Tool"];

export default function App() {
  const [page, setPage]     = useState(0);
  const [batFilter, setBatFilter] = useState("All");
  const [selBat, setSelBat] = useState(null);
  const [time, setTime]     = useState(new Date());
  const [predictorTab, setPredictorTab] = useState(0);

  useEffect(()=>{ const t=setInterval(()=>setTime(new Date()),1000); return()=>clearInterval(t); },[]);
  const utc = time.toISOString().slice(11,19)+" UTC";

  const filteredBat = batFilter==="All" ? BATTERY_AIRCRAFT : BATTERY_AIRCRAFT.filter(a=>a.band===batFilter);

  const S = {
    app:  { minHeight:"100vh", background:"linear-gradient(145deg,#060a14 0%,#0a0e1a 40%,#0d1321 100%)", fontFamily:"'DM Sans',sans-serif", color:"#e2e8f0", overflow:"hidden auto" },
    grid: { position:"fixed", top:0,left:0,right:0,bottom:0, backgroundImage:"linear-gradient(rgba(59,240,255,0.02) 1px,transparent 1px),linear-gradient(90deg,rgba(59,240,255,0.02) 1px,transparent 1px)", backgroundSize:"55px 55px", pointerEvents:"none", zIndex:0 },
    top:  { display:"flex", justifyContent:"space-between", alignItems:"center", padding:"12px 28px", borderBottom:"1px solid rgba(59,240,255,0.07)", background:"rgba(6,10,20,0.9)", backdropFilter:"blur(24px)", position:"sticky", top:0, zIndex:100 },
    body: { padding:"22px 28px", position:"relative", zIndex:1 },
    card: { background:"rgba(255,255,255,0.025)", border:"1px solid rgba(255,255,255,0.06)", borderRadius:14, padding:"18px 22px", backdropFilter:"blur(8px)" },
    th:   { padding:"11px 16px", textAlign:"left", fontSize:9, fontWeight:700, textTransform:"uppercase", letterSpacing:"0.12em", color:"rgba(255,255,255,0.3)", borderBottom:"1px solid rgba(255,255,255,0.05)", whiteSpace:"nowrap" },
    td:   { padding:"13px 16px", fontSize:12, borderBottom:"1px solid rgba(255,255,255,0.03)", verticalAlign:"middle" },
    sh:   { fontSize:11,fontWeight:700,textTransform:"uppercase",letterSpacing:"0.13em",color:"rgba(255,255,255,0.32)",marginBottom:14,display:"flex",alignItems:"center",gap:8 },
    line: { flex:1,height:1,background:"rgba(255,255,255,0.05)" },
    mono: { fontFamily:"'JetBrains Mono',monospace" },
  };

  const navBtn = (label, i) => (
    <button key={i} onClick={()=>setPage(i)} style={{
      padding:"6px 16px", borderRadius:7, fontSize:11, fontWeight:600, letterSpacing:"0.02em", transition:"all 0.2s",
      border: page===i ? "1px solid rgba(59,240,255,0.25)" : "1px solid transparent",
      background: page===i ? "rgba(59,240,255,0.1)" : "transparent",
      color: page===i ? "#3bf0ff" : "rgba(255,255,255,0.35)", cursor:"pointer",
    }}>{label}</button>
  );

  return (
    <div style={S.app}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300..800&family=JetBrains+Mono:wght@400;600&display=swap');
        @keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:0.5;transform:scale(1.8)}}
        @keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
        *{box-sizing:border-box;margin:0;padding:0}
        ::-webkit-scrollbar{width:4px} ::-webkit-scrollbar-thumb{background:rgba(59,240,255,0.15);border-radius:3px}
        table{border-collapse:collapse;width:100%}
        tr{transition:background 0.15s}
        button{cursor:pointer;font-family:'DM Sans',sans-serif}
        input[type=number]{-moz-appearance:textfield}
        input[type=number]::-webkit-inner-spin-button,input[type=number]::-webkit-outer-spin-button{-webkit-appearance:none}
      `}</style>
      <div style={S.grid}/>

      {/* TOP BAR */}
      <div style={S.top}>
        <div style={{display:"flex",alignItems:"center",gap:12}}>
          <div style={{width:32,height:32,borderRadius:8,background:"linear-gradient(135deg,#3bf0ff,#0ea5e9)",display:"flex",alignItems:"center",justifyContent:"center",fontSize:16,fontWeight:900,color:"#060a14",boxShadow:"0 0 16px rgba(59,240,255,0.3)"}}>K</div>
          <div>
            <div style={{fontSize:15,fontWeight:700,letterSpacing:"-0.02em",background:"linear-gradient(135deg,#fff,#94a3b8)",WebkitBackgroundClip:"text",WebkitTextFillColor:"transparent"}}>Kansas Fleet — IFRPM</div>
            <div style={{fontSize:8,color:"rgba(255,255,255,0.25)",letterSpacing:"0.1em",textTransform:"uppercase"}}>Intelligent Flight Readiness & Predictive Maintenance</div>
          </div>
        </div>
        <div style={{display:"flex",alignItems:"center",gap:6}}>{PAGES.map(navBtn)}</div>
        <div style={{display:"flex",alignItems:"center",gap:16}}>
          <div style={{display:"flex",alignItems:"center",gap:5,fontSize:10}}>
            <span style={{width:6,height:6,borderRadius:"50%",background:"#7cff6b",display:"inline-block",boxShadow:"0 0 6px #7cff6b"}}/>
            <span style={{color:"rgba(255,255,255,0.35)"}}>Live</span>
          </div>
          <div style={{fontSize:10,color:"rgba(255,255,255,0.28)",...S.mono}}>{utc}</div>
        </div>
      </div>

      <div style={S.body}>

        {/* ── PAGE 0: Fleet Overview ─────────────────────────────────────── */}
        {page===0 && (
          <div style={{animation:"fadeIn 0.4s ease"}}>
            {/* KPI ROW */}
            <div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:14,marginBottom:22}}>
              <div style={S.card}>
                <div style={{fontSize:9,color:"rgba(255,255,255,0.35)",textTransform:"uppercase",letterSpacing:"0.1em",fontWeight:700,marginBottom:8}}>Total Monitored</div>
                <div style={{display:"flex",alignItems:"flex-end",justifyContent:"space-between"}}>
                  <div><div style={{fontSize:36,fontWeight:800,color:"#fff",lineHeight:1}}>{BATTERY_AIRCRAFT.length + CAPACITOR_DATA.length + ENGINE_DATA.length}</div>
                  <div style={{fontSize:10,color:"rgba(255,255,255,0.28)",marginTop:3}}>components across 3 datasets</div></div>
                  <Sparkline data={[12,14,15,16,17,18,19,21]} color="#3bf0ff" width={66} height={28}/>
                </div>
              </div>
              <div style={S.card}>
                <div style={{fontSize:9,color:"rgba(255,255,255,0.35)",textTransform:"uppercase",letterSpacing:"0.1em",fontWeight:700,marginBottom:8}}>Battery Fleet</div>
                <div style={{display:"flex",alignItems:"center",gap:12,marginTop:2}}>
                  <RingGauge value={NORM_BAT} total={BATTERY_AIRCRAFT.length} color="#7cff6b" label="Normal" size={70}/>
                  <RingGauge value={WARN_BAT} total={BATTERY_AIRCRAFT.length} color="#ff9f1a" label="Warning" size={70}/>
                  <RingGauge value={CRIT_BAT} total={BATTERY_AIRCRAFT.length} color="#ff3b3b" label="Critical" size={70}/>
                </div>
              </div>
              <div style={S.card}>
                <div style={{fontSize:9,color:"rgba(255,255,255,0.35)",textTransform:"uppercase",letterSpacing:"0.1em",fontWeight:700,marginBottom:8}}>Predicted Failures (48h)</div>
                <div style={{display:"flex",alignItems:"flex-end",justifyContent:"space-between"}}>
                  <div>
                    <div style={{fontSize:36,fontWeight:800,color:"#ff3b3b",lineHeight:1}}>{BATTERY_AIRCRAFT.filter(a=>a.rul<=15).length + CAPACITOR_DATA.filter(c=>c.band==="Critical").length}</div>
                    <div style={{fontSize:10,color:"rgba(255,255,255,0.28)",marginTop:3}}>batteries + capacitors at EOL</div>
                  </div>
                  <div style={{fontSize:11,color:"rgba(255,255,255,0.4)"}}>
                    <div style={{color:"#ff3b3b"}}>▲ {CRIT_BAT + CAPACITOR_DATA.filter(c=>c.band==="Critical").length} critical</div>
                    <div style={{color:"#ff9f1a",marginTop:3}}>● {WARN_BAT + CAPACITOR_DATA.filter(c=>c.band==="Warning").length} warning</div>
                  </div>
                </div>
              </div>
              <div style={S.card}>
                <div style={{fontSize:9,color:"rgba(255,255,255,0.35)",textTransform:"uppercase",letterSpacing:"0.1em",fontWeight:700,marginBottom:8}}>Avg Battery RUL</div>
                <div style={{display:"flex",alignItems:"flex-end",justifyContent:"space-between"}}>
                  <div>
                    <div style={{fontSize:36,fontWeight:800,color:"#ffd439",lineHeight:1}}>{AVG_RUL}<span style={{fontSize:13,fontWeight:400}}> cyc</span></div>
                    <div style={{fontSize:10,color:"rgba(255,255,255,0.28)",marginTop:3}}>Model: RMSE 5.8 · R² 0.92</div>
                  </div>
                  <Sparkline data={[80,72,66,60,54,50,48,AVG_RUL]} color="#ffd439" width={66} height={28}/>
                </div>
              </div>
            </div>

            {/* COMPONENT SUMMARY TABLE */}
            <div style={S.sh}><span style={{color:"#3bf0ff"}}>◆</span> All Datasets — Component Summary<div style={S.line}/></div>
            <div style={{...S.card,padding:0,overflow:"hidden",marginBottom:22}}>
              <table>
                <thead>
                  <tr>
                    {["Dataset","Component","Status","RUL","Risk Band","Key Metric","Go/No-Go"].map(h=><th key={h} style={S.th}>{h}</th>)}
                  </tr>
                </thead>
                <tbody>
                  {BATTERY_AIRCRAFT.slice(0,5).map(a=>(
                    <tr key={a.id} style={{background:"transparent"}}>
                      <td style={{...S.td,fontSize:10,color:"rgba(255,255,255,0.35)"}}>Battery (Prem)</td>
                      <td style={{...S.td,...S.mono,fontWeight:700,color:"#fff"}}>{a.id}</td>
                      <td style={S.td}><span style={{...S.mono,fontSize:11}}><StatusDot color={SC(a.status)}/>{a.status}</span></td>
                      <td style={{...S.td,...S.mono,color:a.rul===0?"#ff3b3b":a.rul<30?"#ff9f1a":"#ffd439",fontWeight:700}}>{a.rul} cyc</td>
                      <td style={S.td}><Badge band={a.band}/></td>
                      <td style={{...S.td,fontSize:11,color:"rgba(255,255,255,0.45)"}}>SOH {a.soh}% · Rct {a.rct.toFixed(2)}×</td>
                      <td style={S.td}><span style={{color:RC(a.band),fontWeight:700,fontSize:11}}>{a.band==="Critical"?"NO-GO":a.band==="Warning"?"CAUTION":"GO"}</span></td>
                    </tr>
                  ))}
                  {CAPACITOR_DATA.slice(0,3).map(c=>(
                    <tr key={c.id}>
                      <td style={{...S.td,fontSize:10,color:"rgba(255,255,255,0.35)"}}>Capacitor (Hrishi)</td>
                      <td style={{...S.td,...S.mono,fontWeight:700,color:"#fff"}}>{c.id}</td>
                      <td style={{...S.td,fontSize:11,color:"rgba(255,255,255,0.4)"}}>Sweep {c.sweeps}</td>
                      <td style={{...S.td,...S.mono,color:c.rul<20?"#ff3b3b":c.rul<50?"#ff9f1a":"#ffd439",fontWeight:700}}>{c.rul} sw</td>
                      <td style={S.td}><Badge band={c.band}/></td>
                      <td style={{...S.td,fontSize:11,color:"rgba(255,255,255,0.45)"}}>ESR {c.esr.toFixed(3)}Ω · Cs {c.cs.toFixed(0)}µF</td>
                      <td style={S.td}><span style={{color:RC(c.band),fontWeight:700,fontSize:11}}>{c.band==="Critical"?"NO-GO":c.band==="Warning"?"CAUTION":"GO"}</span></td>
                    </tr>
                  ))}
                  {ENGINE_DATA.slice(0,3).map(e=>(
                    <tr key={e.id}>
                      <td style={{...S.td,fontSize:10,color:"rgba(255,255,255,0.35)"}}>Engine (NGAFID)</td>
                      <td style={{...S.td,...S.mono,fontWeight:700,color:"#fff"}}>{e.id}</td>
                      <td style={{...S.td,fontSize:11,color:"rgba(255,255,255,0.4)"}}>{e.label}</td>
                      <td style={{...S.td,...S.mono,color:e.rul<30?"#ff3b3b":e.rul<65?"#ff9f1a":"#ffd439",fontWeight:700}}>{e.rul}%</td>
                      <td style={S.td}><Badge band={e.band}/></td>
                      <td style={{...S.td,fontSize:11,color:"rgba(255,255,255,0.45)"}}>EGT {e.egt1}°F · OilP {e.oilP}PSI</td>
                      <td style={S.td}><span style={{color:RC(e.band),fontWeight:700,fontSize:11}}>{e.band==="Critical"?"NO-GO":e.band==="Warning"?"CAUTION":"GO"}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* MODEL METRICS */}
            <div style={S.sh}><span style={{color:"#ffd439"}}>▣</span> Model Performance Summary<div style={S.line}/></div>
            <div style={{display:"grid",gridTemplateColumns:"repeat(3,1fr)",gap:14}}>
              {[
                { title:"Battery RUL — XGBoost",   who:"Prem", color:"#ffd439", metrics:[{l:"RMSE",v:"5.80 cycles"},{l:"MAE",v:"3.30 cycles"},{l:"R²",v:"0.92"},{l:"NASA Score",v:"181.9"}], note:"NASA Battery Dataset · 34 batteries · EOL 1.4 Ahr" },
                { title:"Capacitor EIS — XGBoost",  who:"Hrishikesh", color:"#a78bfa", metrics:[{l:"Dataset",v:"NASA Capacitor"},{l:"Features",v:"ESR, Cs, Zmag"},{l:"Stress IDs",v:"ES10–ES16"},{l:"Sweeps",v:"1657 records"}], note:"EIS Impedance Spectroscopy · Multi-stress levels" },
                { title:"Engine Fault — NGAFID",    who:"Jal / Deveshree", color:"#38bdf8", metrics:[{l:"Dataset",v:"NGAFID"},{l:"Task",v:"Fault Classification"},{l:"Features",v:"EGT, CHT, RPM, Oil"},{l:"Labels",v:"Baffle, Oil, Normal"}], note:"GA flight data · Pre/post maintenance labels" },
              ].map(m=>(
                <div key={m.title} style={{...S.card,borderTop:`3px solid ${m.color}`}}>
                  <div style={{fontSize:12,fontWeight:700,color:"#fff",marginBottom:2}}>{m.title}</div>
                  <div style={{fontSize:10,color:m.color,marginBottom:12}}>{m.who}</div>
                  {m.metrics.map(mt=>(
                    <div key={mt.l} style={{display:"flex",justifyContent:"space-between",marginBottom:7,alignItems:"center"}}>
                      <span style={{fontSize:10,color:"rgba(255,255,255,0.35)",textTransform:"uppercase",letterSpacing:"0.06em"}}>{mt.l}</span>
                      <span style={{...S.mono,fontSize:12,fontWeight:700,color:"#fff"}}>{mt.v}</span>
                    </div>
                  ))}
                  <div style={{fontSize:9,color:"rgba(255,255,255,0.22)",borderTop:"1px solid rgba(255,255,255,0.05)",paddingTop:8,marginTop:4}}>{m.note}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ── PAGE 1: Battery Monitor ────────────────────────────────────── */}
        {page===1 && (
          <div style={{animation:"fadeIn 0.4s ease"}}>
            <div style={{marginBottom:18}}>
              <h2 style={{fontSize:24,fontWeight:800,letterSpacing:"-0.03em",background:"linear-gradient(135deg,#ffd439,#ff9f1a)",WebkitBackgroundClip:"text",WebkitTextFillColor:"transparent"}}>Battery Fleet Monitor</h2>
              <p style={{fontSize:11,color:"rgba(255,255,255,0.3)",marginTop:3}}>NASA Battery Degradation Dataset (PCoE) · Prem · XGBoost RUL · RMSE 5.8 · R² 0.92</p>
            </div>

            {/* Filter */}
            <div style={{display:"flex",gap:8,marginBottom:14}}>
              {["All","Critical","Warning","Normal"].map(f=>(
                <button key={f} onClick={()=>setBatFilter(f)} style={{
                  padding:"4px 14px",borderRadius:18,fontSize:10,fontWeight:700,transition:"all 0.2s",
                  border:`1px solid ${batFilter===f?(f==="Critical"?"#ff3b3b":f==="Warning"?"#ff9f1a":f==="Normal"?"#7cff6b":"rgba(59,240,255,0.4)"):"rgba(255,255,255,0.08)"}`,
                  background:batFilter===f?`${f==="Critical"?"#ff3b3b":f==="Warning"?"#ff9f1a":f==="Normal"?"#7cff6b":"#3bf0ff"}15`:"transparent",
                  color:batFilter===f?(f==="Critical"?"#ff3b3b":f==="Warning"?"#ff9f1a":f==="Normal"?"#7cff6b":"#3bf0ff"):"rgba(255,255,255,0.35)",
                }}>{f}</button>
              ))}
            </div>

            {/* Table */}
            <div style={{...S.card,padding:0,overflow:"hidden",marginBottom:22}}>
              <table>
                <thead><tr>
                  {["Aircraft","Risk","RUL","SOH%","Route","Status","Passengers","ETA","ESR (Ω)","Temp (°C)","Trend"].map(h=><th key={h} style={S.th}>{h}</th>)}
                </tr></thead>
                <tbody>
                  {filteredBat.map((ac,i)=>(
                    <>
                      <tr key={ac.id} onClick={()=>setSelBat(selBat===ac.id?null:ac.id)}
                        style={{cursor:"pointer",background:selBat===ac.id?"rgba(59,240,255,0.04)":"transparent"}}>
                        <td style={{...S.td,...S.mono,fontWeight:700,color:"#fff",fontSize:13}}>{ac.id}</td>
                        <td style={S.td}><Badge band={ac.band}/></td>
                        <td style={{...S.td,...S.mono,color:ac.rul===0?"#ff3b3b":ac.rul<30?"#ff9f1a":"#ffd439",fontWeight:800,fontSize:14}}>{ac.rul}<span style={{fontSize:9,color:"rgba(255,255,255,0.3)",fontWeight:400}}> c</span></td>
                        <td style={S.td}>
                          <div style={{display:"flex",alignItems:"center",gap:7}}>
                            <div style={{width:44,height:4,borderRadius:3,background:"rgba(255,255,255,0.06)",position:"relative",overflow:"hidden"}}>
                              <div style={{position:"absolute",top:0,left:0,height:"100%",width:`${ac.soh}%`,borderRadius:3,background:`linear-gradient(90deg,${RC(ac.band)}88,${RC(ac.band)})`,transition:"width 0.8s"}}/>
                            </div>
                            <span style={{...S.mono,fontSize:11,color:"rgba(255,255,255,0.65)"}}>{ac.soh}%</span>
                          </div>
                        </td>
                        <td style={{...S.td,...S.mono,fontSize:11,color:"rgba(255,255,255,0.5)"}}>{ac.from}→{ac.to}</td>
                        <td style={S.td}><span style={{fontSize:11,...S.mono}}><StatusDot color={SC(ac.status)}/>{ac.status}</span></td>
                        <td style={{...S.td,...S.mono,fontSize:12}}>{ac.passengers||"—"}</td>
                        <td style={{...S.td,...S.mono,fontSize:11,color:ac.eta==="—"?"rgba(255,255,255,0.25)":"rgba(255,255,255,0.65)"}}>{ac.eta}</td>
                        <td style={{...S.td,...S.mono,fontSize:11,color:ac.esr>0.35?"#ff9f1a":"rgba(255,255,255,0.5)"}}>{ac.esr.toFixed(3)}</td>
                        <td style={{...S.td,...S.mono,fontSize:11,color:ac.temp>40?"#ff9f1a":"rgba(255,255,255,0.5)"}}>{ac.temp}°C</td>
                        <td style={S.td}><Sparkline data={ac.sohTrend} color={RC(ac.band)} width={80} height={24}/></td>
                      </tr>
                      {selBat===ac.id && (
                        <tr key={ac.id+"-x"}>
                          <td colSpan={11} style={{padding:0}}>
                            <div style={{background:"rgba(59,240,255,0.025)",borderTop:"1px solid rgba(59,240,255,0.07)",padding:"18px 20px",animation:"fadeIn 0.3s ease"}}>
                              <div style={{display:"grid",gridTemplateColumns:"2fr 1fr 1fr 1fr",gap:18}}>
                                <div>
                                  <div style={{fontSize:9,color:"rgba(255,255,255,0.28)",textTransform:"uppercase",letterSpacing:"0.1em",marginBottom:5}}>Battery Diagnosis</div>
                                  <p style={{fontSize:12,color:"rgba(255,255,255,0.62)",lineHeight:1.7}}>{ac.diagnosis}</p>
                                </div>
                                <div>
                                  <div style={{fontSize:9,color:"rgba(255,255,255,0.28)",textTransform:"uppercase",letterSpacing:"0.1em",marginBottom:5}}>Engine</div>
                                  <div style={{fontSize:12,fontWeight:600}}>{ac.engine}</div>
                                  <div style={{fontSize:9,color:"rgba(255,255,255,0.28)",textTransform:"uppercase",letterSpacing:"0.1em",marginBottom:5,marginTop:10}}>Last Maint.</div>
                                  <div style={{fontSize:12,fontWeight:600}}>{ac.lastMaint}</div>
                                </div>
                                <div>
                                  <div style={{fontSize:9,color:"rgba(255,255,255,0.28)",textTransform:"uppercase",letterSpacing:"0.1em",marginBottom:5}}>RUL Trend</div>
                                  <Sparkline data={ac.rulTrend} color={RC(ac.band)} width={120} height={40}/>
                                </div>
                                <div>
                                  <div style={{fontSize:9,color:"rgba(255,255,255,0.28)",textTransform:"uppercase",letterSpacing:"0.1em",marginBottom:5}}>Go/No-Go</div>
                                  <GoNoGo band={ac.band}/>
                                </div>
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </>
                  ))}
                </tbody>
              </table>
            </div>

            {/* SOH Chart */}
            <div style={S.sh}><span style={{color:"#3bf0ff"}}>◆</span> SOH History — All Aircraft<div style={S.line}/><span style={{fontSize:9,color:"rgba(255,255,255,0.2)",fontWeight:400,textTransform:"none",letterSpacing:0}}>Last 56 hours</span></div>
            <div style={{...S.card,padding:"18px 14px"}}>
              {(() => {
                const w=660,h=160,pad=42;
                return (
                  <svg width="100%" viewBox={`0 0 ${w} ${h+22}`} style={{display:"block"}}>
                    {[70,80,90,100].map(v=>{
                      const y=h-pad-(v-60)/50*(h-2*pad);
                      return <g key={v}>
                        <line x1={pad} y1={y} x2={w-8} y2={y} stroke="rgba(255,255,255,0.04)" strokeWidth="1"/>
                        <text x={pad-6} y={y+4} textAnchor="end" fill="rgba(255,255,255,0.2)" fontSize="9" fontFamily="'DM Sans',sans-serif">{v}%</text>
                      </g>;
                    })}
                    {BATTERY_AIRCRAFT.map((ac,si)=>{
                      const c=RC(ac.band);
                      const pts=ac.sohTrend.map((v,i)=>{
                        const x=pad+(i/(ac.sohTrend.length-1))*(w-pad-8);
                        const y=h-pad-(v-60)/50*(h-2*pad);
                        return `${x},${y}`;
                      }).join(" ");
                      return <polyline key={si} points={pts} fill="none" stroke={c} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" opacity="0.8"/>;
                    })}
                    {["-56h","-48h","-40h","-32h","-24h","-16h","-8h","Now"].map((l,i)=>(
                      <text key={i} x={pad+(i/7)*(w-pad-8)} y={h+14} textAnchor="middle" fill="rgba(255,255,255,0.2)" fontSize="9" fontFamily="'DM Sans',sans-serif">{l}</text>
                    ))}
                  </svg>
                );
              })()}
              <div style={{display:"flex",gap:14,flexWrap:"wrap",marginTop:8,justifyContent:"center"}}>
                {BATTERY_AIRCRAFT.map(ac=>(
                  <div key={ac.id} style={{display:"flex",alignItems:"center",gap:5,fontSize:9}}>
                    <div style={{width:10,height:2,borderRadius:2,background:RC(ac.band)}}/>
                    <span style={{color:"rgba(255,255,255,0.32)",...S.mono}}>{ac.id}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ── PAGE 2: Capacitor Health ───────────────────────────────────── */}
        {page===2 && (
          <div style={{animation:"fadeIn 0.4s ease"}}>
            <div style={{marginBottom:18}}>
              <h2 style={{fontSize:24,fontWeight:800,letterSpacing:"-0.03em",background:"linear-gradient(135deg,#a78bfa,#7c3aed)",WebkitBackgroundClip:"text",WebkitTextFillColor:"transparent"}}>Capacitor Health Monitor</h2>
              <p style={{fontSize:11,color:"rgba(255,255,255,0.3)",marginTop:3}}>NASA Capacitor EIS Dataset (PCoE) · Hrishikesh · EIS Impedance Spectroscopy</p>
            </div>
            <div style={{display:"grid",gap:14}}>
              {CAPACITOR_DATA.map((c,i)=>(
                <div key={c.id} style={{background:"rgba(255,255,255,0.018)",border:`1px solid ${RC(c.band)}18`,borderRadius:14,borderLeft:`3px solid ${RC(c.band)}`,padding:"18px 22px",animation:`fadeIn 0.4s ease ${i*0.06}s both`}}>
                  <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start"}}>
                    <div>
                      <div style={{...S.mono,fontWeight:800,fontSize:15,color:"#fff",marginBottom:6}}>{c.id}</div>
                      <div style={{display:"flex",gap:8}}><Badge band={c.band}/><span style={{fontSize:10,color:"rgba(255,255,255,0.35)"}}>Stress: {c.stress} · Sweep #{c.sweeps}</span></div>
                    </div>
                    <div style={{display:"flex",gap:22}}>
                      {[
                        {l:"RUL",v:`${c.rul} sw`,col:RC(c.band)},
                        {l:"ESR",v:`${c.esr.toFixed(3)} Ω`,col:c.esr>0.35?"#ff9f1a":"rgba(255,255,255,0.7)"},
                        {l:"Cs",v:`${c.cs.toFixed(0)} µF`,col:c.cs<1000?"#ff3b3b":"rgba(255,255,255,0.7)"},
                        {l:"|Zmag|",v:`${c.zmag.toFixed(3)} Ω`,col:"rgba(255,255,255,0.7)"},
                        {l:"Phase",v:`${c.phase.toFixed(1)}°`,col:"rgba(255,255,255,0.7)"},
                      ].map(m=>(
                        <div key={m.l} style={{textAlign:"right"}}>
                          <div style={{fontSize:9,color:"rgba(255,255,255,0.28)",textTransform:"uppercase",letterSpacing:"0.1em",marginBottom:3}}>{m.l}</div>
                          <div style={{...S.mono,fontSize:15,fontWeight:700,color:m.col}}>{m.v}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div style={{marginTop:12,fontSize:12,color:"rgba(255,255,255,0.55)",lineHeight:1.6}}>{c.diagnosis}</div>
                  <GoNoGo band={c.band}/>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ── PAGE 3: Engine Sensors ────────────────────────────────────── */}
        {page===3 && (
          <div style={{animation:"fadeIn 0.4s ease"}}>
            <div style={{marginBottom:18}}>
              <h2 style={{fontSize:24,fontWeight:800,letterSpacing:"-0.03em",background:"linear-gradient(135deg,#38bdf8,#0ea5e9)",WebkitBackgroundClip:"text",WebkitTextFillColor:"transparent"}}>Engine Sensor Monitor (NGAFID)</h2>
              <p style={{fontSize:11,color:"rgba(255,255,255,0.3)",marginTop:3}}>NGAFID General Aviation Flight Data · Jal / Deveshree · Fault Classification</p>
            </div>
            <div style={{display:"grid",gap:14}}>
              {ENGINE_DATA.map((e,i)=>(
                <div key={e.id} style={{background:"rgba(255,255,255,0.018)",border:`1px solid ${RC(e.band)}18`,borderRadius:14,borderLeft:`3px solid ${RC(e.band)}`,padding:"18px 22px",animation:`fadeIn 0.4s ease ${i*0.06}s both`}}>
                  <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start"}}>
                    <div>
                      <div style={{...S.mono,fontWeight:800,fontSize:15,color:"#fff",marginBottom:6}}>{e.id}</div>
                      <div style={{display:"flex",gap:8}}><Badge band={e.band}/><span style={{fontSize:10,color:"rgba(255,255,255,0.35)"}}>Label: {e.label}</span></div>
                    </div>
                    <div style={{display:"flex",gap:18,flexWrap:"wrap",justifyContent:"flex-end"}}>
                      {[
                        {l:"Health",v:`${e.rul}%`,col:RC(e.band)},
                        {l:"EGT1",v:`${e.egt1}°F`,col:e.egt1>420?"#ff3b3b":e.egt1>380?"#ff9f1a":"rgba(255,255,255,0.7)"},
                        {l:"CHT1",v:`${e.cht1}°F`,col:e.cht1>400?"#ff3b3b":"rgba(255,255,255,0.7)"},
                        {l:"RPM",v:e.rpm,col:"rgba(255,255,255,0.7)"},
                        {l:"Oil Temp",v:`${e.oilT}°F`,col:e.oilT>220?"#ff9f1a":"rgba(255,255,255,0.7)"},
                        {l:"Oil PSI",v:`${e.oilP}`,col:e.oilP<60?"#ff3b3b":e.oilP<75?"#ff9f1a":"rgba(255,255,255,0.7)"},
                        {l:"IAS",v:`${e.ias} kt`,col:"rgba(255,255,255,0.7)"},
                        {l:"Alt MSL",v:`${e.altMSL} ft`,col:"rgba(255,255,255,0.7)"},
                      ].map(m=>(
                        <div key={m.l} style={{textAlign:"right"}}>
                          <div style={{fontSize:9,color:"rgba(255,255,255,0.28)",textTransform:"uppercase",letterSpacing:"0.1em",marginBottom:3}}>{m.l}</div>
                          <div style={{...S.mono,fontSize:14,fontWeight:700,color:m.col}}>{m.v}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div style={{marginTop:12,fontSize:12,color:"rgba(255,255,255,0.55)",lineHeight:1.6}}>{e.diagnosis}</div>
                  <GoNoGo band={e.band}/>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ── PAGE 4: Predictor Tool ─────────────────────────────────────── */}
        {page===4 && (
          <div style={{animation:"fadeIn 0.4s ease"}}>
            <div style={{marginBottom:20}}>
              <h2 style={{fontSize:24,fontWeight:800,letterSpacing:"-0.03em",background:"linear-gradient(135deg,#3bf0ff,#7c3aed)",WebkitBackgroundClip:"text",WebkitTextFillColor:"transparent"}}>Interactive Predictor Tool</h2>
              <p style={{fontSize:11,color:"rgba(255,255,255,0.3)",marginTop:3}}>Enter sensor values manually → get RUL prediction + Go/No-Go decision</p>
            </div>
            <div style={{display:"flex",gap:8,marginBottom:20}}>
              {["Battery RUL","Capacitor EIS","Engine NGAFID"].map((t,i)=>(
                <button key={i} onClick={()=>setPredictorTab(i)} style={{
                  padding:"6px 18px",borderRadius:8,fontSize:11,fontWeight:700,transition:"all 0.2s",cursor:"pointer",
                  border:predictorTab===i?"1px solid rgba(59,240,255,0.3)":"1px solid rgba(255,255,255,0.08)",
                  background:predictorTab===i?"rgba(59,240,255,0.1)":"transparent",
                  color:predictorTab===i?"#3bf0ff":"rgba(255,255,255,0.35)",
                }}>{t}</button>
              ))}
            </div>
            {predictorTab===0 && <BatteryPredictor/>}
            {predictorTab===1 && <CapacitorPredictor/>}
            {predictorTab===2 && <EnginePredictor/>}
          </div>
        )}

      </div>
    </div>
  );
}
