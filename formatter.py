import json

def render(response):

    # The transport layer normally returns a str.
    # Keep support for bytes in case a raw Reticulum response is passed here.

    if isinstance(response,bytes): response=response.decode()
    if isinstance(response,str): response=json.loads(response)
    if not response.get('ok',False):
        return 'SQL error: '+response.get('error','Unknown error')
    
    # Extract columns and rows from the query response.
    cols=response.get('columns',[])
    rows=response.get('rows',[])

    # If there are no columns, the query was not a SELECT
    # and did not return a result set.
    if not cols:
        return f"OK ({response.get('rows_affected',0)} rows affected)"
    
    # Start each column width with the length of its column name.
    w=[len(str(c)) for c in cols]

    # Expand each column width to fit the longest value in that column.
    for r in rows:
        for i,v in enumerate(r): w[i]=max(w[i],len(str(v)))
    out=[]
    out.append('  '.join(str(c).ljust(w[i]) for i,c in enumerate(cols)))
    out.append('  '.join('-'*x for x in w))
    for r in rows:
        out.append('  '.join(str(v).ljust(w[i]) for i,v in enumerate(r)))
    out.append('')
    out.append(f"{len(rows)} row{'s' if len(rows)!=1 else ''} returned")
    return '\n'.join(out)
