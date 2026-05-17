// =====================================================================
// Смета.AI · Прототип расчётного движка
// MIT License. См. README.md.
//
// Это упрощённая модель для демо-целей. В реальном продукте каждая
// формула проверяется сметчиком и калибруется по базе ФЕР/ТЕР с
// учётом региональных индексов и текущих рыночных цен материалов.
// =====================================================================

const state = {
  region: 1.18,
  floors: 1,
  area: 120,
  ceiling: 3,
  foundation: { type: 'strip', rate: 4500 },
  walls: { type: 'aerated', rate: 13500 },
  thickness: 300,
  roof: { type: 'metal', rate: 2200 },
  windows: 20,
  doors: 6,
  facade: { type: 'plaster', rate: 850 },
  heating: { type: 'gas', rate: 3500 },
  finish: { type: 'none', rate: 0 },
};

function fmt(n) {
  return Math.round(n).toLocaleString('ru-RU') + ' ₽';
}

function fmtRange(n) {
  const low = (n * 0.9) / 1_000_000;
  const high = (n * 1.1) / 1_000_000;
  return `диапазон ${low.toFixed(1).replace('.', ',')}–${high.toFixed(1).replace('.', ',')} млн ₽ · точность ±10%`;
}

function calc() {
  const r = state.region;
  const a = state.area;
  const floors = state.floors;
  const footprint = a / Math.max(1, floors);
  const perimeter = 4 * Math.sqrt(footprint);

  const earth = footprint * 1.1 * 600 * r;

  const foundationDepth = state.foundation.type === 'pile' ? 0 : (state.foundation.type === 'slab' ? 0.4 : 1.8);
  const foundationVolume = state.foundation.type === 'pile'
    ? perimeter * 4
    : (state.foundation.type === 'slab' ? footprint : perimeter * 0.5 * foundationDepth);
  const foundation = foundationVolume * state.foundation.rate * r;

  const wallArea = perimeter * state.ceiling * floors;
  const wallVolume = wallArea * (state.thickness / 1000);
  const walls = wallVolume * state.walls.rate * r;

  const floorsArea = footprint * Math.max(1, floors) * 2700 * r;

  const roofArea = footprint * 1.3;
  const roof = roofArea * state.roof.rate * r;

  const windowsCost = state.windows * 7200 * r;
  const doorsCost = state.doors * 18000 * r;
  const facadeCost = wallArea * state.facade.rate * r;

  const heatingCost = a * state.heating.rate * r;
  const finishCost = a * state.finish.rate * r;

  const electrical = a * 1800 * r;
  const plumbing = a * 1400 * r;

  const subtotal = earth + foundation + walls + floorsArea + roof + windowsCost + doorsCost
    + facadeCost + heatingCost + finishCost + electrical + plumbing;

  const overhead = subtotal * 0.15;
  const profit = subtotal * 0.08;
  const total = subtotal + overhead + profit;

  return {
    earth,
    foundation,
    walls,
    floorsArea,
    roof,
    openings: windowsCost + doorsCost,
    finish: facadeCost + heatingCost + finishCost + electrical + plumbing,
    overhead: overhead + profit,
    total
  };
}

function updateUI() {
  const r = calc();
  document.getElementById('r-earth').textContent = fmt(r.earth);
  document.getElementById('r-foundation').textContent = fmt(r.foundation);
  document.getElementById('r-walls').textContent = fmt(r.walls);
  document.getElementById('r-floors').textContent = fmt(r.floorsArea);
  document.getElementById('r-roof').textContent = fmt(r.roof);
  document.getElementById('r-openings').textContent = fmt(r.openings);
  document.getElementById('r-finish').textContent = fmt(r.finish);
  document.getElementById('r-overhead').textContent = fmt(r.overhead);
  document.getElementById('r-total').textContent = fmt(r.total);
  document.getElementById('total').textContent = fmt(r.total);
  document.getElementById('range').textContent = fmtRange(r.total);
}

window.recalc = updateUI;

function bindPillGroups() {
  document.querySelectorAll('.pill-row[data-group]').forEach(row => {
    const group = row.dataset.group;
    row.addEventListener('click', e => {
      const btn = e.target.closest('.pill-btn');
      if (!btn) return;
      row.querySelectorAll('.pill-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const val = btn.dataset.val;
      const rate = btn.dataset.rate ? parseFloat(btn.dataset.rate) : null;
      if (group === 'floors') state.floors = parseFloat(val);
      else if (group === 'thickness') state.thickness = parseFloat(val);
      else if (state[group] !== undefined) {
        state[group] = { type: val, rate: rate !== null ? rate : state[group].rate };
      }
      updateUI();
    });
  });

  const region = document.getElementById('region');
  if (region) {
    region.addEventListener('change', e => {
      state.region = parseFloat(e.target.selectedOptions[0].dataset.coef);
      updateUI();
    });
  }

  const inputs = {
    area: 'area',
    ceiling: 'ceiling',
    windows: 'windows',
    doors: 'doors'
  };
  Object.entries(inputs).forEach(([id, key]) => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('input', e => {
      const v = parseFloat(e.target.value);
      if (!isNaN(v) && v >= 0) {
        state[key] = v;
        updateUI();
      }
    });
  });
}

window.switchTab = function(mode, btn) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  btn.classList.add('active');
  const ext = document.getElementById('extended-fields');
  if (mode === 'extended') ext.classList.add('shown');
  else ext.classList.remove('shown');
};

window.downloadPdf = function() {
  document.getElementById('modal-title').textContent = 'Скачать смету в PDF';
  document.getElementById('modal-text').textContent = 'В реальном продукте здесь — оплата 1 490 ₽ через ЮKassa и мгновенное скачивание готового документа. В демо можно скачать пример PDF, чтобы оценить формат.';
  document.getElementById('modal').classList.add('shown');
};

window.showCommercial = function() {
  document.getElementById('modal-title').textContent = 'Готовое КП для клиента';
  document.getElementById('modal-text').textContent = 'В реальном продукте генерируется фирменное PDF с разбивкой по этапам, графиком работ, условиями оплаты и гарантиями — на основе шаблона подрядчика. Доступно в тарифе «Активный» и выше.';
  document.getElementById('modal').classList.add('shown');
};

window.closeModal = function() {
  document.getElementById('modal').classList.remove('shown');
};

document.addEventListener('DOMContentLoaded', () => {
  bindPillGroups();
  updateUI();
});
