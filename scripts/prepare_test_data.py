"""Fetch source inputs needed by CI without changing published predictions."""
from concurrent.futures import ThreadPoolExecutor
import refresh
import experiment_model

if __name__=='__main__':
    refresh.acquire()
    experiment_model.RAW.mkdir(parents=True,exist_ok=True)
    with ThreadPoolExecutor(max_workers=5) as pool:list(pool.map(experiment_model.download,range(2010,2027)))
