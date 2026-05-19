'use strict';

// Auto-detect API base: same origin in production, localhost in dev
const API = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://localhost:8000/api'
  : `${window.location.origin}/api`;

/* ── NAVIGATION ── */
const navItems = document.querySelectorAll('.nav-item');
const pages = document.querySelectorAll('.page');
const titles = { overview:'Overview Dashboard', attrition:'Attrition Analysis', hiring:'Hiring Funnel', engagement:'Employee Engagement', compensation:'Compensation & Promotions', diversity:'Diversity & Inclusion', ai:'AI-Powered Insights' };

function showPage(id) {
  pages.forEach(p => p.classList.remove('active'));
  navItems.forEach(n => n.classList.remove('active'));
  document.getElementById('page-' + id).classList.add('active');
  document.getElementById('nav-' + id).classList.add('active');
  document.getElementById('pageTitle').textContent = titles[id];
}
navItems.forEach(item => item.addEventListener('click', e => { e.preventDefault(); showPage(item.dataset.page); }));
document.getElementById('hamburger').addEventListener('click', () => document.getElementById('sidebar').classList.toggle('open'));

/* ── CHART DEFAULTS ── */
Chart.defaults.color = '#94a3b8';
Chart.defaults.borderColor = 'rgba(255,255,255,0.07)';
Chart.defaults.font.family = 'Inter';
const TEAL='#00d4ff', PURPLE='#a855f7', PINK='#ec4899', AMBER='#f59e0b', GREEN='#10b981', RED='#f43f5e';
const COLORS = [TEAL, PURPLE, PINK, AMBER, GREEN, RED];
const DEPTS = ['Engineering','Sales','HR','Finance','Marketing','Operations'];
const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

async function get(url) {
  try { const r = await fetch(url); return await r.json(); } catch(e) { console.error(e); return null; }
}

/* ── SPARKLINES ── */
function spark(id, data, color) {
  const ctx = document.getElementById(id); if(!ctx) return;
  new Chart(ctx, { type:'line', data:{ labels:data.map((_,i)=>i), datasets:[{data, borderColor:color, borderWidth:2, pointRadius:0, tension:.4}] }, options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}}, scales:{x:{display:false},y:{display:false}} } });
}

/* ── OVERVIEW ── */
async function loadOverview() {
  const kpis = await get(`${API}/overview/kpis`);
  const hva  = await get(`${API}/overview/hiring-vs-attrition`);
  const hcd  = await get(`${API}/overview/headcount-by-dept`);

  if (kpis) {
    document.getElementById('kpi-headcount').textContent = kpis.headcount.toLocaleString();
    document.getElementById('kpi-attrition').textContent = kpis.attrition_rate + '%';
    document.getElementById('kpi-esat').innerHTML = kpis.avg_satisfaction + '<span style="font-size:.5em">/10</span>';
    document.getElementById('kpi-burnout').textContent = kpis.burnout_risk + '%';
    document.getElementById('kpi-salary').textContent = '₹ ' + kpis.avg_salary + 'L';
  }

  spark('spark1',[4100,4300,4500,4600,4700, kpis?.headcount||4832], TEAL);
  spark('spark2',[17.2,16.5,16.1,15.5,15.1, kpis?.attrition_rate||14.7], RED);
  spark('spark3',[64,65,68,69,71,72.3], PURPLE);
  spark('spark4',[7.0,7.1,7.3,7.5,7.6, kpis?.avg_satisfaction||7.8], GREEN);
  spark('spark5',[19,20,21,22,22.5, kpis?.burnout_risk||23.1], AMBER);
  spark('spark6',[14.2,15.1,16,16.9,17.5, kpis?.avg_salary||18.4], PINK);

  // Headcount trend line chart
  const deptLabels = hcd ? Object.keys(hcd) : DEPTS;
  new Chart(document.getElementById('headcountTrend'), {
    type:'line',
    data:{ labels:MONTHS, datasets: deptLabels.map((d,i)=>({ label:d, data:MONTHS.map((_,m)=>Math.round((hcd?.[d]||700)*(0.85+m*0.012)+Math.random()*20)), borderColor:COLORS[i%6], backgroundColor:'transparent', borderWidth:2, pointRadius:3, tension:.4 })) },
    options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'bottom',labels:{boxWidth:10,font:{size:11}}}}, scales:{y:{beginAtZero:false}} }
  });

  new Chart(document.getElementById('attritionReasons'), {
    type:'doughnut',
    data:{ labels:['Better Offer','Work-Life','Manager','Growth','Relocation','Other'], datasets:[{data:[32,24,18,14,7,5], backgroundColor:COLORS, borderWidth:0, hoverOffset:8}] },
    options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'bottom',labels:{boxWidth:10,font:{size:10}}}} }
  });

  new Chart(document.getElementById('deptShare'), {
    type:'pie',
    data:{ labels: hcd ? Object.keys(hcd) : DEPTS, datasets:[{data: hcd ? Object.values(hcd) : [1420,890,310,460,620,1132], backgroundColor:COLORS, borderWidth:0, hoverOffset:8}] },
    options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'bottom',labels:{boxWidth:10,font:{size:10}}}} }
  });

  if (hva) {
    new Chart(document.getElementById('hiringVsAttrition'), {
      type:'bar',
      data:{ labels:hva.months, datasets:[
        {label:'New Hires', data:hva.hires, backgroundColor:'rgba(0,212,255,0.7)', borderRadius:4},
        {label:'Exits',     data:hva.exits, backgroundColor:'rgba(244,63,94,0.7)',  borderRadius:4}
      ]},
      options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'top',labels:{boxWidth:10,font:{size:11}}}}, scales:{y:{beginAtZero:true}} }
    });
  }
}

/* ── ATTRITION ── */
async function loadAttrition() {
  const byDept   = await get(`${API}/attrition/by-dept`);
  const byTenure = await get(`${API}/attrition/by-tenure`);
  const riskEmps = await get(`${API}/attrition/risk-employees`);

  if (byDept) {
    const labels = byDept.map(r=>r.Department);
    const rates  = byDept.map(r=>r.attrition_rate);
    new Chart(document.getElementById('attrByDept'), {
      type:'bar',
      data:{ labels, datasets:[{label:'Attrition %', data:rates, backgroundColor:COLORS, borderRadius:6}] },
      options:{ responsive:true, maintainAspectRatio:false, indexAxis:'y', plugins:{legend:{display:false}}, scales:{x:{max:30}} }
    });
  }

  new Chart(document.getElementById('exitReasons'), {
    type:'doughnut',
    data:{ labels:['Voluntary','Involuntary','Retirement','Relocation'], datasets:[{data:[62,18,12,8], backgroundColor:[RED,AMBER,PURPLE,TEAL], borderWidth:0, hoverOffset:8}] },
    options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'bottom',labels:{boxWidth:10}}} }
  });

  if (byTenure) {
    new Chart(document.getElementById('attrByTenure'), {
      type:'bar',
      data:{ labels:Object.keys(byTenure), datasets:[{label:'Attrition %', data:Object.values(byTenure), backgroundColor:'rgba(244,63,94,0.75)', borderRadius:6}] },
      options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}}, scales:{y:{max:50}} }
    });
  }

  new Chart(document.getElementById('attrTrend'), {
    type:'line',
    data:{ labels:MONTHS, datasets:[{label:'Attrition Rate %', data:[15.2,14.8,15.1,14.6,14.9,15.3,15.0,14.7,14.5,14.3,14.1,14.7], borderColor:RED, backgroundColor:'rgba(244,63,94,0.1)', fill:true, tension:.4, pointRadius:4}] },
    options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}}, scales:{y:{min:12,max:18}} }
  });

  // Risk table from ML model
  const tbody = document.getElementById('riskTableBody');
  const rows = riskEmps || [];
  rows.forEach((r,i) => {
    const level = r.RiskScore>=65?'high': r.RiskScore>=40?'medium':'low';
    tbody.innerHTML += `<tr>
      <td>${i+1}</td><td><b>EMP-${r.EmployeeID}</b></td><td>${r.Department}</td>
      <td>${r.Tenure} mo</td><td>${r.Satisfaction}/10</td>
      <td><div class="score-bar"><div class="score-fill" style="width:${Math.round(r.RiskScore*0.8)}px"></div><span>${r.RiskScore}%</span></div></td>
      <td><span class="risk-badge ${level}">${level.toUpperCase()}</span></td>
    </tr>`;
  });
}

/* ── HIRING ── */
async function loadHiring() {
  const funnel  = await get(`${API}/hiring/funnel`);
  const sources = await get(`${API}/hiring/sources`);
  const offer   = await get(`${API}/hiring/offer-acceptance`);

  if (funnel) {
    new Chart(document.getElementById('hiringFunnel'), {
      type:'bar',
      data:{ labels:funnel.map(s=>s.stage), datasets:[{label:'Candidates', data:funnel.map(s=>s.count), backgroundColor:COLORS.map(c=>c+'bb'), borderRadius:6}] },
      options:{ responsive:true, maintainAspectRatio:false, indexAxis:'y', plugins:{legend:{display:false}} }
    });
  }

  if (offer) {
    new Chart(document.getElementById('offerAccept'), {
      type:'bar',
      data:{ labels:Object.keys(offer), datasets:[{label:'Acceptance %', data:Object.values(offer), backgroundColor:COLORS, borderRadius:6}] },
      options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}}, scales:{y:{max:100}} }
    });
  }

  new Chart(document.getElementById('timeToHire'), {
    type:'bar',
    data:{ labels:DEPTS, datasets:[{label:'Days', data:[42,28,24,32,35,30], backgroundColor:'rgba(168,85,247,0.7)', borderRadius:6}] },
    options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}} }
  });

  if (sources) {
    new Chart(document.getElementById('hiringSource'), {
      type:'doughnut',
      data:{ labels:Object.keys(sources), datasets:[{data:Object.values(sources), backgroundColor:COLORS, borderWidth:0, hoverOffset:8}] },
      options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'bottom',labels:{boxWidth:10}}} }
    });
  }
}

/* ── ENGAGEMENT ── */
async function loadEngagement() {
  const sat      = await get(`${API}/engagement/satisfaction-by-dept`);
  const burn     = await get(`${API}/engagement/burnout-by-dept`);
  const sentDist = await get(`${API}/engagement/sentiment`);
  const feedback = await get(`${API}/engagement/feedback`);

  if (sat) {
    new Chart(document.getElementById('satByDept'), {
      type:'bar',
      data:{ labels:Object.keys(sat), datasets:[{label:'Satisfaction /10', data:Object.values(sat), backgroundColor:COLORS, borderRadius:6}] },
      options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}}, scales:{y:{min:0,max:10}} }
    });
  }

  if (sentDist) {
    new Chart(document.getElementById('sentimentDist'), {
      type:'doughnut',
      data:{ labels:Object.keys(sentDist), datasets:[{data:Object.values(sentDist), backgroundColor:[GREEN,AMBER,RED], borderWidth:0, hoverOffset:8}] },
      options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'bottom',labels:{boxWidth:10}}} }
    });
  }

  if (burn) {
    new Chart(document.getElementById('burnoutByDept'), {
      type:'bar',
      data:{ labels:Object.keys(burn), datasets:[{label:'Burnout Risk %', data:Object.values(burn), backgroundColor:'rgba(245,158,11,0.75)', borderRadius:6}] },
      options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}}, scales:{y:{max:60}} }
    });
  }

  new Chart(document.getElementById('engagementTrend'), {
    type:'line',
    data:{ labels:MONTHS, datasets:[
      {label:'Satisfaction', data:[7.2,7.3,7.4,7.5,7.5,7.6,7.7,7.7,7.8,7.8,7.9,7.8], borderColor:GREEN, fill:false, tension:.4, pointRadius:3},
      {label:'Burnout Risk%', data:[20,21,22,22,23,23,24,24,23,23,23,23], borderColor:AMBER, fill:false, tension:.4, pointRadius:3}
    ]},
    options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'top',labels:{boxWidth:10,font:{size:11}}}}, scales:{y:{beginAtZero:false}} }
  });

  const grid = document.getElementById('feedbackGrid');
  (feedback||[]).forEach(f => {
    grid.innerHTML += `<div class="feedback-card">
      <div class="feedback-meta"><span class="feedback-dept">${f.department}</span>
      <span class="sentiment-tag ${f.sentiment.toLowerCase()}">${f.sentiment}</span></div>
      <div class="feedback-text">"${f.text}"</div>
    </div>`;
  });
}

/* ── COMPENSATION ── */
async function loadCompensation() {
  const sal  = await get(`${API}/compensation/salary-by-dept`);
  const prom = await get(`${API}/compensation/promotions`);

  if (sal) {
    new Chart(document.getElementById('salaryDist'), {
      type:'bar',
      data:{ labels:sal.map(r=>r.Department), datasets:[
        {label:'Min',  data:sal.map(r=>r.min_salary), backgroundColor:'rgba(0,212,255,0.4)',  borderRadius:4},
        {label:'Avg',  data:sal.map(r=>r.avg_salary), backgroundColor:'rgba(168,85,247,0.7)', borderRadius:4},
        {label:'Max',  data:sal.map(r=>r.max_salary), backgroundColor:'rgba(236,72,153,0.5)', borderRadius:4}
      ]},
      options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'top',labels:{boxWidth:10,font:{size:11}}}}, scales:{y:{beginAtZero:true}} }
    });
  }

  new Chart(document.getElementById('payBand'), {
    type:'doughnut',
    data:{ labels:['<₹10L','₹10-20L','₹20-35L','₹35-60L','>₹60L'], datasets:[{data:[12,38,30,14,6], backgroundColor:COLORS, borderWidth:0, hoverOffset:8}] },
    options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'bottom',labels:{boxWidth:10}}} }
  });

  if (prom) {
    new Chart(document.getElementById('promotionByDept'), {
      type:'bar',
      data:{ labels:Object.keys(prom), datasets:[{label:'Promotions', data:Object.values(prom), backgroundColor:COLORS, borderRadius:6}] },
      options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}} }
    });
  }

  new Chart(document.getElementById('salaryTrend'), {
    type:'line',
    data:{ labels:['2019','2020','2021','2022','2023','2024'], datasets:[{label:'Avg CTC (₹L)', data:[11.2,11.8,13.0,14.5,16.8,18.4], borderColor:PINK, backgroundColor:'rgba(236,72,153,0.1)', fill:true, tension:.4, pointRadius:5}] },
    options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}}, scales:{y:{beginAtZero:false}} }
  });
}

/* ── DIVERSITY ── */
async function loadDiversity() {
  const gbd  = await get(`${API}/diversity/gender-by-dept`);
  const aged = await get(`${API}/diversity/age-distribution`);
  const et   = await get(`${API}/diversity/employment-type`);

  new Chart(document.getElementById('genderRatio'), {
    type:'doughnut',
    data:{ labels:['Male','Female'], datasets:[{data:[61.6,38.4], backgroundColor:[TEAL,PINK], borderWidth:0, hoverOffset:8}] },
    options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'bottom',labels:{boxWidth:10}}} }
  });

  if (gbd) {
    const depts = Object.keys(gbd);
    new Chart(document.getElementById('genderByDept'), {
      type:'bar',
      data:{ labels:depts, datasets:[
        {label:'Male%',   data:depts.map(d=>gbd[d].Male),   backgroundColor:'rgba(0,212,255,0.7)',  borderRadius:4},
        {label:'Female%', data:depts.map(d=>gbd[d].Female), backgroundColor:'rgba(236,72,153,0.7)', borderRadius:4}
      ]},
      options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'top',labels:{boxWidth:10,font:{size:11}}}}, scales:{y:{max:100}} }
    });
  }

  if (aged) {
    new Chart(document.getElementById('ageDist'), {
      type:'bar',
      data:{ labels:Object.keys(aged), datasets:[{label:'Employees', data:Object.values(aged), backgroundColor:'rgba(168,85,247,0.7)', borderRadius:6}] },
      options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}} }
    });
  }

  if (et) {
    new Chart(document.getElementById('empType'), {
      type:'doughnut',
      data:{ labels:Object.keys(et), datasets:[{data:Object.values(et), backgroundColor:COLORS, borderWidth:0, hoverOffset:8}] },
      options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'bottom',labels:{boxWidth:10}}} }
    });
  }
}

/* ── AI INSIGHTS ── */
async function loadAI() {
  const metrics = await get(`${API}/ai/model-metrics`);
  const roc     = await get(`${API}/ai/roc-curve`);
  const fi      = await get(`${API}/ai/feature-importance`);

  // Update metric pills with real values
  if (metrics?.random_forest) {
    const m = metrics.random_forest;
    document.querySelectorAll('.metric-pill').forEach((el,i) => {
      const vals = [m.precision+'%', m.recall+'%', m.f1+'%', m.auc];
      if(vals[i]) el.innerHTML = el.innerHTML.replace(/<b>.*?<\/b>/, `<b>${vals[i]}</b>`);
    });
  }

  if (roc) {
    new Chart(document.getElementById('rocCurve'), {
      type:'line',
      data:{ datasets:[
        {label:`RF (AUC=${roc.rf?.auc})`, data:roc.rf?.fpr.map((x,i)=>({x,y:roc.rf.tpr[i]})), borderColor:TEAL, tension:.4, pointRadius:0, borderWidth:2},
        {label:`LR (AUC=${roc.lr?.auc})`, data:roc.lr?.fpr.map((x,i)=>({x,y:roc.lr.tpr[i]})), borderColor:PURPLE, tension:.4, pointRadius:0, borderWidth:2},
        {label:'Baseline', data:[{x:0,y:0},{x:1,y:1}], borderColor:'rgba(255,255,255,0.2)', borderDash:[4,4], pointRadius:0, borderWidth:1}
      ]},
      options:{ responsive:true, maintainAspectRatio:false, parsing:false, plugins:{legend:{position:'top',labels:{boxWidth:8,font:{size:10}}}}, scales:{x:{type:'linear',title:{display:true,text:'FPR'},min:0,max:1},y:{title:{display:true,text:'TPR'},min:0,max:1}} }
    });
  }

  if (fi) {
    const sorted = Object.entries(fi).sort((a,b)=>b[1]-a[1]);
    new Chart(document.getElementById('featureImportance'), {
      type:'bar',
      data:{ labels:sorted.map(e=>e[0]), datasets:[{label:'Importance', data:sorted.map(e=>e[1]), backgroundColor:'rgba(168,85,247,0.75)', borderRadius:6}] },
      options:{ responsive:true, maintainAspectRatio:false, indexAxis:'y', plugins:{legend:{display:false}} }
    });
  }

  new Chart(document.getElementById('sentimentNLP'), {
    type:'bar',
    data:{ labels:MONTHS, datasets:[
      {label:'Positive', data:[64,65,66,67,68,69,68,67,68,69,69,68], backgroundColor:'rgba(16,185,129,0.7)', borderRadius:4},
      {label:'Negative', data:[15,14,13,12,11,10,11,12,11,10,10,11], backgroundColor:'rgba(244,63,94,0.7)',  borderRadius:4}
    ]},
    options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'top',labels:{boxWidth:10,font:{size:11}}}}, scales:{y:{max:80}} }
  });

  typeNarrative();

  const recs = [
    {icon:'🚨', title:'Sales Retention Programme', desc:'22%+ attrition in Sales is critical. Deploy targeted 1:1s, OTE review, and career pathing within 30 days.', priority:'high', accent:RED},
    {icon:'⏱️', title:'Operations Headcount Review', desc:'Burnout risk is highest in Operations. Recommend 40+ new FTE hires and load redistribution.', priority:'high', accent:AMBER},
    {icon:'🏆', title:'Fast-Track Promotions', desc:'Accelerating promotions for eligible employees could reduce attrition risk by ~18%.', priority:'med', accent:PURPLE},
    {icon:'💬', title:'Manager Effectiveness Training', desc:'18% of exits cite manager issues. Launch bi-monthly 360° manager reviews.', priority:'med', accent:TEAL},
    {icon:'🌍', title:'D&I Leadership Pipeline', desc:'Only 29% women in leadership. Implement mentorship tracks and bias-aware panels.', priority:'low', accent:PINK},
    {icon:'💡', title:'Referral Bonus Expansion', desc:'Referrals show highest acceptance rates. Double referral bonus to improve pipeline.', priority:'low', accent:GREEN},
  ];
  const rg = document.getElementById('recommendationsGrid');
  recs.forEach(r => {
    rg.innerHTML += `<div class="rec-card" style="--accent:${r.accent}">
      <div class="rec-icon">${r.icon}</div><div class="rec-title">${r.title}</div>
      <div class="rec-desc">${r.desc}</div>
      <span class="rec-priority ${r.priority}">${r.priority.toUpperCase()} PRIORITY</span>
    </div>`;
  });
}

/* ── NARRATIVE TYPING ── */
function typeNarrative() {
  const el = document.getElementById('narrativeBody');
  const text = `📋 Executive Summary — FY 2024\n\nWorkforce health shows steady improvement with headcount growing 3.2% YoY. Attrition has declined driven by enhanced retention initiatives in Engineering and Finance.\n\nThe AI-powered Random Forest model (AUC: 0.94) has identified high-risk active employees, primarily in Sales and Marketing. Immediate intervention through manager 1:1 check-ins and compensation review is recommended.\n\nHiring efficiency improved with offer acceptance rising to 72.3%. LinkedIn and referrals remain top sourcing channels. Average time-to-hire is 34 days — 8% faster than industry benchmark.\n\nEmployee sentiment is predominantly positive (68%) with key concerns around work-life balance in Operations and unrealistic targets in Sales. NLP analysis identifies burnout risk requiring urgent attention.\n\n🔑 Priority Actions: (1) Launch Sales retention programme, (2) Review Operations headcount, (3) Expand referral bonuses.`;
  el.textContent = '';
  let i = 0;
  const t = setInterval(() => { el.textContent += text[i++]; if(i>=text.length) clearInterval(t); }, 16);
}

document.getElementById('regenBtn').addEventListener('click', typeNarrative);

/* ── INIT ALL PAGES ── */
loadOverview();
loadAttrition();
loadHiring();
loadEngagement();
loadCompensation();
loadDiversity();
loadAI();
