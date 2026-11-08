"""Fresh read-only profile admission using the unchanged configured identity."""
import base64,json,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];TASK=ROOT/'.local/m2-cpu-profile-20261108-v1'


def new(name,data):
    with (TASK/name).open('x',encoding='utf-8') as f:json.dump(data,f,indent=2);f.write('\n')


def main():
    old=json.loads((ROOT/'.local/m2-selective-compute-20261108-v1/existing-ssh-profile.json').read_text())
    profile=old['selected_profile']
    r=subprocess.run(['rtk','proxy','ssh','-G',profile],capture_output=True,text=True,timeout=10)
    values={};identities=[]
    for line in r.stdout.splitlines():
        row=line.split(maxsplit=1)
        if len(row)!=2:continue
        if row[0]in('user','hostname','port'):values[row[0]]=row[1]
        if row[0]=='identityfile':identities.append(row[1])
    assert values.get('user')=='chaw' and values.get('hostname')in('100.77.149.83','dr-train')
    assert any('id_ed25519_dr_train' in name for name in identities)
    new('ssh-profile.json',{'selected_profile':profile,**values,'identityfile_names':identities,
                          'private_key_read':False,'configuration_changed':False})
    code='''import json,os,pwd,resource,shutil,signal,sys
from pathlib import Path
resource.setrlimit(resource.RLIMIT_CPU,(5,5));resource.setrlimit(resource.RLIMIT_AS,(268435456,268435456));signal.alarm(15)
cpus=sorted(os.sched_getaffinity(0));cpu=cpus[-3] if len(cpus)>=3 else cpus[0];os.sched_setaffinity(0,{cpu})
roots=[Path.home()/'curaloop-tasks'/n for n in ('m2-cpu-profile-20261108-v1','m2-selective-compute-20261108-v1','m2-selective-compute-20261108-v1-export-v1')]
memory={}
for line in Path('/proc/meminfo').read_text().splitlines():
 k,v=line.split(':',1)
 if k in('MemAvailable','MemTotal'):memory[k]=int(v.split()[0])*1024
model=next((s.split(':',1)[1].strip() for s in Path('/proc/cpuinfo').read_text().splitlines() if s.startswith('model name')),None)
print(json.dumps({'user':pwd.getpwuid(os.getuid()).pw_name,'hostname':os.uname().nodename,'cpu_choice':cpu,
 'cpu_model':model,'available_cpus':cpus,'python':sys.version,'memory':memory,'disk_free_bytes':shutil.disk_usage(Path.home()).free,
 'roots_absent':all(not p.exists() and not p.is_symlink() for p in roots),'roots_checked':[str(p) for p in roots]}))
'''
    b64=base64.b64encode(code.encode()).decode()
    cmd="python3 -B -c 'exec(__import__(\"base64\").b64decode(\""+b64+"\"))'"
    r=subprocess.run(['rtk','proxy','ssh','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes',
        '-o','ConnectTimeout=10','-o','ConnectionAttempts=1',profile,cmd],capture_output=True,text=True,timeout=30)
    new('read-only-probe-raw.json',{'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
    assert r.returncode==0,'SSH_ADMISSION_FAILED_RETAINED_ERROR'
    data=json.loads(r.stdout)
    assert data['user']=='chaw' and data['hostname']=='dr-train' and data['roots_absent']
    assert data['memory']['MemAvailable']>8*1024**3 and data['disk_free_bytes']>1024**3
    new('read-only-admission.json',data)
    print(json.dumps({'status':'PASS_READ_ONLY_ADMISSION','cpu':data['cpu_choice'],'cpu_model':data['cpu_model'],'roots_absent':True}))


if __name__=='__main__':main()
