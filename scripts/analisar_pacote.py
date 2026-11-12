import sys,glob,os,numpy as np,librosa,pyloudnorm as pyln,collections,json
def ana(f):
    y,sr=librosa.load(f,sr=48000,mono=False);m=y if y.ndim==1 else y.mean(0);st=y if y.ndim==2 else np.stack([y,y])
    d=len(m)/sr;pk=20*np.log10(np.abs(y).max()+1e-9)
    try: L=pyln.Meter(sr).integrated_loudness(st.T)
    except: L=-99
    S=np.abs(librosa.stft(m,n_fft=4096))**2;fr=librosa.fft_frequencies(sr=sr,n_fft=4096);E=S.sum(1)
    low=E[fr<120].sum()/E.sum();hi=E[fr>6000].sum()/E.sum();cen=(fr*E).sum()/E.sum()
    rms=librosa.feature.rms(y=m)[0];crest=pk-20*np.log10(rms.max()+1e-9)
    corr=np.corrcoef(st[0],st[1])[0,1] if st[0].std()>0 and st[1].std()>0 else 1
    return dict(d=d,pk=pk,L=L,low=low,hi=hi,cen=cen,crest=crest,corr=corr)
res={}
for f in sorted(glob.glob(sys.argv[1]+'/**/*.*',recursive=True)):
    if f.lower().endswith(('.wav','.mp3')):
        try: res[f]=ana(f)
        except Exception as e: print('ERR',f,e)
json.dump(res,default=float,fp=open(sys.argv[2],"w"))
g=collections.defaultdict(list)
for f,r in res.items(): g[os.path.relpath(os.path.dirname(f),sys.argv[1])].append(r)
print(f"{'grupo':28s} n   dur   pico  LUFS  grave% agudo% centro crest corrLR")
for k,v in g.items():
    a=lambda x:np.median([r[x] for r in v])
    print(f"{k[:28]:28s}{len(v):3d} {a('d'):5.1f} {a('pk'):5.1f} {a('L'):6.1f} {100*a('low'):5.1f} {100*a('hi'):5.1f} {a('cen'):6.0f} {a('crest'):5.1f} {a('corr'):5.2f}")
