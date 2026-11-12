import sys,json,subprocess,numpy as np
from scipy.io import wavfile
st,out,db=sys.argv[1],sys.argv[2],float(sys.argv[3])
r=lambda n:wavfile.read(f'{st}/{n}.wav')
sr,v=r('voz');_,m=r('trilha_3d');_,s=r('sfx_3d')
mix=(v+m+s*10**(db/20)).astype(np.float32);pre=f'{out}/pre.wav';wavfile.write(pre,sr,mix)
x=subprocess.run(['ffmpeg','-hide_banner','-i',pre,'-af','loudnorm=I=-14:TP=-1:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True).stderr
j=json.loads(x[x.rindex('{'):x.rindex('}')+1])
ln=f"loudnorm=I=-14:TP=-1:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true"
subprocess.run(['ffmpeg','-y','-v','error','-i',pre,'-af',f'{ln},aresample={sr}','-c:a','pcm_s24le',f'{out}/mix.wav'],check=True)
print(sr,j['input_i'])
