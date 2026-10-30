"""Card rollout steps. `show`: ids of the last released batch + progress. `next`: release up to 100 more ids on a card boundary, rebuild, push."""
import json, subprocess, sys
m = json.load(open('manifest.json')); o = [l.strip() for l in open('rollout_order.txt')]
n = int(open('img_count.txt').read()); prev = int(open('img_prev.txt').read())
if sys.argv[1] == 'show':
    print(json.dumps({'released': n, 'total': len(o), 'done': n >= len(o), 'batch': o[prev:n]}))
elif sys.argv[1] == 'next':
    e = n
    while e < len(o):
        h = m[o[e]]['hash']; f = e
        while f < len(o) and m[o[f]]['hash'] == h: f += 1
        if f > n + 100: break
        e = f
    open('img_prev.txt', 'w').write(str(n)); open('img_count.txt', 'w').write(str(e))
    subprocess.run(['python3', 'build.py', '--max', '80'], check=True)
    subprocess.run('git add -A img_count.txt img_prev.txt feed manifest.json bad_images.json', shell=True, check=True)
    subprocess.run(['git', 'commit', '-q', '-m', f'Rollout: {e} of {len(o)} products live\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>'], check=True)
    subprocess.run('git pull -q --rebase --autostash origin main && git push -q origin main', shell=True, check=True)
    print(n, '->', e)
