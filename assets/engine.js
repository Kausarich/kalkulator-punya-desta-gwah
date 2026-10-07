/* Pure engines. No DOM, sensors, network, or dynamic code evaluation. */
(function (root) {
    'use strict';
    const D = root.DestaData || (typeof require === 'function' ? require('../data.json') : null);
    const EPOCH = 1948439.5;
    const prayers = [['imsak','Imsak'],['fajr','Subuh'],['sunrise','Terbit'],['dhuhr','Dzuhur'],['asr','Ashar'],['maghrib','Maghrib'],['isha','Isya']];
    const rad = x => x * Math.PI / 180, deg = x => x * 180 / Math.PI;
    const mod = (x, n) => ((x % n) + n) % n;
    function finite(x) { if (!Number.isFinite(x)) throw Error('Hasil di luar rentang angka.'); return x; }
    function power(x,y) {
        if (Math.abs(y)>10000) throw Error('Eksponen terlalu besar (maksimum 10000).');
        return finite(Math.pow(x,y));
    }
    function evaluate(expression, mode='DEG', answer=0) {
        if (!expression.trim() || expression.length>256) throw Error('Masukkan ekspresi sepanjang 1–256 karakter.');
        const factor={DEG:Math.PI/180,RAD:1,GRAD:Math.PI/200}[mode];
        if (!factor) throw Error('Mode sudut tidak valid.');
        const functions={sin:x=>Math.sin(x*factor),cos:x=>Math.cos(x*factor),tan:x=>{
            if(Math.abs(Math.cos(x*factor))<1e-12) throw Error('Tangen tidak terdefinisi pada sudut ini.');
            return Math.tan(x*factor);
        },asin:x=>Math.asin(x)/factor,acos:x=>Math.acos(x)/factor,atan:x=>Math.atan(x)/factor,
        sqrt:Math.sqrt,log:Math.log10,ln:Math.log,exp:Math.exp,powten:x=>power(10,x),abs:Math.abs,inv:x=>finite(1/x),square:x=>power(x,2),neg:x=>-x,
        factorial:x=>{if(!Number.isInteger(x)||x<0||x>170)throw Error('Faktorial membutuhkan bilangan bulat 0–170.');let v=1;for(let i=2;i<=x;i++)v*=i;return v;}};
        const tokens=[], source=expression.trim().replaceAll('pow10','powten');
        const pattern=/\s*(?:(\d+(?:\.\d*)?(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?)|([A-Za-z]+)|(\*\*|[()+*/%\-]))/y;
        let pos=0;
        while(pos<source.length){pattern.lastIndex=pos;const m=pattern.exec(source);if(!m)throw Error('Karakter atau angka tidak valid.');tokens.push(m[1]||m[2]||m[3]);pos=pattern.lastIndex;}
        tokens.push('');let cursor=0;
        function parse(minimum=0,depth=0){
            if(depth>64)throw Error('Ekspresi terlalu bertingkat.');
            const token=tokens[cursor++];let left;
            if(token==='+'||token==='-')left=parse(25,depth+1)*(token==='-'?-1:1);
            else if(token==='('){left=parse(0,depth+1);if(tokens[cursor++]!==')')throw Error('Kurung belum lengkap.');}
            else if(Object.hasOwn(functions,token)){
                if(tokens[cursor++]!=='(')throw Error('Fungsi membutuhkan kurung.');
                const arg=parse(0,depth+1);if(tokens[cursor++]!==')')throw Error('Kurung belum lengkap.');left=functions[token](arg);
            }else if(['pi','e','Ans'].includes(token))left={pi:Math.PI,e:Math.E,Ans:answer}[token];
            else if(token && /^[\d.]/.test(token)){
                left=finite(Number(token));
                if(!/e/i.test(token)&&Math.abs(left)>Number.MAX_SAFE_INTEGER)throw Error('Angka melampaui presisi 15 digit; gunakan notasi e atau 10ˣ.');
            }else throw Error('Ekspresi belum lengkap.');
            while(['+','-','*','/','%','**'].includes(tokens[cursor])){
                const op=tokens[cursor],p={'+':10,'-':10,'*':20,'/':20,'%':20,'**':30}[op];if(p<minimum)break;
                cursor++;const right=parse(op==='**'?p:p+1,depth+1);
                if(op==='+')left+=right;else if(op==='-')left-=right;else if(op==='*')left*=right;
                else if(op==='/')left/=right;else if(op==='%')left%=right;else left=power(left,right);
                finite(left);
            }
            return finite(left);
        }
        const value=parse();if(tokens[cursor])throw Error('Operator atau kurung tidak valid.');return value;
    }
    function applyFunction(expression,name){
        if(!expression||/[+*/%(-]$/.test(expression))return expression+name+'(';
        let start;
        if(expression.endsWith(')')){
            let depth=1;start=expression.length-2;
            while(start>=0&&depth){depth+=(expression[start]===')'?1:0)-(expression[start]==='('?1:0);start--;}
            start++;while(start>0&&/[A-Za-z]/.test(expression[start-1]))start--;
        }else{
            const match=expression.match(/(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$|[A-Za-z]+$/);
            if(!match)throw Error('Operand tidak valid.');start=match.index;
        }
        if(start>0&&/[+-]/.test(expression[start-1])&&(start===1||/[(+*/%-]/.test(expression[start-2])))start--;
        return expression.slice(0,start)+name+'('+expression.slice(start)+')';
    }
    function displayExpression(x){return x.replaceAll('pow10','10^').replaceAll('powten','10^').replaceAll('square','sqr').replaceAll('**','^').replaceAll('pi','π').replaceAll('*','×').replaceAll('/','÷');}
    function formatResult(x){finite(x);if(x===0)return '0';if(Math.abs(x)>=1e10||Math.abs(x)<1e-7){const [m,e]=x.toExponential(7).split('e');return `${Number(m)} × 10^${Number(e)}`;}return x.toFixed(8).replace(/\.?0+$/,'');}
    function utcDate(y,m,d){const x=new Date(0);x.setUTCFullYear(y,m-1,d);x.setUTCHours(0,0,0,0);return x;}
    function validateDate(y,m,d){
        if(![y,m,d].every(Number.isInteger)||y<1||y>9999||m<1||m>12||d<1)throw Error('Tanggal Masehi tidak valid (tahun 1–9999).');
        const x=utcDate(y,m,d);if(x.getUTCFullYear()!==y||x.getUTCMonth()+1!==m||x.getUTCDate()!==d)throw Error('Tanggal Masehi tidak valid.');return x;
    }
    function gregorianToJD(y,m,d){return validateDate(y,m,d).getTime()/86400000+2440587.5;}
    function jdToGregorian(jd){const x=new Date((Math.floor(finite(jd)+.5)-.5-2440587.5)*86400000);const r={year:x.getUTCFullYear(),month:x.getUTCMonth()+1,day:x.getUTCDate()};validateDate(r.year,r.month,r.day);return r;}
    function validateOffset(x){if(!Number.isFinite(x)||x< -12||x>14)throw Error('UTC harus antara −12 dan +14 jam.');return x;}
    function julianDay(y,m,d,h=12,n=0,s=0,tz=0){
        if(![h,n,s].every(Number.isInteger)||h<0||h>23||n<0||n>59||s<0||s>59)throw Error('Jam harus 00–23; menit dan detik 00–59.');
        return gregorianToJD(y,m,d)+(h+n/60+s/3600-validateOffset(tz))/24;
    }
    const isHijriLeap=y=>mod(11*y+14,30)<11;
    function hijriMonthDays(y,m){if(!Number.isInteger(y)||y<1||y>9665||!Number.isInteger(m)||m<1||m>12)throw Error('Tahun Hijriah 1–9665 dan bulan 1–12.');return m%2||(m===12&&isHijriLeap(y))?30:29;}
    function hijriToJD(y,m,d){if(!Number.isInteger(d)||d<1||d>hijriMonthDays(y,m))throw Error('Tanggal tidak ada pada bulan Hijriah yang dipilih.');return EPOCH+354*(y-1)+Math.floor((3+11*y)/30)+Math.ceil(29.5*(m-1))+d-1;}
    function jdToHijri(jd){const midnight=Math.floor(finite(jd)+.5)-.5;const year=Math.floor((30*(midnight-EPOCH)+10646)/10631);hijriMonthDays(year,1);let month=1;while(month<12&&midnight>=hijriToJD(year,month+1,1))month++;return {year,month,day:midnight-hijriToJD(year,month,1)+1};}
    const gregorianToHijri=(y,m,d)=>jdToHijri(gregorianToJD(y,m,d));
    const holiday=(m,d)=>D.holidays[`${m}-${d}`]||([13,14,15].includes(d)&&m!==9?'Puasa Ayyamul Bidh':'');
    function validateLocation(lat,lon,tz=0){if(!Number.isFinite(lat)||lat< -90||lat>90)throw Error('Lintang harus antara −90 dan 90°.');if(!Number.isFinite(lon)||lon< -180||lon>180)throw Error('Bujur harus antara −180 dan 180°.');validateOffset(tz);}
    function qibla(lat,lon){
        validateLocation(lat,lon);const phi=rad(lat),target=rad(D.MECCA_LAT),delta=rad(D.MECCA_LON-lon);
        const y=Math.sin(delta),x=Math.cos(phi)*Math.tan(target)-Math.sin(phi)*Math.cos(delta);
        if(Math.hypot(x,y)<1e-12)throw Error('Arah kiblat tidak unik pada koordinat ini.');
        const bearing=mod(deg(Math.atan2(y,x)),360),hav=Math.min(1,Math.max(0,Math.sin((target-phi)/2)**2+Math.cos(phi)*Math.cos(target)*Math.sin(delta/2)**2));
        return {bearing,distance:6371*2*Math.atan2(Math.sqrt(hav),Math.sqrt(1-hav))};
    }
    function prayerHours(lat,lon,tz,y,m,day){
        validateLocation(lat,lon,tz);const d=gregorianToJD(y,m,day)-2451545;
        const g=mod(357.529+.98560028*d,360),q=mod(280.459+.98564736*d,360),l=mod(q+1.915*Math.sin(rad(g))+.020*Math.sin(rad(2*g)),360),e=23.439-.00000036*d;
        const dec=Math.asin(Math.sin(rad(e))*Math.sin(rad(l))),t=Math.tan(rad(e)/2)**2;
        const eq=4*deg(t*Math.sin(2*rad(l))-2*.0167086*Math.sin(rad(g))+4*.0167086*t*Math.sin(rad(g))*Math.cos(2*rad(l))-.5*t**2*Math.sin(4*rad(l))-1.25*.0167086**2*Math.sin(2*rad(g)));
        const noon=12+tz-lon/15-eq/60,phi=rad(lat);
        function angle(alt){const divisor=Math.cos(phi)*Math.cos(dec);if(Math.abs(divisor)<1e-12)return NaN;const value=(Math.sin(rad(alt))-Math.sin(phi)*Math.sin(dec))/divisor;return value>=-1&&value<=1?deg(Math.acos(value)):NaN;}
        const sun=angle(-.8333)/15,dawn=angle(-20)/15,night=angle(-18)/15,asr=angle(deg(Math.atan(1/(1+Math.tan(Math.abs(phi-dec))))))/15;
        return {imsak:noon-dawn-1/6,fajr:noon-dawn,sunrise:noon-sun,dhuhr:noon+1/30,asr:noon+asr,maghrib:noon+sun+1/30,isha:noon+night};
    }
    function formatHour(x){if(!Number.isFinite(x))return 'Tidak tersedia';const minutes=mod(Math.floor(mod(x,24)*60+.5),1440);return `${String(Math.floor(minutes/60)).padStart(2,'0')}:${String(minutes%60).padStart(2,'0')}`;}
    function localDateString(date=new Date()){return `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,'0')}-${String(date.getDate()).padStart(2,'0')}`;}
    function dateParts(now,zone,offset=0){
        if(!zone){const d=new Date(now.getTime()+validateOffset(offset)*3600000);return {year:d.getUTCFullYear(),month:d.getUTCMonth()+1,day:d.getUTCDate(),hour:d.getUTCHours(),minute:d.getUTCMinutes(),second:d.getUTCSeconds()};}
        const parts=new Intl.DateTimeFormat('en-GB',{timeZone:zone,year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',second:'2-digit',hourCycle:'h23'}).formatToParts(now);
        return Object.fromEntries(parts.filter(x=>x.type!=='literal').map(x=>[x.type,Number(x.value)]));
    }
    function zoneOffset(now,zone){const p=dateParts(now,zone);return (utcDate(p.year,p.month,p.day).getTime()+p.hour*3600000+p.minute*60000+p.second*1000-Math.floor(now.getTime()/1000)*1000)/3600000;}
    function schedule(lat,lon,zone=null,offset=0,now=new Date()){
        const local=dateParts(now,zone,offset),events=[];let times;
        for(const shift of [-1,0,1,2]){
            const d=utcDate(local.year,local.month,local.day+shift),y=d.getUTCFullYear(),m=d.getUTCMonth()+1,day=d.getUTCDate();
            const tz=zone?zoneOffset(new Date(d.getTime()+12*3600000),zone):offset;
            const raw=prayerHours(lat,lon,tz,y,m,day),base=d.getTime()-tz*3600000;
            if(shift===0)times=Object.fromEntries(prayers.map(([key])=>[key,'Tidak tersedia']));
            for(const [key,label]of prayers)if(Number.isFinite(raw[key])){const timestamp=base+Math.floor(raw[key]*60+.5)*60000;events.push({key,label,timestamp});if(shift===0){const p=dateParts(new Date(timestamp),zone,offset);times[key]=`${String(p.hour).padStart(2,'0')}:${String(p.minute).padStart(2,'0')}`;}}
        }
        events.sort((a,b)=>a.timestamp-b.timestamp);
        return {date:`${local.year}-${local.month}-${local.day}`,times,events,offset:zone?zoneOffset(now,zone):offset};
    }
    const api={evaluate,power,applyFunction,displayExpression,formatResult,validateDate,utcDate,gregorianToJD,jdToGregorian,julianDay,isHijriLeap,hijriMonthDays,hijriToJD,jdToHijri,gregorianToHijri,holiday,validateOffset,validateLocation,qibla,prayerHours,formatHour,localDateString,dateParts,zoneOffset,schedule,prayers};
    root.DestaEngine=api;if(typeof module!=='undefined')module.exports=api;
})(globalThis);
