"""Push an archived publication without discarding concurrent branch changes."""
import os
import subprocess


def push_archive(branch,run=subprocess.run,attempts=3):
    if not branch or branch.startswith('-'):
        raise ValueError('A branch name is required')
    for attempt in range(attempts):
        if run(['git','push','origin',f'HEAD:refs/heads/{branch}'],check=False).returncode==0:
            return
        if attempt==attempts-1:
            break
        run(['git','fetch','origin',f'refs/heads/{branch}'],check=True)
        result=run(['git','rebase','FETCH_HEAD'],check=False)
        if result.returncode:
            run(['git','rebase','--abort'],check=True)
            raise RuntimeError('Publication archive conflicts with remote history. Recover from the uploaded release bundle; no remote history was overwritten.')
    raise RuntimeError('Publication archive push failed. Deployment may already be public; recover the ledger and receipt from the uploaded release bundle.')


if __name__=='__main__':
    push_archive(os.environ.get('GITHUB_REF_NAME',''))
