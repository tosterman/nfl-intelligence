"""Research-only joint score reconciliation; not a validated football simulator."""
import numpy as np

def reconcile_scores(prior,home_mean,away_mean,tie_probability):
    """KL tilt over existing integer score support, with fixed total tie mass.

    Rows are home scores, columns away scores, starting at zero. Boundary or
    infeasible constraints fail; no clipping, new support or fallback forecast.
    """
    mass=np.array(prior,dtype=float,copy=True)
    target=np.array([home_mean,away_mean],dtype=float)
    if mass.ndim!=2 or min(mass.shape)<2 or not np.isfinite(mass).all() or (mass<0).any() or not np.isfinite(target).all() or not np.isfinite(tie_probability) or not 0<=tie_probability<1:raise ValueError('Invalid joint-score inputs')
    h,a=np.indices(mass.shape);features=np.stack([h,a],axis=-1)
    groups=[]
    for mask,weight in [(h==a,tie_probability),(h!=a,1-tie_probability)]:
        if weight==0:continue
        support=mask&(mass>0)
        if not support.any():raise ValueError('Required settlement support absent')
        groups.append((support,weight,features[support].astype(float),np.log(mass[support])))
    lower=sum(w*x.min(axis=0) for _,w,x,_ in groups);upper=sum(w*x.max(axis=0) for _,w,x,_ in groups)
    if (target<=lower).any() or (target>=upper).any():raise ValueError('Target outside strict attainable bounds')
    def evaluate(theta):
        mean=np.zeros(2);cov=np.zeros((2,2));objective=-float(theta@target);distributions=[]
        for support,w,x,logs in groups:
            z=logs+x@theta;peak=z.max();p=np.exp(z-peak);normalizer=p.sum();p/=normalizer
            mu=p@x;centered=x-mu
            mean+=w*mu;cov+=w*(centered.T@(centered*p[:,None]));objective+=w*(peak+np.log(normalizer))
            distributions.append((support,w*p))
        return mean,cov,objective,distributions
    theta=np.zeros(2)
    for _ in range(100):
        mean,cov,objective,distributions=evaluate(theta);error=mean-target
        if np.max(np.abs(error))<1e-9:
            result=np.zeros_like(mass)
            for support,p in distributions:result[support]=p
            return result
        try:step=np.linalg.solve(cov,error)
        except np.linalg.LinAlgError:raise ValueError('Degenerate joint-score support') from None
        if not np.isfinite(step).all():raise ValueError('Unstable joint-score constraints')
        accepted=False
        for power in range(40):
            candidate=theta-step*(.5**power)
            candidate_mean,_,candidate_objective,_=evaluate(candidate)
            if candidate_objective<objective and np.isfinite(candidate_objective) or np.linalg.norm(candidate_mean-target)<np.linalg.norm(error)*.5:
                theta=candidate;accepted=True;break
        if not accepted:raise ValueError('Joint-score constraints did not converge')
    raise ValueError('Joint-score iteration limit exceeded')
