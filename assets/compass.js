/* Sensor lifecycle with cancellable generations; can be tested without hardware. */
(function(root){
    'use strict';
    class Compass {
        constructor(env,callbacks={}){this.env=env;this.callbacks=callbacks;this.generation=0;this.active=false;this.pending=false;this.valid=false;this.timer=null;this.source=null;this.listener=e=>this.orientation(e);}
        status(message){this.callbacks.status?.(message);}
        stop(message='Kompas dijeda. Referensi utara sejati di atas.'){
            this.generation++;this.active=false;this.pending=false;this.valid=false;this.source=null;
            this.env.window.removeEventListener('deviceorientation',this.listener,true);this.env.window.removeEventListener('deviceorientationabsolute',this.listener,true);
            this.env.clearTimeout(this.timer);this.timer=null;this.callbacks.reset?.();this.status(message);
        }
        async start(){
            this.stop('Meminta lokasi dan izin sensor…');const generation=this.generation;this.pending=true;this.status('Meminta lokasi dan izin sensor…');
            const orientation=this.env.window.DeviceOrientationEvent;
            let permission;
            try{permission=orientation?.requestPermission?orientation.requestPermission():Promise.resolve('granted');}catch(error){permission=Promise.resolve('denied');}
            // Attach a rejection handler immediately, even while GPS is pending.
            permission=Promise.resolve(permission).catch(()=> 'denied');
            try{
                const position=await new Promise((resolve,reject)=>{
                    if(!this.env.navigator.geolocation){reject(Error('GPS tidak tersedia. Gunakan koordinat manual.'));return;}
                    this.env.navigator.geolocation.getCurrentPosition(resolve,reject,{enableHighAccuracy:true,timeout:10000,maximumAge:0});
                });
                if(generation!==this.generation)return;
                this.callbacks.location?.(position);
                const grant=await permission;if(generation!==this.generation)return;
                this.pending=false;if(grant!=='granted'){this.status('Izin sensor ditolak. Arah statis tetap tersedia.');return;}
                this.active=true;this.status('Menunggu heading absolut perangkat…');
                this.env.window.addEventListener('deviceorientationabsolute',this.listener,true);this.env.window.addEventListener('deviceorientation',this.listener,true);this.watch(generation);
            }catch(error){if(generation===this.generation)this.stop(`Lokasi belum diperoleh: ${error.message || 'izin ditolak'}. Gunakan koordinat manual.`);}
        }
        watch(generation){this.env.clearTimeout(this.timer);this.timer=this.env.setTimeout(()=>{if(generation!==this.generation)return;this.valid=false;this.callbacks.reset?.();this.status('Heading absolut tidak tersedia atau berhenti. Gunakan arah statis.');},3000);}
        orientation(event){
            if(!this.active)return;
            let heading,source;
            if(Number.isFinite(event.webkitCompassHeading)){
                if(Number.isFinite(event.webkitCompassAccuracy)&&(event.webkitCompassAccuracy<0||event.webkitCompassAccuracy>35)){this.valid=false;this.callbacks.reset?.();this.status('Sensor kurang akurat. Jauhkan logam dan gerakkan perangkat membentuk angka 8.');return;}
                heading=event.webkitCompassHeading;source='webkit';
            }else if(event.absolute===true&&Number.isFinite(event.alpha)){
                if(this.source==='webkit')return;
                source='absolute';
                // Require the device to be flat: avoid claiming unsupported 3D accuracy.
                if(Math.abs(event.beta||0)>15||Math.abs(event.gamma||0)>15){this.valid=false;this.callbacks.reset?.();this.status('Letakkan perangkat mendatar untuk membaca kompas.');return;}
                heading=360-event.alpha;
            }else return;
            const screen=this.env.window.screen?.orientation?.angle||0;
            heading=((heading+screen)%360+360)%360;this.source=source;this.valid=true;this.watch(this.generation);this.callbacks.heading?.(heading);
        }
    }
    root.DestaCompass=Compass;if(typeof module!=='undefined')module.exports=Compass;
})(globalThis);
