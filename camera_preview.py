"""Explicitly started browser-only camera preview. No frame capture or uploads."""
import streamlit as st

CAMERA_HTML = r"""<!doctype html><html><head><style>
body{margin:0;background:#080e1b;color:#cee6ef;font:12px system-ui}button{padding:9px;margin:5px 5px 8px 0;background:#12253b;border:1px solid #59aebe;border-radius:5px;color:#dcf7ff}video{width:100%;max-height:240px;background:#020711;border-radius:8px;transform:scaleX(-1)}p{line-height:1.5}#status{color:#84d9db}
</style></head><body>
<button id="start">Start local camera</button><button id="stop">Stop camera</button>
<p id="status" role="status" aria-live="polite">Camera off</p>
<video id="preview" autoplay muted playsinline aria-label="Local camera preview"></video>
<p>Browser preview only. No recording, saved image, upload or AI analysis.</p>
<script>
const video=document.getElementById('preview'),status=document.getElementById('status'),start=document.getElementById('start');
let stream=null,generation=0,pending=false;
function stopCamera(){
 generation++;
 if(stream){stream.getTracks().forEach(track=>track.stop());stream=null;}
 video.srcObject=null;start.disabled=pending;status.textContent=pending?'Camera off. A browser permission request is still pending; close these controls to reset.':'Camera off';
}
start.onclick=async()=>{
 if(pending)return;
 const attempt=++generation;pending=true;start.disabled=true;status.textContent='Waiting for camera permission';
 const timer=setTimeout(()=>{if(attempt===generation&&!stream){generation++;status.textContent='Camera did not start. Browser permission or device access is unresolved. Close and reopen these controls to reset.';}},20000);
 try{
  const incoming=await navigator.mediaDevices.getUserMedia({video:{width:{ideal:640},height:{ideal:480}},audio:false});
  if(attempt!==generation||document.hidden){incoming.getTracks().forEach(track=>track.stop());status.textContent='Camera off';return;}
  stream=incoming;video.srcObject=stream;
  stream.getVideoTracks().forEach(track=>track.addEventListener('ended',stopCamera,{once:true}));
  await video.play();status.textContent='Camera active — local preview only';
 }catch(error){
  if(attempt!==generation){status.textContent='Camera off';return;}
  stopCamera();
  const messages={NotAllowedError:'Camera permission denied. Camera remains off.',NotFoundError:'No camera found.',NotReadableError:'Camera is busy or unavailable.'};
  status.textContent=messages[error.name]||'Camera preview unavailable. Camera remains off.';
 }finally{clearTimeout(timer);pending=false;start.disabled=Boolean(stream);}
};
document.getElementById('stop').onclick=stopCamera;
window.addEventListener('pagehide',stopCamera);
window.addEventListener('beforeunload',stopCamera);
document.addEventListener('visibilitychange',()=>{if(document.hidden)stopCamera();});
</script></body></html>"""


def render_camera_preview():
    st.iframe(CAMERA_HTML,height=390,alt="Opt-in local camera preview; no AI image analysis")
