"""Original lightweight wireframe face, driven by local speech events."""
import json
import streamlit as st
from voice_output import speech_markup

FACE_HTML = """<canvas id="face" width="360" height="410" role="img" aria-label="Original animated JARVIS wireframe face"></canvas>
<div id="face-state" role="status" aria-live="polite" style="text-align:center;color:#75edeb;letter-spacing:2px;margin:8px">JARVIS / READY</div>
<p style="font-size:10px;color:#8fa9bd;text-align:center">Animated face. Mouth movement follows spoken words; lip-sync is approximate.</p>"""
FACE_JS = r"""<script>
const face=document.getElementById('face'),ctx=face.getContext('2d'),faceState=document.getElementById('face-state');
const reduced=REDUCED_MOTION||matchMedia('(prefers-reduced-motion: reduce)').matches;
const initialState=INITIAL_STATE;
let phase=initialState,mouthUntil=0,last=0,animation,frames=0,boundaries=0,dirty=true;
face.style.width='100%';face.style.height='350px';face.style.maxHeight='350px';face.style.objectFit='contain';
function setPhase(value){dirty=true;phase=value;face.dataset.phase=value;mouthUntil=0;faceState.textContent='JARVIS / '+value.toUpperCase();}
setPhase(initialState);
window.addEventListener('jarvis-speech',event=>setPhase(event.detail==='ready'?initialState:event.detail));
window.addEventListener('jarvis-boundary',()=>{if(phase==='speaking'&&!reduced){mouthUntil=performance.now()+160;face.dataset.speechBoundaries=String(++boundaries);}});
function draw(time){
 animation=requestAnimationFrame(draw);
 if(document.hidden||time-last<1000/24||(reduced&&!dirty))return;last=time;dirty=false;
 const turn=reduced?0:Math.sin(time/4200)*6;
 const lift=reduced?0:Math.sin(time/2400)*2;
 const blink=!reduced&&time%5200<130;
 const opening=phase==='speaking'&&time<mouthUntil?6:0;
 face.dataset.frames=String(++frames);face.dataset.mouth=opening?'open':'closed';
 ctx.clearRect(0,0,360,410);ctx.save();ctx.translate(180+turn,195+lift);
 ctx.strokeStyle='#4de2ed';ctx.lineWidth=.7;ctx.shadowColor='#2aaeea';ctx.shadowBlur=2;
 // Independent latitude/longitude facial mesh, no external artwork or model.
 const rows=15,cols=12,points=[];
 for(let row=0;row<=rows;row++){
  const latitude=-Math.PI/2+row*Math.PI/rows;
  const y=Math.sin(latitude)*145;
  const width=Math.cos(latitude)*(row>9?87:104);
  const line=[];
  for(let col=0;col<=cols;col++){
   const longitude=-Math.PI/2+col*Math.PI/cols;
   const x=Math.sin(longitude)*width;
   const depth=Math.cos(longitude)*Math.cos(latitude);
   line.push([x+turn*depth,y+depth*7]);
  }
  points.push(line);
 }
 function segment(a,b){ctx.beginPath();ctx.moveTo(...a);ctx.lineTo(...b);ctx.stroke();}
 function wire(a,b){ctx.moveTo(...a);ctx.lineTo(...b);}
 ctx.beginPath();
 for(let r=0;r<=rows;r++)for(let c=0;c<=cols;c++){
  if(c<cols)wire(points[r][c],points[r][c+1]);
  if(r<rows)wire(points[r][c],points[r+1][c]);
  if(r<rows&&c<cols)wire(points[r][c],points[r+1][c+1]);
 }
 ctx.stroke();
 // Eyes, brows, nose and lips remain legible over the mesh.
 ctx.shadowBlur=12;ctx.lineWidth=2;ctx.strokeStyle='#b9ffff';
 for(const side of [-1,1]){
  ctx.beginPath();ctx.ellipse(side*40,-22,20,blink?1:7,0,0,Math.PI*2);ctx.stroke();
  if(!blink){ctx.fillStyle='#d4ffff';ctx.beginPath();ctx.arc(side*40+turn*.2,-22,3,0,Math.PI*2);ctx.fill();}
  segment([side*23,-44],[side*59,-41]);
 }
 ctx.lineWidth=1;segment([0,-15],[-9,28]);segment([-9,28],[10,28]);
 ctx.beginPath();ctx.ellipse(0,60,25,2+opening,0,0,Math.PI*2);ctx.stroke();
 segment([-40,129],[-49,171]);segment([40,129],[49,171]);
 segment([-49,171],[-100,191]);segment([49,171],[100,191]);
 ctx.restore();
}
animation=requestAnimationFrame(draw);
window.addEventListener('pagehide',()=>cancelAnimationFrame(animation));
</script>"""


def moving_face_markup(text, state="ready", reduced_motion=False):
    state={"thinking":"processing", "transcribing":"transcribing", "error":"needs attention"}.get(state,"ready")
    markup=speech_markup(text or "Hello. I am JARVIS. My voice and movement controls are ready.","Speak latest reply" if text else "Test face and voice")
    markup=markup.replace('<button id="speak"',FACE_HTML+'<button id="speak"',1)
    script=FACE_JS.replace('REDUCED_MOTION',json.dumps(bool(reduced_motion))).replace('INITIAL_STATE',json.dumps(state))
    return markup.replace('</body>',script+'</body>')


def render_moving_face(text="", state="ready", reduced_motion=False):
    st.iframe(moving_face_markup(text,state,reduced_motion),height=580,alt="Animated JARVIS face with local speech and interrupt controls")
