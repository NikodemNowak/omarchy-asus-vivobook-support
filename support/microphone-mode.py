#!/usr/bin/env python3
"""Optional session-only PipeWire echo cancellation; preserve previous defaults."""
import json, os, pathlib, subprocess, sys, fcntl
runtime=pathlib.Path(os.environ['XDG_RUNTIME_DIR'])
state=runtime/'vivobook-microphone-mode.json'
def call(*args):
    return subprocess.check_output(['pactl', *args], text=True).strip()
def modules():
    return [{'index': line.split()[0]} for line in call('list','short','modules').splitlines()
            if line.split() and line.split()[0].isdigit() and 'module-echo-cancel' in line
            and 'source_name=vivobook_conference_mic' in line]
with (runtime/'vivobook-microphone-mode.lock').open('w') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX)
    mode=sys.argv[1]
    if mode=='conference':
        if state.exists():
            old=json.loads(state.read_text())
            if any(str(m['index'])==old['module'] for m in modules()):
                sys.exit(0)
            state.unlink()
        old={'source':call('get-default-source'),'sink':call('get-default-sink')}
        muted=call('get-source-mute',old['source']).endswith('yes')
        old['module']=call('load-module','module-echo-cancel',
            'source_name=vivobook_conference_mic','sink_name=vivobook_conference_output',
            'source_master='+old['source'],'sink_master='+old['sink'],
            'source_properties=device.description=Vivobook-Conference-Microphone',
            'sink_properties=device.description=Vivobook-Conference-Speakers',
            'aec_method=webrtc','rate=48000','channels=1','channel_map=mono')
        state.write_text(json.dumps(old))
        try:
            call('set-source-mute','vivobook_conference_mic','1' if muted else '0')
            call('set-default-source','vivobook_conference_mic')
            call('set-default-sink','vivobook_conference_output')
        except Exception:
            call('unload-module',old['module'])
            call('set-default-source',old['source'])
            call('set-default-sink',old['sink'])
            state.unlink()
            raise
    elif mode=='normal':
        if state.exists():
            old=json.loads(state.read_text())
            available=[str(m['index']) for m in modules()]
            if old['module'] in available:
                muted=call('get-source-mute','vivobook_conference_mic').endswith('yes')
                call('set-source-mute',old['source'],'1' if muted else '0')
                call('unload-module',old['module'])
            call('set-default-source',old['source'])
            call('set-default-sink',old['sink'])
            state.unlink()
    else:
        raise SystemExit('Usage: microphone-mode.py normal|conference')
