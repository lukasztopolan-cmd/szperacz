const defaultHunters = [
  {id:1,name:"BMW E90/E91 do 15k Wrocław",portal:"both",keyword:"bmw e90",priceTo:15000,location:"Wrocław",radius:100,active:true,hits:12},
  {id:2,name:"iPhone 13/14 do 1800zł",portal:"olx",keyword:"iphone 13",priceTo:1800,location:"Wrocław",radius:50,active:true,hits:8},
  {id:3,name:"Rower elektryczny",portal:"allegro",keyword:"rower elektryczny",priceTo:4000,location:"Dolnośląskie",radius:0,active:false,hits:3},
];

const mockOffers = [
  {title:"BMW E90 320d 2008r 230kkm - Okazja!",price:"13 900 zł",loc:"Wrocław, Fabryczna",time:"2 min temu",portal:"OLX",img:"https://images.unsplash.com/photo-1555215695-3004980ad54e?w=200",new:true},
  {title:"iPhone 13 128GB stan idealny pudełko",price:"1 650 zł",loc:"Wrocław, Krzyki",time:"5 min temu",portal:"Allegro Lokalnie",img:"https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=200",new:true},
  {title:"BMW E91 318d Touring 2009 automat",price:"14 500 zł",loc:"Oława (29km)",time:"12 min temu",portal:"OLX",img:"https://images.unsplash.com/photo-1555215695-3004980ad54e?w=200",new:false},
  {title:"Rower elektryczny Ecobike 2023 600km",price:"3 200 zł",loc:"Legnica",time:"31 min temu",portal:"OLX",img:"https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=200",new:false},
];

function renderHunters(){
  const list = document.getElementById('huntersList');
  const hunters = JSON.parse(localStorage.getItem('hunters')||'null') || defaultHunters;
  list.innerHTML = hunters.map(h=>`
    <div class="hunter-item">
      <div class="hunter-info">
        <h4>${h.name} ${h.active?'🟢':'⚪️'}</h4>
        <p>${h.keyword} • do ${h.priceTo}zł • ${h.location} +${h.radius}km • ${h.hits} upolowanych</p>
      </div>
      <div class="hunter-actions">
        <button class="icon-btn" onclick="toggleHunter(${h.id})">${h.active?'⏸️':'▶️'}</button>
        <button class="icon-btn" onclick="deleteHunter(${h.id})">🗑️</button>
      </div>
    </div>
  `).join('');
}

function renderOffers(){
  const list = document.getElementById('offersList');
  list.innerHTML = mockOffers.map(o=>`
    <div class="offer-card ${o.new?'new':''}">
      <img class="offer-img" src="${o.img}" loading="lazy">
      <div class="offer-content">
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span class="badge ${o.portal.includes('OLX')?'badge-olx':'badge-allegro'}">${o.portal}</span>
          <span class="offer-time">${o.time}</span>
        </div>
        <div class="offer-title">${o.title}</div>
        <div class="offer-price">${o.price}</div>
        <div class="offer-meta"><span>📍 ${o.loc}</span></div>
      </div>
    </div>
  `).join('');
}

function addHunter(){
  const name = document.getElementById('name').value || document.getElementById('keyword').value;
  const portal = document.getElementById('portal').value;
  const keyword = document.getElementById('keyword').value;
  const priceTo = document.getElementById('priceTo').value;
  const location = document.getElementById('location').value;
  const radius = document.getElementById('radius').value;
  if(!keyword){alert('Wpisz słowo kluczowe np. bmw e90');return}
  const hunters = JSON.parse(localStorage.getItem('hunters')||'null') || defaultHunters;
  hunters.unshift({id:Date.now(),name,portal,keyword,priceTo,location,radius,active:true,hits:0});
  localStorage.setItem('hunters',JSON.stringify(hunters));
  renderHunters();
  document.getElementById('name').value='';document.getElementById('keyword').value='';
  alert('✅ Łowca dodany! Backend zacznie sprawdzać co 2 min i wyśle Ci powiadomienie na Telegrama.');
}

function toggleHunter(id){
  let hunters = JSON.parse(localStorage.getItem('hunters')||'null') || defaultHunters;
  hunters = hunters.map(h=>h.id===id?{...h,active:!h.active}:h);
  localStorage.setItem('hunters',JSON.stringify(hunters));
  renderHunters();
}
function deleteHunter(id){
  if(!confirm('Usunąć łowcę?'))return;
  let hunters = JSON.parse(localStorage.getItem('hunters')||'null') || defaultHunters;
  hunters = hunters.filter(h=>h.id!==id);
  localStorage.setItem('hunters',JSON.stringify(hunters));
  renderHunters();
}

renderHunters();
renderOffers();
