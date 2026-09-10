"""Fixed descriptive calibration bins; no fitting or threshold selection."""
import math

def calibration_bins(records):
    for record in records:
        p=record['probability'];outcome=record['outcome']
        if not math.isfinite(p) or not 0<=p<=1 or outcome not in (0,1):
            raise ValueError('Calibration requires finite probabilities and decisive binary outcomes')
    result=[]
    # Match the established retrospective display, fixed before live results.
    for lower,upper in [(0,.4),(.4,.5),(.5,.6),(.6,.7),(.7,1)]:
        group=[r for r in records if lower<=r['probability'] and (r['probability']<upper or upper==1 and r['probability']==1)]
        if not group:continue
        n=len(group);observed=sum(r['outcome'] for r in group)/n;z=1.96
        denominator=1+z*z/n
        center=(observed+z*z/(2*n))/denominator
        half=z*math.sqrt(observed*(1-observed)/n+z*z/(4*n*n))/denominator
        result.append({'lower':lower,'upper':upper,'count':n,'predicted':sum(r['probability'] for r in group)/n,'observed':observed,
            'observedLow95':max(0,center-half),'observedHigh95':min(1,center+half)})
    return result
