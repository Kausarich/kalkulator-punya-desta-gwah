(function(){
    'use strict';
    const E=DestaEngine,get=id=>document.getElementById(id);
    initCalculator();initCalendar();const qibla=initQibla();
    function tab(id,focus=false){
        qibla.pause();for(const name of ['calc','julian','qibla','calendar']){const selected=name===id;get('tab-'+name).hidden=!selected;get('tab-button-'+name).setAttribute('aria-selected',String(selected));get('tab-button-'+name).tabIndex=selected?0:-1;}
        if(id==='qibla')qibla.refresh();if(focus)get('tab-button-'+id).focus();
    }
    const tabs=['calc','julian','qibla','calendar'];tabs.forEach((id,i)=>{get('tab-button-'+id).onclick=()=>tab(id);get('tab-button-'+id).onkeydown=event=>{let next;if(event.key==='ArrowRight')next=(i+1)%4;if(event.key==='ArrowLeft')next=(i+3)%4;if(event.key==='Home')next=0;if(event.key==='End')next=3;if(next!==undefined){event.preventDefault();tab(tabs[next],true);}};});
    document.addEventListener('visibilitychange',()=>{if(document.hidden)qibla.pause();else if(!get('tab-qibla').hidden)qibla.refresh();});window.addEventListener('pagehide',()=>qibla.pause());
    function setNow(){const now=new Date();get('jd-year').value=now.getFullYear();get('jd-month').value=now.getMonth()+1;get('jd-day').value=now.getDate();get('jd-time').value=[now.getHours(),now.getMinutes(),now.getSeconds()].map(x=>String(x).padStart(2,'0')).join(':');get('jd-utc').value=-now.getTimezoneOffset()/60;}
    function calculateJD(){try{for(const id of ['jd-year','jd-month','jd-day','jd-time','jd-utc'])if(!get(id).value)throw Error('Lengkapi semua kolom.');const [h,m,s=0]=get('jd-time').value.split(':').map(Number);const result=E.julianDay(Number(get('jd-year').value),Number(get('jd-month').value),Number(get('jd-day').value),h,m,s,Number(get('jd-utc').value));get('jd-result').textContent=`JD: ${result.toFixed(6)}\nMJD: ${(result-2400000.5).toFixed(6)}`;get('jd-error').hidden=true;}catch(error){get('jd-error').textContent=error.message;get('jd-error').hidden=false;get('jd-result').textContent='Hasil belum tersedia.';}}
    get('jd-form').onsubmit=e=>{e.preventDefault();calculateJD();};get('jd-form').addEventListener('input',()=>get('jd-result').textContent='Masukan berubah — tekan Hitung JD.');get('jd-now').onclick=()=>{setNow();calculateJD();};setNow();calculateJD();
    const requested=new URLSearchParams(location.search).get('tab')||location.hash.slice(1);if(tabs.includes(requested))tab(requested);
})();
