"""Read-only existing SSH-profile probe; no credentials/configuration changes."""
import base64
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / '.local/m2-selective-compute-20261108-v1'


def new(name, data):
    with (PRIVATE / name).open('x', encoding='utf-8') as f:
        json.dump(data,f,indent=2); f.write('\n')


profiles = {}
for profile in ('dr-train','100.77.149.83'):
    result = subprocess.run(['rtk','proxy','ssh','-G',profile],capture_output=True,text=True,timeout=10)
    values = {}
    identities = []
    for line in result.stdout.splitlines():
        row = line.split(maxsplit=1)
        if len(row) != 2: continue
        if row[0] in ('hostname','user','port'): values[row[0]] = row[1]
        if row[0] == 'identityfile': identities.append(row[1])
    values['identityfile_names'] = identities
    profiles[profile] = values
usable = [p for p in profiles if profiles[p].get('user')=='chaw' and
          profiles[p].get('hostname') in ('dr-train','100.77.149.83') and
          any('id_ed25519_dr_train' in i for i in profiles[p]['identityfile_names'])]
assert usable, 'NO_MATCHING_EXISTING_PROFILE'
profile = usable[0]
known = subprocess.run(['rtk','proxy','ssh-keygen','-F',profiles[profile]['hostname']],capture_output=True,text=True,timeout=10)
new('existing-ssh-profile.json', {'selected_profile':profile,'effective_profiles':profiles,
    'known_host_lookup_exit':known.returncode,'private_key_contents_read':False,'config_changed':False})
assert known.returncode == 0, 'NO_EXISTING_KNOWN_HOST_ENTRY'
code = '''import importlib.metadata,json,os,pwd,resource,shutil,signal
from pathlib import Path
resource.setrlimit(resource.RLIMIT_CPU,(5,6));resource.setrlimit(resource.RLIMIT_AS,(268435456,268435456))
signal.alarm(15)
cpus=sorted(os.sched_getaffinity(0));os.sched_setaffinity(0,{cpus[-1]});os.nice(19)
packages={}
for name in ('numpy','scipy','scikit-learn','joblib','threadpoolctl'):
 try:packages[name]=importlib.metadata.version(name)
 except importlib.metadata.PackageNotFoundError:packages[name]=None
memory={}
for line in Path('/proc/meminfo').read_text().splitlines():
 key,value=line.split(':',1)
 if key in ('MemAvailable','MemTotal'):memory[key]=int(value.split()[0])*1024
print(json.dumps({'user':pwd.getpwuid(os.getuid()).pw_name,'hostname':os.uname().nodename,
 'cpus':cpus,'memory':memory,'disk_free_bytes':shutil.disk_usage(Path.home()).free,
 'packages':packages,'fresh_root_exists':(Path.home()/'curaloop-tasks/m2-selective-compute-20261108-v1').exists(),
 'tools':{n:shutil.which(n) for n in ('python3','systemd-run','systemctl')},
 'python':__import__('sys').version,'cpu_seconds':__import__('time').process_time()}))
'''
encoded = base64.b64encode(code.encode()).decode()
command = "python3 -c 'exec(__import__(\"base64\").b64decode(\""+encoded+"\"))'"
run = subprocess.run(['rtk','proxy','ssh','-o','BatchMode=yes','-o','IdentitiesOnly=yes',
    '-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=10','-o','ConnectionAttempts=1',
    profile,command],capture_output=True,text=True,timeout=30)
new('ssh-probe-raw.json',{'exit_code':run.returncode,'stdout':run.stdout,'stderr':run.stderr})
assert run.returncode == 0, 'SSH_PROBE_FAILED_RETAINED_ERROR'
data=json.loads(next(s for s in run.stdout.splitlines() if s.startswith('{')))
assert data['user']=='chaw' and data['hostname']=='dr-train'
assert data['fresh_root_exists'] is False
assert data['memory']['MemAvailable'] > 16*1024**3 and data['disk_free_bytes'] > 4*1024**3
new('remote-read-only-admission.json',data)
print(json.dumps({'profile':profile,'user':data['user'],'hostname':data['hostname'],
    'free_memory_bytes':data['memory']['MemAvailable'],'packages':data['packages'],
    'fresh_root_exists':data['fresh_root_exists'],'python':data['python']}))
