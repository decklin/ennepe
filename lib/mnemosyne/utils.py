def clean(s, maxwords=None):
    words = s.strip().lower().split()
    if maxwords: words = words[:maxwords]
    words = [''.join([c for c in w if c.isalnum()]) for w in words]
    return '-'.join(words)

u = {}
def unique(namespace, k, id):
    u.setdefault(namespace, {})
    ns = u[namespace]

    try:
        assert ns[k] == id
    except KeyError:
        ns[k] = id
    except AssertionError:
        while ns.has_key(k):
            components = k.split('-')
            try:
                serial = int(components[-1])
                components[-1] = str(serial + 1)
                k = '-'.join(components)
            except ValueError:
                k += '-1'
        ns[k] = id

    return k
