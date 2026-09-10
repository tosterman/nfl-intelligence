"""Create locally served WOFF2 subsets from the licensed original typefaces."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.tools'))
from fontTools import subset
from fontTools.ttLib import TTFont
for path in (ROOT/'data/raw/font-originals').glob('*.ttf'):
    font=TTFont(path);options=subset.Options();options.flavor='woff2';options.layout_features=['*']
    sub=subset.Subsetter(options=options);sub.populate(unicodes=list(range(32,384))+list(range(0x2000,0x2070))+list(range(0x2190,0x2200)));sub.subset(font)
    output=ROOT/'public/fonts'/path.with_suffix('.woff2').name
    font.flavor='woff2';font.save(output)
    print(path.name,path.stat().st_size,'->',output.stat().st_size)
