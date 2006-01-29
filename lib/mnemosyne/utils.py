def clean(s, maxwords=None):
    words = s.strip().lower().split()
    if maxwords: words = words[:maxwords]
    words = [''.join([c for c in w if c.isalnum()]) for w in words]
    return '-'.join(words)

u = {}
def unique(e, ns, k):
    if not u.has_key(ns): u[ns] = {}
    ns = u[ns]

    # XXX: aaaaaaaaaaaaaaaaaaagh MY EYES
    while True:
        if ns.has_key(k):
            if ns[k] == e.id:
                return k
            else:
                c = k.split('-')
                try:
                    serial = int(c[-1])
                    c[-1] = str(serial + 1)
                    k = '-'.join(c)
                except ValueError:
                    k += '-1'
        else:
            ns[k] = e.id
            return k
