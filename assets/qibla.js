(function(root){
    'use strict';
    const E=root.DestaEngine,D=root.DestaData;
    root.initQibla=function(){
        const get=id=>document.getElementById(id),state={mode:'manual',zone:null,location:null,schedule:null,bearing:0,aligned:false};
        const rose=get('compass-rose'),status=get('compass-status');
        function reset(){rose.style.transform='rotate(0deg)';get('q-marker').style.transform='translate(-50%,-50%)';state.aligned=false;rose.parentElement.setAttribute('aria-label',`Arah statis ${state.bearing.toFixed(1)} derajat dari utara sejati`);}
        const sensor=new root.DestaCompass({window,navigator,setTimeout,clearTimeout},{reset,status:message=>{status.textContent=message;get('sensor-toggle').textContent=(sensor.active||sensor.pending)?'Jeda kompas':'Aktifkan kompas';},location:position=>{
            state.zone=null;get('q-city').value='';get('q-lat').value=position.coords.latitude.toFixed(6);get('q-lon').value=position.coords.longitude.toFixed(6);get('q-tz').value=-new Date().getTimezoneOffset()/60;
            get('gps-status').textContent=`Koordinat diperbarui${Number.isFinite(position.coords.accuracy)?`; ketelitian lokasi ±${Math.round(position.coords.accuracy)} m`:''}. UTC mengikuti perangkat; periksa jika berbeda.`;compute('Lokasi GPS');
        },heading:heading=>{
            if(!state.location)return;rose.style.transform=`rotate(${-heading}deg)`;get('q-marker').style.transform=`translate(-50%,-50%) rotate(${heading}deg)`;
            let diff=((state.bearing-heading+540)%360)-180;const aligned=Math.abs(diff)<=3;
            status.textContent=aligned?'Perkiraan arah sejajar. Cocokkan dengan referensi utara sejati.':`Perkiraan: putar ${diff>0?'kanan':'kiri'} ${Math.round(Math.abs(diff))}°. Referensi sensor belum dikoreksi deklinasi.`;
            rose.parentElement.setAttribute('aria-label',status.textContent);
            if(aligned&&!state.aligned&&navigator.vibrate&&!matchMedia('(prefers-reduced-motion: reduce)').matches)navigator.vibrate(50);
            state.aligned=aligned;get('sensor-toggle').textContent='Jeda kompas';
        }});
        function error(message){get('q-error').textContent=message;get('q-error').hidden=!message;}
        function renderSchedule(){const s=state.schedule;get('prayer-date').textContent=`${s.date} · ${state.location.name} · UTC${s.offset>=0?'+':''}${s.offset}`;for(const [key]of E.prayers)get('prayer-'+key).textContent=s.times[key];}
        function compute(name){
            try{
                for(const id of ['q-lat','q-lon','q-tz'])if(get(id).value.trim()==='')throw Error('Lengkapi lintang, bujur, dan UTC.');
                const lat=Number(get('q-lat').value),lon=Number(get('q-lon').value),offset=Number(get('q-tz').value);E.validateLocation(lat,lon,offset);
                const bearing=E.qibla(lat,lon),location={lat,lon,offset,zone:state.zone,name:name||(state.zone?D.cities[Number(get('q-city').value)]?.name:'Koordinat manual')||'Koordinat manual'};
                const schedule=E.schedule(lat,lon,location.zone,offset);
                state.location=location;state.schedule=schedule;state.bearing=bearing.bearing;get('q-needle').hidden=false;get('q-marker').hidden=false;
                get('q-result').textContent=`${location.name}\nArah ${bearing.bearing.toFixed(2)}° dari utara sejati\nJarak ke Ka’bah ${bearing.distance.toLocaleString('id-ID',{maximumFractionDigits:1})} km`;
                get('q-zone').textContent=state.zone?`Zona ${state.zone}; UTC dan DST menyesuaikan tanggal.`:'UTC manual; sesuaikan dengan zona lokasi.';
                if(state.zone)get('q-tz').value=schedule.offset;
                get('q-needle').style.transform=`rotate(${bearing.bearing}deg)`;const angle=(bearing.bearing-90)*Math.PI/180;
                get('q-marker').style.left=`${50+37*Math.cos(angle)}%`;get('q-marker').style.top=`${50+37*Math.sin(angle)}%`;renderSchedule();tick();error('');
                if(!sensor.valid)reset();
            }catch(failure){state.location=null;state.schedule=null;state.bearing=0;get('q-needle').hidden=true;get('q-marker').hidden=true;sensor.stop('Lengkapi lokasi yang valid sebelum memakai kompas.');get('q-result').textContent='Hasil belum tersedia.';get('prayer-countdown').textContent='Jadwal belum tersedia.';for(const [key]of E.prayers)get('prayer-'+key).textContent='—';error(failure.message);}
        }
        function tick(){if(!state.location||!state.schedule)return;const now=new Date(),l=state.location,p=E.dateParts(now,l.zone,l.offset),key=`${p.year}-${p.month}-${p.day}`;
            if(key!==state.schedule.date){state.schedule=E.schedule(l.lat,l.lon,l.zone,l.offset,now);renderSchedule();}
            const stamp=now.getTime(),next=state.schedule.events.find(event=>event.timestamp>stamp),previous=state.schedule.events.filter(event=>event.timestamp<=stamp).at(-1);
            for(const [id]of E.prayers){get('card-'+id).classList.toggle('active',previous?.key===id);get('card-'+id).classList.toggle('next',next?.key===id);}
            if(!next){get('prayer-countdown').textContent='Waktu berikutnya tidak tersedia untuk lokasi ini.';return;}
            const seconds=Math.max(0,Math.ceil((next.timestamp-stamp)/1000)),clock=[Math.floor(seconds/3600),Math.floor(seconds%3600/60),seconds%60].map(n=>String(n).padStart(2,'0')).join(':');get('prayer-countdown').textContent=`Menuju ${next.label}: ${clock}`;
        }
        get('q-city').add(new Option('Koordinat manual',''));D.cities.forEach((city,i)=>get('q-city').add(new Option(city.name,i)));
        get('q-city').onchange=()=>{sensor.stop();const val=get('q-city').value;if(val===''){state.zone=null;dirty();return;}const city=D.cities[Number(val)];state.zone=city.zone;get('q-lat').value=city.lat;get('q-lon').value=city.lon;get('q-tz').value=E.zoneOffset(new Date(),city.zone);compute(city.name);};
        function dirty(){state.zone=null;state.location=null;state.schedule=null;state.bearing=0;get('q-needle').hidden=true;get('q-marker').hidden=true;get('q-city').value='';sensor.stop('Lokasi berubah. Hitung ulang untuk memperbarui arah.');get('q-result').textContent='Lokasi berubah — tekan Hitung.';get('q-zone').textContent='UTC manual.';get('prayer-countdown').textContent='Jadwal menunggu perhitungan ulang.';for(const [key]of E.prayers)get('prayer-'+key).textContent='—';}
        for(const id of ['q-lat','q-lon','q-tz'])get(id).addEventListener('input',dirty);
        get('qibla-form').onsubmit=event=>{event.preventDefault();sensor.stop();compute();};
        function mode(value){state.mode=value;sensor.stop();get('q-mode-manual').setAttribute('aria-pressed',String(value==='manual'));get('q-mode-gps').setAttribute('aria-pressed',String(value==='gps'));get('gps-panel').hidden=value!=='gps';get('sensor-controls').hidden=value!=='gps';}
        get('q-mode-manual').onclick=()=>mode('manual');get('q-mode-gps').onclick=()=>mode('gps');get('sensor-toggle').onclick=()=>(sensor.active||sensor.pending)?sensor.stop():sensor.start();get('sensor-calibrate').onclick=()=>{sensor.stop('Jauhkan logam, gerakkan perangkat membentuk angka 8, lalu tekan Aktifkan kompas.');};
        for(const [key,label]of E.prayers){const card=document.createElement('div');card.id='card-'+key;card.className='prayer-card';const title=document.createElement('span');title.textContent=label;const value=document.createElement('strong');value.id='prayer-'+key;value.textContent='—';card.append(title,value);get('prayer-grid').append(card);}
        get('q-city').value='0';get('q-city').onchange();setInterval(()=>{if(!document.hidden&&!get('tab-qibla').hidden)tick();},1000);
        return {pause:()=>sensor.stop(),refresh:()=>{if(state.location)compute(state.location.name);},state,sensor};
    };
})(globalThis);
