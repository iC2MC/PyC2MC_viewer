from warnings import warn
from ._venn import generate_petal_labels, draw_venn
from functools import partial

OLD_COLORS = [
    [.36, .75, .38, .50],
    [.35, .61, .83, .50],
    [.96, .93, .34, .60],
    [.95, .35, .38, .40],
    [.99, .46, .00, .30],
    [.32, .32, .75, .20]
]

def get_labels(data, fill=["number"]):
    warn((
        "`get_labels()` is retained for backwards compatibility; " +
        "use `generate_petal_labels()` or the higher level `venn()` instead"
    ))
    fmt = ""
    if "logic" in fill:
        fmt += "{logic}: "
    if "number" in fill:
        fmt += "{size} "
    if "percent" in fill:
        fmt += "({percentage:.1f}%)"
    return generate_petal_labels(data, fmt)

def vennx(labels, names, colors=OLD_COLORS, figsize=(9, 9), dpi=None, fontsize=14):
    n_sets = len(names)
    warn((
        "`venn{}()` is retained for backwards compatibility; ".format(n_sets) +
        "use `venn()` instead"
    ))
    if dpi is not None:
        warn("Option `dpi` is deprecated and has no effect")
    ax = draw_venn(
        petal_labels=labels, dataset_labels=names, hint_hidden=False,
        colors=colors, figsize=figsize, fontsize=fontsize,
        legend_loc="best", ax=None
    )
    return ax.figure, ax

venn2 = partial(vennx, names=["AB"])
venn3 = partial(vennx, names=["ABC"])
venn4 = partial(vennx, names=["ABCD"])
venn5 = partial(vennx, names=["ABCDE"])
venn6 = partial(vennx, names=["ABCDEF"])
